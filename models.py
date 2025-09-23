from pydantic import BaseModel, Field
from typing import Any, List, Dict


class Question(BaseModel):
    question: str = Field(..., min_length=1, max_length=500)


class QueryResult(BaseModel):
    question: str
    generated_sql: str
    rows: List[Dict[str, Any]]
    row_count: int


