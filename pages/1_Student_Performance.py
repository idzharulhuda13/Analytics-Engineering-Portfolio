import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import duckdb
from pathlib import Path

ROOT = Path(__file__).parent.parent

# ──────────────────────────────────────────────
# Page Configuration
# ──────────────────────────────────────────────
st.set_page_config(page_title="Student Performance Analysis", page_icon="📊", layout="wide")

# ──────────────────────────────────────────────
# Styles
# ──────────────────────────────────────────────
st.markdown("""
    <style>
    /* Global Styles */
    [data-testid="stAppViewContainer"], .main { background-color: #f8fafc; }
    [data-testid="stSidebar"] { background-color: #ffffff; }
    [data-testid="stHeader"] { background-color: transparent; }
    
    h1, h2, h3, h4, h5, h6 { color: #0f172a !important; font-weight: 800; }
    p, span, li, div { color: #334155; }
    /* Floating card base styling for specific elements */
    .element-container:has(.stMetric),
    .element-container:has(.stPlotlyChart),
    .element-container:has(.stDataFrame),
    .floating-card {
        background-color: #ffffff !important;
        border: 1px solid #e2e8f0 !important;
        border-radius: 16px !important;
        padding: 20px !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08) !important;
        transition: transform 0.3s ease, box-shadow 0.3s ease !important;
        margin-bottom: 20px !important;
    }
    
    .element-container:has(.stMetric):hover,
    .element-container:has(.stPlotlyChart):hover,
    .element-container:has(.stDataFrame):hover,
    .floating-card:hover {
        transform: translateY(-5px) !important;
        box-shadow: 0 12px 24px rgba(0, 0, 0, 0.15) !important;
    }

    /* Override dark theme Selectboxes inside dark mode logic */
    div[data-baseweb="select"] > div {
        background-color: #ffffff !important;
        color: #000000 !important;
        border: 1px solid #e2e8f0 !important;
        border-radius: 8px !important;
    }
    div[data-baseweb="select"] span {
        color: #000000 !important;
    }

    /* Fix Plotly wrapper styling to ensure it stretches well */
    .stPlotlyChart {
        padding: 10px !important;
    }

    /* Metric styling */
    [data-testid="stMetricValue"] { color: #4f46e5 !important; font-weight: 700; }
    [data-testid="stMetricLabel"] { color: #64748b !important; }
    
    /* Tabs styling */
    .stTabs [data-baseweb="tab-list"] { background-color: transparent; }
    .stTabs [data-baseweb="tab"] { color: #64748b; font-weight: 600; }
    .stTabs [aria-selected="true"] { color: #4f46e5 !important; border-bottom-color: #4f46e5 !important; }
    
    /* Sidebar header */
    .sidebar .sidebar-content { background-image: none; }
    </style>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────────
# Data Loading
# ──────────────────────────────────────────────
@st.cache_data
def load_data():
    con = duckdb.connect(str(ROOT / "data" / "portfolio.duckdb"), read_only=True)
    df = con.execute("SELECT * FROM src_student_performance").df()
    con.close()
    # Add total and average scores
    df['total score'] = df['math score'] + df['reading score'] + df['writing score']
    df['average score'] = df['total score'] / 3
    # Determine pass status: standard passing grade is usually 60%
    df['pass status'] = ((df['math score'] >= 60) & (df['reading score'] >= 60) & (df['writing score'] >= 60)).map({True: 'Passed', False: 'Failed'})
    return df

df = load_data()

# ──────────────────────────────────────────────
# Sidebar Filters
# ──────────────────────────────────────────────
with st.sidebar:
    st.title("📊 Filter Data")
    gender = st.multiselect("Gender", options=df["gender"].unique(), default=df["gender"].unique())
    race = st.multiselect("Race/Ethnicity", options=df["race/ethnicity"].unique(), default=df["race/ethnicity"].unique())
    education = st.multiselect("Parental Education", options=df["parental level of education"].unique(), default=df["parental level of education"].unique())
    lunch = st.multiselect("Lunch Program", options=df["lunch"].unique(), default=df["lunch"].unique())

filtered_df = df[
    (df["gender"].isin(gender)) & 
    (df["race/ethnicity"].isin(race)) & 
    (df["parental level of education"].isin(education)) &
    (df["lunch"].isin(lunch))
]

# ──────────────────────────────────────────────
# Sidebar Metrics (Optional)
# ──────────────────────────────────────────────
# st.sidebar.divider()
# st.sidebar.metric("Sample Size", len(filtered_df))

# ──────────────────────────────────────────────
# Main Dashboard
# ──────────────────────────────────────────────
st.title("📊 Student Performance Analysis")

# Header Overview Card
st.markdown("<div class='floating-card'>Exploratory Data Analysis of student exam scores based on various demographic factors. Use the sidebar on the left to filter the dataset and explore correlations.</div>", unsafe_allow_html=True)

# KPI Row
st.subheader("Key Performance Indicators")

if not filtered_df.empty:
    kpi_cols = st.columns(5)
    with kpi_cols[0]:
        st.metric("Total Students", len(filtered_df))
    with kpi_cols[1]:
        st.metric("Math Avg", f"{filtered_df['math score'].mean():.1f}")
    with kpi_cols[2]:
        st.metric("Reading Avg", f"{filtered_df['reading score'].mean():.1f}")
    with kpi_cols[3]:
        st.metric("Writing Avg", f"{filtered_df['writing score'].mean():.1f}")
    with kpi_cols[4]:
        pass_rate = list(filtered_df['pass status']).count('Passed') / len(filtered_df) * 100
        st.metric("Pass Rate", f"{pass_rate:.1f}%")
else:
    st.warning("No data available for the selected filters.")

st.divider()

# Charts Section
col1, col2 = st.columns(2)

def update_plot_theme(fig):
    fig.update_layout(
        template="plotly_white",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=20, r=20, t=50, b=20)
    )
    return fig

with col1:
    st.subheader("Score Distributions")
    score_type = st.selectbox("Select Score Type", ["math score", "reading score", "writing score", "average score"])
    fig_dist = px.histogram(filtered_df, x=score_type, color="gender", marginal="box", 
                             title=f"Distribution of {score_type.title()}",
                             color_discrete_sequence=["#4f46e5", "#ec4899"])
    update_plot_theme(fig_dist)
    st.plotly_chart(fig_dist, use_container_width=True)

with col2:
    st.subheader("Correlation Analysis")
    
    # Allow user to choose axes for deeper exploration
    scatter_cols = st.columns(2)
    with scatter_cols[0]:
        x_axis = st.selectbox("X-Axis Score", ["math score", "reading score", "writing score"], index=1)
    with scatter_cols[1]:
        y_axis = st.selectbox("Y-Axis Score", ["math score", "reading score", "writing score"], index=2)
        
    fig_scatter = px.scatter(filtered_df, x=x_axis, y=y_axis, color="test preparation course",
                             hover_data=["math score", "reading score", "writing score"],
                             title=f"{x_axis.replace(' score', '').title()} vs {y_axis.replace(' score', '').title()} Scores",
                             color_discrete_sequence=["#4f46e5", "#10b981"])
    update_plot_theme(fig_scatter)
    st.plotly_chart(fig_scatter, use_container_width=True)

st.divider()

st.subheader("Impact of Parental Education & Test Prep")
col3, col4 = st.columns(2)

with col3:
    fig_box = px.box(filtered_df, x="parental level of education", y="average score", color="gender",
                     title="Avg Score by Parental Education",
                     color_discrete_sequence=["#4f46e5", "#ec4899"])
    update_plot_theme(fig_box)
    fig_box.update_layout(xaxis={'categoryorder':'total descending'})
    st.plotly_chart(fig_box, use_container_width=True)

with col4:
    test_prep_avg = filtered_df.groupby("test preparation course")["average score"].mean().reset_index()
    fig_bar = px.bar(test_prep_avg, x="test preparation course", y="average score", 
                     title="Impact of Test Prep Course",
                     color="test preparation course",
                     color_discrete_sequence=["#4f46e5", "#10b981"])
    update_plot_theme(fig_bar)
    st.plotly_chart(fig_bar, use_container_width=True)

st.divider()

# Raw Data Card
st.subheader("Top Performers Preview")
st.markdown("<p style='color: #64748b; margin-bottom: 1rem;'>Top 50 students based on their overall average score across all subjects.</p>", unsafe_allow_html=True)

# Sort by average score to make the view more insightful
top_performers = filtered_df.sort_values(by="average score", ascending=False).head(50)
top_performers = top_performers.reset_index(drop=True)
top_performers.index += 1 # 1-based ranking index

st.dataframe(top_performers, use_container_width=True)
st.divider()

st.subheader("💡 Key Insights")
if not filtered_df.empty:
    insights = []
    
    # Test Prep Insight
    prep_groups = filtered_df.groupby("test preparation course")["average score"].mean()
    if "none" in prep_groups and "completed" in prep_groups:
        diff = prep_groups["completed"] - prep_groups["none"]
        insights.append(f"🎓 <b>Test Preparation:</b> Students who completed the course scored <b>{diff:.1f}</b> points higher on average.")
        
    # Lunch Insight
    lunch_groups = filtered_df.groupby("lunch")["average score"].mean()
    if "standard" in lunch_groups and "free/reduced" in lunch_groups:
        diff = lunch_groups["standard"] - lunch_groups["free/reduced"]
        insights.append(f"🥪 <b>Socioeconomic Impact:</b> Students with standard lunch scored <b>{diff:.1f}</b> points higher on average than those with free/reduced lunch.")
        
    # Top Demographic
    if len(filtered_df["race/ethnicity"].unique()) > 1:
        top_group = filtered_df.groupby("race/ethnicity")["average score"].mean().idxmax()
        top_score = filtered_df.groupby("race/ethnicity")["average score"].mean().max()
        insights.append(f"🏆 <b>Top Demographic:</b> <b>{top_group.title()}</b> is the highest performing highlighted group with an average score of <b>{top_score:.1f}</b>.")
    
    # Max Score Category
    scores_mean = {
        "Math": filtered_df["math score"].mean(),
        "Reading": filtered_df["reading score"].mean(),
        "Writing": filtered_df["writing score"].mean()
    }
    best_subject = ""
    best_score = -1
    for k, v in scores_mean.items():
        if v > best_score:
            best_score = v
            best_subject = k
            
    insights.append(f"📚 <b>Strongest Subject:</b> The current group performs best in <b>{best_subject}</b> (avg: <b>{best_score:.1f}</b>).")

    insights_html = "<div class='floating-card'><ul style='color: #334155; line-height: 1.8; margin-bottom: 0; font-size: 1.05rem;'>"
    for insight in insights:
        insights_html += f"<li style='margin-bottom: 8px;'>{insight}</li>"
    insights_html += "</ul></div>"
    st.markdown(insights_html, unsafe_allow_html=True)
else:
    st.info("No data available to generate insights.")

# Footer
st.divider()
st.caption("© 2026 Idzharul Huda | Built with Streamlit, Plotly and DuckDB")
