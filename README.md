# Spacepilot: GenAI-Powered Space Mission Intelligence Copilot 🛰️

[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Framework-Streamlit](https://img.shields.io/badge/Frontend-Streamlit-FF4B4B.svg)](https://streamlit.io/)
[![Database-SQLite](https://img.shields.io/badge/Database-SQLite-003B57.svg)](https://www.sqlite.org/)
[![License-MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Theme-Def--Space](https://img.shields.io/badge/Theme-Def--Space%20AI%202026-orange.svg)](#context--motivation)

**Spacepilot** is a unified Generative AI decision-support platform engineered for aerospace operations, defense earth observation, and satellite health monitoring. It bridges the gap between structured satellite telemetry databases and voluminous flight operating documentation.

Developed by **Saheli Mahanty**, National Institute of Technology Durgapur, as a B.Tech Computer Science and Engineering Capstone, inspired by the **Def-Space Artificial Intelligence Programme 2026** organized by the **Bharat Space Education Research Centre (BSERC)** under the theme *"Towards Viksit Bharat: Innovating, Collaborating and Aspiring to Global Space Leadership"*.

---

## 📌 Context & Motivation

During space and defense operations, flight directors and ground station controllers face two critical bottlenecks:
1. **Query Friction:** Mission operators cannot afford to manually write complex multi-table SQL joins during time-critical orbital passes or anomaly alerts.
2. **Knowledge Silos:** Real-time sensor telemetry (battery drops, temperature excursions, gyroscope drift) is disconnected from official flight operating manuals, leading to delayed anomaly triage.

**Spacepilot** resolves this by integrating **Natural Language-to-SQL (NL2SQL)**, **Automated Telemetry Anomaly Detection**, and **Retrieval-Augmented Generation (RAG)** into an intuitive mission copilot.

---

## 🏛️ System Architecture

```
                          [User Query / Plain English]
                                       │
            ┌──────────────────────────┼──────────────────────────┐
            ▼                          ▼                          ▼
  [Module 1: Text-to-SQL]   [Module 2: Anomaly Triage]   [Module 3: Mission RAG]
            │                          │                          │
   (Schema Linking &          (Z-Score & Threshold      (Document Ingestion,
    Safe SQL Generation)       Deviation Engine)         Chunking & Search)
            │                          │                          │
            ▼                          ▼                          ▼
   [Read-Only Validator]       [Live Telemetry Alert]     [Flight Manual SOPs]
            │                          │                          │
            ▼                          └────────────┬─────────────┘
  [SQLite Telemetry DB]                             ▼
  (7 Satellites / 1.1k pts)            [LLM Reasoning & Synthesis]
            │                         (Gemini 1.5 Flash / Local LLM)
            └──────────────────────────┬──────────────────────────┘
                                       ▼
                       [Interactive Streamlit Dashboard]
                    - Executed SQL & Live Data Tables
                    - Dynamic Plotly Telemetry Trend Lines
                    - Ground-Station Action Sequences & SOP Citations
```

---

## ✨ Key Features

### 1. 📊 Natural Language-to-SQL (Text-to-SQL)
* Converts conversational English questions into optimized, read-only SQLite queries.
* **SQL Safety Guard:** Rejects destructive operations (`DROP`, `DELETE`, `INSERT`, `ALTER`, etc.).
* **Automated Self-Correction:** When query syntax fails, the error message is fed back into the LLM to automatically repair the SQL.
* **Auto-Visualization:** Automatically detects time-series telemetry and renders dynamic Plotly charts.

### 2. 🚨 Autonomous Anomaly Triage
* Continuously scans telemetry channels for abnormal thresholds:
  * Battery Undervoltage ($< 18\text{ V}$) & Thermal Runaway ($> 45^\circ\text{C}$).
  * Attitude Control Gyroscope Drift ($> 0.05^\circ/\text{s}$).
  * Solar Eclipse Battery Discharge.
* Cross-references detected anomalies with mission documentation using RAG to produce **Emergency Ground Command Sequences** (e.g., payload load shedding, Bus-B switching, Safe-Hold mode).

### 3. 📚 Mission Knowledge Assistant (RAG)
* Semantic and keyword retrieval over flight manuals, technical specifications, and operating procedures (SOPs).
* Grounded answers with explicit source document citations.

---

## 🛠️ Tech Stack

* **Language:** Python 3.10+
* **Frontend:** Streamlit
* **Database:** SQLite3 / Pandas
* **Generative AI & LLMs:** Google Gemini 1.5 Flash API (`google-genai` / `google-generativeai`)
* **Information Retrieval:** Custom Vector / Lexical Chunker & Retrieval Engine
* **Data Visualization:** Plotly Express

---

## 🚀 Quick Start Guide

### 1. Clone the Repository
```bash
git clone https://github.com/sahelimahanty/Spacepilot.git
cd Spacepilot
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
Spacepilot/
│
├── .env.example               # Environment variable template
├── .gitignore                 # Standard Python/Git ignore rules
├── README.md                  # Complete project documentation
├── requirements.txt           # Python package dependencies
├── app.py                     # Streamlit multi-tab user interface
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
    ├── database.py            # SQLite connection, schema extractor, and query validator
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
