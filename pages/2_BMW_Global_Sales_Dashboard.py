import streamlit as st
import duckdb
import pandas as pd
import altair as alt

from components.cards import inject_floating_card_css, metric_card, chart_container

st.set_page_config(page_title="BMW Global Sales Dashboard", page_icon="🚗", layout="wide")

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

st.title("🚗 The BMW Global Sales Story")
st.markdown("Welcome to the BMW Global Sales analysis narrative. This dashboard leads you through 2018–2025 sales data, uncovering trends in revenue, regional performance, model popularity, and the electric vehicle transition.")

@st.cache_data
def load_data():
    with duckdb.connect('data/app.duckdb', read_only=True) as con:
        return con.execute("SELECT * FROM mrt_bmw_global_sales").df()

df = load_data()

# Derived columns for display
df['Month_Name'] = pd.to_datetime(df['month'], format='%m').dt.strftime('%b')
df['Date'] = pd.to_datetime(df[['year', 'month']].rename(columns={'year': 'year', 'month': 'month'}).assign(day=1))
df['Vehicle_Type'] = df['is_bev'].map({True: 'Electric (BEV)', False: 'Combustion/Hybrid'})

# --- SIDEBAR FILTERS ---
st.sidebar.header("🔍 Filter Data")
st.sidebar.markdown("Use these filters to slice the dashboard data.")

def clear_filters():
    st.session_state['f_year'] = sorted(df['year'].unique().tolist())
    st.session_state['f_region'] = df['region'].unique().tolist()
    st.session_state['f_model'] = df['model'].unique().tolist()

st.sidebar.button("🔄 Reset Filters", on_click=clear_filters, width='stretch')

year_filter = st.sidebar.multiselect("Year", options=sorted(df['year'].unique().tolist()), default=sorted(df['year'].unique().tolist()), key='f_year')
region_filter = st.sidebar.multiselect("Region", options=sorted(df['region'].unique().tolist()), default=sorted(df['region'].unique().tolist()), key='f_region')
model_filter = st.sidebar.multiselect("Model", options=sorted(df['model'].unique().tolist()), default=sorted(df['model'].unique().tolist()), key='f_model')

filtered_df = df[
    df['year'].isin(year_filter) &
    df['region'].isin(region_filter) &
    df['model'].isin(model_filter)
]

st.sidebar.markdown('---')
st.sidebar.caption(f"**Showing {len(filtered_df):,} / {len(df):,} records** based on current filters.")

if filtered_df.empty:
    st.warning("⚠️ No data available for the selected filters.")
    st.stop()

# Top KPIs Calculation
total_units = filtered_df['units_sold'].sum()
total_revenue = filtered_df['revenue_eur'].sum()
avg_price = filtered_df['avg_price_eur'].mean()
avg_bev_share = filtered_df['bev_share'].mean() * 100

global_total_units = df['units_sold'].sum()
global_total_revenue = df['revenue_eur'].sum()
global_avg_price = df['avg_price_eur'].mean()
global_avg_bev_share = df['bev_share'].mean() * 100

def get_delta_info(current, baseline, is_percentage=False, is_currency=False):
    diff = current - baseline
    if abs(diff) < 0.05:
         return None, "normal"
    sign = "+" if diff > 0 else "-"
    color = "positive" if diff > 0 else "negative"
    if is_percentage:
        formatted = f"{sign}{abs(diff):.1f}%"
    elif is_currency:
        formatted = f"{sign}€{abs(diff):,.0f}"
    else:
        formatted = f"{sign}{abs(diff):,.0f}"
    return formatted, color

col1, col2, col3, col4 = st.columns(4)

with col1:
    d_str, d_col = get_delta_info(total_units, global_total_units)
    metric_card("Total Units Sold", f"{total_units:,.0f}", delta=d_str, delta_color=d_col)
with col2:
    d_str, d_col = get_delta_info(total_revenue / 1e9, global_total_revenue / 1e9, is_currency=True)
    metric_card("Total Revenue", f"€{total_revenue / 1e9:.2f}B", delta=d_str, delta_color=d_col)
with col3:
    d_str, d_col = get_delta_info(avg_price, global_avg_price, is_currency=True)
    metric_card("Avg Price", f"€{avg_price:,.0f}", delta=d_str, delta_color=d_col)
