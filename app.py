import streamlit as st
import os
import sys

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.database import DatabaseManager
from src.text_to_sql import TextToSQLEngine
from src.anomaly_engine import AnomalyEngine
from src.rag_engine import RAGEngine

# Page Configuration
st.set_page_config(
    page_title="AstraOps | GenAI Space Mission Copilot",
    page_icon="🛰️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling
st.markdown("""
<style>
    .main-title {
        font-size: 2.3rem;
        font-weight: 700;
        color: #1E3A8A;
        margin-bottom: 0px;
    }
    .sub-title {
        font-size: 1.05rem;
        color: #4B5563;
        margin-bottom: 20px;
    }
    .badge {
        background-color: #E0E7FF;
        color: #3730A3;
        padding: 4px 10px;
        border-radius: 6px;
        font-weight: 600;
        font-size: 0.85rem;
        display: inline-block;
        margin-bottom: 12px;
    }
</style>
""", unsafe_allow_html=True)

# Initialize Session State & Singletons
@st.cache_resource
def init_services(api_key=None):
    db = DatabaseManager()
    rag = RAGEngine()
    sql_engine = TextToSQLEngine(db, api_key=api_key)
    anomaly_engine = AnomalyEngine(db, rag, api_key=api_key)
    return db, rag, sql_engine, anomaly_engine

# Sidebar Configuration
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/satellite-in-orbit.png", width=64)
    st.title("AstraOps Config")
    st.markdown("**Def-Space Mission Copilot**")
    st.markdown('<span class="badge">Viksit Bharat Def-Space 2026</span>', unsafe_allow_html=True)
    
    api_key_input = st.text_input("Gemini API Key (Optional)", type="password", placeholder="Enter key or uses .env")
    st.info("💡 If no API key is provided, AstraOps runs in **Offline / Demo Mode** using local heuristics and document rankers.")
    
    st.divider()
    st.markdown("### 🎯 Quick Viva Prompts")
    quick_query = st.selectbox(
        "Select a sample query to test:",
        [
            "Custom Query",
            "Show satellites with battery voltage under 15V",
            "List all Indian military and defense satellites",
            "Show all satellites in Geostationary Orbit (GEO)",
            "Identify satellites experiencing high gyro drift rates"
        ]
    )

db, rag, sql_engine, anomaly_engine = init_services(api_key=api_key_input)

# Header Section
st.markdown('<h1 class="main-title">🛰️ AstraOps – Space Mission Intelligence Copilot</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">A Unified GenAI Platform combining <b>Natural Language-to-SQL</b>, <b>Telemetry Anomaly Triage</b>, and <b>Mission Knowledge RAG</b>.</p>', unsafe_allow_html=True)

# Main Application Tabs
tab1, tab2, tab3 = st.tabs([
    "📊 Natural Language to SQL (Telemetry)", 
    "🚨 Autonomous Anomaly Triage", 
    "📚 Mission Knowledge Assistant (RAG)"
])

# -------------------------------------------------------------
# TAB 1: TEXT-TO-SQL TELEMETRY
# -------------------------------------------------------------
with tab1:
    st.subheader("Query Satellite Database in Plain English")
    st.caption("Ask questions about spacecraft orbital parameters, sensor readings, or operational status.")

    default_prompt = "" if quick_query == "Custom Query" else quick_query
    user_query = st.text_input("Enter natural language query:", value=default_prompt, placeholder="e.g. Find all active satellites with battery voltage below 15V")

    col_btn1, col_btn2 = st.columns([1, 5])
    run_query = col_btn1.button("Execute Query", type="primary")

    if run_query and user_query:
        with st.spinner("Translating English to SQL & executing..."):
            generated_sql = sql_engine.generate_sql(user_query)
            
            st.markdown("#### Generated SQL Query")
            st.code(generated_sql, language="sql")
            
            # Execute Query
            data, error_msg, cols = db.execute_query(generated_sql)
            
            if error_msg:
                st.error(f"Execution Error: {error_msg}")
                st.info("Attempting automated self-correction loop...")
                corrected_sql = sql_engine.self_correct_sql(user_query, generated_sql, error_msg)
                st.code(corrected_sql, language="sql")
                data, error_msg, cols = db.execute_query(corrected_sql)

            if data is not None:
                st.success(f"Query executed successfully.")
                
                # Check if data is pandas DataFrame or list of rows
                if hasattr(data, 'empty'):
                    is_empty = data.empty
                else:
                    is_empty = len(data) == 0

                if is_empty:
                    st.warning("No records matched the query criteria.")
                else:
                    st.markdown("#### Results Data Table")
                    st.dataframe(data, use_container_width=True)
                    
                    # Auto Visualization if timestamp and numeric values exist
                    try:
                        import plotly.express as px
                        if hasattr(data, 'columns') and 'timestamp' in data.columns:
                            num_cols = [c for c in data.columns if c in ['battery_voltage', 'battery_temp_c', 'solar_panel_current', 'gyro_drift_rate']]
                            if num_cols:
                                fig = px.line(data, x='timestamp', y=num_cols[0], color='name' if 'name' in data.columns else None, title=f"Telemetry Trend: {num_cols[0]}")
                                st.plotly_chart(fig, use_container_width=True)
                    except Exception:
                        pass

                    # Executive Summary
                    st.markdown("#### 🤖 Mission Analyst Summary")
                    summary = sql_engine.explain_results(user_query, generated_sql, str(data[:5] if isinstance(data, list) else data.head(5).to_dict()))
                    st.write(summary)

# -------------------------------------------------------------
# TAB 2: ANOMALY TRIAGE COPILOT
# -------------------------------------------------------------
with tab2:
    st.subheader("Autonomous Telemetry Anomaly Detection & Triage")
    st.caption("Scans active telemetry for power loss, thermal runaway, or attitude control drift, contextualizing them with flight manuals.")

    anomalies = anomaly_engine.scan_recent_anomalies()
    
    if not anomalies:
        st.success("All satellite subsystems reporting NOMINAL. No critical anomalies detected.")
    else:
        st.warning(f"⚠️ Detected {len(anomalies)} active anomalies across the constellation.")
        
        # Display anomaly list
        selected_anomaly_idx = st.selectbox(
            "Select an anomaly to diagnose:",
            range(len(anomalies)),
            format_func=lambda i: f"[{anomalies[i].get('satellite_name')}] {anomalies[i].get('subsystem_alert')} at {anomalies[i].get('timestamp')}"
        )

        selected_record = anomalies[selected_anomaly_idx]
        
        # Telemetry metrics cards
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Satellite", selected_record.get('satellite_name'))
        col2.metric("Battery Voltage", f"{selected_record.get('battery_voltage')} V")
        col3.metric("Battery Temp", f"{selected_record.get('battery_temp_c')} °C")
        col4.metric("Gyro Drift Rate", f"{selected_record.get('gyro_drift_rate')} deg/s")

        if st.button("Generate Root-Cause Diagnosis (RAG + GenAI)", type="primary"):
            with st.spinner("Consulting flight operations SOP and synthesizing diagnosis..."):
                result = anomaly_engine.diagnose_anomaly(selected_record, llm_engine=sql_engine)
                
                st.markdown("---")
                st.markdown(result["diagnosis"])
                
                st.markdown("**Cited Flight Documentation:**")
                for doc in result["cited_documents"]:
                    st.markdown(f"- 📄 `{doc}`")

# -------------------------------------------------------------
# TAB 3: MISSION KNOWLEDGE ASSISTANT (RAG)
# -------------------------------------------------------------
with tab3:
    st.subheader("Mission Operations Documentation & SOP Retrieval")
    st.caption("Ask questions about spacecraft operating limits, emergency load-shedding procedures, and mission specs.")

    rag_question = st.text_input("Ask a question about flight manuals / technical documentation:", placeholder="e.g. What are the battery voltage thresholds and emergency actions for INSAT-3DR?")
    
    if st.button("Search Knowledge Base", type="primary") and rag_question:
        with st.spinner("Searching mission manuals & generating grounded response..."):
            rag_result = rag_engine.answer_question(rag_question, llm_engine=sql_engine)
            
            st.markdown("#### Answer")
            st.markdown(rag_result["answer"])
            
            if rag_result["citations"]:
                st.markdown("#### Document Citations")
                for cite in rag_result["citations"]:
                    st.markdown(f"- 📖 `{cite}`")

# Footer
st.divider()
st.caption("AstraOps v1.0.0 | National Institute of Technology Durgapur | Def-Space Artificial Intelligence Capstone")
