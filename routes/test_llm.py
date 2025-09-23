from fastapi import APIRouter, HTTPException
import logging

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import StrOutputParser

from settings import settings
from prompt import SQL_PROMPT


router = APIRouter(prefix="/test/llm", tags=["test"])
logger = logging.getLogger("nl2sql")


llm = ChatGoogleGenerativeAI(model=settings.gemini_model or "gemini-1.5-flash", temperature=0, google_api_key=settings.gemini_api_key)
chain = SQL_PROMPT | llm | StrOutputParser()


@router.get("")
def test_llm():
    try:
        out = chain.invoke({"question": "how many rows are in products?", "max_limit": settings.max_limit})
        return {"ok": True, "message": "LLM is reachable", "sample_sql": out.strip()[:200]}
    except Exception as e:
        logger.exception("LLM test failed")
        raise HTTPException(status_code=502, detail=f"LLM error: {type(e).__name__}: {e}")


