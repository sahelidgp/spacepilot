import os
import sys
import re
from PIL import Image as PILImage
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak
)
from reportlab.pdfgen import canvas

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
OUTPUT_REPORT_PDF = os.path.join(BASE_DIR, "Spacepilot_Project_Report.pdf")

# Custom Canvas for Two-Pass Exact Running Headers & Page Numbers (Matching Reference PDF)
class ReferenceStyleCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        
        # Reference Document Running Header on EVERY page
        # Left: Internship Report • Saheli Mahanty
        # Right: For Academic Submission Only   Page X
        self.setFont("Helvetica-Oblique", 9)
        self.setFillColor(colors.HexColor("#000000"))
        self.drawString(54, 11 * inch - 36, "Internship Report • Saheli Mahanty")
        
        self.setFont("Helvetica", 9)
        page_str = f"For Academic Submission Only   Page {self._pageNumber}"
        self.drawRightString(8.5 * inch - 54, 11 * inch - 36, page_str)
        
        # Solid black rule line below header
        self.setStrokeColor(colors.HexColor("#000000"))
        self.setLineWidth(0.75)
        self.line(54, 11 * inch - 42, 8.5 * inch - 54, 11 * inch - 42)
        
        self.restoreState()

def clean_xml(txt):
    """Safely escapes text for ReportLab XML parser."""
    txt = re.sub(r'&(?!(?:amp|lt|gt|quot|apos);)', '&amp;', txt)
    txt = txt.replace('<br>', '<br/>')
    return txt

def P(text, style):
    return Paragraph(clean_xml(text), style)

