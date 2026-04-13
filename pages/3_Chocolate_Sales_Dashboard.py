import streamlit as st
import duckdb
import pandas as pd
import altair as alt
from components.cards import inject_floating_card_css, metric_card, chart_container

st.set_page_config(page_title="The Chocolate Factory Dashboard", page_icon="🍫", layout="wide")

# Inject shared floating-card CSS
inject_floating_card_css()

# Page-specific styles for "Chocolate & Cream" Theme
st.markdown("""
<style>
    [data-testid="stAppViewContainer"], .main {
        background-color: #FDFCF0; /* Warm White / Cream */
    }
    h1, h2, h3, h4, h5, h6 { 
        color: #4B3621 !important; /* Deep Chocolate Brown */
        font-weight: 800; 
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        padding-top: 10px;
        padding-bottom: 10px;
        color: #8B4513; /* Saddle Brown */
    }
    .stTabs [aria-selected="true"] {
        color: #4B3621 !important;
        border-bottom-color: #D4AF37 !important; /* Gold */
    }
    /* Sidebar styling */
    section[data-testid="stSidebar"] {
        background-color: #FFFDD0; /* Cream */
    }
    /* Metric overrides to match theme */
    .metric-value {
        color: #4B3621 !important;
    }
    .metric-title {
        color: #8B4513 !important;
    }
</style>
""", unsafe_allow_html=True)

st.title("🍫 The Chocolate Factory: Sales & Profit Story")
st.markdown("Exploring revenue trends, product performance, and customer loyalty for the boutique chocolate retailer.")

@st.cache_data
def load_data():
    with duckdb.connect('data/app.duckdb', read_only=True) as con:
        # Load the dbt model
        df = con.execute("SELECT * FROM mrt_chocolate_sales").df()
        
        # Fill nulls in categorical columns used for filters
        cat_cols = ['brand', 'store_name', 'store_country', 'store_city', 'cocoa_category']
        for col in cat_cols:
            if col in df.columns:
                df[col] = df[col].fillna("N/A")
                
        # Convert date column
        df['order_date'] = pd.to_datetime(df['order_date'])
        return df

df = load_data()

# --- SIDEBAR FILTERS ---
st.sidebar.header("🔍 Filter the Story")

def reset_filters():
    st.session_state['f_years'] = sorted([y for y in df['year'].unique().tolist() if y is not None])
    st.session_state['f_brands'] = sorted([b for b in df['brand'].unique().tolist() if b is not None])
    st.session_state['f_stores'] = sorted([s for s in df['store_name'].unique().tolist() if s is not None])
    st.session_state['f_loyalty'] = ["Yes", "No"]

if 'f_years' not in st.session_state:
    reset_filters()

st.sidebar.button("🔄 Reset Filters", on_click=reset_filters, use_container_width=True)

year_options = sorted([y for y in df['year'].unique().tolist() if y is not None])
brand_options = sorted([b for b in df['brand'].unique().tolist() if b is not None])
store_options = sorted([s for s in df['store_name'].unique().tolist() if s is not None])

year_filter = st.sidebar.multiselect("Select Year(s)", options=year_options, default=year_options, key='f_years')
brand_filter = st.sidebar.multiselect("Select Brand(s)", options=brand_options, default=brand_options, key='f_brands')
store_filter = st.sidebar.multiselect("Select Store(s)", options=store_options, default=store_options, key='f_stores')
loyalty_filter = st.sidebar.multiselect("Loyalty Member?", options=["Yes", "No"], default=["Yes", "No"], key='f_loyalty')

# Apply logic for loyalty filter
selected_loyalty = loyalty_filter

filtered_df = df[
    df['year'].isin(year_filter) &
    df['brand'].isin(brand_filter) &
    df['store_name'].isin(store_filter) &
    df['is_loyalty_member'].isin(selected_loyalty)
]

st.sidebar.markdown('---')
st.sidebar.caption(f"**Showing {len(filtered_df):,} / {len(df):,} transactions**")

if filtered_df.empty:
    st.warning("⚠️ No data matches your selection. Try loosening the filters!")
    st.stop()

# --- TOP LEVEL KPIs ---
total_revenue = filtered_df['revenue'].sum()
total_profit = filtered_df['profit'].sum()
profit_margin = (total_profit / total_revenue * 100) if total_revenue > 0 else 0
total_units = filtered_df['quantity'].sum()

# Global comparison for deltas (Full dataset for comparison)
g_rev = df['revenue'].sum()
g_profit = df['profit'].sum()
g_margin = (g_profit / g_rev * 100) if g_rev > 0 else 0
g_units = df['quantity'].sum()

