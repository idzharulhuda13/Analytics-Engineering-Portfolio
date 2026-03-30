import streamlit as st
import duckdb
import pandas as pd
import json

from components.cards import inject_floating_card_css, floating_card

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
    con.execute("CREATE TABLE projects (title VARCHAR, description VARCHAR, skills VARCHAR, url VARCHAR)")
    con.executemany("INSERT INTO projects VALUES (?, ?, ?, ?)", [
        ("DataVerse AI Analyst Dashboard", "An intelligent analytics platform that leverages LLMs to provide automated insights, storytelling, and strategic recommendations from complex datasets. Features a proactive agentic framework for data exploration.", "Python, Streamlit, LLMs, Agent Development Kit (ADK), AI Engineering", "https://dataverse-appv2.streamlit.app/"),
        ("Automated Essay Scoring (Thesis)", "Built a deep learning model using Python, Word2Vec, and TensorFlow to score essays (±1,700 samples). Achieved 91.23% Kappa score on Kaggle Hewlett Foundation dataset.", "Python, Word2Vec, TensorFlow", "https://drive.google.com/file/d/1gJnExAv1NCzscZ9PJ9VDgSPgkb8s6-7H/view?usp=sharing"),
        ("Telehealth Cost-effectiveness Study (Paper)", "Demonstrated that telehealth-powered managed care was 7× more cost-effective than conventional care for Acute Respiratory Infection (ARI).", "Data Analysis, Publication", "https://drive.google.com/file/d/1PecpBASX9lJHY5WK_SQKr1oxhzeNxaLc/view?usp=drive_link")
    ])

    # Certifications
    con.execute("CREATE TABLE certifications (title VARCHAR, description VARCHAR, url VARCHAR)")
    con.executemany("INSERT INTO certifications VALUES (?, ?, ?)", [
        ("Google Data Analytics Professional Certificate", "Proficient in data-driven decision-making, including cleaning, analyzing, and visualizing data to solve business problems.", "https://www.coursera.org/account/accomplishments/specialization/certificate/ZR3UPFBES77R"),
        ("Microsoft Technology Associate: Database Fundamentals (MTA)", "Gained foundational knowledge in designing, querying, and managing databases with a focus on data integrity, security, and performance.", "https://www.certiport.com/portal/Pages/PrintTranscriptInfo.aspx?action=Cert&id=132&cvid=nq44slXIg2zg3ddmnLS/EQ==")
    ])

    return con

con = init_database()

def get_profile() -> dict[str, str]:
    return {str(k): str(v) for k, v in con.execute("SELECT key, value FROM profile").fetchall()}

profile = get_profile()

# ──────────────────────────────────────────────
# Styles
# ──────────────────────────────────────────────
# Inject shared floating-card CSS
inject_floating_card_css()

# Page-specific styles
st.markdown("""
    <style>
    [data-testid="stAppViewContainer"], .main { background-color: #f8fafc; }
    [data-testid="stSidebar"] { background-color: #ffffff; }
    [data-testid="stHeader"] { background-color: transparent; }
    h1, h2, h3, h4, h5, h6 { color: #0f172a !important; font-weight: 800; }
    p, span, li, div { color: #334155; }
    .stTabs [data-baseweb="tab-list"] { padding-bottom: 1rem; }
    .stTabs [data-baseweb="tab"] { color: #475569; }
    .stTabs [aria-selected="true"] { color: #4f46e5 !important; }
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
floating_card(profile['bio'])

st.divider()

# ──────────────────────────────────────────────
# Main Content Tabs
# ──────────────────────────────────────────────
tab_exp, tab_proj, tab_cert, tab_skills, tab_edu = st.tabs([
    "💼 Experience", 
    "📂 Projects", 
    "📜 Certifications",
    "🛠️ Skills", 
    "🎓 Education", 
])

with tab_exp:
    st.subheader("Professional Experience")
    exp_data = con.execute("SELECT * FROM experience ORDER BY sort_id").df()
    for _, row in exp_data.iterrows():
        bullets = json.loads(row['bullets'])
        bullets_html = "".join([f"<li class='resume-bullet'>{b}</li>" for b in bullets])
        skills_html = "".join([f"<span class='skill-tag'>{s.strip()}</span>" for s in row['skills'].split(',')])
        floating_card(f"""
            <div class='exp-title'>{row['role']}</div>
            <div class='exp-company'>{row['company']}</div>
            <div class='exp-meta'>{row['location']} | {row['period']}</div>
            <ul>{bullets_html}</ul>
            <div style='margin-top: 10px;'>{skills_html}</div>
        """)

with tab_skills:
    st.subheader("Skills")
    skills_data = con.execute("SELECT category, skills_list FROM skills").df()
    for _, row in skills_data.iterrows():
        floating_card(f"<strong>{row['category']}:</strong> {row['skills_list']}")

with tab_edu:
    st.subheader("Education")
    edu = con.execute("SELECT * FROM education").fetchone()
    if edu:
        floating_card(f"""
            <strong>{edu[1]}</strong><br>
            <em>{edu[0]}</em> | {edu[2]} | {edu[3]}<br><br>
            {edu[4]}
        """)

with tab_proj:
    st.subheader("Projects")
    projects = con.execute("SELECT title, description, skills, url FROM projects").fetchall()
    for title, desc, skills, url in projects:
        skills_html = "".join([f"<span class='skill-tag'>{s.strip()}</span>" for s in skills.split(',')])
        # Link in the title
        clickable_title = f"<a href='{url}' target='_blank' style='text-decoration: none; color: #1e293b; border-bottom: 2px solid transparent; transition: border-bottom 0.3s ease;'>{title} 🔗</a>" if url else title
        floating_card(f"""
            <div style='margin-bottom: 8px;'>
                <strong style='font-size: 1.15rem;'>{clickable_title}</strong>
            </div>
            {desc}
            <div style='margin-top: 12px;'>{skills_html}</div>
        """)

with tab_cert:
    st.subheader("Certifications")
    certs = con.execute("SELECT title, description, url FROM certifications").fetchall()
    for title, desc, url in certs:
        clickable_title = f"<a href='{url}' target='_blank' style='text-decoration: none; color: #1e293b;'>{title} 🔗</a>" if url else title
        floating_card(f"""
            <strong style='font-size: 1.1rem;'>{clickable_title}</strong><br>
            <div style='margin-top: 5px;'>{desc}</div>
        """)

# Footer
st.divider()
st.caption(f"© 2026 {profile['name']} | Built with Streamlit and DuckDB")