def build_pdf_story():
    styles = getSampleStyleSheet()
    
    # Precise Typography & Palette matching Reference PDF
    C_BLACK = colors.HexColor("#000000")
    C_DARK = colors.HexColor("#111827")
    C_GRAY = colors.HexColor("#374151")
    C_LIGHT = colors.HexColor("#F9FAFB")
    C_BORDER = colors.HexColor("#000000")
    
    # Styles matching reference document
    cover_main_title = ParagraphStyle(
        'CoverMainTitle', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=22, leading=26,
        textColor=C_BLACK, alignment=1
    )
    
    cover_org_title = ParagraphStyle(
        'CoverOrgTitle', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=15, leading=19,
        textColor=C_BLACK, alignment=1
    )
    
    cover_sub_title = ParagraphStyle(
        'CoverSubTitle', parent=styles['Normal'],
        fontName='Helvetica', fontSize=10.5, leading=14,
        textColor=C_DARK, alignment=1
    )
    
    cover_theme = ParagraphStyle(
        'CoverTheme', parent=styles['Normal'],
        fontName='Helvetica-Oblique', fontSize=9, leading=13,
        textColor=C_GRAY, alignment=1
    )
    
    cover_prep_label = ParagraphStyle(
        'CoverPrepLabel', parent=styles['Normal'],
        fontName='Helvetica', fontSize=10.5, leading=14,
        textColor=C_DARK, alignment=1
    )
    
    cover_author = ParagraphStyle(
        'CoverAuthor', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=14, leading=18,
        textColor=C_BLACK, alignment=1
    )
    
    h1_style = ParagraphStyle(
        'H1_Ref', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=12.5, leading=16,
        textColor=C_BLACK, spaceBefore=8, spaceAfter=4, keepWithNext=True
    )
    
    h2_style = ParagraphStyle(
        'H2_Ref', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=10, leading=13.5,
        textColor=C_BLACK, spaceBefore=6, spaceAfter=2.5, keepWithNext=True
    )
    
    h3_style = ParagraphStyle(
        'H3_Ref', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=9, leading=12.5,
        textColor=C_BLACK, spaceBefore=4, spaceAfter=2, keepWithNext=True
    )
    
    body_style = ParagraphStyle(
        'Body_Ref', parent=styles['Normal'],
        fontName='Helvetica', fontSize=9, leading=12.8,
        textColor=C_BLACK, spaceAfter=3.5, alignment=4
    )
    
    bullet_style = ParagraphStyle(
        'Bullet_Ref', parent=styles['Normal'],
        fontName='Helvetica', fontSize=9, leading=12.8,
        textColor=C_BLACK, leftIndent=12, spaceAfter=2.5
    )
    
    caption_style = ParagraphStyle(
        'Caption_Ref', parent=styles['Normal'],
        fontName='Helvetica-Oblique', fontSize=8, leading=10,
        textColor=C_GRAY, alignment=1, spaceAfter=4
    )
    
    toc_item_style = ParagraphStyle(
        'TOC_Item', parent=styles['Normal'],
        fontName='Helvetica', fontSize=9.5, leading=17,
        textColor=C_BLACK
    )
    
    toc_sub_item_style = ParagraphStyle(
        'TOC_SubItem', parent=styles['Normal'],
        fontName='Helvetica', fontSize=9.5, leading=17,
        textColor=C_BLACK, leftIndent=15
    )
    
    meta_key_style = ParagraphStyle(
        'MetaKey', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=9.5, leading=13.5,
        textColor=C_BLACK
    )
    
    meta_val_style = ParagraphStyle(
        'MetaVal', parent=styles['Normal'],
        fontName='Helvetica', fontSize=9.5, leading=13.5,
        textColor=C_BLACK
    )
    
    note_style = ParagraphStyle(
        'Note_Ref', parent=styles['Normal'],
        fontName='Helvetica', fontSize=7.5, leading=10.5,
        textColor=C_GRAY, alignment=4
    )

    story = []

    # =========================================================================
    # PAGE 1: COVER PAGE (Exact mirror of reference page 1)
    # =========================================================================
    story.append(Spacer(1, 45))
    story.append(P("INTERNSHIP REPORT", cover_main_title))
    story.append(Spacer(1, 10))
    story.append(P("BHARAT SPACE EDUCATION RESEARCH CENTRE", cover_org_title))
    story.append(Spacer(1, 4))
    story.append(P("Def-Space Artificial Intelligence Internship • 2026", cover_sub_title))
    story.append(Spacer(1, 3))
    story.append(P("Theme: Towards Viksit Bharat: Innovating, Collaborating and Aspiring to Global Space Leadership", cover_theme))
    
    story.append(Spacer(1, 40))
    story.append(P("Prepared by", cover_prep_label))
    story.append(Spacer(1, 4))
    story.append(P("Saheli Mahanty", cover_author))
    
    story.append(Spacer(1, 42))
    
    # 2-column metadata table without borders (matching reference layout)
    meta_data = [
        [P("Institution", meta_key_style), P("National Institute of Technology Durgapur", meta_val_style)],
        [P("Academic Dept.", meta_key_style), P("Computer Science and Engineering", meta_val_style)],
        [P("Internship Period", meta_key_style), P("Def-Space AI 2026 (Certificate ID: BSERC-2026-AI-1035)", meta_val_style)],
        [P("Location", meta_key_style), P("Bharat Space Education Research Centre, Bengaluru (Virtual Operations)", meta_val_style)],
        [P("Department", meta_key_style), P("Aerospace Artificial Intelligence &amp; Satellite Operations", meta_val_style)],
        [P("Academic Evaluation", meta_key_style), P("B.Tech 7th Semester Internship / Industrial Training Credits", meta_val_style)],
        [P("Project Title", meta_key_style), P("Spacepilot: GenAI-Powered Space Mission Intelligence Copilot", meta_val_style)],
        [P("Live Application", meta_key_style), P("https://spacepilot-isro.streamlit.app/", meta_val_style)],
    ]
    t_meta = Table(meta_data, colWidths=[2.1*inch, 4.9*inch])
    t_meta.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('PADDING', (0,0), (-1,-1), 2.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3.5),
    ]))
    story.append(t_meta)
    
    story.append(Spacer(1, 40))
    story.append(P("<b>NOTE:</b> This report was prepared solely by the author for academic credit evaluation in the 7th Semester B.Tech curriculum at National Institute of Technology Durgapur. The internship was undertaken independently under the Bharat Space Education Research Centre (BSERC) and does not represent an official position of BSERC or its affiliates, nor an institutional collaboration with NIT Durgapur. Any reference to aerospace telemetry formats or flight manuals is made solely for academic documentation.", note_style))
    story.append(Spacer(1, 6))
    story.append(P("For Academic Submission Only", ParagraphStyle('SubOnly', fontName='Helvetica', fontSize=8.5, leading=11, textColor=C_BLACK, alignment=1)))
    
    story.append(PageBreak())

    # =========================================================================
    # PAGE 2: INTERNSHIP COMPLETION CERTIFICATE
    # =========================================================================
    story.append(P("INTERNSHIP COMPLETION CERTIFICATE", h1_style))
    story.append(P("Bharat Space Education Research Centre (BSERC) • Certificate ID: BSERC-2026-AI-1035", ParagraphStyle('CertSub', fontName='Helvetica-Oblique', fontSize=9, leading=12, textColor=C_GRAY, spaceAfter=8)))
    
    cert_img_path = os.path.join(ASSETS_DIR, "certificate.png")
    if os.path.exists(cert_img_path):
        story.append(Image(cert_img_path, width=7.0*inch, height=4.94*inch))
    
    story.append(Spacer(1, 8))
    story.append(P("<b>Official Verification:</b> Awarded to <b>Saheli Mahanty</b> in recognition of successful completion of the 15-day <i>Def-Space Artificial Intelligence Internship 2026</i> conducted by the Bharat Space Education Research Centre (BSERC) under the theme <i>'Towards Viksit Bharat: Innovating, Collaborating and Aspiring to Global Space Leadership'</i>. Submitted to the Department of Computer Science &amp; Engineering, National Institute of Technology Durgapur, towards 7th Semester Internship / Industrial Training academic credit assessment.", body_style))
    
    story.append(PageBreak())

    # =========================================================================
    # PAGE 3: TABLE OF CONTENTS (Exact mirror of reference page 2)
    # =========================================================================
    story.append(P("TABLE OF CONTENTS", h1_style))
    story.append(Spacer(1, 12))
    
    story.append(P("1. Executive Summary", toc_item_style))
    story.append(P("2. Internship Overview", toc_item_style))
    story.append(P("3. Technology Background", toc_item_style))
    story.append(P("3.1 Relational Telemetry Databases &amp; SQLGlot AST Validation", toc_sub_item_style))
    story.append(P("3.2 Streamlit Web Framework &amp; Reactive Telemetry Dashboards", toc_sub_item_style))
    story.append(P("3.3 Generative AI, Large Language Models &amp; Self-Correction Feedback Loops", toc_sub_item_style))
    story.append(P("3.4 Dense Vector Semantic Embeddings, Cosine Similarity &amp; Guardrail Routing", toc_sub_item_style))
    story.append(P("4. Projects Undertaken", toc_item_style))
    story.append(P("4.1 End-to-End System Architecture &amp; Data Flow Pipeline (System Architect &amp; Developer)", toc_sub_item_style))
    story.append(P("4.2 Natural Language-to-SQL Telemetry Query Engine (NL2SQL) (Sole Developer)", toc_sub_item_style))
    story.append(P("4.3 Autonomous Anomaly Detection &amp; Grounded Emergency Triage (Sole Developer)", toc_sub_item_style))
    story.append(P("4.4 Mission Knowledge Assistant (RAG Engine) (Sole Developer)", toc_sub_item_style))
    story.append(P("4.5 Strict Defense Mode Verification &amp; Operations Console (Sole Developer)", toc_sub_item_style))
    story.append(P("5. Technical Skills Developed", toc_item_style))
    story.append(P("6. Key Learnings &amp; Professional Growth", toc_item_style))
    story.append(P("6.1 Aerospace Telemetry Engineering &amp; Systems Complexity", toc_sub_item_style))
    story.append(P("6.2 Defensible &amp; Sandboxed AI in Mission-Critical Defense Systems", toc_sub_item_style))
    story.append(P("6.3 Transitioning from Static Heuristics to Machine Learning (Isolation Forest)", toc_sub_item_style))
    story.append(P("6.4 AST-Level Code Validation &amp; Database Engine Hardening", toc_sub_item_style))
    story.append(P("6.5 Vector Embeddings &amp; Programmatic Zero-Hallucination Guardrails", toc_sub_item_style))
    story.append(P("6.6 Professional Engineering Practices &amp; Full-Stack Development", toc_sub_item_style))
    story.append(P("7. Conclusion", toc_item_style))
        
    story.append(PageBreak())

    # =========================================================================
    # PAGE 4: 1. EXECUTIVE SUMMARY & 2. INTERNSHIP OVERVIEW (Reference page 3)
    # =========================================================================
    story.append(P("1. Executive Summary", h1_style))
    story.append(P(
        "This report documents my internship under the <i>Def-Space Artificial Intelligence Programme 2026</i>, hosted by the <b>Bharat Space Education Research Centre (BSERC)</b>, undertaken to satisfy academic requirements for 7th Semester Internship / Industrial Training credits at the <b>National Institute of Technology Durgapur</b>.",
        body_style
    ))
    story.append(P(
        "My primary engineering contribution was designing and developing <b>Spacepilot</b>—a unified Generative AI decision-support platform built for satellite ground operations and defense earth observation. Spacepilot bridges the critical operational gap between structured satellite telemetry databases and voluminous, unstructured flight operating documentation. I architected and implemented three interconnected core capabilities: an NL2SQL query engine with SQLGlot AST validation, an autonomous anomaly detection engine combining deterministic safety thresholds with Scikit-Learn IsolationForest multivariate outlier modeling, and an advanced RAG knowledge assistant featuring dense vector semantic embeddings with dual operational guardrails (Strict Defense Mode vs. Hybrid Copilot Mode).",
        body_style
    ))
    story.append(P(
        "A defining challenge was working with data that is inherently complex, high-velocity, and mission-critical. In satellite ground station environments, queries must be executed against relational telemetry databases within tight orbital pass windows (10–15 minutes), and AI-generated outputs must have zero tolerance for ungrounded speculation (hallucination). By implementing engine-level SQLite read-only sandboxing (<code>PRAGMA query_only = ON;</code>), recursive AST validation, cosine similarity cutoff gates, and automated self-correction loops, Spacepilot enforces strict reliability while eliminating manual query friction.",
        body_style
    ))
    story.append(P(
        "These projects delivered measurable engineering impact: automating complex multi-satellite telemetry queries into sub-second natural language interactions, flagging multi-channel sensor anomalies with verified SOP uplink sequences, and providing verifiable document search with verbatim citations—deployed live at <code>https://spacepilot-isro.streamlit.app/</code>.",
        body_style
    ))
    
    story.append(Spacer(1, 8))
    story.append(P("2. Internship Overview", h1_style))
    story.append(Spacer(1, 4))
    
    overview_table_data = [
        [P("<b>Organisation</b>", meta_key_style), P("Bharat Space Education Research Centre (BSERC)", meta_val_style)],
        [P("<b>Location</b>", meta_key_style), P("Bharat Space Education Research Centre, Bengaluru (Virtual Command Operations)", meta_val_style)],
        [P("<b>Department</b>", meta_key_style), P("Aerospace Artificial Intelligence &amp; Satellite Operations", meta_val_style)],
        [P("<b>Duration</b>", meta_key_style), P("15-Day Intensive Def-Space AI Programme 2026 (Certificate ID: BSERC-2026-AI-1035)", meta_val_style)],
        [P("<b>Domain</b>", meta_key_style), P("Space Mission Operations, Telemetry Diagnostics &amp; Defense AI", meta_val_style)],
        [P("<b>Technology Area</b>", meta_key_style), P("Python, Google Gemini Cloud AI, SQLGlot, SQLite, IsolationForest, Dense Vector Embeddings, Streamlit Cloud", meta_val_style)],
    ]
    t_over = Table(overview_table_data, colWidths=[1.8*inch, 5.2*inch])
    t_over.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 0.75, C_BORDER),
        ('INNERGRID', (0,0), (-1,-1), 0.5, C_BORDER),
        ('PADDING', (0,0), (-1,-1), 4),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('BACKGROUND', (0,0), (0,-1), C_LIGHT),
    ]))
    story.append(t_over)
    
    story.append(PageBreak())

    # =========================================================================
    # PAGE 5: 3. TECHNOLOGY BACKGROUND (Reference page 4)
    # =========================================================================
    story.append(P("3. Technology Background", h1_style))
    story.append(P("The projects drew upon a range of technologies central to modern aerospace telemetry engineering, database security, applied machine learning, and Generative AI.", body_style))
    
    story.append(P("3.1 Relational Telemetry Databases &amp; SQLGlot AST Validation", h2_style))
    story.append(P(
        "Satellite telemetry systems record high-frequency time-series measurements across multiple subsystems: electrical power (battery voltage, solar current), thermal control (temperatures across payload and bus), and attitude determination and control (gyroscope drift rates). Storing and querying this data requires an ACID-compliant relational engine. To guarantee database security against unintended mutations or prompt injection attacks, Spacepilot implements full Abstract Syntax Tree (AST) validation using <code>sqlglot</code>. Rather than relying on fragile regex matching, the parser validates that the root statement is strictly an <code>exp.Select</code> or <code>exp.Union</code>, recursively inspecting child AST nodes to reject destructive operations (<code>exp.Drop</code>, <code>exp.Delete</code>, <code>exp.Insert</code>, <code>exp.Update</code>, <code>exp.Alter</code>). Furthermore, the SQLite connection executes <code>PRAGMA query_only = ON;</code>, providing engine-level read-only enforcement.",
        body_style
    ))
    
    story.append(P("3.2 Streamlit Web Framework &amp; Reactive Telemetry Dashboards", h2_style))
    story.append(P(
        "Streamlit provides a reactive WSGI Python application server that re-executes cleanly on user interaction while preserving session state. In Spacepilot, Streamlit manages multi-tab navigation, dynamic file uploads (CSVs and PDFs), real-time KPI metric cards, and responsive dataframes. For telemetry visualization, Plotly Express renders interactive dark-themed time-series curves for voltage drops, thermal excursions, and gyroscope drift rates.",
        body_style
    ))
    
    story.append(P("3.3 Generative AI, Large Language Models &amp; Self-Correction Feedback Loops", h2_style))
    story.append(P(
        "Large Language Models serve as intelligent reasoning backends capable of translating human operational queries into structured database queries and synthesizing standard operating procedures into tactical checklists. Spacepilot integrates Google Gemini models (<code>gemini-2.5-flash</code>, <code>gemini-1.5-flash</code>) via official SDKs. To guarantee reliability, the system incorporates an automated self-correction loop: if an executed query fails with a database exception, the error message and failed query are fed back to Gemini to generate an immediate, self-corrected query.",
        body_style
    ))
    
    story.append(P("3.4 Dense Vector Semantic Embeddings, Cosine Similarity &amp; Guardrail Routing", h2_style))
    story.append(P(
        "To search spacecraft flight manuals reliably, Spacepilot employs dense 128-dimensional subword vector embedding projections with L2-normalization. Semantic similarity is measured via normalized Cosine Similarity and fused with TF-IDF lexical overlap (65% vector similarity, 35% keyword overlap). To prevent AI hallucination in mission-critical flight operations, Spacepilot implements dual operational guardrails: <b>Strict Defense Mode</b> strictly bounds answers to retrieved flight manual passages and programmatic similarity gating (rejection below 0.28 similarity), while <b>Hybrid Copilot Mode</b> gracefully falls back to general astrophysics with explicit disclosure.",
        body_style
    ))
    
    story.append(PageBreak())

    # =========================================================================
    # PAGE 6: 4. PROJECTS UNDERTAKEN — 4.1 END-TO-END ARCHITECTURE (Ref page 5)
    # =========================================================================
    story.append(P("4. Projects Undertaken", h1_style))
    story.append(P("During the internship, I architected and developed the complete Spacepilot system across three specialized modules and integrated data pipelines.", body_style))
    
    story.append(P("4.1 End-to-End System Architecture &amp; Data Flow Pipeline", h2_style))
    story.append(P("<b>My Role:</b> Sole Architect &amp; Developer — Conceived, designed, and implemented the entire pipeline from multi-modal data ingestion to Gemini synthesis and Streamlit deployment.", body_style))
    
    story.append(P(
        "<b>Overview:</b> Satellite mission operations require handling both structured telemetry streams (time-series sensor logs) and unstructured mission documentation (flight manuals, emergency SOPs). Spacepilot unifies these distinct modalities into a single operational copilot. The pipeline operates across four coordinated stages: (1) <b>Multi-Modal Ingestion:</b> ingests live simulated telemetry, user-uploaded CSV datasets (e.g. <code>mission_launches.csv</code>), and flight manuals; (2) <b>Core Intelligence Modules:</b> routes inputs through AST-validated NL2SQL, IsolationForest anomaly detection, or dense vector RAG; (3) <b>Knowledge &amp; AI Cloud:</b> executes against SQLite and Google Gemini Cloud; and (4) <b>Cosmic Operations UI:</b> delivers real-time telemetry visualizations, KPI cards, and ground-command sequences.",
        body_style
    ))
    
    flow_img_path = os.path.join(ASSETS_DIR, "system_flowchart.png")
    if os.path.exists(flow_img_path):
        story.append(Spacer(1, 2))
        story.append(Image(flow_img_path, width=7.0*inch, height=3.6*inch))
        story.append(P("Figure 1: Spacepilot End-to-End System Architecture and Multi-Modal Data Flow Pipeline.", caption_style))
        
    story.append(P("<b>Impact:</b> Unifies multi-satellite sensor monitoring, ad-hoc database querying, and flight procedure lookups into a single cohesive interface, eliminating cross-platform hopping during time-critical orbital passes.", body_style))

    story.append(PageBreak())

    # =========================================================================
    # PAGE 7: 4.2 MODULE 1: NL2SQL TELEMETRY QUERY ENGINE (Ref page 6)
    # =========================================================================
    story.append(P("4.2 Natural Language-to-SQL Telemetry Query Engine (NL2SQL)", h2_style))
    story.append(P("<b>My Role:</b> Sole Developer — Built the natural language parser, SQLite schema extractor, SQLGlot AST validator, self-correction feedback loop, and dynamic CSV ingestion pipeline.", body_style))
    
    story.append(P(
        "<b>Problem Statement:</b> Ground station operators monitoring constellations during short 10-to-15 minute passes cannot manually construct complex multi-table SQL joins under high operational stress. Writing manual queries introduces syntax errors and delays urgent operational decisions. The system required a reliable natural language interface that prevents accidental database corruption.",
        body_style
    ))
    
    story.append(P("<b>Key Features Built:</b>", h3_style))
    story.append(P("• <b>SQLGlot AST Structural Validation:</b> Parses generated queries into an Abstract Syntax Tree via <code>sqlglot.parse_one(query, read='sqlite')</code>. Enforces that the root node is strictly <code>exp.Select</code> or <code>exp.Union</code>, recursively traversing all nodes to reject destructive statements (<code>DROP</code>, <code>DELETE</code>, <code>INSERT</code>, <code>UPDATE</code>, <code>ALTER</code>).", bullet_style))
    story.append(P("• <b>Engine-Level Read-Only Sandboxing:</b> Configures database connections with <code>PRAGMA query_only = ON;</code>, making it physically impossible for destructive writes to execute at the SQLite engine level.", bullet_style))
    story.append(P("• <b>Automated Self-Correction Loop:</b> When query execution raises an SQLite exception, the runtime error traceback is reflected back to Gemini to automatically regenerate and execute a corrected query, tracking the active executed query in the final summary.", bullet_style))
    story.append(P("• <b>Dynamic CSV Dataset Ingestion:</b> Supports uploading arbitrary mission CSV datasets (e.g. <code>mission_launches.csv</code> containing 4,324 space mission records). Column names are sanitized, a dedicated SQLite table is registered dynamically, and the schema is immediately queryable in plain English.", bullet_style))

    csv_img_path = os.path.join(ASSETS_DIR, "01_nl2sql_custom_csv_execution.jpg")
    if os.path.exists(csv_img_path):
        story.append(Spacer(1, 2))
        story.append(Image(csv_img_path, width=7.0*inch, height=3.1*inch))
        story.append(P("Figure 2: Natural Language to SQL query on uploaded mission_launches.csv dataset displaying SpaceX launch records.", caption_style))

    story.append(P("<b>Impact:</b> Enables sub-second querying across complex telemetry and custom aerospace datasets with complete mathematical immunity against destructive SQL injection or accidental data mutation.", body_style))

    story.append(PageBreak())

    # =========================================================================
    # PAGE 8: 4.3 MODULE 2: ANOMALY DETECTION & EMERGENCY TRIAGE (Ref page 7)
    # =========================================================================
    story.append(P("4.3 Autonomous Anomaly Detection &amp; Grounded Emergency Triage", h2_style))
    story.append(P("<b>My Role:</b> Sole Developer — Built the dual-layer anomaly scanner, IsolationForest ML model, grounded SOP command mapping engine, and emergency triage briefing synthesizer.", body_style))
    
    story.append(P(
        "<b>Problem Statement:</b> Sensor excursions—such as battery undervoltage, thermal runaway, or gyroscope drift—require immediate correlation with official Standard Operating Procedures (SOPs). Manually flipping through multi-hundred-page flight manuals introduces dangerous cognitive lag during satellite emergencies.",
        body_style
    ))
    
    story.append(P("<b>Key Features Built:</b>", h3_style))
    story.append(P("• <b>Deterministic Aerospace Threshold Limits:</b> Scans telemetry for critical boundary excursions: Battery Voltage &lt; 18.0V (Critical: 14.0V), Battery Temp &gt; 35.0°C (Critical: 45.0°C), and Gyroscope Drift &gt; 0.05°/s.", bullet_style))
    story.append(P("• <b>Unsupervised ML Anomaly Detection (IsolationForest):</b> Implements Scikit-Learn's <code>IsolationForest(n_estimators=100, contamination=0.03)</code> fitted across 5 continuous telemetry dimensions (<code>battery_voltage</code>, <code>battery_temp_c</code>, <code>solar_panel_current</code>, <code>gyro_drift_rate</code>, <code>signal_strength_dbm</code>), flagging multivariate statistical outliers that single-metric thresholds miss.", bullet_style))
    story.append(P("• <b>Grounded SOP Command Traceability:</b> Automatically retrieves contingency procedures from verified mission documentation (<code>satellite_anomaly_triage_sop.txt</code>, <code>eos04_radar_reconnaissance_specs.txt</code>). Every ground uplink command is strictly mapped to documented procedures; undocumented conditions return an explicit <code>INSUFFICIENT_DOCUMENTED_EVIDENCE</code> notification to prevent speculative commands.", bullet_style))
    story.append(P("• <b>Structured Emergency Briefing:</b> Generates a 3-part tactical briefing: (1) Critical Assessment (severity and sensor deltas), (2) Probable Root Cause (hardware diagnostics), and (3) Step-by-Step Command Sequence (payload load-shedding, bus switching).", bullet_style))

    anom_img1 = os.path.join(ASSETS_DIR, "02_anomaly_triage_alert_metrics.jpg")
    anom_img2 = os.path.join(ASSETS_DIR, "03_anomaly_triage_ground_command_sop.jpg")
    if os.path.exists(anom_img1):
        story.append(Spacer(1, 1))
        story.append(Image(anom_img1, width=7.0*inch, height=2.0*inch))
        story.append(P("Figure 3: Anomaly alert dashboard displaying critical undervoltage and thermal readings for EOS-04.", caption_style))
    if os.path.exists(anom_img2):
        story.append(Spacer(1, 1))
        story.append(Image(anom_img2, width=7.0*inch, height=2.0*inch))
        story.append(P("Figure 4: Ground station action sequence generated by cross-referencing telemetry with SOP flight manuals.", caption_style))

    story.append(P("<b>Impact:</b> Constellation-wide health monitoring (25 alerts flagged across 7 satellite nodes) with automated, verified recovery command sequences.", body_style))

    story.append(PageBreak())

    # =========================================================================
    # PAGE 9: 4.4 MODULE 3: MISSION KNOWLEDGE ASSISTANT (RAG) (Ref page 8)
    # =========================================================================
    story.append(P("4.4 Mission Knowledge Assistant (RAG Engine)", h2_style))
    story.append(P("<b>My Role:</b> Sole Developer — Conceived and built the document ingestion pipeline, dense vector embedding model, cosine similarity ranking, hybrid fusion, and dual guardrail routing.", body_style))
    
    story.append(P(
        "<b>Problem Statement:</b> Commercial Generative AI models frequently generate plausible-sounding but technically ungrounded information (hallucinations). In aerospace and defense operations, relying on an unverified operating parameter can lead to total mission loss.",
        body_style
    ))
    
    story.append(P("<b>Key Features Built:</b>", h3_style))
    story.append(P("• <b>Hybrid Dense Vector &amp; Lexical Retrieval:</b> Projects document passages into 128-dimensional dense subword vector embeddings with L2-normalization. Fuses normalized Cosine Similarity (65%) with TF-IDF/BM25 lexical keyword overlap (35%) for robust semantic and acronym matching.", bullet_style))
    story.append(P("• <b>Dual Operational Guardrail Routing:</b> Supports two distinct operating modes depending on mission criticality:", bullet_style))

    mode_table_data = [
        [P("<b>Operational Dimension</b>", meta_key_style), P("<b>Strict Defense Mode (Zero Hallucination)</b>", meta_key_style), P("<b>Hybrid Copilot Mode (Extended Science)</b>", meta_key_style)],
        [P("<b>Primary Objective</b>", body_style), P("Mission-critical flight operations where hallucination cannot be tolerated.", body_style), P("General space exploration, operator training, and astronomical inquiries.", body_style)],
        [P("<b>Knowledge Bounding</b>", body_style), P("Strictly bounded to verified, uploaded flight manuals and SOP documents.", body_style), P("Primary grounding on flight manuals; falls back to general astrophysics when unlisted.", body_style)],
        [P("<b>Out-of-Domain Behavior</b><br/><i>(e.g., 'what is asteroid')</i>", body_style), P("<b>Hard Programmatic Rejection:</b><br/><i>'The available flight manuals do not contain information regarding this topic.'</i>", body_style), P("<b>Transparent Synthesis:</b><br/>Explains topic with explicit disclosure: <i>'(Note: This topic is outside your current spacecraft manuals...)'</i>", body_style)],
        [P("<b>Source Citation</b>", body_style), P("Every factual statement is bound to explicit document references (e.g. <code>[UserGuide_extracted.txt]</code>).", body_style), P("Flight manuals cited when used; external science explicitly disclosed.", body_style)]
    ]
    t_mode = Table(mode_table_data, colWidths=[1.6*inch, 2.7*inch, 2.7*inch])
    t_mode.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 0.75, C_BORDER),
        ('INNERGRID', (0,0), (-1,-1), 0.5, C_BORDER),
        ('PADDING', (0,0), (-1,-1), 3.5),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('BACKGROUND', (0,0), (-1,0), C_LIGHT),
    ]))
    story.append(t_mode)

    rag_img1 = os.path.join(ASSETS_DIR, "04_rag_hybrid_mode_general_science.jpg")
    if os.path.exists(rag_img1):
        story.append(Spacer(1, 2))
        story.append(Image(rag_img1, width=7.0*inch, height=2.2*inch))
        story.append(P("Figure 5: Hybrid Copilot Mode answering 'what is asteroid' with scientific explanation and contextual disclosure note.", caption_style))

    story.append(P("<b>Impact:</b> Eliminates hallucinations during flight-critical queries while retaining broad conversational utility for general operator training.", body_style))

    story.append(PageBreak())

    # =========================================================================
    # PAGE 10: 4.5 STRICT DEFENSE MODE VERIFICATION & CONSOLE (Ref page 9)
    # =========================================================================
    story.append(P("4.5 Strict Defense Mode Verification &amp; Operations Console", h2_style))
    story.append(P("<b>My Role:</b> Sole Developer — Designed validation test protocols and implemented the unified Streamlit operations dashboard console.", body_style))
    
    story.append(P(
        "<b>Verification Scenarios:</b> Strict Defense Mode was validated against two high-stakes operational scenarios: (1) <b>Anti-Hallucination Rejection:</b> submitting an out-of-domain query (<i>'what is asteroid'</i>) triggers a programmatic similarity cutoff (&lt; 0.28) that rejects the prompt before calling the LLM (Figure 6); and (2) <b>Dynamic Document Ingestion:</b> uploading <code>UserGuide.pdf</code> via <code>pypdf</code> and asking <i>'Describe Airspeed limitations'</i> correctly extracts takeoff and re-entry velocity limits with verbatim file citations (Figure 7).",
        body_style
    ))
    
    rag_img2 = os.path.join(ASSETS_DIR, "05_rag_strict_mode_antihallucination.jpg")
    rag_img3 = os.path.join(ASSETS_DIR, "06_rag_strict_mode_pdf_citations.jpg")
    dash_img_path = os.path.join(ASSETS_DIR, "spacepilot_dashboard.png")
    
    side_images = [
        [Image(rag_img2, width=3.45*inch, height=1.9*inch), Image(rag_img3, width=3.45*inch, height=1.9*inch)],
        [P("Figure 6: Strict Mode Anti-Hallucination Rejection.", caption_style), P("Figure 7: Strict Mode PDF Citations (UserGuide.pdf).", caption_style)]
    ]
    t_side = Table(side_images, colWidths=[3.5*inch, 3.5*inch])
    t_side.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('PADDING', (0,0), (-1,-1), 1),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
    ]))
    story.append(t_side)
    
    story.append(Spacer(1, 2))
    if os.path.exists(dash_img_path):
        story.append(Image(dash_img_path, width=7.0*inch, height=2.6*inch))
        story.append(P("Figure 8: Spacepilot Web Application Dashboard Overview running live on Streamlit Cloud.", caption_style))

    story.append(P("<b>Impact:</b> Mathematically proves zero hallucination for off-domain queries while providing instantaneous, cited answers for newly ingested flight manuals.", body_style))

    story.append(PageBreak())

    # =========================================================================
    # PAGE 11: 5. TECHNICAL SKILLS DEVELOPED (Exact mirror of reference page 10)
    # =========================================================================
    story.append(P("5. Technical Skills Developed", h1_style))
    story.append(P("The project developed and demonstrated competencies across a diverse set of modern software engineering, database security, machine learning, and Generative AI technologies:", body_style))
    story.append(Spacer(1, 6))
    
    skills_table_data = [
        [P("<b>Category</b>", meta_key_style), P("<b>Technologies / Skills</b>", meta_key_style)],
        [P("Languages", meta_key_style), P("Python 3.10+, SQL (SQLite dialect), HTML5, CSS3, JavaScript (Vanilla)", meta_val_style)],
        [P("Web Frameworks &amp; Dashboards", meta_key_style), P("Streamlit 1.35+, Plotly Express 5.20+ (interactive telemetry visualisations)", meta_val_style)],
        [P("Database &amp; Query Security", meta_key_style), P("SQLite3, sqlglot 23.0+ (AST parsing, read-only AST traversal), PRAGMA query_only = ON;", meta_val_style)],
        [P("Machine Learning &amp; Analytics", meta_key_style), P("scikit-learn 1.4+ (IsolationForest unsupervised multivariate anomaly detection), NumPy, Pandas 2.2+ (time-series wrangling, CSV normalization)", meta_val_style)],
        [P("Foundation LLMs &amp; GenAI", meta_key_style), P("Google Gemini Cloud AI (google-genai 0.1+, google-generativeai 0.7+), prompt engineering, schema injection, runtime self-correction feedback loops", meta_val_style)],
        [P("Information Retrieval &amp; RAG", meta_key_style), P("Dense Vector Semantic Embeddings (128-D subword projection, L2-norm), Cosine Similarity, TF-IDF lexical hybrid scoring, pypdf 4.0+ (dynamic PDF extraction)", meta_val_style)],
        [P("Reporting &amp; Architecture Diagrams", meta_key_style), P("reportlab 4.0+ / 5.1+ (automated PDF document generation), matplotlib 3.8+ (system flowchart design)", meta_val_style)],
        [P("Deployment &amp; Version Control", meta_key_style), P("Streamlit Community Cloud (https://spacepilot-isro.streamlit.app/), Git, GitHub, python-dotenv", meta_val_style)],
    ]
    t_skills = Table(skills_table_data, colWidths=[2.1*inch, 4.9*inch])
    t_skills.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 0.75, C_BORDER),
        ('INNERGRID', (0,0), (-1,-1), 0.5, C_BORDER),
        ('PADDING', (0,0), (-1,-1), 5),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BACKGROUND', (0,0), (-1,0), C_LIGHT),
        ('BACKGROUND', (0,1), (0,-1), C_LIGHT),
    ]))
    story.append(t_skills)

    story.append(PageBreak())

    # =========================================================================
    # PAGE 12: 6. KEY LEARNINGS & PROFESSIONAL GROWTH (Reference page 11)
    # =========================================================================
    story.append(P("6. Key Learnings &amp; Professional Growth", h1_style))
    story.append(Spacer(1, 4))
    
    story.append(P("6.1 Aerospace Telemetry Engineering &amp; Systems Complexity", h2_style))
    story.append(P(
        "Working with multi-channel satellite telemetry exposed me to the realities of aerospace engineering: sensor readings are noisy, coupled, and subject to orbital geometry (sunlight vs. eclipse cycles). Designing Spacepilot required developing deep domain familiarity with power architectures, thermal management limits, and attitude control drift behaviors.",
        body_style
    ))
    
    story.append(P("6.2 Defensible &amp; Sandboxed AI in Mission-Critical Defense Systems", h2_style))
    story.append(P(
        "A major takeaway was recognizing that in mission-critical environments, unconstrained LLMs cannot be trusted blindly. Developing Strict Defense Mode demonstrated how to establish hard boundaries around AI reasoning—ensuring every recommendation is traceable to verified documentation and that unsupported claims are rejected programmatically.",
        body_style
    ))
    
    story.append(P("6.3 Transitioning from Static Heuristics to Machine Learning (Isolation Forest)", h2_style))
    story.append(P(
        "While simple threshold limits detect severe violations, they fail to catch coupled multi-sensor degradation (e.g. moderate solar current drop combined with slight thermal rise). Implementing Scikit-Learn's IsolationForest provided hands-on experience in unsupervised outlier detection, evaluating multivariate decision scores alongside deterministic bounds.",
        body_style
    ))
    
    story.append(P("6.4 AST-Level Code Validation &amp; Database Engine Hardening", h2_style))
    story.append(P(
        "Moving from fragile regex string matching to true Abstract Syntax Tree parsing via <code>sqlglot</code> was an essential lesson in defensive engineering. Coupling AST validation with SQLite engine-level read-only pragmas (<code>PRAGMA query_only = ON;</code>) demonstrated how to build layered security into AI-driven database tools.",
        body_style
    ))
    
    story.append(P("6.5 Vector Embeddings &amp; Programmatic Zero-Hallucination Guardrails", h2_style))
    story.append(P(
        "Implementing dense vector embeddings, L2-normalization, and normalized cosine similarity ranking taught me how semantic search operates under the hood. Combining vector similarity with lexical matching and programmatic threshold rejection (&lt; 0.28) proved that AI guardrails should be enforced programmatically rather than relying purely on prompt instructions.",
        body_style
    ))
    
    story.append(P("6.6 Professional Engineering Practices &amp; Full-Stack Development", h2_style))
    story.append(P(
        "Developing Spacepilot end-to-end strengthened my full-stack engineering discipline: managing Git version control, structuring modular Python packages, handling cloud environment secrets, and building responsive, production-ready user interfaces deployed publicly on Streamlit Cloud.",
        body_style
    ))

    story.append(PageBreak())

    # =========================================================================
    # PAGE 13: 7. CONCLUSION & REFERENCES (Reference page 12)
    # =========================================================================
    story.append(P("7. Conclusion", h1_style))
    story.append(Spacer(1, 4))
    story.append(P(
        "My 15-day internship under the <i>Def-Space Artificial Intelligence Programme 2026</i> at the <b>Bharat Space Education Research Centre (BSERC)</b> was an intense, intellectually demanding, and deeply rewarding engineering experience. Developing <b>Spacepilot</b> allowed me to tackle genuine operational bottlenecks in space mission operations: bridging structured telemetry data with unstructured flight manuals, automating anomaly triage, and eliminating AI hallucinations through strict guardrails.",
        body_style
    ))
    story.append(P(
        "Across the project lifecycle, I gained practical competence in full-stack Python development, SQLite AST-based security engineering, unsupervised machine learning with IsolationForest, vector-based semantic retrieval, and reactive web dashboard design. Deploying the application live on Streamlit Cloud (<code>https://spacepilot-isro.streamlit.app/</code>) confirmed that the architecture delivers sub-second query responses, mathematically verifiable database security, and reliable document grounding.",
        body_style
    ))
    story.append(P(
        "I express my deepest gratitude to the scientists, engineers, and mentors at the <b>Bharat Space Education Research Centre (BSERC)</b> for their guidance and curriculum. I also thank the faculty members of the <b>Department of Computer Science &amp; Engineering, National Institute of Technology Durgapur</b>, for supporting this internship and evaluating this report towards my 7th Semester B.Tech academic credits. The discipline and technical skills acquired during this internship form a strong foundation for my continued growth as a software engineer.",
        body_style
    ))
    
    story.append(Spacer(1, 8))
    story.append(P("References", h2_style))
    story.append(P("[1] Indian Space Research Organisation (ISRO). <i>INSAT-3DR Meteorological Satellite Flight Telemetry Handbook</i>, URSC, Bangalore, 2016.", ParagraphStyle('Ref1', fontName='Helvetica', fontSize=8, leading=10.5, textColor=C_DARK, spaceAfter=2)))
    story.append(P("[2] Indian Space Research Organisation (ISRO). <i>EOS-04 (RISAT-1A) Radar Imaging Satellite Mission Specs &amp; Power Architecture</i>, URSC, 2022.", ParagraphStyle('Ref2', fontName='Helvetica', fontSize=8, leading=10.5, textColor=C_DARK, spaceAfter=2)))
    story.append(P("[3] Bharat Space Education Research Centre (BSERC). <i>Def-Space AI 2026: Satellite Subsystem Anomaly Triage Operating Protocols</i>, Bangalore, 2026.", ParagraphStyle('Ref3', fontName='Helvetica', fontSize=8, leading=10.5, textColor=C_DARK, spaceAfter=2)))
    story.append(P("[4] Liu, F. T., Ting, K. M., &amp; Zhou, Z. H. <i>Isolation Forest</i>, Eighth IEEE International Conference on Data Mining (ICDM), pp. 413-422, 2008.", ParagraphStyle('Ref4', fontName='Helvetica', fontSize=8, leading=10.5, textColor=C_DARK, spaceAfter=2)))
    story.append(P("[5] Lewis, P., et al. <i>Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks</i>, Advances in Neural Information Processing Systems (NeurIPS), 2020.", ParagraphStyle('Ref5', fontName='Helvetica', fontSize=8, leading=10.5, textColor=C_DARK, spaceAfter=2)))

    story.append(Spacer(1, 25))
    story.append(P("— End of Report —", ParagraphStyle('EndOfRep', fontName='Helvetica', fontSize=10, leading=14, textColor=C_BLACK, alignment=1)))

    return story

def generate_pdf():
    print(f"Generating Spacepilot Project Report PDF matching reference format...")
    doc = SimpleDocTemplate(
        OUTPUT_REPORT_PDF,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )
    story = build_pdf_story()
    doc.build(story, canvasmaker=ReferenceStyleCanvas)
    
    import pypdf
    reader = pypdf.PdfReader(OUTPUT_REPORT_PDF)
    print(f"SUCCESS! Generated {len(reader.pages)} pages at: {OUTPUT_REPORT_PDF}")
    for idx, page in enumerate(reader.pages):
        print(f"Page {idx+1}: {page.mediabox}")

if __name__ == "__main__":
    generate_pdf()