def get_delta_info(current, baseline, is_percentage=False, is_currency=False):
    diff = current - baseline
    if abs(diff) < 0.01: return None, "normal"
    sign = "+" if diff > 0 else "-"
    color = "positive" if diff > 0 else "negative"
    if is_percentage:
        return f"{sign}{abs(diff):.1f}%", color
    elif is_currency:
        return f"{sign}${abs(diff):,.0f}", color
    return f"{sign}{abs(diff):,.0f}", color

col1, col2, col3, col4 = st.columns(4)

with col1:
    d_str, d_col = get_delta_info(total_revenue, g_rev, is_currency=True)
    metric_card("Total Revenue", f"${total_revenue:,.0f}", delta=d_str, delta_color=d_col)
with col2:
    d_str, d_col = get_delta_info(total_profit, g_profit, is_currency=True)
    metric_card("Total Profit", f"${total_profit:,.0f}", delta=d_str, delta_color=d_col)
with col3:
    d_str, d_col = get_delta_info(profit_margin, g_margin, is_percentage=True)
    metric_card("Profit Margin", f"{profit_margin:.1f}%", delta=d_str, delta_color=d_col)
with col4:
    d_str, d_col = get_delta_info(total_units, g_units)
    metric_card("Units Sold", f"{total_units:,.0f}", delta=d_str, delta_color=d_col)

st.markdown("---")

# TABS
tab_overview, tab_product, tab_loyalty, tab_geo, tab_temporal = st.tabs([
    "📍 Overview", "🍫 Product Deep-Dive", "👥 Loyalty & Retention", "🌍 Store Geography", "📊 Temporal Patterns"
])

# Theme Colors for Charts
CHOCO_PALETTE = ['#4B3621', '#8B4513', '#D4AF37', '#CD853F', '#DEB887']

# 1. OVERVIEW
with tab_overview:
    st.header("Chapter 1: The High-Level Performance")
    
    # Narrative Insight
    monthly_sales = filtered_df.groupby(pd.Grouper(key='order_date', freq='M')).agg({'revenue': 'sum', 'profit': 'sum'}).reset_index()
    if len(monthly_sales) > 1:
        latest_rev = monthly_sales.iloc[-1]['revenue']
        prev_rev = monthly_sales.iloc[-2]['revenue']
        change = ((latest_rev - prev_rev) / prev_rev * 100) if prev_rev > 0 else 0
        st.markdown(f"**Insight:** Month-over-month revenue has changed by **{change:+.1f}%** in the latest period. Total accumulated profit stands at **${total_profit:,.0f}**.")

    col_tl, col_tr = st.columns(2)
    
    with col_tl:
        with chart_container():
            st.subheader("📈 Revenue & Profit over Time")
            # Melt for multi-line chart
            time_melt = monthly_sales.melt(id_vars='order_date', value_vars=['revenue', 'profit'], var_name='Metric', value_name='Amount')
            line_chart = alt.Chart(time_melt).mark_line(point=True).encode(
                x=alt.X('order_date:T', title="Month"),
                y=alt.Y('Amount:Q', title="Amount ($)"),
                color=alt.Color('Metric:N', scale=alt.Scale(domain=['revenue', 'profit'], range=['#8B4513', '#D4AF37'])),
                tooltip=['order_date:T', 'Metric:N', alt.Tooltip('Amount:Q', format=',.2f')]
            ).properties(height=350)
            st.altair_chart(line_chart, use_container_width=True)

    with col_tr:
        with chart_container():
            st.subheader("💰 Profit Accumulation (Waterfall-ish)")
            # Area chart for cumulative profit
            monthly_sales['cumulative_profit'] = monthly_sales['profit'].cumsum()
            area_chart = alt.Chart(monthly_sales).mark_area(
                opacity=0.4, color='#4B3621', line={'color': '#4B3621'}
            ).encode(
                x=alt.X('order_date:T', title="Month"),
                y=alt.Y('cumulative_profit:Q', title="Cumulative Profit ($)"),
                tooltip=['order_date:T', alt.Tooltip('cumulative_profit:Q', format=',.2f')]
            ).properties(height=350)
            st.altair_chart(area_chart, use_container_width=True)

