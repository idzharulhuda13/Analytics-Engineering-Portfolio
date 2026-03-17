import streamlit as st
import duckdb
import pandas as pd
import json

# ──────────────────────────────────────────────
# Page Configuration
# ──────────────────────────────────────────────
st.set_page_config(
    page_title="Idzharul Huda | Portfolio",
    page_icon="🤖",
    layout="wide",
)

# ──────────────────────────────────────────────
# DuckDB In-Memory Database for Portfolio Data
# ──────────────────────────────────────────────
@st.cache_resource
def init_database():
    con = duckdb.connect(":memory:")
    
    # Profile
    con.execute("CREATE TABLE profile (key VARCHAR, value VARCHAR)")
    con.executemany("INSERT INTO profile VALUES (?, ?)", [
        ("name", "Idzharul Huda"),
        ("tagline", "Analytics Engineer | Data Scientist | AI Engineer"),
        ("email", st.secrets["personal"]["email"]),
        ("linkedin", st.secrets["personal"]["linkedin"]),
        ("github", st.secrets["personal"]["github"]),
        ("phone", st.secrets["personal"]["phone"]),
        ("location", st.secrets["personal"]["location"]),
        ("bio", "I'm an Analytics Engineer specializing in DBT, SQL, and BigQuery, focused on building a reliable single source of truth for data-driven decisions. At Rey.id, I delivered a 30% increase in pipeline efficiency, built automated data quality checks that cut manual review effort by 50%, and pioneered a dbt + Metabase framework that enabled 40+ stakeholders to self-serve analytics. My goal is to create scalable, trustworthy data systems that empower teams to move faster with confidence.")
    ])

    # Skills - No levels/scoring
    con.execute("CREATE TABLE skills (category VARCHAR, skills_list VARCHAR)")
    con.executemany("INSERT INTO skills VALUES (?, ?)", [
        ("Data Analytics & Engineering", "SQL, Python, Google Apps Script, BigQuery, DBT (Data Build Tool), Airflow"),
        ("Visualization & BI Tools", "Looker Studio (Google Data Studio), Metabase, Tableau"),
        ("Machine Learning & AI", "Statistical Analysis, LLMs (Gemini, OpenAI), YOLO, OCR, TensorFlow, WinSteps Rasch Analysis"),
        ("Collaboration & Dev Tools", "Git, Streamlit, Google Workspace, Google Sheet, Excel"),
    ])

    # Experience
    con.execute("CREATE TABLE experience (company VARCHAR, role VARCHAR, location VARCHAR, period VARCHAR, bullets JSON, skills VARCHAR, sort_id INTEGER)")
    con.execute("""
        INSERT INTO experience VALUES 
        ('Rey.id', 'Analytics Engineer', 'Jakarta, Indonesia', '08/2022 - Current', 
        '["Boosted report accuracy by 13% (82% to 95%) by automating Care Health Insurance System Solution (CHISS) workflows with dynamic master mapping.", "Optimized a key datamart model''s data processing, making it 9 times faster and decreasing BigQuery slot time consumption by over 96% and data shuffled by 58%. These optimizations contributed to a 30% increase in overall data pipeline efficiency.", "Developed and enforced ISO 27001:2022 aligned data handling standards across analytics workflows, strengthening security and trust with partners.", "Built end-to-end data quality checks and automated discrepancy detection tools, cutting manual error resolution time by 50%.", "Migrated data infrastructure from Google Sheets to BigQuery, creating a single source of truth and reducing report generation time from daily to hourly.", "Pioneered a DBT + Metabase pilot project enabling 40+ stakeholders to self-serve analytics without analyst intervention.", "Developed automated persistency analysis model to track member retention trends, influencing product improvement decisions.", "Built 10+ automated dashboards (Metabase, Looker Studio) used by marketing, operations, and finance teams to make faster, data-driven decisions."]', 'SQL, BigQuery, DBT, Looker Studio, Metabase, Airflow', 1),
        
        ('Olvo.ai', 'AI Engineer', 'Hong Kong, China', '04/2024 - 01/2025', 
        '["Digitized thousands of hardcopy documents into structured datasets using OCR, YOLO, and GPT-4, improving document handling efficiency by 70%.", "Designed an LLM-based embedding system to standardize hospital formularies, enabling seamless medication data sharing across institutions.", "Built a real-time client demo app with Streamlit, directly contributing to the company’s first $1M+ sale.", "Automated claims verification & pricing audits with ML models, reducing manual review workload by 60%."]', 'Python, Streamlit, OCR, YOLO, GPT-4', 2),
        
        ('Ministry of Education and Culture Republic of Indonesia', 'Data Analyst', 'Jakarta, Indonesia', '11/2023 - 11/2024', 
        '["Led statistical analysis using WinSteps Rasch Analysis to enhance accuracy in student talent & interest categorization.", "Created a multi-level difficulty assessment categorization pipeline in Python, streamlining nationwide student fitness assessments.", "Developed standardized norms for student fitness evaluation, adopted as part of the national feasibility study.", "Authored clear, replicable project documentation to ensure transparency for future implementations."]', 'Python, WinSteps Rasch Analysis, Statistical Analysis', 3)
    """)

    # Education
    con.execute("CREATE TABLE education (institution VARCHAR, degree VARCHAR, location VARCHAR, period VARCHAR, details VARCHAR)")
    con.execute("INSERT INTO education VALUES (?, ?, ?, ?, ?)", 
        ("Sebelas Maret University", "Bachelor of Computer Science", "Surakarta, Indonesia", "08/2018 - 03/2022", "Studied Computer Science at Sebelas Maret University, learning about programming, software development, and problem-solving.")
    )

    # Projects
    con.execute("CREATE TABLE projects (title VARCHAR, description VARCHAR, skills VARCHAR)")
    con.executemany("INSERT INTO projects VALUES (?, ?, ?)", [
        ("Automated Essay Scoring (Thesis)", "Built a deep learning model using Python, Word2Vec, and TensorFlow to score essays (±1,700 samples). Achieved 91.23% Kappa score on Kaggle Hewlett Foundation dataset.", "Python, Word2Vec, TensorFlow"),
        ("Telehealth Cost-effectiveness Study (Paper)", "Demonstrated that telehealth-powered managed care was 7× more cost-effective than conventional care for Acute Respiratory Infection (ARI).", "Data Analysis, Publication")
    ])

    # Certifications
    con.execute("CREATE TABLE certifications (title VARCHAR, description VARCHAR)")
    con.executemany("INSERT INTO certifications VALUES (?, ?)", [
        ("Google Data Analytics Professional Certificate", "Proficient in data-driven decision-making, including cleaning, analyzing, and visualizing data to solve business problems."),
        ("Microsoft Technology Associate: Database Fundamentals (MTA)", "Gained foundational knowledge in designing, querying, and managing databases with a focus on data integrity, security, and performance.")
    ])

    return con