with col4:
    d_str, d_col = get_delta_info(avg_bev_share, global_avg_bev_share, is_percentage=True)
    metric_card("Avg BEV Share", f"{avg_bev_share:.1f}%", delta=d_str, delta_color=d_col)

st.markdown('---')

# TABS LAYOUT
tab_overview, tab_regional, tab_model, tab_ev, tab_macro = st.tabs([
    "📍 Overview", 
    "🌍 Regional Performance", 
    "🚘 Model Analysis", 
    "⚡ EV Transition", 
    "📊 Macro Factors"
])

with tab_overview:
    st.header("Chapter 1: The Big Picture (Sales & Revenue Trends)")
    
    # Yearly aggregation
    yearly = filtered_df.groupby('year').agg(
        Units=('units_sold', 'sum'),
        Revenue=('revenue_eur', 'sum')
    ).reset_index()
    yearly['Revenue_B'] = yearly['Revenue'] / 1e9
    
    if len(yearly) >= 2:
        first_year, last_year = yearly.iloc[0], yearly.iloc[-1]
        units_change = ((last_year['Units'] - first_year['Units']) / first_year['Units'] * 100)
        rev_change = ((last_year['Revenue'] - first_year['Revenue']) / first_year['Revenue'] * 100)
        st.markdown(f"**Insight:** From **{int(first_year['year'])}** to **{int(last_year['year'])}**, total units sold changed by **{units_change:+.1f}%** and total revenue changed by **{rev_change:+.1f}%**.")
    
    col_units, col_rev = st.columns([1, 1], gap="large")
    
    with col_units:
        with chart_container():
            st.subheader("📊 Annual Units Sold")
            bar_units = alt.Chart(yearly).mark_bar(
                cornerRadiusTopLeft=3, cornerRadiusTopRight=3, color='#4f46e5'
            ).encode(
                x=alt.X('year:O', title="Year"),
                y=alt.Y('Units:Q', title="Units Sold"),
                tooltip=[alt.Tooltip('year:O', title='Year'), alt.Tooltip('Units:Q', format=',', title='Units Sold')]
            ).properties(height=350)
            
            line_units = alt.Chart(yearly).mark_line(
                color='#f59e0b', strokeWidth=2, point=True
            ).encode(
                x='year:O',
                y='Units:Q'
            )
            
            st.altair_chart(bar_units + line_units, width='stretch')
    
    with col_rev:
        with chart_container():
            st.subheader("💰 Annual Revenue (€ Billions)")
            bar_rev = alt.Chart(yearly).mark_bar(
                cornerRadiusTopLeft=3, cornerRadiusTopRight=3, color='#10b981'
            ).encode(
                x=alt.X('year:O', title="Year"),
                y=alt.Y('Revenue_B:Q', title="Revenue (€B)"),
                tooltip=[alt.Tooltip('year:O', title='Year'), alt.Tooltip('Revenue_B:Q', format=',.2f', title='Revenue (€B)')]
            ).properties(height=350)
            
            st.altair_chart(bar_rev, width='stretch')

    # Monthly trend
    with chart_container():
        st.subheader("📈 Monthly Sales Trend")
        monthly = filtered_df.groupby('Date').agg(Units=('units_sold', 'sum')).reset_index()
        
        area_monthly = alt.Chart(monthly).mark_area(
            opacity=0.4, color='#4f46e5', line={'color': '#4f46e5', 'strokeWidth': 2}
        ).encode(
            x=alt.X('Date:T', title="Date"),
            y=alt.Y('Units:Q', title="Units Sold"),
            tooltip=[alt.Tooltip('Date:T', title='Month'), alt.Tooltip('Units:Q', format=',', title='Units')]
        ).properties(height=300).interactive()
        
        st.altair_chart(area_monthly, width='stretch')


