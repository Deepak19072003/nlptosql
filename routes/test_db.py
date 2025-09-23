from fastapi import APIRouter, HTTPException
import logging
import psycopg
from psycopg_pool import ConnectionPool
from psycopg.rows import dict_row

from settings import settings


router = APIRouter(prefix="/test/db", tags=["test"])
logger = logging.getLogger("nl2sql")


pool = ConnectionPool(conninfo=settings.database_url, min_size=1, max_size=5, kwargs={"connect_timeout": 10})


def get_conn():
    conn = pool.getconn()
    with conn.cursor() as cur:
        cur.execute("SET SESSION CHARACTERISTICS AS TRANSACTION READ ONLY")
        cur.execute(f"SET statement_timeout TO {settings.statement_timeout_ms}")
    return conn


def put_conn(conn):
    if conn:
        pool.putconn(conn)


@router.get("")
def test_db():
    conn = None
    try:
        conn = get_conn()
        with conn:
            with conn.cursor() as cur:
                cur.execute("BEGIN READ ONLY")
                cur.execute("SELECT version(), current_database(), current_user;")
                v, db, usr = cur.fetchone()
        return {"ok": True, "message": "DB is reachable", "version": v, "db": db, "user": usr}
    except Exception as e:
        logger.exception("DB test failed")
        raise HTTPException(status_code=502, detail=f"DB error: {type(e).__name__}: {e}")
    finally:
        if conn:
            put_conn(conn)


