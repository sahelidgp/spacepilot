import sqlite3
import os
import re

try:
    import pandas as pd
    HAS_PANDAS = True
except ImportError:
    HAS_PANDAS = False

class DatabaseManager:
    def __init__(self, db_path=None):
        if db_path is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            self.db_path = os.path.join(base_dir, "data", "satellites.db")
        else:
            self.db_path = db_path

    def get_connection(self):
        return sqlite3.connect(self.db_path)

    def get_schema(self) -> str:
        """Extracts table names, column names, data types, and sample rows for LLM prompting."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
        tables = [row[0] for row in cursor.fetchall()]
        
        schema_text = []
        for table in tables:
            cursor.execute(f"PRAGMA table_info({table});")
            columns = cursor.fetchall()
            col_desc = ", ".join([f"{col[1]} ({col[2]})" for col in columns])
            
            cursor.execute(f"SELECT * FROM {table} LIMIT 2;")
            sample_rows = cursor.fetchall()
            
            schema_text.append(f"Table: {table}")
            schema_text.append(f"Columns: {col_desc}")
            schema_text.append(f"Sample data: {sample_rows}\n")
            
        conn.close()
        return "\n".join(schema_text)

    def validate_sql(self, sql_query: str) -> tuple[bool, str]:
        """Ensures queries are strictly read-only SELECT statements (SQL Injection & Destructive Action Prevention)."""
        clean_query = sql_query.strip().strip(";").lower()
        
        forbidden_keywords = ["drop", "delete", "insert", "update", "alter", "create", "truncate", "replace", "grant", "revoke"]
        for kw in forbidden_keywords:
            if re.search(rf"\b{kw}\b", clean_query):
                return False, f"Security Violation: Destructive operation '{kw.upper()}' is forbidden. Read-only queries only."

        if not (clean_query.startswith("select") or clean_query.startswith("with")):
            return False, "Query must be a SELECT statement."

        return True, "Valid"

    def execute_query(self, sql_query: str):
        """Executes a SQL query safely and returns (data, error_message, column_names)."""
        is_valid, validation_msg = self.validate_sql(sql_query)
        if not is_valid:
            return None, validation_msg, []

        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(f"EXPLAIN QUERY PLAN {sql_query}")
            
            if HAS_PANDAS:
                df = pd.read_sql_query(sql_query, conn)
                conn.close()
                return df, None, list(df.columns)
            else:
                cursor.execute(sql_query)
                rows = cursor.fetchall()
                col_names = [description[0] for description in cursor.description]
                conn.close()
                return rows, None, col_names
        except Exception as e:
            return None, str(e), []