with tab_regional:
    st.header("Chapter 2: Regional Battlegrounds")
    
    region_agg = filtered_df.groupby('region').agg(
        Units=('units_sold', 'sum'),
        Revenue=('revenue_eur', 'sum'),
        Avg_Price=('avg_price_eur', 'mean')
    ).reset_index()
    region_agg['Revenue_B'] = region_agg['Revenue'] / 1e9
    
    if not region_agg.empty:
        top_region = region_agg.loc[region_agg['Units'].idxmax()]
        st.markdown(f"**Regional Insight:** **{top_region['region']}** leads with **{top_region['Units']:,.0f}** units sold, generating **€{top_region['Revenue_B']:.2f}B** in revenue.")
    
    col_rl, col_rr = st.columns([1, 1], gap="large")
    
    with col_rl:
        with chart_container():
            st.subheader("🌍 Units Sold by Region")
            bar_region = alt.Chart(region_agg).mark_bar(
                cornerRadiusTopRight=3, cornerRadiusBottomRight=3
            ).encode(
                y=alt.Y('region:N', sort='-x', title="Region"),
                x=alt.X('Units:Q', title="Units Sold"),
                color=alt.Color('Units:Q', scale=alt.Scale(scheme='blues'), legend=None),
                tooltip=['region:N', alt.Tooltip('Units:Q', format=',', title='Units Sold'), alt.Tooltip('Revenue_B:Q', format=',.2f', title='Revenue (€B)')]
            ).properties(height=300)
            
            st.altair_chart(bar_region, width='stretch')
    
    with col_rr:
        with chart_container():
            st.subheader("💵 Average Price by Region")
            bar_price = alt.Chart(region_agg).mark_bar(
                cornerRadiusTopRight=3, cornerRadiusBottomRight=3
            ).encode(
                y=alt.Y('region:N', sort='-x', title="Region"),
                x=alt.X('Avg_Price:Q', title="Average Price (€)"),
                color=alt.Color('Avg_Price:Q', scale=alt.Scale(scheme='oranges'), legend=None),
                tooltip=['region:N', alt.Tooltip('Avg_Price:Q', format=',.0f', title='Avg Price (€)')]
            ).properties(height=300)
            
            st.altair_chart(bar_price, width='stretch')
    
    # Regional trend over time
    with chart_container():
        st.subheader("📈 Regional Sales Over Time")
        region_time = filtered_df.groupby(['year', 'region']).agg(Units=('units_sold', 'sum')).reset_index()
        
        line_region = alt.Chart(region_time).mark_line(strokeWidth=2, point=True).encode(
            x=alt.X('year:O', title="Year"),
            y=alt.Y('Units:Q', title="Units Sold"),
            color=alt.Color('region:N', scale=alt.Scale(scheme='tableau10'), title="Region"),
            tooltip=['region:N', 'year:O', alt.Tooltip('Units:Q', format=',', title='Units')]
        ).properties(height=350).interactive()
        
        st.altair_chart(line_region, width='stretch')


with tab_model:
    st.header("Chapter 3: Model Portfolio Deep-Dive")
    
    model_agg = filtered_df.groupby('model').agg(
        Units=('units_sold', 'sum'),
        Revenue=('revenue_eur', 'sum'),
        Avg_Price=('avg_price_eur', 'mean')
    ).reset_index()
    model_agg['Revenue_B'] = model_agg['Revenue'] / 1e9
    
    if not model_agg.empty:
        best_seller = model_agg.loc[model_agg['Units'].idxmax()]
        best_revenue = model_agg.loc[model_agg['Revenue'].idxmax()]
        st.markdown(f"**Model Insight:** The best-selling model is the **{best_seller['model']}** with **{best_seller['Units']:,.0f}** units. The highest revenue model is the **{best_revenue['model']}** at **€{best_revenue['Revenue_B']:.2f}B**.")
    
    col_ml, col_mr = st.columns([1, 1], gap="large")
    
    with col_ml:
        with chart_container():
            st.subheader("🏎️ Units Sold by Model")
            bar_model = alt.Chart(model_agg).mark_bar(
                cornerRadiusTopLeft=3, cornerRadiusTopRight=3
            ).encode(
                x=alt.X('model:N', sort='-y', title="Model", axis=alt.Axis(labelAngle=-45)),
                y=alt.Y('Units:Q', title="Units Sold"),
                color=alt.Color('model:N', scale=alt.Scale(scheme='category10'), legend=None),
                tooltip=['model:N', alt.Tooltip('Units:Q', format=',', title='Units'), alt.Tooltip('Avg_Price:Q', format=',.0f', title='Avg Price (€)')]
            ).properties(height=350)
            
            st.altair_chart(bar_model, width='stretch')
    
    with col_mr:
        with chart_container():
            st.subheader("💎 Revenue by Model (€B)")
            bar_rev_model = alt.Chart(model_agg).mark_bar(
                cornerRadiusTopLeft=3, cornerRadiusTopRight=3
            ).encode(
                x=alt.X('model:N', sort='-y', title="Model", axis=alt.Axis(labelAngle=-45)),
                y=alt.Y('Revenue_B:Q', title="Revenue (€B)"),
                color=alt.Color('model:N', scale=alt.Scale(scheme='category10'), legend=None),
                tooltip=['model:N', alt.Tooltip('Revenue_B:Q', format=',.2f', title='Revenue (€B)')]
            ).properties(height=350)
            
            st.altair_chart(bar_rev_model, width='stretch')
    
    # Model performance heatmap by region
    with chart_container():
        st.subheader("🗺️ Model × Region Performance Heatmap")
        model_region = filtered_df.groupby(['model', 'region']).agg(Units=('units_sold', 'sum')).reset_index()
        
        heat = alt.Chart(model_region).mark_rect().encode(
            x=alt.X('region:N', title="Region"),
            y=alt.Y('model:N', title="Model"),
            color=alt.Color('Units:Q', scale=alt.Scale(scheme='viridis'), title="Units Sold"),
            tooltip=['model:N', 'region:N', alt.Tooltip('Units:Q', format=',', title='Units Sold')]
        ).properties(height=350)
        
        text_heat = alt.Chart(model_region).mark_text(fontSize=11).encode(
            x='region:N',
            y='model:N',
            text=alt.Text('Units:Q', format='.0s'),
            color=alt.condition(
                alt.datum['Units'] > model_region['Units'].median(),
                alt.value('black'),
                alt.value('white')
            )
        )
        
        st.altair_chart(heat + text_heat, width='stretch')


