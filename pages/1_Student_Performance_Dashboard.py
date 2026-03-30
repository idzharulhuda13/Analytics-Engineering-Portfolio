import streamlit as st
import duckdb
import pandas as pd
import altair as alt

from components.cards import inject_floating_card_css, metric_card, chart_container

st.set_page_config(page_title="Student Performance Dashboard", page_icon="📈", layout="wide")

# Inject shared floating-card CSS
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
    /* Simple styling for tabs to look slightly better */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        padding-top: 10px;
        padding-bottom: 10px;
    }
</style>
""", unsafe_allow_html=True)

st.title("🎓 The Student Performance Story")
st.markdown("Welcome to the Student Performance analysis narrative. This dashboard is designed to lead you step-by-step through the data, uncovering the layers of insights that drive academic success.")

@st.cache_data
def load_data():
    with duckdb.connect('data/app.duckdb', read_only=True) as con:
        return con.execute("SELECT *, average_score AS avg_score FROM mrt_student_performance").df()

df = load_data()

# --- SIDEBAR FILTERS ---
st.sidebar.header("🔍 Filter Data")
st.sidebar.markdown("Use these filters to slice the dashboard data.")

def clear_filters():
    st.session_state['f_gender'] = df['gender'].unique().tolist()
    st.session_state['f_race'] = sorted(df['race_ethnicity'].unique().tolist())
    st.session_state['f_edu'] = df['parental_education'].unique().tolist()
    st.session_state['f_lunch'] = df['lunch'].unique().tolist()
    st.session_state['f_prep'] = df['test_prep'].unique().tolist()

st.sidebar.button("🔄 Reset Filters", on_click=clear_filters, use_container_width=True)

gender_filter = st.sidebar.multiselect("Gender", options=df['gender'].unique().tolist(), default=df['gender'].unique().tolist(), key='f_gender')
race_filter = st.sidebar.multiselect("Race / Ethnicity", options=sorted(df['race_ethnicity'].unique().tolist()), default=sorted(df['race_ethnicity'].unique().tolist()), key='f_race')
edu_filter = st.sidebar.multiselect("Parental Education", options=df['parental_education'].unique().tolist(), default=df['parental_education'].unique().tolist(), key='f_edu')
lunch_filter = st.sidebar.multiselect("Lunch Type", options=df['lunch'].unique().tolist(), default=df['lunch'].unique().tolist(), key='f_lunch')
prep_filter = st.sidebar.multiselect("Test Prep", options=df['test_prep'].unique().tolist(), default=df['test_prep'].unique().tolist(), key='f_prep')

filtered_df = df[
    df['gender'].isin(gender_filter) &
    df['race_ethnicity'].isin(race_filter) &
    df['parental_education'].isin(edu_filter) &
    df['lunch'].isin(lunch_filter) &
    df['test_prep'].isin(prep_filter)
]

st.sidebar.markdown('---')
st.sidebar.caption(f"**Showing {len(filtered_df):,} / {len(df):,} students** based on current filters.")

if filtered_df.empty:
    st.warning("⚠️ No data available for the selected filters.")
    st.stop()

# Top KPIs Calculation
global_avg_math = df['math_score'].mean()
global_avg_reading = df['reading_score'].mean()
global_avg_writing = df['writing_score'].mean()
global_pass_rate = (len(df[df['avg_score'] >= 60]) / len(df) * 100) if len(df) > 0 else 0

total_students = len(filtered_df)
avg_math = filtered_df['math_score'].mean()
avg_reading = filtered_df['reading_score'].mean()
avg_writing = filtered_df['writing_score'].mean()
avg_overall = filtered_df['avg_score'].mean()
pass_rate = (len(filtered_df[filtered_df['avg_score'] >= 60]) / total_students * 100) if total_students > 0 else 0

def get_delta_info(current, baseline, is_percentage=False):
    diff = current - baseline
    if abs(diff) < 0.05:
         return None, "normal"
    sign = "+" if diff > 0 else "-"
    color = "positive" if diff > 0 else "negative"
    formatted = f"{sign}{abs(diff):.1f}%" if is_percentage else f"{sign}{abs(diff):.1f} pts"
    return formatted, color

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    metric_card("Total Students", f"{total_students:,}")
with col2:
    d_str, d_col = get_delta_info(avg_math, global_avg_math)
    metric_card("Avg Math", f"{avg_math:.1f}", delta=d_str, delta_color=d_col)
with col3:
    d_str, d_col = get_delta_info(avg_reading, global_avg_reading)
    metric_card("Avg Reading", f"{avg_reading:.1f}", delta=d_str, delta_color=d_col)
with col4:
    d_str, d_col = get_delta_info(avg_writing, global_avg_writing)
    metric_card("Avg Writing", f"{avg_writing:.1f}", delta=d_str, delta_color=d_col)
with col5:
    d_str, d_col = get_delta_info(pass_rate, global_pass_rate, is_percentage=True)
    metric_card("Pass Rate (≥60)", f"{pass_rate:.1f}%", delta=d_str, delta_color=d_col)

st.markdown('---')

# TABS LAYOUT
tab_overview, tab_prep, tab_socio, tab_demo, tab_syn = st.tabs([
    "📍 Overview", 
    "📚 Test Preparation", 
    "🌍 Socioeconomics", 
    "👥 Demographics", 
    "🔗 Subject Synergies"
])

with tab_overview:
    st.header("Chapter 1: The Baseline (Performance & Outcomes)")
    
    col_hist, col_pass = st.columns([1, 1], gap="large")
    
    with col_hist:
        dist_subject = st.selectbox("Select Subject for Distribution", ["math_score", "reading_score", "writing_score", "avg_score"], format_func=lambda x: x.replace('_', ' ').title(), key='dist_sub')
        mean_val = filtered_df[dist_subject].mean()
        std_val = filtered_df[dist_subject].std()
        
        st.markdown(f"**Insight:** Average {dist_subject.replace('_', ' ')} is **{mean_val:.1f}** (SD: **{std_val:.1f}**).")
        
        with chart_container():
            st.subheader("📊 Score Distribution")
            hist = alt.Chart(filtered_df).mark_area(
                opacity=0.6, interpolate='step'
            ).encode(
                x=alt.X(f"{dist_subject}:Q", bin=alt.Bin(maxbins=30), title="Score"),
                y=alt.Y('count()', title="Count"),
                color=alt.value('#4f46e5'),
                tooltip=[alt.Tooltip('count()', title='Students')]
            ).properties(height=350).interactive()
            
            st.altair_chart(hist, use_container_width=True)

    with col_pass:
        st.markdown("**Insight:** Looking at the proportion of students passing (Overall Score ≥ 60).")
        st.write("") # spacing to align with selectbox
        st.write("") 
        
        # Determine Pass/Fail status
        pf_df = filtered_df.copy()
        pf_df['Status'] = pf_df['avg_score'].apply(lambda x: 'Passing (≥60)' if x >= 60 else 'Failing (<60)')
        
        with chart_container():
            st.subheader("🏆 Pass vs Fail Breakdown")
            # 100% stacked bar chart
            bar_pf = alt.Chart(pf_df).mark_bar().encode(
                x=alt.X('sum(count):Q', stack="normalize", axis=alt.Axis(format='%'), title="Proportion of Students"),
                y=alt.Y('test_prep:N', title="Test Preparation"),
                color=alt.Color('Status:N', scale=alt.Scale(domain=['Passing (≥60)', 'Failing (<60)'], range=['#10b981', '#ef4444'])),
                tooltip=['test_prep', 'Status', alt.Tooltip('sum(count):Q', title='Students')]
            ).transform_aggregate(
                count='count()',
                groupby=['test_prep', 'Status']
            ).properties(height=350)
            
            st.altair_chart(bar_pf, use_container_width=True)


with tab_prep:
    st.header("Chapter 2: The Impact of Effort")
    prep_stats = filtered_df.groupby('test_prep')[['math_score', 'reading_score', 'writing_score']].mean()
    if 'completed' in prep_stats.index and 'none' in prep_stats.index:
        m_gain = ((prep_stats.loc['completed', 'math_score'] - prep_stats.loc['none', 'math_score']) / prep_stats.loc['none', 'math_score'] * 100)
        r_gain = ((prep_stats.loc['completed', 'reading_score'] - prep_stats.loc['none', 'reading_score']) / prep_stats.loc['none', 'reading_score'] * 100)
        w_gain = ((prep_stats.loc['completed', 'writing_score'] - prep_stats.loc['none', 'writing_score']) / prep_stats.loc['none', 'writing_score'] * 100)
        st.markdown(f"**Actionable Insight:** Completing the preparation course resulted in a score increase of **{m_gain:.1f}%** in Math, **{r_gain:.1f}%** in Reading, and **{w_gain:.1f}%** in Writing compared to students with no preparation.")
    else:
        st.markdown("**Actionable Insight:** Complete the 'Test Prep' filter to see comparative gains between course participants.")

    with chart_container():
        st.subheader("📚 Test Preparation Impact")
        prep_df = filtered_df.groupby('test_prep')[['math_score', 'reading_score', 'writing_score']].mean().reset_index()
        prep_melted = prep_df.melt(id_vars='test_prep', var_name='Subject', value_name='Average Score')
        prep_melted['Subject'] = prep_melted['Subject'].str.replace('_score', '').str.title()
        
        bar_prep = alt.Chart(prep_melted).mark_bar(cornerRadiusTopLeft=3, cornerRadiusTopRight=3).encode(
            x=alt.X('Subject:N', title="Subject", axis=alt.Axis(labelAngle=0)),
            y=alt.Y('Average Score:Q', title="Average Score"),
            color=alt.Color('test_prep:N', scale=alt.Scale(domain=['none', 'completed'], range=['#94a3b8', '#10b981']), title="Test Preparation"),
            xOffset='test_prep:N',
            tooltip=['test_prep:N', 'Subject:N', alt.Tooltip('Average Score:Q', format='.1f')]
        ).properties(height=350)
        
        st.altair_chart(bar_prep, use_container_width=True)


with tab_socio:
    st.header("Chapter 3: Environmental & Socioeconomic Context")
    lunch_stats = filtered_df.groupby('lunch')['avg_score'].mean()
    lunch_gap = lunch_stats.get('standard', 0) - lunch_stats.get('free/reduced', 0)
    edu_stats = filtered_df.groupby('parental_education')['avg_score'].mean()
    edu_gap = edu_stats.get("master's degree", 0) - edu_stats.get("high school", 0)

    st.markdown(f"**Socioeconomic Insight:** Students with standard lunch outscore their peers by **{lunch_gap:.1f}** points on average. Additionally, students whose parents have a Master's degree show a **{edu_gap:.1f}** point advantage over those with a High School education.")

    col_bl, col_br = st.columns((1, 1), gap="large")

    with col_bl:
        with chart_container():
            st.subheader("🍎 Score Density by Lunch Type")
            # Using Violin / Density representation via Altair
            density_lunch = alt.Chart(filtered_df).transform_density(
                'avg_score',
                as_=['avg_score', 'density'],
                groupby=['lunch']
            ).mark_area(opacity=0.6).encode(
                x=alt.X('avg_score:Q', title="Average Score"),
                y=alt.Y('density:Q', title="Density", axis=alt.Axis(labels=False, ticks=False)),
                color=alt.Color('lunch:N', scale=alt.Scale(domain=['standard', 'free/reduced'], range=['#0ea5e9', '#f59e0b']), legend=alt.Legend(title="Lunch Type")),
                tooltip=['lunch:N', alt.Tooltip('avg_score:Q', format='.1f')]
            ).properties(height=350).interactive()
            
            st.altair_chart(density_lunch, use_container_width=True)

    with col_br:
        with chart_container():
            st.subheader("🎓 Parental Education Influence")
            edu_df = filtered_df.groupby('parental_education')['avg_score'].mean().reset_index()
            
            bar_edu = alt.Chart(edu_df).mark_bar(cornerRadiusTopRight=3, cornerRadiusBottomRight=3).encode(
                y=alt.Y('parental_education:N', sort='-x', title="Parental Education Level"),
                x=alt.X('avg_score:Q', title="Average Score"),
                color=alt.Color('avg_score:Q', scale=alt.Scale(scheme='oranges'), legend=None),
                tooltip=['parental_education:N', alt.Tooltip('avg_score:Q', format='.1f')]
            ).properties(height=350)
            
            st.altair_chart(bar_edu, use_container_width=True)


with tab_demo:
    st.header("Chapter 4: Demographic Variances")
    demo_agg = filtered_df.groupby(['gender', 'race_ethnicity'])['avg_score'].mean().reset_index()
    if not demo_agg.empty:
        top_row = demo_agg.loc[demo_agg['avg_score'].idxmax()]
        st.markdown(f"**Demographic Insight:** The highest performing segment is **{top_row['gender'].title()}** students in **{top_row['race_ethnicity'].title()}**, who achieved an average overall score of **{top_row['avg_score']:.1f}**.")

    with chart_container():
        st.subheader("👥 Performance by Gender & Race/Ethnicity")
        heat_chart = alt.Chart(filtered_df).mark_rect().encode(
            x=alt.X('race_ethnicity:N', title="Race / Ethnicity", axis=alt.Axis(labelAngle=-45)),
            y=alt.Y('gender:N', title="Gender"),
            color=alt.Color('mean(avg_score):Q', scale=alt.Scale(scheme='viridis'), title="Avg Score"),
            tooltip=['race_ethnicity:N', 'gender:N', alt.Tooltip('mean(avg_score):Q', format='.1f')]
        ).properties(height=350)

        text = alt.Chart(filtered_df).transform_aggregate(
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


with tab_syn:
    st.header("Chapter 5: Subject Synergies")
    col_scatter_ctrl = st.columns([1, 1, 1, 1])
    with col_scatter_ctrl[0]:
        scatter_x = st.selectbox("X-Axis", ["math_score", "reading_score", "writing_score"], index=0, key='scatter_x', format_func=lambda x: x.replace('_', ' ').title())
    with col_scatter_ctrl[1]:
        scatter_y = st.selectbox("Y-Axis", ["math_score", "reading_score", "writing_score"], index=1, key='scatter_y', format_func=lambda x: x.replace('_', ' ').title())
    with col_scatter_ctrl[2]:
        scatter_color = st.selectbox("Color By", ["gender", "lunch", "test_prep", "race_ethnicity", "parental_education"], index=0, key='scatter_color', format_func=lambda x: x.replace('_', ' ').title())

    corr = filtered_df[scatter_x].corr(filtered_df[scatter_y])
    strength = "strong" if abs(corr) > 0.7 else "moderate" if abs(corr) > 0.4 else "weak"
    st.markdown(f"**Synergy Insight:** There is a **{strength}** correlation of **{corr:.2f}** between {scatter_x.replace('_', ' ').title()} and {scatter_y.replace('_', ' ').title()} performance.")

    with chart_container():
        st.subheader("🔗 Subject Correlation")
        scatter = alt.Chart(filtered_df).mark_circle(size=60, opacity=0.7).encode(
            x=alt.X(f"{scatter_x}:Q", scale=alt.Scale(zero=False), title=scatter_x.replace('_', ' ').title()),
            y=alt.Y(f"{scatter_y}:Q", scale=alt.Scale(zero=False), title=scatter_y.replace('_', ' ').title()),
            color=alt.Color(f"{scatter_color}:N", title=scatter_color.replace('_', ' ').title()),
            tooltip=['gender', 'race_ethnicity', 'lunch', 'test_prep', f'{scatter_x}', f'{scatter_y}', 'avg_score']
        ).properties(height=400).interactive()
        
        st.altair_chart(scatter, use_container_width=True)

st.markdown("---")
st.header("💡 Summary & Key Insights")
st.info("""
**Through the data we've explored, a few key pillars of student success become clear:**

1. **The Power of Preparation:** Across all subsets of data, completing a test preparation course acts as a consistent catalyst for higher average scores.
2. **The Societal Baseline:** Students with standard lunch types and those whose parents have attained college-level education consistently show a higher baseline of academic performance, underscoring the vast impact of strong environmental support.
3. **Skill Interconnectedness:** Reading and Writing scores exhibit a highly dense, positive correlation—excelling in literacy almost guarantees paired success. Math scores, while still correlated, show greater independent variance.
""")

st.divider()
st.caption("Insights generated automatically using Streamlit, DuckDB, and Altair.")