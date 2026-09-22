"""
Word Document Generator for EV Driving Range Prediction
Converts README.md into a fully styled Microsoft Word (.docx) document.
No emojis used. Professional academic/engineering layout.
"""

import os
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

def set_cell_background(cell, fill_hex):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    tcPr.append(shd)

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for m, val in [('top', top), ('bottom', bottom), ('left', left), ('right', right)]:
        node = OxmlElement(f'w:{m}')
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tcPr.append(tcMar)

def create_document(output_path: str, assets_dir: str):
    doc = Document()

    # Set 1-inch margins
    sections = doc.sections
    for section in sections:
        section.top_margin = Inches(1)
        section.bottom_margin = Inches(1)
        section.left_margin = Inches(1)
        section.right_margin = Inches(1)

    # Styles & Fonts
    COLOR_PRIMARY = RGBColor(15, 30, 60)       # Navy
    COLOR_ACCENT = RGBColor(29, 78, 216)       # Blue
    COLOR_DARK = RGBColor(30, 41, 59)          # Dark Slate
    COLOR_MUTED = RGBColor(100, 116, 139)      # Gray

    # Document Title
    p_title = doc.add_paragraph()
    r_title = p_title.add_run("Electric Vehicle Driving Range Prediction")
    r_title.font.name = "Arial"
    r_title.font.size = Pt(24)
    r_title.font.bold = True
    r_title.font.color.rgb = COLOR_PRIMARY
    p_title.space_after = Pt(4)

    # Subtitle
    p_sub = doc.add_paragraph()
    r_sub = p_sub.add_run("A Machine Learning Framework for Real-World EV Range Estimation")
    r_sub.font.name = "Arial"
    r_sub.font.size = Pt(13)
    r_sub.font.color.rgb = COLOR_ACCENT
    p_sub.space_after = Pt(12)

    # Overview Paragraph
    p_desc = doc.add_paragraph()
    p_desc.paragraph_format.line_spacing = 1.15
    r_desc = p_desc.add_run(
        "A machine learning framework for predicting real-world remaining driving range in Battery Electric Vehicles (BEVs), "
        "specifically calibrated for the 2013 Nissan Leaf (24 kWh battery pack) based on the University of Michigan "
        "Vehicle Energy Dataset (VED) telemetry schema."
    )
    r_desc.font.name = "Arial"
    r_desc.font.size = Pt(10.5)
    r_desc.font.color.rgb = COLOR_DARK
    p_desc.space_after = Pt(16)

    # Section 1: Overview
    h1 = doc.add_heading(level=1)
    r_h1 = h1.add_run("1. Overview")
    r_h1.font.name = "Arial"
    r_h1.font.size = Pt(16)
    r_h1.font.bold = True
    r_h1.font.color.rgb = COLOR_PRIMARY
    h1.space_before = Pt(14)
    h1.space_after = Pt(6)

    p1 = doc.add_paragraph()
    p1.paragraph_format.line_spacing = 1.15
    r1 = p1.add_run(
        "Accurate driving range estimation is critical to mitigating driver range anxiety. This repository implements an "
        "end-to-end regression pipeline that accounts for non-linear physical dynamics:"
    )
    r1.font.name = "Arial"
    r1.font.size = Pt(10.5)
    r1.font.color.rgb = COLOR_DARK
    p1.space_after = Pt(6)

    bullets1 = [
        ("Aerodynamic drag losses", "scaling with the cube of speed (P_drag proportional to v^3)."),
        ("Electro-chemical degradation", "in sub-zero winter temperatures (< 15 deg C)."),
        ("Cabin HVAC energy consumption", "(PTC heaters and A/C compressor drawing up to 4.5 kW)."),
        ("Gravitational resistance", "on road inclines and hilly terrain.")
    ]
    for b_title, b_text in bullets1:
        p_b = doc.add_paragraph(style='List Bullet')
        p_b.paragraph_format.space_after = Pt(3)
        p_b.paragraph_format.line_spacing = 1.15
        r_bt = p_b.add_run(b_title + ": ")
        r_bt.font.name = "Arial"
        r_bt.font.size = Pt(10)
        r_bt.font.bold = True
        r_bt.font.color.rgb = COLOR_DARK
        r_bx = p_b.add_run(b_text)
        r_bx.font.name = "Arial"
        r_bx.font.size = Pt(10)
        r_bx.font.color.rgb = COLOR_DARK

    p1_concl = doc.add_paragraph()
    p1_concl.paragraph_format.line_spacing = 1.15
    p1_concl.paragraph_format.space_before = Pt(6)
    p1_concl.paragraph_format.space_after = Pt(16)
    r1_c = p1_concl.add_run(
        "Three regression models were evaluated: Random Forest Regressor, Gradient Boosting Regressor, and Support Vector Regressor (SVR). "
        "SVR with a Radial Basis Function (RBF) kernel achieved the highest accuracy (R2 = 0.9953, MAE = 1.30 km) and was deployed as the primary model."
    )
    r1_c.font.name = "Arial"
    r1_c.font.size = Pt(10.5)
    r1_c.font.color.rgb = COLOR_DARK

    # Section 2: Model Performance Scoreboard
    h2 = doc.add_heading(level=1)
    r_h2 = h2.add_run("2. Model Performance Scoreboard")
    r_h2.font.name = "Arial"
    r_h2.font.size = Pt(16)
    r_h2.font.bold = True
    r_h2.font.color.rgb = COLOR_PRIMARY
    h2.space_before = Pt(14)
    h2.space_after = Pt(6)

    p2 = doc.add_paragraph()
    p2.paragraph_format.space_after = Pt(8)
    r2 = p2.add_run("Evaluated on an unseen 20% test holdout split (1,000 driving trips):")
    r2.font.name = "Arial"
    r2.font.size = Pt(10.5)
    r2.font.color.rgb = COLOR_DARK

    # Scoreboard Table
    table = doc.add_table(rows=4, cols=5)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    col_widths = [Inches(2.6), Inches(1.2), Inches(1.2), Inches(1.1), Inches(1.4)]

    headers = ["Model Architecture", "MAE", "RMSE", "R2 Score", "Status"]
    for i, h in enumerate(headers):
        cell = table.cell(0, i)
        cell.width = col_widths[i]
        set_cell_background(cell, "0F1E3C")
        set_cell_margins(cell, top=120, bottom=120, left=150, right=150)
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        r = p.add_run(h)
        r.font.name = "Arial"
        r.font.size = Pt(9.5)
        r.font.bold = True
        r.font.color.rgb = RGBColor(255, 255, 255)

    data_rows = [
        ["Support Vector Regressor (SVR)", "1.30 km", "1.92 km", "0.9953", "Deployed Champion"],
        ["Gradient Boosting Regressor", "1.88 km", "2.69 km", "0.9909", "Baseline Comparison"],
        ["Random Forest Regressor", "2.52 km", "3.61 km", "0.9835", "Baseline Comparison"]
    ]

    for row_idx, row_vals in enumerate(data_rows, start=1):
        bg_color = "F1F5F9" if row_idx % 2 == 1 else "FFFFFF"
        for col_idx, val in enumerate(row_vals):
            cell = table.cell(row_idx, col_idx)
            cell.width = col_widths[col_idx]
            set_cell_background(cell, bg_color)
            set_cell_margins(cell, top=100, bottom=100, left=150, right=150)
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            r = p.add_run(val)
            r.font.name = "Arial"
            r.font.size = Pt(9.5)
            r.font.color.rgb = COLOR_DARK
            if row_idx == 1:
                r.font.bold = True

    # Embed plot image
    img_file = os.path.join(assets_dir, "ev_model_comparison.png")
    if os.path.exists(img_file):
        p_img_title = doc.add_paragraph()
        p_img_title.paragraph_format.space_before = Pt(14)
        p_img_title.paragraph_format.space_after = Pt(4)
        r_it = p_img_title.add_run("Actual vs. Predicted Range Comparison:")
        r_it.font.name = "Arial"
        r_it.font.size = Pt(10.5)
        r_it.font.bold = True
        r_it.font.color.rgb = COLOR_PRIMARY

        doc.add_picture(img_file, width=Inches(6.5))
        p_cap = doc.add_paragraph()
        p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_cap.paragraph_format.space_before = Pt(4)
        p_cap.paragraph_format.space_after = Pt(16)
        r_cap = p_cap.add_run("Figure 1: Benchmark evaluation scatter plot showing ideal y=x reference.")
        r_cap.font.name = "Arial"
        r_cap.font.size = Pt(8.5)
        r_cap.font.color.rgb = COLOR_MUTED

    # Section 3: Repository Structure
    h3 = doc.add_heading(level=1)
    r_h3 = h3.add_run("3. Repository Structure")
    r_h3.font.name = "Arial"
    r_h3.font.size = Pt(16)
    r_h3.font.bold = True
    r_h3.font.color.rgb = COLOR_PRIMARY
    h3.space_before = Pt(14)
    h3.space_after = Pt(6)

    tree_text = (
        ".\n"
        "|-- .gitignore                         # Standard git ignore rules\n"
        "|-- README.md                          # Project documentation and guide\n"
        "|-- requirements.txt                   # Python package dependencies\n"
        "|-- app.py                             # Interactive Streamlit Web Application\n"
        "|-- data/\n"
        "|   `-- ev_driving_dataset.csv         # 5,000 trip records (VED Nissan Leaf specification)\n"
        "|-- models/\n"
        "|   `-- svr_pipeline.joblib            # Pre-trained SVR pipeline (StandardScaler + SVR)\n"
        "|-- notebooks/\n"
        "|   `-- ev_range_prediction.ipynb      # Executable Jupyter Notebook with analysis & plots\n"
        "|-- src/\n"
        "|   |-- __init__.py\n"
        "|   |-- data_generator.py              # Physics-grounded EV data simulation module\n"
        "|   |-- train.py                       # Training, benchmarking, and serialization script\n"
        "|   `-- predict.py                     # Standalone CLI inference utility\n"
        "|-- assets/\n"
        "|   `-- ev_model_comparison.png        # Benchmark evaluation scatter plot\n"
        "|-- docs/\n"
        "|   `-- PROJECT_REPORT.md              # Detailed academic/technical report\n"
        "`-- EV_Range_Prediction_Presentation.pptx # Widescreen presentation slide deck"
    )

    p_tree = doc.add_paragraph()
    p_tree.paragraph_format.line_spacing = 1.0
    p_tree.paragraph_format.space_after = Pt(16)
    r_tree = p_tree.add_run(tree_text)
    r_tree.font.name = "Courier New"
    r_tree.font.size = Pt(8.5)
    r_tree.font.color.rgb = RGBColor(15, 23, 42)

    # Section 4: Installation and Setup
    h4 = doc.add_heading(level=1)
    r_h4 = h4.add_run("4. Installation and Setup")
    r_h4.font.name = "Arial"
    r_h4.font.size = Pt(16)
    r_h4.font.bold = True
    r_h4.font.color.rgb = COLOR_PRIMARY
    h4.space_before = Pt(14)
    h4.space_after = Pt(6)

    inst_steps = [
        ("Prerequisites:", "Python 3.10 or higher. Recommended: Virtual environment (venv)."),
        ("Step 1 - Clone Repository:", "git clone https://github.com/airlord-0/EV-range-range-prediction.git\ncd EV-range-range-prediction"),
        ("Step 2 - Virtual Environment:", "python3 -m venv venv\nsource venv/bin/activate  # On Windows: venv\\Scripts\\activate"),
        ("Step 3 - Install Dependencies:", "pip install -r requirements.txt")
    ]

    for s_title, s_code in inst_steps:
        p_st = doc.add_paragraph()
        p_st.paragraph_format.space_before = Pt(4)
        p_st.paragraph_format.space_after = Pt(2)
        r_st = p_st.add_run(s_title)
        r_st.font.name = "Arial"
        r_st.font.size = Pt(10)
        r_st.font.bold = True
        r_st.font.color.rgb = COLOR_PRIMARY

        p_cd = doc.add_paragraph()
        p_cd.paragraph_format.line_spacing = 1.05
        p_cd.paragraph_format.space_after = Pt(6)
        r_cd = p_cd.add_run(s_code)
        r_cd.font.name = "Courier New"
        r_cd.font.size = Pt(9)
        r_cd.font.color.rgb = COLOR_DARK

    # Section 5: Usage
    h5 = doc.add_heading(level=1)
    r_h5 = h5.add_run("5. Usage")
    r_h5.font.name = "Arial"
    r_h5.font.size = Pt(16)
    r_h5.font.bold = True
    r_h5.font.color.rgb = COLOR_PRIMARY
    h5.space_before = Pt(14)
    h5.space_after = Pt(6)

    usage_items = [
        ("Launch Interactive Web Application:", "streamlit run app.py\nStarts local web server with interactive sliders for speed, temperature, SoC, slope, and HVAC power."),
        ("Retrain Models & Benchmark:", "python src/train.py\nRegenerates the dataset, evaluates all candidate models, and exports the champion model."),
        ("Run Standalone CLI Predictor:", "python src/predict.py\nPredicts remaining range for sample operational scenarios."),
        ("View Jupyter Notebook:", "jupyter lab notebooks/ev_range_prediction.ipynb\nInteractive exploration, mathematical formulas, and inline visualization.")
    ]

    for u_title, u_desc in usage_items:
        p_ut = doc.add_paragraph()
        p_ut.paragraph_format.space_before = Pt(4)
        p_ut.paragraph_format.space_after = Pt(2)
        r_ut = p_ut.add_run(u_title)
        r_ut.font.name = "Arial"
        r_ut.font.size = Pt(10)
        r_ut.font.bold = True
        r_ut.font.color.rgb = COLOR_PRIMARY

        p_ud = doc.add_paragraph()
        p_ud.paragraph_format.line_spacing = 1.05
        p_ud.paragraph_format.space_after = Pt(6)
        r_ud = p_ud.add_run(u_desc)
        r_ud.font.name = "Courier New"
        r_ud.font.size = Pt(9)
        r_ud.font.color.rgb = COLOR_DARK

    # Section 6: Real-World Scenario Examples
    h6 = doc.add_heading(level=1)
    r_h6 = h6.add_run("6. Real-World Scenario Examples")
    r_h6.font.name = "Arial"
    r_h6.font.size = Pt(16)
    r_h6.font.bold = True
    r_h6.font.color.rgb = COLOR_PRIMARY
    h6.space_before = Pt(14)
    h6.space_after = Pt(6)

    scenarios = [
        ("Scenario 1: Harsh Winter Highway", "Inputs: -5 deg C, 100 km/h, 80% SoC, 4.0 kW Heater", "Predicted Range: 39.8 km (~62% penalty due to cold chemistry and drag)."),
        ("Scenario 2: Mild Spring Urban Commute", "Inputs: +20 deg C, 40 km/h, 80% SoC, HVAC Off", "Predicted Range: 106.3 km (Optimal operating zone)."),
        ("Scenario 3: Hot Summer Mountain Climb", "Inputs: +34 deg C, 60 km/h, 50% SoC, +4% Grade, 2.5 kW A/C", "Predicted Range: 37.1 km.")
    ]

    for sc_title, sc_in, sc_out in scenarios:
        p_sc = doc.add_paragraph(style='List Bullet')
        p_sc.paragraph_format.line_spacing = 1.15
        p_sc.paragraph_format.space_after = Pt(4)
        r_sct = p_sc.add_run(sc_title + "\n")
        r_sct.font.name = "Arial"
        r_sct.font.size = Pt(10)
        r_sct.font.bold = True
        r_sct.font.color.rgb = COLOR_PRIMARY

        r_sci = p_sc.add_run("  - " + sc_in + "\n")
        r_sci.font.name = "Arial"
        r_sci.font.size = Pt(9.5)
        r_sci.font.color.rgb = COLOR_DARK

        r_sco = p_sc.add_run("  - " + sc_out)
        r_sco.font.name = "Arial"
        r_sco.font.size = Pt(9.5)
        r_sco.font.bold = True
        r_sco.font.color.rgb = COLOR_ACCENT

    # Section 7: License
    h7 = doc.add_heading(level=1)
    r_h7 = h7.add_run("7. License")
    r_h7.font.name = "Arial"
    r_h7.font.size = Pt(16)
    r_h7.font.bold = True
    r_h7.font.color.rgb = COLOR_PRIMARY
    h7.space_before = Pt(14)
    h7.space_after = Pt(6)

    p_lic = doc.add_paragraph()
    r_lic = p_lic.add_run("This project is licensed under the Apache License 2.0.")
    r_lic.font.name = "Arial"
    r_lic.font.size = Pt(10.5)
    r_lic.font.color.rgb = COLOR_DARK

    doc.save(output_path)
    print(f"Document successfully created at: {output_path}")

if __name__ == "__main__":
    out_docx = "/Users/airlord/Desktop/COA/Project_Documentation.docx"
    assets = "/Users/airlord/Desktop/COA/assets"
    create_document(out_docx, assets)
