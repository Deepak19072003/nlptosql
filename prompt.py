from langchain_core.prompts import ChatPromptTemplate


SQL_PROMPT = ChatPromptTemplate.from_template(
    """You convert a user question to a single SELECT SQL statement for PostgreSQL.

Rules:
 - Use only tables: customers(id,name,email), products(id,name,price), orders(id,customer_id,product_id,quantity,order_date)
 - Output SQL ONLY, no commentary or code fences
 - One statement only
 - NO DDL/DML (no INSERT/UPDATE/DELETE/CREATE/ALTER/DROP/TRUNCATE)
 - Must include LIMIT <= {max_limit}
 - Use qualified column names when joins are present

Question: {question}
SQL:"""
)


