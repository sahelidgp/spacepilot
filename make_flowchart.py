import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches

def draw_system_flowchart(output_path):
    fig, ax = plt.subplots(figsize=(10, 6.2), dpi=300)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis('off')

    # Background color
    fig.patch.set_facecolor('#FFFFFF')
    ax.set_facecolor('#FFFFFF')

    # Color Palette
    PRIMARY = '#0F172A'    # Deep Slate
    BORDER_CLR = '#475569' # Slate border
    FILL_INPUT = '#F1F5F9' # Very light gray
    FILL_MOD1 = '#EFF6FF'  # Light Blue
    FILL_MOD2 = '#FEF2F2'  # Light Red
    FILL_MOD3 = '#FAF5FF'  # Light Violet
    FILL_DB = '#F0FDF4'    # Light Green
    FILL_AI = '#F5F3FF'    # Soft Purple
    FILL_OUT = '#ECFDF5'   # Mint Green

    def add_box(x, y, w, h, text, title="", fill='#FFFFFF', border=BORDER_CLR, rx=1.5):
        box = patches.FancyBboxPatch(
            (x, y), w, h,
            boxstyle=f"round,pad=0.5,rounding_size={rx}",
            facecolor=fill, edgecolor=border, linewidth=1.5
        )
        ax.add_patch(box)
        if title:
            ax.text(x + w/2, y + h - 2.8, title, ha='center', va='center',
                    fontsize=9, fontweight='bold', color=PRIMARY, fontfamily='sans-serif')
            ax.text(x + w/2, y + (h - 2.8)/2, text, ha='center', va='center',
                    fontsize=7.8, color='#334155', fontfamily='sans-serif', linespacing=1.2)
        else:
            ax.text(x + w/2, y + h/2, text, ha='center', va='center',
                    fontsize=8.2, fontweight='bold', color=PRIMARY, fontfamily='sans-serif', linespacing=1.2)

    def add_arrow(x1, y1, x2, y2, label=""):
        ax.annotate(
            "", xy=(x2, y2), xytext=(x1, y1),
            arrowprops=dict(arrowstyle="->", color='#64748B', lw=1.5, shrinkA=3, shrinkB=3)
        )
        if label:
            mx, my = (x1 + x2)/2, (y1 + y2)/2
            ax.text(mx, my + 1.2, label, ha='center', va='bottom', fontsize=7, color='#64748B', fontweight='bold')

    # 1. TOP: OPERATOR INPUTS (y: 86 - 96)
    add_box(3, 85, 28, 11, "Natural Language Telemetry Questions\n(e.g., 'Show satellites with battery < 15V')", "Operator Natural Queries", FILL_INPUT, '#38BDF8')
    add_box(36, 85, 28, 11, "Multi-Channel Sensor Stream\n& Custom CSV Uploads (mission_launches)", "Telemetry Ingestion", FILL_INPUT, '#38BDF8')
    add_box(69, 85, 28, 11, "Flight Operating Manuals (SOPs)\n& Custom PDF Specs (UserGuide.pdf)", "Aerospace Documentation", FILL_INPUT, '#38BDF8')

    # 2. MIDDLE: CORE THREE MODULES (y: 46 - 72)
    # Module 1
    add_box(3, 44, 28, 28, 
            "• Runtime Schema Extraction\n• Multi-Model SQL Generation\n• Read-Only AST Guardrails\n  (Blocks DROP, DELETE, INSERT)\n• Automated Self-Correction Loop\n• Pandas & SQLite Execution", 
            "Module 1: NL2SQL Engine", FILL_MOD1, '#3B82F6')
    
    # Module 2
    add_box(36, 44, 28, 28, 
            "• Continuous Telemetry Scanner\n• Critical Threshold Detection:\n  - Battery Voltage (< 18.0 V)\n  - Battery Temperature (> 35 °C)\n  - Gyroscope Drift (> 0.05 °/s)\n• Real-Time Delta Metric Badges\n• Ground Command SOP Sequencing", 
            "Module 2: Anomaly Triage", FILL_MOD2, '#EF4444')

    # Module 3
    add_box(69, 44, 28, 28, 
            "• PyPDF Page-by-Page Extraction\n• Context-Inheriting Chunker\n• Dual Guardrail Mode Router:\n  - Strict Mode (Hard Rejection)\n  - Hybrid Mode (General Science)\n• Lexical TF-IDF Search\n• Verbatim Source Document Citations", 
            "Module 3: Knowledge RAG", FILL_MOD3, '#8B5CF6')

    # 3. LOWER-MIDDLE: STORAGE & CLOUD AI LAYER (y: 20 - 34)
    add_box(5, 22, 25, 12, "SQLite3 Database\n(7 Satellites, 1,176 Telemetry pts\n+ Ingested CSV Tables)", "Relational Database", FILL_DB, '#10B981')
    add_box(37.5, 22, 25, 12, "Google Gemini Cloud AI\n(gemini-3.5-flash-lite & fallbacks\nOffline Rule-Based Heuristic)", "Foundation LLM Engine", FILL_AI, '#A855F7')
    add_box(70, 22, 25, 12, "Mission SOP Documentation\n(INSAT-3DR, EOS-04, Chandrayaan-3,\nIndexed PDF Knowledge Chunks)", "Flight Manual SOPs", FILL_DB, '#10B981')

    # 4. BOTTOM: STREAMLIT OPERATIONS DASHBOARD (y: 2 - 12)
    add_box(15, 2, 70, 11, 
            "Interactive Streamlit Console (spacepilot-isro.streamlit.app) · Cosmic Black & Violet Dark Theme\nTab 1: SQL Telemetry & CSV Ingestion | Tab 2: Anomaly Health & Uplink Command | Tab 3: RAG Document Assistant", 
            "Spacepilot Operations Dashboard (Live Web App)", FILL_OUT, '#059669')

    # CONNECTING ARROWS
    # Inputs to Modules
    add_arrow(17, 85, 17, 72)
    add_arrow(50, 85, 50, 72)
    add_arrow(83, 85, 83, 72)

    # Modules to Storage / LLM
    add_arrow(17, 44, 17, 34)     # Mod 1 to SQLite
    add_arrow(23, 44, 38, 34)     # Mod 1 to Gemini
    add_arrow(50, 44, 50, 34)     # Mod 2 to Gemini
    add_arrow(48, 44, 25, 34)     # Mod 2 to SQLite (scans telemetry)
    add_arrow(60, 44, 75, 34)     # Mod 2 to SOPs
    add_arrow(83, 44, 83, 34)     # Mod 3 to SOPs
    add_arrow(77, 44, 60, 34)     # Mod 3 to Gemini

    # Storage / LLM to Streamlit Dashboard
    add_arrow(17, 22, 25, 13)
    add_arrow(50, 22, 50, 13)
    add_arrow(83, 22, 75, 13)

    plt.tight_layout()
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Flowchart successfully generated at: {output_path}")

if __name__ == '__main__':
    assets_dir = 'C:/Users/Saheli Mahanty/.gemini/antigravity/scratch/spacepilot/assets'
    draw_system_flowchart(os.path.join(assets_dir, 'system_flowchart.png'))
