import re
from typing import Set

from settings import settings


danger_keywords = re.compile(
    r"\b(INSERT|UPDATE|DELETE|CREATE|ALTER|DROP|TRUNCATE|GRANT|REVOKE|VACUUM|COPY|CALL|DO|EXECUTE|MERGE)\b",
    re.IGNORECASE,
)


def is_single_statement(sql: str) -> bool:
    return sql.count(";") <= 1


def only_select(sql: str) -> bool:
    return re.match(r"^\s*SELECT\b", sql, re.IGNORECASE) is not None


def ensure_limit(sql: str) -> str:
    if re.search(r"\bLIMIT\b", sql, re.IGNORECASE):
        def repl(m):
            try:
                return f"LIMIT {min(int(m.group(1)), settings.max_limit)}"
            except Exception:
                return f"LIMIT {settings.max_limit}"
        return re.sub(r"\bLIMIT\s+(\d+)", repl, sql, flags=re.IGNORECASE)
    return sql.rstrip("; \n\t") + f" LIMIT {settings.max_limit}"


def tables_are_allowed(sql: str, allowed: Set[str] | None = None) -> bool:
    allowed_tables = allowed or settings.allowed_tables
    pairs = re.findall(r"\bFROM\s+([a-z_][\w]*)|\bJOIN\s+([a-z_][\w]*)", sql, re.IGNORECASE)
    found = set()
    for a, b in pairs:
        if a:
            found.add(a.lower())
        if b:
            found.add(b.lower())
    return all(t in allowed_tables for t in found)


def sanitize_sql(sql: str) -> str:
    raw = sql.strip()
    raw = re.sub(r"^```(?:sql)?\s*|\s*```$", "", raw, flags=re.IGNORECASE)

    if not is_single_statement(raw):
        raise ValueError("Multiple statements are not allowed.")
    if not only_select(raw):
        raise ValueError("Only SELECT queries are allowed.")
    if danger_keywords.search(raw):
        raise ValueError("Disallowed SQL keyword found.")
    if not tables_are_allowed(raw):
        raise ValueError("Query references tables outside the allow-list.")
    raw = ensure_limit(raw)
    return raw


