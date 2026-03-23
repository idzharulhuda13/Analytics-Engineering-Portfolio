import streamlit as st
import duckdb
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="Student Performance Dashboard", page_icon="📈", layout="wide")

# Custom CSS for cards
st.markdown("""
<style>
    .metric-card {
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 20px;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .metric-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 10px 15px rgba(0, 0, 0, 0.1);
    }
    .metric-title {
        color: #64748b;
        font-size: 1rem;
        font-weight: 600;
        margin-bottom: 8px;
    }
    .metric-value {
        color: #0f172a;
        font-size: 2.2rem;
        font-weight: 800;
    }
    [data-testid="stAppViewContainer"], .main {
        background-color: #f8fafc;
    }
    h1, h2, h3, h4, h5, h6 { 
        color: #0f172a !important; 
        font-weight: 800; 
    }
</style>
""", unsafe_allow_html=True)

st.title("🎓 Student Performance Analytics")
st.markdown("A comprehensive analysis of student scores based on demographics, test preparation, and background. Explore the insights below to understand what drives academic success.")

@st.cache_resource
def load_data():
    # Connect to the local DuckDB database where dbt models are materialized
    con = duckdb.connect('data/portfolio.duckdb', read_only=True)
    return con

con = load_data()
# Use the pre-computed mrt_student_performance table from dbt
df = con.execute("SELECT *, average_score AS avg_score FROM mrt_student_performance").df()

# Top KPIs
col1, col2, col3, col4 = st.columns(4)

total_students = len(df)
avg_math = df['math_score'].mean()
avg_reading = df['reading_score'].mean()
avg_writing = df['writing_score'].mean()
avg_overall = df['avg_score'].mean()

with col1:
    st.markdown(f'<div class="metric-card"><div class="metric-title">Total Students</div><div class="metric-value">{total_students:,}</div></div>', unsafe_allow_html=True)
with col2:
    st.markdown(f'<div class="metric-card"><div class="metric-title">Avg Math Score</div><div class="metric-value">{avg_math:.1f}</div></div>', unsafe_allow_html=True)
with col3:
    st.markdown(f'<div class="metric-card"><div class="metric-title">Avg Reading Score</div><div class="metric-value">{avg_reading:.1f}</div></div>', unsafe_allow_html=True)
with col4:
    st.markdown(f'<div class="metric-card"><div class="metric-title">Avg Overall Score</div><div class="metric-value">{avg_overall:.1f}</div></div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Layout for Row 1
col_l, col_r = st.columns((1, 1), gap="large")

with col_l:
    st.subheader("📊 Score Distribution")
    dist_subject = st.selectbox("Select Subject", ["math_score", "reading_score", "writing_score", "avg_score"], format_func=lambda x: x.replace('_', ' ').title())
    
    fig_hist = px.histogram(
        df, x=dist_subject, nbins=30, 
        marginal="box",
        color_discrete_sequence=['#4f46e5'],
    )
    fig_hist.update_layout(
        plot_bgcolor='rgba(0,0,0,0)', 
        paper_bgcolor='rgba(0,0,0,0)', 
        margin=dict(t=20, b=10, l=10, r=10),
        xaxis_title="Score",
        yaxis_title="Count"
    )
    st.plotly_chart(fig_hist, use_container_width=True)

with col_r:
    st.subheader("📚 Test Preparation Impact")
    prep_df = df.groupby('test_prep')[['math_score', 'reading_score', 'writing_score']].mean().reset_index()
    prep_melted = prep_df.melt(id_vars='test_prep', var_name='Subject', value_name='Average Score')
    prep_melted['Subject'] = prep_melted['Subject'].str.replace('_score', '').str.title()
    
    fig_prep = px.bar(
        prep_melted, x='Subject', y='Average Score', color='test_prep', barmode='group',
        color_discrete_map={"none": "#94a3b8", "completed": "#10b981"},
        text_auto=".1f"
    )
    fig_prep.update_layout(
        plot_bgcolor='rgba(0,0,0,0)', 
        paper_bgcolor='rgba(0,0,0,0)', 
        margin=dict(t=20, b=10, l=10, r=10),
        xaxis_title="Subject",
        yaxis_title="Average Score",
        legend_title="Test Prep"
    )
    st.plotly_chart(fig_prep, use_container_width=True)

st.markdown("<br>", unsafe_allow_html=True)

# Layout for Row 2
col_bl, col_br = st.columns((1, 1), gap="large")

with col_bl:
    st.subheader("🍎 Impact of Lunch Type")
    fig_lunch = px.box(
        df, x='lunch', y='avg_score', color='lunch', 
        color_discrete_map={"standard": "#0ea5e9", "free/reduced": "#f59e0b"},
        points="all"
    )
    fig_lunch.update_layout(
        plot_bgcolor='rgba(0,0,0,0)', 
        paper_bgcolor='rgba(0,0,0,0)', 
        margin=dict(t=20, b=10, l=10, r=10),
        xaxis_title="Lunch Type",
        yaxis_title="Average Score",
        showlegend=False
    )
    st.plotly_chart(fig_lunch, use_container_width=True)

with col_br:
    st.subheader("🎓 Parental Education Influence")
    # Order by average score
    edu_df = df.groupby('parental_education')['avg_score'].mean().sort_values().reset_index()
    fig_edu = px.bar(
        edu_df, y='parental_education', x='avg_score', orientation='h',
        color='avg_score', color_continuous_scale="fall",
        text_auto=".1f"
    )
    fig_edu.update_layout(
        plot_bgcolor='rgba(0,0,0,0)', 
        paper_bgcolor='rgba(0,0,0,0)', 
        margin=dict(t=20, b=10, l=10, r=10),
        xaxis_title="Average Score",
        yaxis_title="Parental Education Level",
        coloraxis_showscale=False
    )
    st.plotly_chart(fig_edu, use_container_width=True)

st.markdown("<br>", unsafe_allow_html=True)
st.subheader("👥 Performance by Gender & Race/Ethnicity")

# Heatmap of Avg Score across Gender and Race/Ethnicity
heat_df = df.groupby(['gender', 'race_ethnicity'])['avg_score'].mean().unstack().round(1)
fig_heat = px.imshow(
    heat_df, text_auto=True, aspect="auto",
    color_continuous_scale="oxy"
)
fig_heat.update_layout(
    plot_bgcolor='rgba(0,0,0,0)', 
    paper_bgcolor='rgba(0,0,0,0)', 
    margin=dict(t=20, b=10, l=10, r=10),
    xaxis_title="Race / Ethnicity",
    yaxis_title="Gender"
)
st.plotly_chart(fig_heat, use_container_width=True)

st.divider()
st.caption("Insights generated automatically using Streamlit, DuckDB, and Plotly.")