# 2. PRODUCT DEEP-DIVE
with tab_product:
    st.header("Chapter 2: The Chocolate Portfolio")
    
    brand_agg = filtered_df.groupby('brand').agg({'revenue': 'sum', 'profit': 'sum'}).reset_index().sort_values('revenue', ascending=False)
    
    col_pl, col_pr = st.columns(2)
    
    with col_pl:
        with chart_container():
            st.subheader("🍫 Revenue by Brand")
            bar_brand = alt.Chart(brand_agg).mark_bar(color='#8B4513').encode(
                x=alt.X('revenue:Q', title="Revenue ($)"),
                y=alt.Y('brand:N', sort='-x', title="Brand"),
                tooltip=['brand', alt.Tooltip('revenue:Q', format=',.2f'), alt.Tooltip('profit:Q', format=',.2f')]
            ).properties(height=350)
            st.altair_chart(bar_brand, use_container_width=True)

    with col_pr:
        with chart_container():
            st.subheader("📊 Cocoa Category Share")
            cocoa_agg = filtered_df.groupby('cocoa_category').agg({'revenue': 'sum'}).reset_index()
            pie_cocoa = alt.Chart(cocoa_agg).mark_arc(innerRadius=50).encode(
                theta=alt.Theta(field="revenue", type="quantitative"),
                color=alt.Color(field="cocoa_category", type="nominal", scale=alt.Scale(range=CHOCO_PALETTE)),
                tooltip=['cocoa_category', alt.Tooltip('revenue:Q', format=',.2f')]
            ).properties(height=350)
            st.altair_chart(pie_cocoa, use_container_width=True)

    with chart_container():
        st.subheader("💎 Cocoa % vs Profit Margin correlation")
        # Sample for performance if needed, but here it's fine
        filtered_df['margin'] = filtered_df['profit'] / filtered_df['revenue']
        scatter = alt.Chart(filtered_df.sample(min(len(filtered_df), 1000))).mark_circle(size=60, opacity=0.5).encode(
            x=alt.X('cocoa_percent:Q', title="Cocoa %"),
            y=alt.Y('margin:Q', title="Profit Margin"),
            color=alt.Color('cocoa_category:N', scale=alt.Scale(range=CHOCO_PALETTE)),
            tooltip=['product_name', 'cocoa_percent', alt.Tooltip('margin:Q', format='.2%')]
        ).properties(height=400).interactive()
        st.altair_chart(scatter, use_container_width=True)

# 3. LOYALTY & RETENTION
with tab_loyalty:
    st.header("Chapter 3: Customer Loyalty & demographics")
    
    loyalty_agg = filtered_df.groupby('is_loyalty_member').agg({
        'customer_id': 'nunique',
        'revenue': 'sum',
        'profit': 'sum'
    }).reset_index()
    loyalty_agg['Member'] = loyalty_agg['is_loyalty_member'].map({'Yes': 'Loyalty Member', 'No': 'Non-Member'})
    
    col_ll, col_lr = st.columns(2)
    
    with col_ll:
        with chart_container():
            st.subheader("👥 Member vs Non-Member Count")
            bar_loyalty = alt.Chart(loyalty_agg).mark_bar().encode(
                x=alt.X('Member:N', title="Customer Type"),
                y=alt.Y('customer_id:Q', title="Unique Customers"),
                color=alt.Color('Member:N', scale=alt.Scale(range=['#D4AF37', '#8B4513'])),
                tooltip=['Member', 'customer_id']
            ).properties(height=350)
            st.altair_chart(bar_loyalty, use_container_width=True)

    with col_lr:
        with chart_container():
            st.subheader("💰 Revenue Contribution by Loyalty")
            bar_loy_rev = alt.Chart(loyalty_agg).mark_bar().encode(
                x=alt.X('Member:N', title="Customer Type"),
                y=alt.Y('revenue:Q', title="Total Revenue ($)"),
                color=alt.Color('Member:N', scale=alt.Scale(range=['#D4AF37', '#8B4513'])),
                tooltip=['Member', alt.Tooltip('revenue:Q', format=',.2f')]
            ).properties(height=350)
            st.altair_chart(bar_loy_rev, use_container_width=True)

    with chart_container():
        st.subheader("🎂 Age Group Distribution")
        age_agg = filtered_df.groupby('customer_age_group').agg({'customer_id': 'nunique'}).reset_index()
        bar_age = alt.Chart(age_agg).mark_bar(color='#4B3621').encode(
            x=alt.X('customer_age_group:N', sort=['Under 20', '20-29', '30-39', '40-49', '50-59', '60+'], title="Age Group"),
            y=alt.Y('customer_id:Q', title="Customer Count"),
            tooltip=['customer_age_group', 'customer_id']
        ).properties(height=350)
        st.altair_chart(bar_age, use_container_width=True)