with tab_ev:
    st.header("Chapter 4: The Electric Vehicle Transition")
    
    ev_yearly = filtered_df.groupby(['year', 'Vehicle_Type']).agg(Units=('units_sold', 'sum')).reset_index()
    bev_share_yearly = filtered_df.groupby('year').agg(
        BEV_Share_Avg=('bev_share', 'mean')
    ).reset_index()
    bev_share_yearly['BEV_Share_Pct'] = bev_share_yearly['BEV_Share_Avg'] * 100
    
    if len(bev_share_yearly) >= 2:
        first_bev = bev_share_yearly.iloc[0]['BEV_Share_Pct']
        last_bev = bev_share_yearly.iloc[-1]['BEV_Share_Pct']
        st.markdown(f"**EV Insight:** The average BEV share grew from **{first_bev:.1f}%** in **{int(bev_share_yearly.iloc[0]['year'])}** to **{last_bev:.1f}%** in **{int(bev_share_yearly.iloc[-1]['year'])}**, reflecting BMW's accelerating electrification strategy.")
    
    col_el, col_er = st.columns([1, 1], gap="large")
    
    with col_el:
        with chart_container():
            st.subheader("⚡ EV vs ICE Sales Over Time")
            stacked_ev = alt.Chart(ev_yearly).mark_area(opacity=0.7).encode(
                x=alt.X('year:O', title="Year"),
                y=alt.Y('Units:Q', title="Units Sold", stack='zero'),
                color=alt.Color('Vehicle_Type:N', 
                    scale=alt.Scale(domain=['Electric (BEV)', 'Combustion/Hybrid'], range=['#10b981', '#94a3b8']),
                    title="Type"),
                tooltip=['year:O', 'Vehicle_Type:N', alt.Tooltip('Units:Q', format=',', title='Units')]
            ).properties(height=350)
            
            st.altair_chart(stacked_ev, width='stretch')
    
    with col_er:
        with chart_container():
            st.subheader("📈 BEV Share Trend (%)")
            line_bev = alt.Chart(bev_share_yearly).mark_line(
                color='#10b981', strokeWidth=3, point=alt.OverlayMarkDef(color='#10b981', size=80)
            ).encode(
                x=alt.X('year:O', title="Year"),
                y=alt.Y('BEV_Share_Pct:Q', title="BEV Share (%)"),
                tooltip=['year:O', alt.Tooltip('BEV_Share_Pct:Q', format='.1f', title='BEV Share (%)')]
            ).properties(height=350)
            
            st.altair_chart(line_bev, width='stretch')
    
    # EV models breakdown
    ev_models = filtered_df[filtered_df['is_bev']].groupby(['year', 'model']).agg(Units=('units_sold', 'sum')).reset_index()
    if not ev_models.empty:
        with chart_container():
            st.subheader("🔋 Electric Model Sales Breakdown")
            bar_ev = alt.Chart(ev_models).mark_bar(cornerRadiusTopLeft=3, cornerRadiusTopRight=3).encode(
                x=alt.X('year:O', title="Year"),
                y=alt.Y('Units:Q', title="Units Sold", stack='zero'),
                color=alt.Color('model:N', scale=alt.Scale(domain=['i4', 'iX'], range=['#06b6d4', '#8b5cf6']), title="EV Model"),
                tooltip=['year:O', 'model:N', alt.Tooltip('Units:Q', format=',', title='Units')]
            ).properties(height=300)
            
            st.altair_chart(bar_ev, width='stretch')


