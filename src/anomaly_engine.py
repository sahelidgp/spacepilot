from src.database import DatabaseManager

class AnomalyEngine:
    def __init__(self, db_manager: DatabaseManager = None, rag_engine = None, api_key: str = None):
        self.db = db_manager or DatabaseManager()
        self.rag = rag_engine
        self.api_key = api_key

    def scan_recent_anomalies(self) -> list[dict]:
        """Scans the telemetry database for critical deviations and active alerts."""
        query = """
        SELECT 
            t.id, t.timestamp, s.name as satellite_name, s.satellite_id, s.orbit_type,
            t.battery_voltage, t.battery_temp_c, t.solar_panel_current,
            t.gyro_drift_rate, t.signal_strength_dbm, t.subsystem_alert
        FROM telemetry t
        JOIN satellites s ON t.satellite_id = s.satellite_id
        WHERE t.subsystem_alert != 'NOMINAL'
           OR t.battery_voltage < 18.0
           OR t.battery_temp_c > 35.0
           OR t.gyro_drift_rate > 0.05
        ORDER BY t.timestamp DESC
        LIMIT 25;
        """
        rows, err, cols = self.db.execute_query(query)
        if err or not rows:
            return []

        anomalies = []
        if hasattr(rows, 'to_dict'):
            anomalies = rows.to_dict(orient="records")
        else:
            for row in rows:
                anomalies.append(dict(zip(cols, row)))
        return anomalies

    def diagnose_anomaly(self, anomaly_record: dict, llm_engine = None) -> dict:
        """Combines telemetry reading with RAG flight manual retrieval and LLM root-cause synthesis."""
        sat_name = anomaly_record.get("satellite_name", "Unknown")
        alert = anomaly_record.get("subsystem_alert", "UNKNOWN_ALERT")
        volt = anomaly_record.get("battery_voltage", "N/A")
        temp = anomaly_record.get("battery_temp_c", "N/A")
        gyro = anomaly_record.get("gyro_drift_rate", "N/A")
        ts = anomaly_record.get("timestamp", "N/A")

        # Build query for RAG
        rag_query = f"{sat_name} {alert} battery undervolt thermal drift emergency procedure"
        relevant_docs = []
        if self.rag:
            relevant_docs = self.rag.search(rag_query, top_k=2)

        context_str = "\n\n".join([f"[{d['source']}]: {d['content']}" for d in relevant_docs]) if relevant_docs else "No specific document retrieved."

        # Generate diagnosis
        if llm_engine and getattr(llm_engine, 'client', None):
            prompt = f"""You are Spacepilot Flight Triage AI. Analyze this satellite telemetry anomaly using the retrieved SOP flight manual.

TELEMETRY DATA:
- Satellite: {sat_name}
- Timestamp: {ts}
- Alert Code: {alert}
- Battery Voltage: {volt} V (Nominal: 28-32V)
- Battery Temp: {temp} °C (Nominal: 10-25°C)
- Gyroscope Drift: {gyro} deg/s (Nominal: <0.005)

RELEVANT FLIGHT MANUAL DOCUMENTATION:
{context_str}

Please generate an Emergency Triage Response formatted in Markdown:
1. **Critical Assessment**: State the severity (CRITICAL / WARNING) and immediate danger.
2. **Probable Root Cause**: Cite relevant thresholds from the documentation.
3. **Recommended Ground Command Sequence**: Step-by-step actions (e.g. load shedding, safe-hold, bus switching).
"""
            diagnosis_text = llm_engine._generate_llm_response(prompt).strip()
        else:
            # Fallback rule-based explanation
            if "BATTERY" in alert or (isinstance(volt, (int, float)) and volt < 15.0):
                diagnosis_text = f"""### ⚠️ CRITICAL ASSESSMENT: Severe Battery Undervoltage ({volt}V) & Overheat ({temp}°C)
* **Satellite:** {sat_name} at {ts}
* **Probable Root Cause:** According to ISRO-DRDO-ANOMALY-SOP, battery voltage under 14V combined with temperatures exceeding 45°C indicates potential thermal runaway or power bus short-circuit following a peak radar imaging pass.
* **Recommended Ground Action Sequence:**
  1. Issue immediate payload load-shedding command via ground station.
  2. Inhibit high-power radar transmitter circuits.
  3. Switch regulator to Secondary Redundant Bus (Bus-B).
  4. Command cold-side radiator reorientation to deep space."""
            elif "GYRO" in alert or (isinstance(gyro, (int, float)) and gyro > 0.05):
                diagnosis_text = f"""### ⚠️ WARNING: Attitude & Orbit Control (AOCS) Gyro Drift ({gyro} deg/s)
* **Satellite:** {sat_name} at {ts}
* **Probable Root Cause:** Gyro drift rate exceeds the 0.005 deg/s threshold. Reaction wheel saturation or fiber-optic gyro diode degradation.
* **Recommended Ground Action Sequence:**
  1. Initiate reaction wheel momentum desaturation using magnetic torquers (MTQs).
  2. Cross-verify pointing attitude with optical star trackers.
  3. If drift persists > 0.1 deg/s, command transition to Sun-Pointing Safe-Hold Mode (SPSHM)."""
            else:
                diagnosis_text = f"""### ℹ️ NOTICE: Telemetry Anomaly Detected ({alert})
* **Satellite:** {sat_name} recorded abnormal parameters at {ts}.
* **Action:** Review subsystem logs and verify telemetry health trends across adjacent ground station passes."""

        return {
            "satellite": sat_name,
            "timestamp": ts,
            "alert": alert,
            "diagnosis": diagnosis_text,
            "cited_documents": [d.get("source") for d in relevant_docs] if relevant_docs else ["Standard Flight Operating Guidelines"]
        }