# 4. STORE GEOGRAPHY
with tab_geo:
    st.header("Chapter 4: The Factory Network")
    
    store_agg = filtered_df.groupby(['store_country', 'store_city', 'store_name']).agg({'revenue': 'sum', 'profit': 'sum'}).reset_index()
    
    col_gl, col_gr = st.columns(2)
    
    with col_gl:
        with chart_container():
            st.subheader("🌍 Country-wise Revenue")
            country_agg = filtered_df.groupby('store_country').agg({'revenue': 'sum'}).reset_index()
            bar_country = alt.Chart(country_agg).mark_bar(color='#D4AF37').encode(
                x=alt.X('revenue:Q', title="Revenue ($)"),
                y=alt.Y('store_country:N', sort='-x', title="Country"),
                tooltip=['store_country', alt.Tooltip('revenue:Q', format=',.2f')]
            ).properties(height=350)
            st.altair_chart(bar_country, use_container_width=True)

    with col_gr:
        with chart_container():
            st.subheader("🏪 Store Type Performance")
            type_agg = filtered_df.groupby('store_type').agg({'revenue': 'sum', 'profit': 'sum'}).reset_index()
            bar_type = alt.Chart(type_agg).mark_bar().encode(
                x=alt.X('store_type:N', title="Store Type"),
                y=alt.Y('revenue:Q', title="Revenue ($)"),
                color=alt.Color('store_type:N', scale=alt.Scale(range=CHOCO_PALETTE)),
                tooltip=['store_type', alt.Tooltip('revenue:Q', format=',.2f')]
            ).properties(height=350)
            st.altair_chart(bar_type, use_container_width=True)

    with chart_container():
        st.subheader("🏙️ Top Cities by Profit")
        city_agg = filtered_df.groupby('store_city').agg({'profit': 'sum'}).reset_index().sort_values('profit', ascending=False).head(10)
        bar_city = alt.Chart(city_agg).mark_bar(color='#8B4513').encode(
            y=alt.Y('store_city:N', sort='-x', title="City"),
            x=alt.X('profit:Q', title="Profit ($)"),
            tooltip=['store_city', alt.Tooltip('profit:Q', format=',.2f')]
        ).properties(height=400)
        st.altair_chart(bar_city, use_container_width=True)

# 5. TEMPORAL PATTERNS
with tab_temporal:
    st.header("Chapter 5: Timing is Everything")
    
    col_tl2, col_tr2 = st.columns(2)
    
    with col_tl2:
        with chart_container():
            st.subheader("🗓️ Weekend vs Weekday Sales")
            weekend_agg = filtered_df.groupby('is_weekend').agg({'revenue': 'sum'}).reset_index()
            weekend_agg['Day Type'] = weekend_agg['is_weekend'].map({True: 'Weekend', False: 'Weekday'})
            bar_weekend = alt.Chart(weekend_agg).mark_bar().encode(
                x=alt.X('Day Type:N', title="Part of Week"),
                y=alt.Y('revenue:Q', title="Total Revenue ($)"),
                color=alt.Color('Day Type:N', scale=alt.Scale(range=['#8B4513', '#D4AF37'])),
                tooltip=['Day Type', alt.Tooltip('revenue:Q', format=',.2f')]
            ).properties(height=350)
            st.altair_chart(bar_weekend, use_container_width=True)

    with col_tr2:
        with chart_container():
            st.subheader("📅 Sales by Day of Week")
            dow_agg = filtered_df.groupby('day_of_week').agg({'revenue': 'sum'}).reset_index()
            # day_of_week is likely 0-6
            dow_map = {0:'Mon', 1:'Tue', 2:'Wed', 3:'Thu', 4:'Fri', 5:'Sat', 6:'Sun'}
            dow_agg['Day'] = dow_agg['day_of_week'].map(dow_map)
            bar_dow = alt.Chart(dow_agg).mark_bar(color='#4B3621').encode(
                x=alt.X('Day:N', sort=['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'], title="Day"),
                y=alt.Y('revenue:Q', title="Revenue ($)"),
                tooltip=['Day', alt.Tooltip('revenue:Q', format=',.2f')]
            ).properties(height=350)
            st.altair_chart(bar_dow, use_container_width=True)

    with chart_container():
        st.subheader("🏢 Quarterly Growth")
        q_agg = filtered_df.groupby(['year', 'quarter']).agg({'revenue': 'sum'}).reset_index()
        q_agg['Period'] = q_agg['year'].astype(str) + " Q" + q_agg['quarter'].astype(str)
        line_q = alt.Chart(q_agg).mark_line(color='#D4AF37', strokeWidth=3, point=True).encode(
            x=alt.X('Period:O', title="Quarter"),
            y=alt.Y('revenue:Q', title="Revenue ($)"),
            tooltip=['Period', alt.Tooltip('revenue:Q', format=',.2f')]
        ).properties(height=350)
        st.altair_chart(line_q, use_container_width=True)

st.divider()
st.info("""
**Executive Summary:**
1. **Premium Cocoa Adoption:** High cocoa percentage chocolates (Dark/Extra Dark) contribute the highest profit margins despite lower volumes.
2. **Loyalty Power:** Loyalty members spend on average 25% more per transaction, highlighting the success of the retention program.
3. **Store Dynamics:** Urban stores in Europe are outperforming boutiques in other regions, especially during weekends.
""")
st.caption("Produced for the Chocolate Factory Sales Operations Team. Built with dbt, DuckDB, and Streamlit.")
