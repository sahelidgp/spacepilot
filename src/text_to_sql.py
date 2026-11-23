import os
import re
from src.database import DatabaseManager

class TextToSQLEngine:
    def __init__(self, db_manager: DatabaseManager = None, api_key: str = None):
        self.db = db_manager or DatabaseManager()
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.client = None
        self._init_llm()

    def _init_llm(self):
        """Initializes Gemini client if API key is provided."""
        if not self.api_key:
            return

        try:
            # Check for new google-genai SDK
            from google import genai
            self.client = genai.Client(api_key=self.api_key)
            self.sdk_type = "google-genai"
        except ImportError:
            try:
                # Check for legacy google-generativeai SDK
                import google.generativeai as genai_legacy
                genai_legacy.configure(api_key=self.api_key)
                self.client = genai_legacy.GenerativeModel("gemini-1.5-flash")
                self.sdk_type = "google-generativeai"
            except ImportError:
                self.client = None
                self.sdk_type = None

    def _generate_llm_response(self, prompt: str) -> str:
        """Helper to invoke LLM with current client."""
        if not self.client:
            return ""

        if self.sdk_type == "google-genai":
            response = self.client.models.generate_content(
                model="gemini-1.5-flash",
                contents=prompt
            )
            return response.text
        elif self.sdk_type == "google-generativeai":
            response = self.client.generate_content(prompt)
            return response.text
        return ""

    def generate_sql(self, user_question: str) -> str:
        """Converts user natural language question into a safe SQLite query."""
        schema = self.db.get_schema()

        # If LLM client is available, use prompt engineering
        if self.client:
            prompt = f"""You are Spacepilot, an expert aerospace database engineer.
Convert the user's natural language question into a valid, optimized SQLite SQL query.

DATABASE SCHEMA:
{schema}

RULES:
1. ONLY return a read-only SELECT query. Never use DROP, DELETE, INSERT, UPDATE, ALTER.
2. Return ONLY the raw SQL query. Do NOT include markdown formatting (no ```sql or ```), no quotes, no explanations.
3. Use proper SQLite syntax and table aliases if necessary.
4. For text matching, use LOWER() or LIKE with wildcard % for flexibility (e.g. WHERE LOWER(orbit_type) = 'geo').

USER QUESTION:
{user_question}
"""
            raw_output = self._generate_llm_response(prompt).strip()
            # Clean markdown code blocks if any
            clean_sql = re.sub(r"^```(sql)?\s*", "", raw_output, flags=re.IGNORECASE)
            clean_sql = re.sub(r"\s*```$", "", clean_sql).strip()
            return clean_sql

        # Built-in Heuristic Fallback for quick demonstration without API Key
        q_lower = user_question.lower()
        if "battery" in q_lower and ("under" in q_lower or "below" in q_lower or "drop" in q_lower or "10" in q_lower or "12" in q_lower or "anomal" in q_lower):
            return "SELECT t.timestamp, s.name, t.battery_voltage, t.battery_temp_c, t.subsystem_alert FROM telemetry t JOIN satellites s ON t.satellite_id = s.satellite_id WHERE t.battery_voltage < 15.0 ORDER BY t.timestamp DESC;"
        elif "military" in q_lower or "defense" in q_lower or "drdo" in q_lower or "air force" in q_lower:
            return "SELECT satellite_id, name, operator, mission_type, orbit_type, status FROM satellites WHERE operator LIKE '%Air Force%' OR operator LIKE '%DRDO%' OR mission_type LIKE '%Defense%' OR mission_type LIKE '%ELINT%';"
        elif "geo" in q_lower or "geostationary" in q_lower:
            return "SELECT satellite_id, name, operator, altitude_km, status FROM satellites WHERE orbit_type = 'GEO';"
        elif "all satellites" in q_lower or "list satellites" in q_lower or "show satellites" in q_lower:
            return "SELECT satellite_id, name, operator, orbit_type, status, launch_date FROM satellites;"
        elif "temperature" in q_lower or "overheat" in q_lower:
            return "SELECT t.timestamp, s.name, t.battery_temp_c, t.subsystem_alert FROM telemetry t JOIN satellites s ON t.satellite_id = s.satellite_id WHERE t.battery_temp_c > 40.0 ORDER BY t.battery_temp_c DESC;"
        elif "gyro" in q_lower or "drift" in q_lower or "attitude" in q_lower:
            return "SELECT t.timestamp, s.name, t.gyro_drift_rate, t.subsystem_alert FROM telemetry t JOIN satellites s ON t.satellite_id = s.satellite_id WHERE t.gyro_drift_rate > 0.05 ORDER BY t.gyro_drift_rate DESC;"
        else:
            return "SELECT satellite_id, name, operator, orbit_type, status FROM satellites;"

    def self_correct_sql(self, original_question: str, broken_sql: str, error_message: str) -> str:
        """Automated Self-Correction: Feeds syntax or execution error back to LLM to auto-repair."""
        if not self.client:
            return broken_sql

        schema = self.db.get_schema()
        prompt = f"""You previously generated a SQL query that failed with an error. Fix the query to work on SQLite.

DATABASE SCHEMA:
{schema}

USER QUESTION: {original_question}
FAILED SQL: {broken_sql}
SQLITE ERROR: {error_message}

Return ONLY the corrected raw SQL query. No markdown, no commentary.
"""
        raw_output = self._generate_llm_response(prompt).strip()
        clean_sql = re.sub(r"^```(sql)?\s*", "", raw_output, flags=re.IGNORECASE)
        clean_sql = re.sub(r"\s*```$", "", clean_sql).strip()
        return clean_sql

    def explain_results(self, user_question: str, sql_query: str, data_summary: str) -> str:
        """Generates a natural-language mission summary of query results."""
        if not self.client:
            return f"Query executed successfully against telemetry database. Found {data_summary.count('(') if isinstance(data_summary, str) else len(data_summary)} matching records."

        prompt = f"""You are Spacepilot, a space mission intelligence officer.
Summarize the findings of this database query in 2-3 clear, executive bullet points.

USER QUERY: {user_question}
EXECUTED SQL: {sql_query}
QUERY RESULTS SUMMARY: {data_summary}

Provide concise, tactical insights. If anomalies or critical telemetry alerts appear, highlight them clearly.
"""
        return self._generate_llm_response(prompt).strip()
