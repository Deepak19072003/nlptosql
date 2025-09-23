# main.py
from fastapi import FastAPI, HTTPException
import logging
from dotenv import load_dotenv, find_dotenv

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import StrOutputParser

from settings import settings
from prompt import SQL_PROMPT
from models import Question
from services import sanitize_sql
from routes.health import router as health_router
from routes.test_llm import router as test_llm_router
from routes.test_db import router as test_db_router

# ---------------------------
# Env
# ---------------------------
load_dotenv(find_dotenv(usecwd=True), override=True)

# ---------------------------
# FastAPI app
# ---------------------------
app = FastAPI(title="NL→SQL API", version="1.0.0")

# Basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("nl2sql")

# keeping DB helpers within test_db route module to avoid duplication here

# ---------------------------
# LLM: Runnable chain (Prompt -> LLM -> String)
# ---------------------------
llm = ChatGoogleGenerativeAI(model=settings.gemini_model or "gemini-1.5-flash", temperature=0, google_api_key=settings.gemini_api_key)

# Alternative: enable custom model via env (commented)
# _llm_kwargs = {
#     "model": GEMINI_MODEL,
#     "temperature": 0,
#     "google_api_key": GEMINI_API_KEY,
# }
# llm = ChatGoogleGenerativeAI(**_llm_kwargs)

chain = SQL_PROMPT | llm | StrOutputParser()

# SQL safety helpers moved to services.py

# ---------------------------
# Routes
# ---------------------------
app.include_router(health_router)

app.include_router(test_llm_router)

app.include_router(test_db_router)

@app.post("/ask")
def ask(q: Question):
    conn = None
    try:
        # 1) Generate SQL
        try:
            generated_sql = chain.invoke({"question": q.question, "max_limit": settings.max_limit}).strip()
        except Exception as e:
            logger.exception("LLM generation failed")
            raise HTTPException(status_code=502, detail=f"LLM error: {type(e).__name__}: {e}")

        # 2) Validate
        try:
            safe_sql = sanitize_sql(generated_sql)
        except ValueError as ve:
            logger.info("Unsafe SQL rejected: %s", ve)
            raise HTTPException(status_code=400, detail=f"Unsafe SQL: {ve}")

        # 3) Execute with psycopg (v3)
        try:
            import psycopg
            from psycopg.rows import dict_row
            from psycopg_pool import ConnectionPool
            pool = ConnectionPool(conninfo=settings.database_url, min_size=1, max_size=5, kwargs={"connect_timeout": 10})
            def get_conn():
                conn_ = pool.getconn()
                with conn_.cursor() as cur:
                    cur.execute("SET SESSION CHARACTERISTICS AS TRANSACTION READ ONLY")
                    cur.execute(f"SET statement_timeout TO {settings.statement_timeout_ms}")
                return conn_
            def put_conn(c):
                if c:
                    pool.putconn(c)
            conn = get_conn()
            with conn:
                with conn.cursor(row_factory=dict_row) as cur:
                    cur.execute("BEGIN READ ONLY")
                    cur.execute(safe_sql)
                    rows = cur.fetchmany(settings.max_limit)
        except Exception as e:
            logger.exception("DB execution failed")
            raise HTTPException(status_code=502, detail=f"DB error: {type(e).__name__}: {e}")

        return {
            "question": q.question,
            "generated_sql": safe_sql,
            "rows": rows,
            "row_count": len(rows),
        }

    finally:
        if conn:
            put_conn(conn)

# ---------------------------
# Dev entrypoint (optional)
# ---------------------------
if __name__ == "__main__":
    # Run: python main.py   (for quick local testing)
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
