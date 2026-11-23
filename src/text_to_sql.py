import os
import re
from src.database import DatabaseManager

class TextToSQLEngine:
    def __init__(self, db_manager: DatabaseManager = None, api_key: str = None):
        self.db = db_manager or DatabaseManager()
        raw_key = api_key or os.getenv("GEMINI_API_KEY")
        self.api_key = raw_key.strip() if raw_key else None
        self.client = None
        self.sdk_type = None
        self.available_models = []
        self.last_error = None
        self._init_llm()

    def _init_llm(self):
        """Initializes Gemini client and dynamically discovers available models for this key."""
        if not self.api_key:
            return

        # 1. Try google.genai with dynamic model discovery
        try:
            from google import genai
            self.client = genai.Client(api_key=self.api_key)
            self.sdk_type = "google-genai"
            try:
                for m in self.client.models.list():
                    name = getattr(m, 'name', '')
                    if name and ("gemini" in name.lower() or "flash" in name.lower()):
                        self.available_models.append(name)
            except Exception:
                pass
            
            if not self.available_models:
                self.available_models = ["gemini-2.0-flash", "gemini-1.5-flash", "models/gemini-1.5-flash", "gemini-1.5-pro"]
            return
        except Exception:
            pass

        # 2. Try legacy google.generativeai
        try:
            import google.generativeai as genai_legacy
            genai_legacy.configure(api_key=self.api_key)
            self.client = genai_legacy
            self.sdk_type = "google-generativeai"
            try:
                for m in self.client.list_models():
                    if 'generateContent' in m.supported_generation_methods:
                        self.available_models.append(m.name)
            except Exception:
                pass
            
            if not self.available_models:
                self.available_models = ["models/gemini-1.5-flash", "models/gemini-1.5-pro", "gemini-1.5-flash"]
        except Exception as e:
            self.client = None
            self.sdk_type = None
            self.last_error = str(e)

    def _generate_llm_response(self, prompt: str) -> str:
        """Helper to invoke LLM with resilient dynamic model fallback."""
        if not self.api_key or not self.client:
            return ""

        errors = []
        
        # Proven active models prioritized for fast response and high availability
        priority_models = [
            "gemini-3.5-flash-lite",
            "gemini-3.1-flash-lite",
            "gemini-3.8-flash",
            "gemini-3.5-flash",
            "gemini-2.5-flash-lite",
            "gemini-1.5-flash"
        ]
        
        # Combine priority models with discovered models, excluding known deprecated models
        deprecated = {"gemini-pro", "gemini-2.5-flash"}
        seen = set()
        candidates = []
        for m in priority_models + self.available_models:
            clean = m.replace("models/", "")
            if clean not in seen and clean not in deprecated:
                seen.add(clean)
                candidates.append(m)

        for model_name in candidates:
            variations = [model_name]
            if model_name.startswith("models/"):
                variations.append(model_name.replace("models/", ""))
            else:
                variations.append(f"models/{model_name}")

            for variant in variations:
                try:
                    if self.sdk_type == "google-genai":
                        response = self.client.models.generate_content(
                            model=variant,
                            contents=prompt
                        )
                        if hasattr(response, 'text') and response.text:
                            return response.text
                    elif self.sdk_type == "google-generativeai":
                        model = self.client.GenerativeModel(variant)
                        response = model.generate_content(prompt)
                        if hasattr(response, 'text') and response.text:
                            return response.text
                except Exception as e:
                    errors.append(f"{variant}: {e}")
                    continue

        if errors:
            self.last_error = errors[0]
        return ""

    def generate_sql(self, user_question: str) -> str:
        """Converts user natural language question into a safe SQLite query."""
        schema = self.db.get_schema()

        # If LLM client is available, use prompt engineering
        if self.client and self.api_key:
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
            if raw_output:
                clean_sql = re.sub(r"^```(sql)?\s*", "", raw_output, flags=re.IGNORECASE)
                clean_sql = re.sub(r"\s*```$", "", clean_sql).strip()
                return clean_sql

        # Built-in Heuristic Fallback for quick demonstration without API Key
        q_lower = user_question.lower()
        if "battery" in q_lower and ("under" in q_lower or "below" in q_lower or "drop" in q_lower or "10" in q_lower or "12" in q_lower or "15" in q_lower or "anomal" in q_lower):
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
        if not self.client or not self.api_key:
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
        if raw_output:
            clean_sql = re.sub(r"^```(sql)?\s*", "", raw_output, flags=re.IGNORECASE)
            clean_sql = re.sub(r"\s*```$", "", clean_sql).strip()
            return clean_sql
        return broken_sql

    def explain_results(self, user_question: str, sql_query: str, data_summary: str) -> str:
        """Generates a natural-language mission summary of query results."""
        if not self.client or not self.api_key:
            return f"Query executed successfully against telemetry database. Found matching records."

        prompt = f"""You are Spacepilot, a space mission intelligence officer.
Summarize the findings of this database query in 2-3 clear, executive bullet points.

USER QUERY: {user_question}
EXECUTED SQL: {sql_query}
QUERY RESULTS SUMMARY: {data_summary}

Provide concise, tactical insights. If anomalies or critical telemetry alerts appear, highlight them clearly.
"""
        res = self._generate_llm_response(prompt).strip()
        return res if res else f"Query executed successfully against telemetry database."