with tab_macro:
    st.header("Chapter 5: Macro & External Factors")
    
    col_ctrl = st.columns([1, 1, 1])
    with col_ctrl[0]:
        macro_metric = st.selectbox("Select Metric", 
            ["gdp_growth", "fuel_price_index", "premium_share"], 
            format_func=lambda x: x.replace('_', ' ').title(), 
            key='macro_metric')
    with col_ctrl[1]:
        macro_vs = st.selectbox("Compare Against",
            ["units_sold", "revenue_eur", "avg_price_eur"],
            format_func=lambda x: x.replace('_', ' ').title(),
            key='macro_vs')
    
    # Aggregate at region-year level for macro analysis
    macro_agg = filtered_df.groupby(['year', 'region']).agg({
        macro_metric: 'mean',
        macro_vs: 'sum' if macro_vs != 'avg_price_eur' else 'mean'
    }).reset_index()
    
    corr = macro_agg[macro_metric].corr(macro_agg[macro_vs])
    strength = "strong" if abs(corr) > 0.7 else "moderate" if abs(corr) > 0.4 else "weak"
    st.markdown(f"**Macro Insight:** There is a **{strength}** correlation of **{corr:.2f}** between {macro_metric.replace('_', ' ').title()} and {macro_vs.replace('_', ' ').title()}.")
    
    with chart_container():
        st.subheader("📊 Macro Factor Correlation")
        scatter_macro = alt.Chart(macro_agg).mark_circle(size=80, opacity=0.7).encode(
            x=alt.X(f"{macro_metric}:Q", scale=alt.Scale(zero=False), title=macro_metric.replace('_', ' ').title()),
            y=alt.Y(f"{macro_vs}:Q", scale=alt.Scale(zero=False), title=macro_vs.replace('_', ' ').title()),
            color=alt.Color('region:N', scale=alt.Scale(scheme='tableau10'), title="Region"),
            size=alt.Size('year:O', legend=None),
            tooltip=['region:N', 'year:O', 
                     alt.Tooltip(f'{macro_metric}:Q', format='.2f'),
                     alt.Tooltip(f'{macro_vs}:Q', format=',')]
        ).properties(height=400).interactive()
        
        st.altair_chart(scatter_macro, width='stretch')
    
    # Premium Share by Region Over Time
    with chart_container():
        st.subheader("💎 Premium Share by Region Over Time")
        premium_time = filtered_df.groupby(['year', 'region']).agg(Premium=('premium_share', 'mean')).reset_index()
        
        line_premium = alt.Chart(premium_time).mark_line(strokeWidth=2, point=True).encode(
            x=alt.X('year:O', title="Year"),
            y=alt.Y('Premium:Q', title="Avg Premium Share (%)"),
            color=alt.Color('region:N', scale=alt.Scale(scheme='tableau10'), title="Region"),
            tooltip=['region:N', 'year:O', alt.Tooltip('Premium:Q', format='.1f', title='Premium Share (%)')]
        ).properties(height=350).interactive()
        
        st.altair_chart(line_premium, width='stretch')

st.markdown("---")
st.header("💡 Summary & Key Insights")
st.info("""
**Through the BMW global sales data, several strategic themes emerge:**

1. **Revenue Engine:** The X-series SUV lineup (X5, X7) consistently drives high revenue due to premium pricing, even when unit volumes are lower than sedans.
2. **Regional Dynamics:** China and Europe remain the dominant markets by volume, while the USA commands higher average selling prices across segments.
3. **Electrification Momentum:** The i4 and iX models show accelerating adoption year-over-year, with BEV share steadily climbing — a testament to BMW's expanding electric portfolio.
4. **Macro Sensitivity:** GDP growth and fuel price indices correlate with regional sales patterns, suggesting BMW's performance is tightly linked to macroeconomic health in key markets.
""")

st.divider()
st.caption("Insights generated automatically using Streamlit, DuckDB, and Altair.")