con = init_database()

def get_profile() -> dict[str, str]:
    return {str(k): str(v) for k, v in con.execute("SELECT key, value FROM profile").fetchall()}

profile = get_profile()

# ──────────────────────────────────────────────
# Styles
# ──────────────────────────────────────────────
st.markdown("""
    <style>
    /* Force light background and typography */
    [data-testid="stAppViewContainer"], .main { background-color: #f8fafc; }
    [data-testid="stSidebar"] { background-color: #ffffff; }
    [data-testid="stHeader"] { background-color: transparent; }
    h1, h2, h3, h4, h5, h6 { color: #0f172a !important; font-weight: 800; }
    p, span, li, div { color: #334155; }
    .stTabs [data-baseweb="tab-list"] { padding-bottom: 1rem; }
    .stTabs [data-baseweb="tab"] { color: #475569; }
    .stTabs [aria-selected="true"] { color: #4f46e5 !important; }

    /* Floating card */
    .floating-card {
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 14px;
        padding: 1.5rem;
        margin-bottom: 1.2rem;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.12);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    .floating-card:hover {
        transform: translateY(-6px);
        box-shadow: 0 14px 28px rgba(0, 0, 0, 0.2);
    }

    .exp-title { color: #0f172a !important; font-weight: 700; font-size: 1.2rem; margin-bottom: 0.2rem; }
    .exp-company { color: #4f46e5 !important; font-weight: 600; font-size: 1.1rem; }
    .exp-meta { color: #64748b !important; font-size: 0.9rem; margin-bottom: 0.8rem; }
    .resume-bullet { margin-bottom: 0.5rem; line-height: 1.5; color: #334155; }
    .social-link { text-decoration: none; color: #4f46e5 !important; font-weight: 600; margin-right: 15px; }
    .skill-tag { background: #e0e7ff; color: #4f46e5 !important; padding: 2px 10px; border-radius: 12px; font-size: 0.8rem; font-weight: 600; display: inline-block; margin: 2px 4px 2px 0; border: 1px solid #c7d2fe; }
    </style>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────────
# Sidebar
# ──────────────────────────────────────────────
with st.sidebar:
    # st.image("https://api.dicebear.com/7.x/avataaars/svg?seed=Idzharul", width=150)
    st.title(profile["name"])
    st.write(profile["tagline"])
    st.markdown(f"📍 {profile['location']}")
    st.markdown(f"📧 {profile['email']}")
    st.markdown(f"📞 {profile['phone']}")
    st.divider()
    st.markdown(f"[LinkedIn]({profile['linkedin']}) | [GitHub]({profile['github']})")

# ──────────────────────────────────────────────
# Header / Hero
# ──────────────────────────────────────────────
st.title(f"Hi, I'm {profile['name'].split()[0]} 👋")
st.markdown(f"<div class='floating-card'>{profile['bio']}</div>", unsafe_allow_html=True)

st.divider()

# ──────────────────────────────────────────────
# Main Content Tabs
# ──────────────────────────────────────────────
tab_exp, tab_skills, tab_edu, tab_proj, tab_cert = st.tabs([
    "💼 Experience", 
    "🛠️ Skills", 
    "🎓 Education", 
    "📂 Projects", 
    "📜 Certifications"
])

with tab_exp:
    st.subheader("Professional Experience")
    exp_data = con.execute("SELECT * FROM experience ORDER BY sort_id").df()
    for _, row in exp_data.iterrows():
        bullets = json.loads(row['bullets'])
        bullets_html = "".join([f"<li class='resume-bullet'>{b}</li>" for b in bullets])
        skills_html = "".join([f"<span class='skill-tag'>{s.strip()}</span>" for s in row['skills'].split(',')])
        card_html = f"""
        <div class='floating-card'>
            <div class='exp-title'>{row['role']}</div>
            <div class='exp-company'>{row['company']}</div>
            <div class='exp-meta'>{row['location']} | {row['period']}</div>
            <ul>{bullets_html}</ul>
            <div style='margin-top: 10px;'>{skills_html}</div>
        </div>
        """
        st.markdown(card_html, unsafe_allow_html=True)

with tab_skills:
    st.subheader("Skills")
    skills_data = con.execute("SELECT category, skills_list FROM skills").df()
    for _, row in skills_data.iterrows():
        st.markdown(f"<div class='floating-card'><strong>{row['category']}:</strong> {row['skills_list']}</div>", unsafe_allow_html=True)

with tab_edu:
    st.subheader("Education")
    edu = con.execute("SELECT * FROM education").fetchone()
    if edu:
        edu_html = f"""
        <div class='floating-card'>
            <strong>{edu[1]}</strong><br>
            <em>{edu[0]}</em> | {edu[2]} | {edu[3]}<br><br>
            {edu[4]}
        </div>
        """
        st.markdown(edu_html, unsafe_allow_html=True)

with tab_proj:
    st.subheader("Projects")
    projects = con.execute("SELECT title, description, skills FROM projects").fetchall()
    for title, desc, skills in projects:
        skills_html = "".join([f"<span class='skill-tag'>{s.strip()}</span>" for s in skills.split(',')])
        proj_html = f"""
        <div class='floating-card'>
            <strong>{title}</strong><br>
            {desc}
            <div style='margin-top: 10px;'>{skills_html}</div>
        </div>
        """
        st.markdown(proj_html, unsafe_allow_html=True)

with tab_cert:
    st.subheader("Certifications")
    certs = con.execute("SELECT title, description FROM certifications").fetchall()
    for title, desc in certs:
        cert_html = f"""
        <div class='floating-card'>
            <strong>{title}</strong><br>
            {desc}
        </div>
        """
        st.markdown(cert_html, unsafe_allow_html=True)

# Footer
st.divider()
st.caption(f"© 2026 {profile['name']} | Built with Streamlit and DuckDB")
