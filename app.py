import streamlit as st
import os
import sys
from dotenv import load_dotenv

# Load local environment variables from .env
load_dotenv()

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.database import DatabaseManager
from src.text_to_sql import TextToSQLEngine
from src.anomaly_engine import AnomalyEngine
from src.rag_engine import RAGEngine

# Page Configuration
st.set_page_config(
    page_title="Spacepilot | Space Mission Intelligence Copilot",
    page_icon="🛰️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Black & Violet Cosmic Space Theme CSS
st.markdown("""
<style>
    /* Typography */
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600;700&family=Outfit:wght@300;400;600;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Outfit', sans-serif;
    }

    code, pre {
        font-family: 'JetBrains Mono', monospace !important;
    }

    /* Cosmic Deep Black & Violet Backgrounds */
    [data-testid="stAppViewContainer"] {
        background: radial-gradient(circle at 50% 0%, #16072D 0%, #090314 55%, #040108 100%) !important;
        color: #F5F3FF;
    }

    [data-testid="stHeader"] {
        background: transparent !important;
    }

    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0F051F 0%, #06010D 100%) !important;
        border-right: 1px solid rgba(168, 85, 247, 0.22) !important;
    }

    /* Main Hero Title Styling */
    .hero-title {
        font-size: 2.7rem;
        font-weight: 800;
        background: linear-gradient(90deg, #C084FC 0%, #E879F9 50%, #A78BFA 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 4px;
        letter-spacing: -0.5px;
        filter: drop-shadow(0 0 25px rgba(192, 132, 252, 0.35));
    }
    
    .hero-subtitle {
        font-size: 1.05rem;
        color: #C4B5FD;
        margin-bottom: 24px;
        font-weight: 300;
        opacity: 0.9;
    }

    /* Cosmic Glassmorphism KPI Stat Cards */
    .kpi-card {
        background: linear-gradient(135deg, rgba(28, 11, 52, 0.75) 0%, rgba(13, 5, 25, 0.88) 100%);
        border: 1px solid rgba(168, 85, 247, 0.28);
        border-radius: 14px;
        padding: 16px 20px;
        backdrop-filter: blur(12px);
        box-shadow: 0 8px 30px rgba(124, 58, 237, 0.14);
        transition: transform 0.25s ease, border-color 0.25s ease, box-shadow 0.25s ease;
    }
    .kpi-card:hover {
        transform: translateY(-3px);
        border-color: rgba(216, 180, 254, 0.65);
        box-shadow: 0 12px 35px rgba(168, 85, 247, 0.32);
    }
    .kpi-title {
        font-size: 0.82rem;
        color: #A78BFA;
        text-transform: uppercase;
        letter-spacing: 0.09em;
        margin-bottom: 6px;
        font-weight: 600;
    }
    .kpi-value {
        font-size: 1.65rem;
        font-weight: 700;
        color: #FAF5FF;
        font-family: 'JetBrains Mono', monospace;
        text-shadow: 0 0 15px rgba(192, 132, 252, 0.3);
    }
    .kpi-sub {
        font-size: 0.75rem;
        color: #C084FC;
        margin-top: 4px;
    }

    /* Violet Cosmic Status Badges */
    .badge-primary {
        background: rgba(147, 51, 234, 0.22);
        color: #E9D5FF;
        border: 1px solid rgba(168, 85, 247, 0.45);
        padding: 5px 12px;
        border-radius: 9999px;
        font-size: 0.78rem;
        font-weight: 600;
        display: inline-flex;
        align-items: center;
        gap: 8px;
        box-shadow: 0 0 15px rgba(168, 85, 247, 0.25);
    }
    .badge-warning {
        background: rgba(245, 158, 11, 0.18);
        color: #FDE68A;
        border: 1px solid rgba(245, 158, 11, 0.4);
        padding: 5px 12px;
        border-radius: 9999px;
        font-size: 0.78rem;
        font-weight: 600;
    }
    .badge-critical {
        background: rgba(244, 63, 94, 0.22);
        color: #FECDD3;
        border: 1px solid rgba(244, 63, 94, 0.45);
        padding: 6px 14px;
        border-radius: 9999px;
        font-size: 0.8rem;
        font-weight: 600;
        box-shadow: 0 0 20px rgba(244, 63, 94, 0.25);
    }
    .pulsing-dot {
        height: 8px;
        width: 8px;
        background-color: #C084FC;
        border-radius: 50%;
        display: inline-block;
        box-shadow: 0 0 8px #C084FC, 0 0 16px #9333EA;
    }

    /* Cosmic Diagnosis Panel */
    .diagnosis-box {
        background: linear-gradient(135deg, rgba(32, 9, 52, 0.9) 0%, rgba(14, 4, 25, 0.95) 100%);
        border: 1px solid rgba(244, 63, 94, 0.4);
        border-left: 4px solid #E11D48;
        border-radius: 12px;
        padding: 22px;
        margin-top: 15px;
        box-shadow: 0 8px 30px rgba(225, 29, 72, 0.15);
    }

    /* Primary Gradient Buttons */
    .stButton > button[kind="primary"], .stButton > button {
        background: linear-gradient(135deg, #7C3AED 0%, #9333EA 50%, #C026D3 100%) !important;
        color: #FFFFFF !important;
        border: none !important;
        border-radius: 9px !important;
        font-weight: 600 !important;
        padding: 8px 18px !important;
        box-shadow: 0 4px 18px rgba(147, 51, 234, 0.35) !important;
        transition: all 0.2s ease !important;
    }
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 26px rgba(192, 132, 252, 0.55) !important;
    }

    /* Streamlit Tabs with Violet Glow */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
        background: transparent;
        border-bottom: 1px solid rgba(168, 85, 247, 0.2);
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 10px 10px 0px 0px;
        padding: 10px 20px;
        font-weight: 600;
        color: #C4B5FD !important;
        background: transparent;
        transition: all 0.2s ease;
    }
    .stTabs [aria-selected="true"] {
        color: #FAF5FF !important;
        background: rgba(147, 51, 234, 0.18) !important;
        border-bottom: 2px solid #C084FC !important;
        box-shadow: 0 -4px 15px rgba(168, 85, 247, 0.2);
    }

    /* Inputs with Violet Glow */
    div[data-baseweb="input"] {
        background-color: #0E051D !important;
        border: 1px solid rgba(168, 85, 247, 0.3) !important;
        border-radius: 9px !important;
    }
    div[data-baseweb="input"]:focus-within {
        border-color: #C084FC !important;
        box-shadow: 0 0 16px rgba(192, 132, 252, 0.35) !important;
    }
</style>
""", unsafe_allow_html=True)

# Initialize Services without caching to ensure fresh modules & keys
def init_services(api_key=None):
    db = DatabaseManager()
    rag = RAGEngine()
    sql_engine = TextToSQLEngine(db, api_key=api_key)
    anomaly_engine = AnomalyEngine(db, rag, api_key=api_key)
    return db, rag, sql_engine, anomaly_engine

# Sidebar Configuration
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/satellite-in-orbit.png", width=60)
    st.markdown("### **Spacepilot Operations**")
    st.markdown('<span class="badge-primary"><span class="pulsing-dot"></span> LIVE CONSTELLATION TELEMETRY</span>', unsafe_allow_html=True)
    st.caption("National Institute of Technology Durgapur | Def-Space AI 2026")
    
    st.divider()
    env_key = os.getenv("GEMINI_API_KEY", "")
    api_key_input = st.text_input("Gemini API Key", value=env_key, type="password", placeholder="Paste API Key or loads from .env")
    if not api_key_input:
        st.info("⚡ **Offline / Demo Mode Active**\nRunning with built-in heuristic parsing, SQL safety guards, and local SOP document search.")
    else:
        st.success("✨ **Connected to Gemini Cloud AI**")
        
    st.divider()
    st.markdown("#### 🎯 Quick Viva Prompts")
    quick_query = st.selectbox(
        "Load sample demonstration question:",
        [
            "Custom Query",
            "Show satellites with battery voltage under 15V",
            "List all Indian military and defense satellites",
            "Show all satellites in Geostationary Orbit (GEO)",
            "Identify satellites experiencing high gyro drift rates"
        ]
    )
    
    st.divider()
    st.markdown("#### 🛰️ Constellation Nodes")
    st.markdown("""
    - **INSAT-3DR** `[GEO • 35,786 km]`
    - **Cartosat-3** `[SSO • 505 km]`
    - **GSAT-29** `[GEO • 35,786 km]`
    - **EOS-04 (RISAT-1A)** `[SSO • 529 km]`
    - **EMISAT (ELINT)** `[SSO • 748 km]`
    - **GSAT-7A (IAF)** `[GEO • 35,786 km]`
    """)

db, rag, sql_engine, anomaly_engine = init_services(api_key=api_key_input)
rag_engine = rag

# Top Hero Section
st.markdown('<div class="hero-title">🛰️ Spacepilot Mission Intelligence</div>', unsafe_allow_html=True)
st.markdown('<div class="hero-subtitle">Autonomous Generative AI Copilot for Satellite Telemetry Triage, Text-to-SQL Querying, and Mission Knowledge Synthesis.</div>', unsafe_allow_html=True)

# Constellation KPI Header Bar
k1, k2, k3, k4 = st.columns(4)
with k1:
    st.markdown("""
    <div class="kpi-card">
        <div class="kpi-title">Active Payloads</div>
        <div class="kpi-value">7 Nodes</div>
        <div class="kpi-sub">ISRO / DRDO / IAF</div>
    </div>
    """, unsafe_allow_html=True)

with k2:
    st.markdown("""
    <div class="kpi-card">
        <div class="kpi-title">Cached Telemetry</div>
        <div class="kpi-value">1,176 Pts</div>
        <div class="kpi-sub">7-Day Time-Series Stream</div>
    </div>
    """, unsafe_allow_html=True)

with k3:
    st.markdown("""
    <div class="kpi-card">
        <div class="kpi-title">Constellation Health</div>
        <div class="kpi-value" style="color: #F87171;">25 Alerts</div>
        <div class="kpi-sub" style="color: #FCA5A5;">Subsystems Flagged</div>
    </div>
    """, unsafe_allow_html=True)

with k4:
    st.markdown("""
    <div class="kpi-card">
        <div class="kpi-title">SQL Guardrails</div>
        <div class="kpi-value" style="color: #10B981;">SECURE</div>
        <div class="kpi-sub" style="color: #6EE7B7;">Read-Only Sandboxed</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Main Navigation Tabs
tab1, tab2, tab3 = st.tabs([
    "📊 Natural Language to SQL (Telemetry)", 
    "🚨 Autonomous Anomaly Triage", 
    "📚 Mission Knowledge Assistant (RAG)"
])

# -------------------------------------------------------------
# TAB 1: TEXT-TO-SQL TELEMETRY
# -------------------------------------------------------------
with tab1:
    st.markdown("### 💬 Natural Language Telemetry Query Engine")
    st.caption("Translate operational questions about orbital parameters, voltage levels, or subsystem health into executed SQL.")

    # Dynamic CSV Dataset Upload Section
    with st.expander("📤 Upload Custom CSV Dataset (Satellite / Telemetry Records)", expanded=False):
        st.caption("Upload any CSV file to automatically create a new database table and query it in natural language.")
        up_csv_col1, up_csv_col2 = st.columns([4, 1])
        with up_csv_col1:
            uploaded_csv = st.file_uploader(
                "Choose a CSV file",
                type=["csv"],
                help="Upload any structured telemetry or satellite CSV dataset",
                label_visibility="collapsed"
            )
        with up_csv_col2:
            if uploaded_csv is not None:
                if st.button("📥 Import CSV Table", type="secondary", use_container_width=True):
                    with st.spinner(f"Ingesting {uploaded_csv.name} into SQLite..."):
                        tbl_name = uploaded_csv.name.lower().replace(".csv", "")
                        success, msg = db.import_csv_as_table(tbl_name, uploaded_csv.getvalue())
                        if success:
                            st.success(msg)
                            st.rerun()
                        else:
                            st.error(f"Import failed: {msg}")

        # Active tables badge list
        tables_summary = db.get_tables_summary()
        if tables_summary:
            st.markdown("**Active Queryable Database Tables:**")
            badges = " &nbsp;|&nbsp; ".join([f"`🗄️ {t['table']} ({t['row_count']:,} rows)`" for t in tables_summary])
            st.markdown(badges)

    default_prompt = "" if quick_query == "Custom Query" else quick_query
    
    col_input, col_action = st.columns([5, 1])
    with col_input:
        user_query = st.text_input(
            "Enter your query in plain English:",
            value=default_prompt,
            placeholder="e.g. Find all active satellites with battery voltage below 15V",
            label_visibility="collapsed"
        )
    with col_action:
        run_query = st.button("🚀 Run Query", type="primary", use_container_width=True)

    if (run_query or quick_query != "Custom Query") and user_query:
        with st.spinner("Analyzing schema & translating natural language to SQL..."):
            generated_sql = sql_engine.generate_sql(user_query)
            
            # Show SQL Container
            st.markdown("##### 🔍 Generated & Validated SQL")
            st.code(generated_sql, language="sql")
            
            # Execute Query
            data, error_msg, cols = db.execute_query(generated_sql)
            
            # Automated Self-Correction Loop
            if error_msg:
                st.error(f"Execution Error: {error_msg}")
                st.warning("⚡ Triggering automated GenAI self-correction loop...")
                corrected_sql = sql_engine.self_correct_sql(user_query, generated_sql, error_msg)
                st.code(corrected_sql, language="sql")
                data, error_msg, cols = db.execute_query(corrected_sql)

            if data is not None:
                # Check emptiness
                is_empty = data.empty if hasattr(data, 'empty') else len(data) == 0

                if is_empty:
                    st.warning("Query executed successfully, but returned 0 matching records.")
                else:
                    st.markdown("##### 📋 Result Dataset")
                    st.dataframe(data, use_container_width=True)
                    
                    # Auto Dynamic Telemetry Plotting
                    try:
                        import plotly.express as px
                        if hasattr(data, 'columns') and 'timestamp' in data.columns:
                            num_cols = [c for c in data.columns if c in ['battery_voltage', 'battery_temp_c', 'solar_panel_current', 'gyro_drift_rate']]
                            if num_cols:
                                chart_col = num_cols[0]
                                fig = px.line(
                                    data,
                                    x='timestamp',
                                    y=chart_col,
                                    color='name' if 'name' in data.columns else None,
                                    title=f"Telemetry Stream Analysis: {chart_col.replace('_', ' ').title()}",
                                    template="plotly_dark",
                                    color_discrete_sequence=["#C084FC", "#E879F9", "#818CF8", "#F472B6", "#A78BFA"]
                                )
                                fig.update_traces(line=dict(width=2.5))
                                fig.update_layout(
                                    paper_bgcolor="rgba(14, 5, 29, 0.75)",
                                    plot_bgcolor="rgba(9, 3, 19, 0.75)",
                                    font=dict(family="Outfit, sans-serif", color="#F5F3FF")
                                )
                                st.plotly_chart(fig, use_container_width=True)
                    except Exception:
                        pass

                    # Executive Summary
                    st.markdown("##### 🤖 Mission Analyst Summary")
                    summary = sql_engine.explain_results(
                        user_query,
                        generated_sql,
                        str(data[:5] if isinstance(data, list) else data.head(5).to_dict())
                    )
                    st.info(summary)

# -------------------------------------------------------------
# TAB 2: ANOMALY TRIAGE COPILOT
# -------------------------------------------------------------
with tab2:
    st.markdown("### 🚨 Autonomous Anomaly Detection & Emergency Triage")
    st.caption("Real-time telemetry monitor scanning for thermal excursions, battery depletion, and reaction wheel drift.")

    anomalies = anomaly_engine.scan_recent_anomalies()
    
    if not anomalies:
        st.success("🟢 All constellation nodes reporting nominal telemetry. Zero critical alerts.")
    else:
        st.markdown(f'<div class="badge-critical">⚠️ {len(anomalies)} TELEMETRY ANOMALIES FLAGGED ACROSS CONSTELLATION</div>', unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Anomaly Selector Dropdown
        selected_anomaly_idx = st.selectbox(
            "Select an active anomaly alert to investigate:",
            range(len(anomalies)),
            format_func=lambda i: f"[{anomalies[i].get('satellite_name')}] {anomalies[i].get('subsystem_alert')} — Timestamp: {anomalies[i].get('timestamp')}"
        )

        selected_record = anomalies[selected_anomaly_idx]
        
        # Telemetry Quick-Look Cards
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.metric("🛰️ Satellite", selected_record.get('satellite_name'), delta=selected_record.get('orbit_type'))
        with c2:
            volt_val = selected_record.get('battery_voltage')
            st.metric("⚡ Battery Voltage", f"{volt_val} V", delta="-18.2 V Critical" if volt_val < 15 else "Nominal", delta_color="inverse")
        with c3:
            temp_val = selected_record.get('battery_temp_c')
            st.metric("🌡️ Battery Temp", f"{temp_val} °C", delta="+29.7 °C Overheat" if temp_val > 40 else "Nominal", delta_color="inverse")
        with c4:
            gyro_val = selected_record.get('gyro_drift_rate')
            st.metric("🧭 Gyro Drift Rate", f"{gyro_val} °/s", delta="Attitude Drift" if gyro_val > 0.05 else "Nominal", delta_color="inverse")

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🚨 Generate Ground Command Triage Briefing (RAG + GenAI)", type="primary"):
            with st.spinner("Cross-referencing flight manuals, SOP thresholds, and synthesizing diagnosis..."):
                try:
                    result = anomaly_engine.diagnose_anomaly(selected_record, llm_engine=sql_engine)
                except Exception as e:
                    st.warning(f"Note: Cloud LLM response encountered an issue ({e}). Serving offline SOP diagnosis.")
                    result = anomaly_engine.diagnose_anomaly(selected_record, llm_engine=None)
                
                st.markdown("""
                <div class="diagnosis-box">
                """, unsafe_allow_html=True)
                
                st.markdown(result["diagnosis"])
                
                st.markdown("---")
                st.markdown("##### 📄 Consulted Standard Operating Procedures (SOPs):")
                for doc in result["cited_documents"]:
                    st.markdown(f"- 📘 `{doc}`")
                    
                st.markdown("</div>", unsafe_allow_html=True)

# -------------------------------------------------------------
# TAB 3: MISSION KNOWLEDGE ASSISTANT (RAG)
# -------------------------------------------------------------
with tab3:
    col_t3_title, col_t3_mode = st.columns([3, 2])
    with col_t3_title:
        st.markdown("### 📚 Space Mission Flight Manuals & SOP Knowledge Base")
    with col_t3_mode:
        selected_mode_label = st.radio(
            "Guardrail Mode",
            ["🌐 Hybrid Copilot Mode", "🛡️ Strict Defense Mode"],
            horizontal=True,
            label_visibility="collapsed"
        )
    
    rag_mode = "strict" if "Strict" in selected_mode_label else "hybrid"
    
    if rag_mode == "strict":
        st.caption("🛡️ **Strict Defense Mode:** Answers strictly from verified uploaded spacecraft manuals with citations. Rejects off-topic queries to prevent hallucination.")
    else:
        st.caption("🌐 **Hybrid Copilot Mode:** Cites flight manuals when available; seamlessly explains general astronomy/space science when manuals don't contain it.")

    # Dynamic Document Upload Section
    with st.expander("📤 Upload Custom Spacecraft Manuals or Research Papers (PDF / TXT)", expanded=False):
        st.caption("Upload your own ISRO/NASA mission reports, satellite telemetry specs, or research whitepapers to dynamically expand Spacepilot's knowledge base.")
        up_col1, up_col2 = st.columns([4, 1])
        with up_col1:
            uploaded_file = st.file_uploader(
                "Choose a PDF or TXT document",
                type=["pdf", "txt", "md"],
                label_visibility="collapsed"
            )
        with up_col2:
            if uploaded_file is not None:
                if st.button("📥 Index File", type="secondary", use_container_width=True):
                    with st.spinner(f"Extracting and indexing text from {uploaded_file.name}..."):
                        success, msg = rag.ingest_uploaded_file(uploaded_file.name, uploaded_file.getvalue())
                        if success:
                            st.success(msg)
                            st.rerun()
                        else:
                            st.error(f"Ingestion failed: {msg}")

        # Show list of active indexed documents
        current_docs = sorted(list(set(c["source"] for c in rag.chunks)))
        st.markdown("**Indexed Knowledge Base Documents:**")
        doc_badges = " &nbsp;|&nbsp; ".join([f"`📄 {d}`" for d in current_docs])
        st.markdown(doc_badges)

    rag_col, rag_btn = st.columns([5, 1])
    with rag_col:
        rag_question = st.text_input(
            "Ask a question regarding flight operating documentation:",
            placeholder="e.g. What are the battery voltage thresholds and emergency actions for INSAT-3DR?",
            label_visibility="collapsed"
        )
    with rag_btn:
        search_rag = st.button("📖 Search Manuals", type="primary", use_container_width=True)
    
    if search_rag and rag_question:
        with st.spinner("Searching embedded space flight manuals and extracting citations..."):
            try:
                rag_result = rag.answer_question(rag_question, llm_engine=sql_engine, mode=rag_mode)
            except Exception as e:
                st.warning(f"Note: Cloud LLM response encountered an issue ({e}). Serving offline manual search.")
                rag_result = rag.answer_question(rag_question, llm_engine=None, mode=rag_mode)
            
            st.markdown("##### 🤖 Mission Knowledge Synthesis")
            st.markdown(f"""
            <div class="kpi-card" style="border-left: 4px solid #60A5FA;">
                {rag_result["answer"]}
            </div>
            """, unsafe_allow_html=True)
            
            if rag_result["citations"]:
                st.markdown("<br>##### 📑 Document Sources & Citations", unsafe_allow_html=True)
                for cite in rag_result["citations"]:
                    st.markdown(f"- 📖 **{cite}**")
                    
            if rag_result.get("retrieved_context"):
                with st.expander("🔍 View Raw Retrieved Document Passages"):
                    for idx, chunk in enumerate(rag_result["retrieved_context"]):
                        st.markdown(f"**Passage {idx+1} (Source: {chunk['source']}):**")
                        st.text(chunk["content"])

# Footer
st.divider()
st.markdown("""
<div style="text-align: center; color: #64748B; font-size: 0.85rem; padding: 10px 0;">
    <b>Spacepilot v1.1.0</b> | Department of Computer Science & Engineering | <b>National Institute of Technology Durgapur</b><br>
    <i>Inspired by Def-Space Artificial Intelligence Programme 2026 (Bharat Space Education Research Centre)</i>
</div>
""", unsafe_allow_html=True)
