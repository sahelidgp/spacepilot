# Spacepilot: GenAI-Powered Space Mission Intelligence Copilot 🛰️

[![Live-Demo](https://img.shields.io/badge/Live%20Demo-spacepilot--isro.streamlit.app-FF4B4B?style=for-the-badge&logo=streamlit)](https://spacepilot-isro.streamlit.app/)

[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Framework-Streamlit](https://img.shields.io/badge/Frontend-Streamlit-FF4B4B.svg)](https://streamlit.io/)
[![Database-SQLite](https://img.shields.io/badge/Database-SQLite-003B57.svg)](https://www.sqlite.org/)
[![License-MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Theme-Def--Space](https://img.shields.io/badge/Theme-Def--Space%20AI%202026-orange.svg)](#context--motivation)

> 🚀 **Live Deployment URL:** **[https://spacepilot-isro.streamlit.app/](https://spacepilot-isro.streamlit.app/)**  
> 📄 **Academic Project Report (PDF):** **[Spacepilot_Project_Report.pdf](Spacepilot_Project_Report.pdf)** (Includes Internship Certificate & Module Workings)

**Spacepilot** is a unified Generative AI decision-support platform engineered for aerospace operations, defense earth observation, and satellite health monitoring. It bridges the gap between structured satellite telemetry databases and voluminous flight operating documentation.

Developed by **Saheli Mahanty**, National Institute of Technology Durgapur, as a B.Tech Computer Science and Engineering Capstone, inspired by the **Def-Space Artificial Intelligence Programme 2026** organized by the **Bharat Space Education Research Centre (BSERC)** under the theme *"Towards Viksit Bharat: Innovating, Collaborating and Aspiring to Global Space Leadership"*.

---

## 🖥️ Live Application Interface

![Spacepilot Mission Intelligence Dashboard](assets/spacepilot_dashboard.png)

---

## 📌 Context & Motivation

During space and defense operations, flight directors and ground station controllers face two critical bottlenecks:
1. **Query Friction:** Mission operators cannot afford to manually write complex multi-table SQL joins during time-critical orbital passes or anomaly alerts.
2. **Knowledge Silos:** Real-time sensor telemetry (battery drops, temperature excursions, gyroscope drift) is disconnected from official flight operating manuals, leading to delayed anomaly triage.

**Spacepilot** resolves this by integrating **Natural Language-to-SQL (NL2SQL)**, **Automated Telemetry Anomaly Detection**, and **Retrieval-Augmented Generation (RAG)** into an intuitive mission copilot.

---

## 🏛️ System Architecture & Workflow

```mermaid
flowchart TD
    classDef client fill:#1E1035,stroke:#C084FC,stroke-width:2px,color:#FAF5FF;
    classDef module fill:#120726,stroke:#A855F7,stroke-width:2px,color:#E9D5FF;
    classDef storage fill:#07020E,stroke:#38BDF8,stroke-width:2px,color:#BAE6FD;
    classDef ai fill:#2E1065,stroke:#E879F9,stroke-width:2px,color:#FDF4FF;
    classDef output fill:#0E051D,stroke:#34D399,stroke-width:2px,color:#D1FAE5;

    User(["🧑‍🚀 Ground Station Operator / Flight Director"]):::client

    subgraph Ingestion ["📥 Real-Time Multi-Modal Data Ingestion"]
        CSVUpload["📤 Custom CSV Datasets (e.g. mission_launches.csv)"]:::storage
        PDFUpload["📄 Custom PDF/TXT Manuals (e.g. UserGuide.pdf)"]:::storage
        LiveStream["📡 Synthetic Satellite Telemetry Stream"]:::storage
    end

    subgraph CoreModules ["🛰️ Spacepilot Intelligent Engine"]
        subgraph Mod1 ["Module 1: Text-to-SQL Engine"]
            NLU["Natural Language Query Parser"]:::module
            SQLGen["Read-Only SQL Generator + AST Validator"]:::module
            SelfCorrect["Automated Self-Correction Loop"]:::module
        end

        subgraph Mod2 ["Module 2: Autonomous Anomaly Triage"]
            Scanner["Continuous Telemetry Scanner (Voltage / Temp / Drift)"]:::module
            AlertGen["Critical Metric Excursion Detector"]:::module
            BriefingGen["Tactical Ground Command Synthesizer"]:::module
        end

        subgraph Mod3 ["Module 3: Mission Knowledge Assistant (RAG)"]
            PyPDF["PyPDF Context-Inheriting Chunker"]:::module
            DualMode{"Guardrail Mode Router"}:::module
            StrictMode["🛡️ Strict Defense Mode\n(Zero Hallucination Guardrail)"]:::module
            HybridMode["🌐 Hybrid Copilot Mode\n(Extended Space Science)"]:::module
        end
    end

    subgraph KnowledgeBases ["🗄️ Knowledge & Storage Layer"]
        SQLiteDB[("SQLite Database\n(satellites, telemetry, custom CSVs)")]:::storage
        FlightManuals[("Mission Flight Manuals & SOPs\n(INSAT-3DR, EOS-04, SOPs, Uploads)")]:::storage
    end

    subgraph AICloud ["🧠 Generative AI Synthesis (Google Gemini Cloud)"]
        GeminiLLM["Gemini 3.5 Flash / 1.5 Flash\n(Dynamic Fallback Engine)"]:::ai
    end

    subgraph UI ["🖥️ Cosmic Black & Violet Dashboard (Streamlit Cloud)"]
        Tabs["Interactive Multi-Tab Operations Console"]:::output
        Visuals["Dynamic Plotly Telemetry Time-Series & KPI Cards"]:::output
        UplinkCommands["Ground-Station Emergency Command Sequences"]:::output
    end

    User -->|"Plain English Query / Uploads"| CoreModules
    CSVUpload --> SQLiteDB
    PDFUpload --> PyPDF
    LiveStream --> SQLiteDB
    
    NLU --> SQLGen --> SQLiteDB
    SQLGen -.->|"Syntax Error"| SelfCorrect --> GeminiLLM
    
    Scanner --> SQLiteDB
    AlertGen --> Scanner
    AlertGen --> BriefingGen
    
    PyPDF --> FlightManuals
    DualMode --> StrictMode
    DualMode --> HybridMode
    FlightManuals --> DualMode
    
    BriefingGen --> GeminiLLM
    StrictMode --> GeminiLLM
    HybridMode --> GeminiLLM
    SQLGen --> GeminiLLM
    
    GeminiLLM --> UI
    SQLiteDB --> UI
```

---

## 📸 Core Modules & Working Demonstrations

Spacepilot integrates three autonomous Generative AI modules designed for high-stakes aerospace and defense operations. Below are live execution walkthroughs from the deployed platform.

---

### Module 1: 📊 Natural Language Telemetry Query Engine (NL2SQL)

The **Text-to-SQL Engine** translates operational space questions into mathematically precise, sandboxed SQLite queries.

* **How it Works:** 
  1. The LLM receives the live SQLite database schema along with operational table definitions.
  2. It generates optimized read-only SQL, bounded by strict AST safety filters that immediately abort destructive statements (`DROP`, `DELETE`, `INSERT`, `ALTER`).
  3. If a generated query encounters a syntax or runtime error, an automated **self-correction feedback loop** sends the database error back to Gemini to iteratively fix and rerun the query.
* **Dynamic CSV Dataset Ingestion:** 
  Operators can upload arbitrary mission CSV datasets (e.g., `mission_launches.csv` containing **4,324 space mission records**). Spacepilot dynamically normalizes column headers, creates dedicated SQLite tables, and exposes them to natural language querying in seconds.

![Natural Language to SQL Query Engine](assets/01_nl2sql_custom_csv_execution.jpg)
*Live execution: Querying `"list all data of spacex organization"` across a dynamically uploaded `mission_launches.csv` dataset, automatically generating `SELECT * FROM mission_launches WHERE LOWER(Organisation) = 'spacex'` with real-time tabular rendering.*

---

### Module 2: 🚨 Autonomous Anomaly Detection & Emergency Triage Copilot

Spacecraft health monitoring requires immediate correlation between real-time telemetry spikes and official standard operating procedures (SOPs).

* **How it Works:**
  1. The anomaly engine continuously scans constellation telemetry streams across primary channels (battery voltage, battery temperature, solar panel currents, attitude gyroscope drift).
  2. Critical excursions are immediately flagged with color-coded delta metrics (e.g., **10.12 V** [$\downarrow -18.2\text{ V}$ Critical] and **54.67 °C** [$\uparrow +29.7\text{ }^\circ\text{C}$ Overheat]).
  3. When an operator triggers ground triage, the engine retrieves the corresponding emergency procedures from verified mission flight manuals (e.g., `satellite_anomaly_triage_sop.txt` and `eos04_radar_reconnaissance_specs.txt`).
  4. The LLM synthesizes an operational **Ground Command Triage Briefing** structured into:
     - **Critical Assessment:** Severity rating, immediate mission risks, and telemetry delta breakdown.
     - **Probable Root Cause:** Cross-referenced hardware diagnostics (e.g., secondary power bus short circuit, payload thermal runaway).
     - **Tactical Command Sequence:** Step-by-step ground-station uplink commands (e.g., emergency payload load-shedding, disabling active synthetic aperture radar, switching regulator to Secondary Redundant Bus-B).

![Autonomous Anomaly Alert & Critical Telemetry](assets/02_anomaly_triage_alert_metrics.jpg)
*Real-time telemetry alert for EOS-04 (RISAT-1A) showing severe undervoltage and thermal spikes.*

![Recommended Emergency Ground Command Sequence](assets/03_anomaly_triage_ground_command_sop.jpg)
*Synthesized Ground Command Triage Briefing outlining root causes and step-by-step contingency commands.*

---

### Module 3: 📚 Mission Knowledge Assistant (RAG Engine)

The **Mission Knowledge Assistant** enables conversational intelligence over technical manuals, satellite design specifications, and standard operating procedures with dynamic PDF/TXT document ingestion.

#### 🛡️ Strict Defense Mode vs. 🌐 Hybrid Copilot Mode

To ensure operational reliability during critical space missions, Spacepilot introduces dual operational guardrail modes:

| Feature / Dimension | 🛡️ Strict Defense Mode (Zero Hallucination) | 🌐 Hybrid Copilot Mode (Extended Science) |
| :--- | :--- | :--- |
| **Operational Goal** | Mission-critical flight operations, payload telemetry adherence, and zero-tolerance for AI hallucination. | General space exploration, flight operator training, educational briefing, and astronomical queries. |
| **Knowledge Bounding** | Strictly bounded to verified, uploaded flight manuals and SOP documents. | Primary grounding on flight manuals; seamlessly falls back to general astrophysics when unlisted. |
| **Out-of-Domain Query Behavior** | **Hard Rejection:** When asked about external topics (e.g., *"what is asteroid"*), it strictly responds: <br>`"The available flight manuals do not contain information regarding this topic."` | **Transparent General Synthesis:** Explains external concepts with a prominent disclosure banner: <br>`*(Note: This topic is outside your current spacecraft flight manuals, but here is the general scientific explanation:)*` |
| **Source Citation** | Every factual claim is bound to explicit document references (e.g., `[UserGuide_extracted.txt]`). | Flight manuals are cited when used; general knowledge is explicitly labeled as external science. |

---

#### 1. Hybrid Copilot Mode in Action
When querying general astronomy topics outside the ingested flight manuals (such as *"what is asteroid"*), Hybrid Mode provides a scientific synthesis covering composition, spectral classes (C-type, S-type, M-type), and orbital distributions (Main Belt, NEAs, Trojans).

![Hybrid Copilot Mode General Science Fallback](assets/04_rag_hybrid_mode_general_science.jpg)
*Hybrid Copilot Mode answering `"what is asteroid"` with automated contextual disclosure.*

---

#### 2. Strict Defense Mode: Anti-Hallucination Rejection
In mission-critical scenarios where operators must avoid ungrounded AI speculation, switching to **Strict Defense Mode** enforces strict retrieval verification. When presented with the exact same out-of-domain query (*"what is asteroid"*), the copilot rejects the question to protect operational integrity:

![Strict Defense Mode Anti-Hallucination Rejection](assets/05_rag_strict_mode_antihallucination.jpg)
*Strict Defense Mode rejecting out-of-domain query to guarantee zero hallucination.*

---

#### 3. Strict Defense Mode: Dynamic Document Ingestion & Verified Citations
Operators can upload new mission manuals (such as `UserGuide.pdf` or mission reports). The system automatically parses pages via `pypdf`, extracts contextual chunks while preserving title metadata, and answers technical inquiries (e.g., *"Describe Airspeed limitations"*) with verbatim document citations (`[UserGuide_extracted.txt]`):

![Strict Defense Mode Custom PDF Q&A with Citations](assets/06_rag_strict_mode_pdf_citations.jpg)
*Strict Defense Mode extracting takeoff and re-entry airspeed thresholds directly from user-uploaded `UserGuide.pdf` with citations.*

---

## 🛠️ Comprehensive Tech Stack

| Layer | Technologies & Libraries | Key Responsibilities in Spacepilot |
| :--- | :--- | :--- |
| **Core Runtime** | `Python 3.10+ / 3.12` | High-performance backend engine, type hints, asynchronous pipeline execution |
| **Web Application & UI** | `Streamlit 1.35+` | Real-time multi-tab operations console with custom **Cosmic Black & Violet** dark theme (`#07020E`, `#120726`), CSS glow animations, and KPI metric cards |
| **Foundation LLMs & GenAI** | `google-genai 0.1+`<br>`google-generativeai 0.7+` | Multi-model Google Gemini inference engine supporting `gemini-3.5-flash-lite`, `gemini-3.1-flash-lite`, `gemini-1.5-flash` with dynamic fallback and self-correction |
| **Safe Database & Storage** | `SQLite3`<br>`sqlglot 23.0+` | Read-only telemetry database with AST query parsing, dynamic schema extraction, and strict injection guardrails (`DROP`, `DELETE`, `INSERT` prevention) |
| **Data Ingestion & Analytics** | `pandas 2.2+` | Time-series telemetry wrangling, dynamic CSV dataset upload, schema normalization, and tabular rendering |
| **Document Processing & RAG** | `pypdf 4.0+`<br>`re`, `math` | Multi-page PDF flight manual parsing, context-inheriting sub-section chunker, stop-word filtered TF-IDF lexical search, dual guardrail modes (*Strict* vs. *Hybrid*) |
| **Data Visualization** | `Plotly Express 5.20+` | Interactive dark-themed telemetry graphs (battery voltage curves, thermal trends, gyro drift rates) |
| **Config & Cloud Secrets** | `python-dotenv 1.0+`<br>`st.secrets` | Seamless secret handling across local development (`.env`) and cloud production (Streamlit Community Cloud Secrets) |
| **Cloud Deployment** | `Streamlit Community Cloud` | Globally accessible, zero-latency public hosting at `https://spacepilot-isro.streamlit.app/` |

---

## 🚀 Quick Start Guide

### 1. Clone the Repository
```bash
git clone https://github.com/sahelidgp/spacepilot.git
cd spacepilot
```

### 2. Set Up Virtual Environment (Recommended)
```bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. (Optional) Configure Gemini API Key
Create a `.env` file from the template:
```bash
cp .env.example .env
```
Add your free Gemini API key:
```env
GEMINI_API_KEY=your_actual_api_key_here
```
*(Note: Spacepilot includes an intelligent offline/demo mode, so the application runs even without an active API key!)*

### 5. Generate Database & Launch Application
```bash
# Generate the simulated telemetry database (satellites.db)
python data/generate_telemetry.py

# Launch the Streamlit Dashboard
streamlit run app.py
```

---

## 📋 Sample Viva Test Queries

| Domain | Natural Language Query | Generated SQL Logic |
| :--- | :--- | :--- |
| **Power Health** | *"Show satellites with battery voltage under 15V"* | `SELECT ... FROM telemetry WHERE battery_voltage < 15.0` |
| **Defense Assets** | *"List all Indian military and defense satellites"* | `SELECT ... FROM satellites WHERE operator LIKE '%Air Force%' OR ...` |
| **Orbital Mechanics** | *"Show all satellites in Geostationary Orbit (GEO)"* | `SELECT ... FROM satellites WHERE orbit_type = 'GEO'` |
| **Attitude Stability** | *"Identify satellites experiencing high gyro drift rates"* | `SELECT ... FROM telemetry WHERE gyro_drift_rate > 0.05` |

---

## 📂 Project Structure

```
spacepilot/
│
├── .env.example               # Environment variable template
├── .gitignore                 # Standard Python/Git ignore rules
├── README.md                  # Complete project documentation
├── requirements.txt           # Python package dependencies
├── app.py                     # Streamlit multi-tab user interface
│
├── assets/                    # Dashboard previews and live execution media
│   ├── spacepilot_dashboard.png
│   ├── 01_nl2sql_custom_csv_execution.jpg
│   ├── 02_anomaly_triage_alert_metrics.jpg
│   ├── 03_anomaly_triage_ground_command_sop.jpg
│   ├── 04_rag_hybrid_mode_general_science.jpg
│   ├── 05_rag_strict_mode_antihallucination.jpg
│   └── 06_rag_strict_mode_pdf_citations.jpg
│
├── data/
│   ├── generate_telemetry.py  # Synthetic telemetry generator with injected anomalies
│   ├── satellites.db          # Pre-built SQLite database
│   └── documents/             # Mission flight manuals and SOP references
│       ├── insat_3dr_telemetry_manual.txt
│       ├── eos04_radar_reconnaissance_specs.txt
│       └── satellite_anomaly_triage_sop.txt
│
└── src/
    ├── __init__.py
    ├── database.py            # SQLite connection, schema extractor, CSV ingestion & validator
    ├── text_to_sql.py         # Natural Language to SQL converter with self-correction
    ├── anomaly_engine.py      # Statistical anomaly scanner and triage engine
    └── rag_engine.py          # Document chunking, search, and cited Q&A
```

---

## 🎓 Academic Defense & Acknowledgments

This project serves as the final year capstone for the **Department of Computer Science & Engineering, National Institute of Technology Durgapur**. 

Special acknowledgment to the **Bharat Space Education Research Centre (BSERC)** for the foundational domain exposure during the **Def-Space Artificial Intelligence Internship 2026**.

**Author:** Saheli Mahanty  
**Institution:** National Institute of Technology Durgapur  
