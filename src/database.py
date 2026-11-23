import sqlite3
import os
import re

try:
    import pandas as pd
    HAS_PANDAS = True
except ImportError:
    HAS_PANDAS = False

try:
    import sqlglot
    from sqlglot import exp
    HAS_SQLGLOT = True
except ImportError:
    HAS_SQLGLOT = False

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
        """Ensures queries are strictly read-only SELECT statements via SQLGlot AST validation."""
        if not sql_query or not sql_query.strip():
            return False, "Query is empty."

        clean_query = sql_query.strip().rstrip(";")

        # 1. SQLGlot AST Parsing & Node Verification
        if HAS_SQLGLOT:
            try:
                expression = sqlglot.parse_one(clean_query, read="sqlite")
                if expression is None:
                    return False, "Security Violation: Failed to parse SQL into a valid AST."
                
                # Check root statement type (must be Select or Union)
                if not isinstance(expression, (exp.Select, exp.Union)):
                    return False, f"Security Violation: Query root must be a SELECT or UNION statement, received '{expression.key.upper()}'."
                
                # Walk all AST nodes to catch embedded destructive statements
                forbidden_nodes = (
                    exp.Drop, exp.Delete, exp.Insert, exp.Update, exp.Alter,
                    exp.Create, exp.Command, exp.TruncateTable
                )
                for node in expression.walk():
                    if isinstance(node, forbidden_nodes):
                        return False, f"Security Violation: AST detected forbidden statement type '{node.key.upper()}'. Read-only queries only."
                
                return True, "Valid (AST Verified Read-Only)"
            except Exception as e:
                # If sqlglot parsing fails, fall through to strict keyword inspection
                pass

        # 2. Strict Fallback Inspection
        forbidden_keywords = ["drop", "delete", "insert", "update", "alter", "create", "truncate", "replace", "grant", "revoke", "attach"]
        lower_q = clean_query.lower()
        for kw in forbidden_keywords:
            if re.search(rf"\b{kw}\b", lower_q):
                return False, f"Security Violation: Destructive operation '{kw.upper()}' is forbidden. Read-only queries only."

        if not (lower_q.startswith("select") or lower_q.startswith("with")):
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
            
            # Enforce read-only constraint at the SQLite engine level
            cursor.execute("PRAGMA query_only = ON;")
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

    def import_csv_as_table(self, table_name: str, csv_bytes: bytes) -> tuple[bool, str]:
        """Loads uploaded CSV data into SQLite database as a new table."""
        try:
            import io
            if not HAS_PANDAS:
                return False, "Pandas is required for CSV ingestion."
            
            # Sanitize table name (only letters, numbers, underscores)
            clean_name = re.sub(r"[^a-zA-Z0-9_]", "_", table_name.lower().replace(".csv", "")).strip("_")
            if not clean_name:
                clean_name = "custom_telemetry"

            # Parse CSV
            df = pd.read_csv(io.BytesIO(csv_bytes))
            
            if df.empty:
                return False, "The uploaded CSV file is empty."

            # Clean column names (strip whitespace, replace spaces with underscores)
            df.columns = [re.sub(r"[^a-zA-Z0-9_]", "_", str(col).strip()).strip("_") for col in df.columns]

            conn = self.get_connection()
            df.to_sql(clean_name, conn, if_exists="replace", index=False)
            conn.close()

            return True, f"Successfully imported table '{clean_name}' with {len(df)} rows and {len(df.columns)} columns."
        except Exception as e:
            return False, str(e)

    def get_tables_summary(self) -> list[dict]:
        """Returns all tables and their row counts."""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
            tables = [r[0] for r in cursor.fetchall()]
            summary = []
            for t in tables:
                cursor.execute(f"SELECT COUNT(*) FROM {t};")
                count = cursor.fetchone()[0]
                summary.append({"table": t, "row_count": count})
            conn.close()
            return summary
        except Exception:
            return []

