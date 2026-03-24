import streamlit as st
import duckdb
import pandas as pd
import altair as alt

from components.cards import inject_floating_card_css, metric_card, chart_container

st.set_page_config(page_title="Student Performance Dashboard", page_icon="📈", layout="wide")

# Inject shared floating-card CSS (includes metric-card + container hover)
inject_floating_card_css()

# Page-specific styles
st.markdown("""
<style>
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
    metric_card("Total Students", f"{total_students:,}")
with col2:
    metric_card("Avg Math Score", f"{avg_math:.1f}")
with col3:
    metric_card("Avg Reading Score", f"{avg_reading:.1f}")
with col4:
    metric_card("Avg Overall Score", f"{avg_overall:.1f}")

st.markdown("<br>", unsafe_allow_html=True)

# Layout for Row 1
col_l, col_r = st.columns((1, 1), gap="large")

with col_l:
    with chart_container():
        st.subheader("📊 Score Distribution")
        dist_subject = st.selectbox("Select Subject", ["math_score", "reading_score", "writing_score", "avg_score"], format_func=lambda x: x.replace('_', ' ').title())
        
        # Altair Histogram
        hist = alt.Chart(df).mark_bar(color='#4f46e5').encode(
            x=alt.X(f"{dist_subject}:Q", bin=alt.Bin(maxbins=30), title="Score"),
            y=alt.Y('count()', title="Count")
        ).properties(height=300)
        
        st.altair_chart(hist, use_container_width=True)

with col_r:
    with chart_container():
        st.subheader("📚 Test Preparation Impact")
        prep_df = df.groupby('test_prep')[['math_score', 'reading_score', 'writing_score']].mean().reset_index()
        prep_melted = prep_df.melt(id_vars='test_prep', var_name='Subject', value_name='Average Score')
        prep_melted['Subject'] = prep_melted['Subject'].str.replace('_score', '').str.title()
        
        # Altair Grouped Bar Chart
        bar_prep = alt.Chart(prep_melted).mark_bar().encode(
            x=alt.X('Subject:N', title="Subject"),
            y=alt.Y('Average Score:Q', title="Average Score"),
            color=alt.Color('test_prep:N', scale=alt.Scale(domain=['none', 'completed'], range=['#94a3b8', '#10b981']), title="Test Preparation"),
            xOffset='test_prep:N'
        ).properties(height=300)
        
        st.altair_chart(bar_prep, use_container_width=True)

st.markdown("<br>", unsafe_allow_html=True)

# Layout for Row 2
col_bl, col_br = st.columns((1, 1), gap="large")

with col_bl:
    with chart_container():
        st.subheader("🍎 Impact of Lunch Type")
        # Altair Box Plot
        box_lunch = alt.Chart(df).mark_boxplot(extent='min-max').encode(
            x=alt.X('lunch:N', title="Lunch Type"),
            y=alt.Y('avg_score:Q', title="Average Score"),
            color=alt.Color('lunch:N', scale=alt.Scale(domain=['standard', 'free/reduced'], range=['#0ea5e9', '#f59e0b']), legend=None)
        ).properties(height=300)
        
        st.altair_chart(box_lunch, use_container_width=True)

with col_br:
    with chart_container():
        st.subheader("🎓 Parental Education Influence")
        edu_df = df.groupby('parental_education')['avg_score'].mean().reset_index()
        
        # Altair Horizontal Bar Chart
        bar_edu = alt.Chart(edu_df).mark_bar().encode(
            y=alt.Y('parental_education:N', sort='-x', title="Parental Education Level"),
            x=alt.X('avg_score:Q', title="Average Score"),
            color=alt.Color('avg_score:Q', scale=alt.Scale(scheme='oranges'), legend=None)
        ).properties(height=300)
        
        st.altair_chart(bar_edu, use_container_width=True)

st.markdown("<br>", unsafe_allow_html=True)

with chart_container():
    st.subheader("👥 Performance by Gender & Race/Ethnicity")

    # Altair Heatmap
    heat_chart = alt.Chart(df).mark_rect().encode(
        x=alt.X('race_ethnicity:N', title="Race / Ethnicity"),
        y=alt.Y('gender:N', title="Gender"),
        color=alt.Color('mean(avg_score):Q', scale=alt.Scale(scheme='viridis'), title="Avg Score"),
        tooltip=['race_ethnicity:N', 'gender:N', 'mean(avg_score):Q']
    ).properties(height=300)

    # Add text labels to heatmap
    text = alt.Chart(df).transform_aggregate(
        mean_avg_score='mean(avg_score)',
        groupby=['race_ethnicity', 'gender']
    ).mark_text().encode(
        x=alt.X('race_ethnicity:N'),
        y=alt.Y('gender:N'),
        text=alt.Text('mean_avg_score:Q', format='.1f'),
        color=alt.condition(
            alt.datum['mean_avg_score'] > 70,
            alt.value('black'),
            alt.value('white')
        )
    )

    st.altair_chart(heat_chart + text, use_container_width=True)

st.divider()
st.caption("Insights generated automatically using Streamlit, DuckDB, and Altair.")