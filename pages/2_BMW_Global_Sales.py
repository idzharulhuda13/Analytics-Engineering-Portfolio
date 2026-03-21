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
st.set_page_config(page_title="BMW Global Sales Analysis", page_icon="🚗", layout="wide")

# ──────────────────────────────────────────────
# Styles
# ──────────────────────────────────────────────
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');

    /* Global Styles */
    [data-testid="stAppViewContainer"], .main { background-color: #f8fafc; font-family: 'Inter', sans-serif; }
    [data-testid="stSidebar"] { background-color: #ffffff; }
    [data-testid="stHeader"] { background-color: transparent; }

    h1, h2, h3, h4, h5, h6 { color: #0f172a !important; font-weight: 800; }
    p, span, li, div { color: #334155; }

    /* Floating card */
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

    /* Override Selectboxes */
    div[data-baseweb="select"] > div {
        background-color: #ffffff !important;
        color: #000000 !important;
        border: 1px solid #e2e8f0 !important;
        border-radius: 8px !important;
    }
    div[data-baseweb="select"] span { color: #000000 !important; }

    .stPlotlyChart { padding: 10px !important; }

    /* Metric styling */
    [data-testid="stMetricValue"] { color: #1d4ed8 !important; font-weight: 700; }
    [data-testid="stMetricLabel"] { color: #64748b !important; }
    [data-testid="stMetricDelta"] > div { font-weight: 600; }

    /* Tabs styling */
    .stTabs [data-baseweb="tab-list"] { background-color: transparent; }
    .stTabs [data-baseweb="tab"] { color: #64748b; font-weight: 600; }
    .stTabs [aria-selected="true"] { color: #1d4ed8 !important; border-bottom-color: #1d4ed8 !important; }

    .sidebar .sidebar-content { background-image: none; }

    /* Hero banner */
    .hero-banner {
        background: linear-gradient(135deg, #1e3a5f 0%, #1d4ed8 50%, #3b82f6 100%);
        color: #ffffff !important;
        border-radius: 16px;
        padding: 2rem 2.5rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 8px 24px rgba(29, 78, 216, 0.25);
    }
    .hero-banner h1, .hero-banner h2, .hero-banner p, .hero-banner span {
        color: #ffffff !important;
    }
    .hero-banner .subtitle {
        font-size: 1.05rem;
        opacity: 0.9;
        margin-top: 0.3rem;
    }

    /* Insight card */
    .insight-card {
        background: linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%);
        border: 1px solid #bfdbfe;
        border-radius: 14px;
        padding: 1.2rem 1.5rem;
        margin-bottom: 1rem;
        line-height: 1.7;
    }
    .insight-card b { color: #1e40af; }
    </style>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────────
# Color Palette
# ──────────────────────────────────────────────
BMW_COLORS = ["#1d4ed8", "#3b82f6", "#60a5fa", "#93c5fd", "#0ea5e9", "#06b6d4", "#14b8a6", "#6366f1"]
REGION_COLORS = {"Europe": "#1d4ed8", "China": "#dc2626", "USA": "#059669", "RestOfWorld": "#f59e0b"}
MODEL_COLORS = {
    "3 Series": "#1d4ed8", "5 Series": "#7c3aed", "X3": "#059669",
    "X5": "#dc2626", "X7": "#f59e0b", "i4": "#0ea5e9",
    "iX": "#ec4899", "MINI": "#6b7280"
}

MONTH_MAP = {1: "Jan", 2: "Feb", 3: "Mar", 4: "Apr", 5: "May", 6: "Jun",
             7: "Jul", 8: "Aug", 9: "Sep", 10: "Oct", 11: "Nov", 12: "Dec"}

# ──────────────────────────────────────────────
# Data Loading
# ──────────────────────────────────────────────
@st.cache_data
def load_data():
    con = duckdb.connect(str(ROOT / "data" / "portfolio.duckdb"), read_only=True)
    df = con.execute("SELECT * FROM src_bmw_global_sales").df()
    con.close()
    
    df["Month_Name"] = df["Month"].map(MONTH_MAP)
    df["Date"] = pd.to_datetime(df["Year"].astype(str) + "-" + df["Month"].astype(str) + "-01")
    df["Revenue_EUR_B"] = df["Revenue_EUR"] / 1e9
    return df

df = load_data()

# ──────────────────────────────────────────────
# DuckDB for fast analytics (Reusing existing in-memory for dashboard logic)
# ──────────────────────────────────────────────
@st.cache_resource
def init_db():
    con = duckdb.connect(":memory:")
    return con

con = init_db()
con.register("sales", df)

# ──────────────────────────────────────────────
# Sidebar Filters
# ──────────────────────────────────────────────
with st.sidebar:
    st.title("🚗 BMW Sales Filters")
    st.markdown("---")

    year_range = st.slider(
        "Year Range",
        min_value=int(df["Year"].min()),
        max_value=int(df["Year"].max()),
        value=(int(df["Year"].min()), int(df["Year"].max()))
    )

    selected_regions = st.multiselect(
        "Region", options=sorted(df["Region"].unique()), default=sorted(df["Region"].unique())
    )

    selected_models = st.multiselect(
        "Model", options=sorted(df["Model"].unique()), default=sorted(df["Model"].unique())
    )

    st.markdown("---")
    st.caption("Dataset: BMW Global Sales 2018–2025")

# Apply filters
filtered_df = df[
    (df["Year"] >= year_range[0]) &
    (df["Year"] <= year_range[1]) &
    (df["Region"].isin(selected_regions)) &
    (df["Model"].isin(selected_models))
]

# ──────────────────────────────────────────────
# Hero Banner
# ──────────────────────────────────────────────
st.markdown("""
<div class='hero-banner'>
    <h1 style='margin:0; font-size: 2rem;'>🚗 BMW Global Sales Dashboard</h1>
    <p class='subtitle'>Comprehensive analysis of BMW automotive sales performance across regions, models, and market dynamics (2018–2025)</p>
</div>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────────
# KPI Row
# ──────────────────────────────────────────────
if not filtered_df.empty:
    total_units = filtered_df["Units_Sold"].sum()
    total_revenue = filtered_df["Revenue_EUR"].sum()
    avg_price = filtered_df["Avg_Price_EUR"].mean()
    avg_bev = filtered_df["BEV_Share"].mean() * 100
    num_records = len(filtered_df)

    # Calculate YoY growth for latest full year in selection
    latest_year = filtered_df["Year"].max()
    prev_year = latest_year - 1
    if prev_year >= year_range[0]:
        latest_rev = filtered_df[filtered_df["Year"] == latest_year]["Revenue_EUR"].sum()
        prev_rev = filtered_df[filtered_df["Year"] == prev_year]["Revenue_EUR"].sum()
        rev_growth = ((latest_rev - prev_rev) / prev_rev * 100) if prev_rev > 0 else 0
    else:
        rev_growth = None

    kpi_cols = st.columns(5)
    with kpi_cols[0]:
        st.metric("Total Units Sold", f"{total_units:,.0f}")
    with kpi_cols[1]:
        st.metric("Total Revenue", f"€{total_revenue/1e9:.2f}B")
    with kpi_cols[2]:
        delta_str = f"{rev_growth:+.1f}%" if rev_growth is not None else None
        st.metric("Revenue (Latest YoY)", f"€{latest_rev/1e9:.2f}B" if rev_growth is not None else "N/A", delta=delta_str)
    with kpi_cols[3]:
        st.metric("Avg Price (EUR)", f"€{avg_price:,.0f}")
    with kpi_cols[4]:
        st.metric("Avg BEV Share", f"{avg_bev:.1f}%")

    st.divider()

    # ──────────────────────────────────────────────
    # Tabs
    # ──────────────────────────────────────────────
    tab_overview, tab_regional, tab_models, tab_ev, tab_data = st.tabs([
        "📈 Sales Overview",
        "🌍 Regional Analysis",
        "🚘 Model Deep-Dive",
        "⚡ EV & Market Trends",
        "📋 Raw Data"
    ])

    def apply_theme(fig, height=450):
        fig.update_layout(
            template="plotly_white",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=30, r=30, t=60, b=30),
            height=height,
            font=dict(family="Inter, sans-serif", size=12),
            legend=dict(
                bgcolor="rgba(255,255,255,0.8)",
                bordercolor="#e2e8f0",
                borderwidth=1,
                font=dict(size=11)
            )
        )
        return fig

    # ──────────────────────────────────────────
    # TAB 1: Sales Overview
    # ──────────────────────────────────────────
    with tab_overview:
        st.subheader("Annual Sales & Revenue Trend")

        yearly = con.execute("""
            SELECT Year,
                   SUM(Units_Sold) as total_units,
                   SUM(Revenue_EUR) / 1e9 as revenue_b,
                   AVG(Avg_Price_EUR) as avg_price
            FROM sales
            WHERE Year BETWEEN ? AND ?
              AND Region IN (SELECT UNNEST(?::VARCHAR[]))
              AND Model IN (SELECT UNNEST(?::VARCHAR[]))
            GROUP BY Year ORDER BY Year
        """, [year_range[0], year_range[1], selected_regions, selected_models]).df()

        col1, col2 = st.columns(2)

        with col1:
            fig_units = go.Figure()
            fig_units.add_trace(go.Bar(
                x=yearly["Year"], y=yearly["total_units"],
                marker_color="#1d4ed8",
                marker_line_color="#1e40af",
                marker_line_width=1,
                name="Units Sold",
                text=yearly["total_units"].apply(lambda x: f"{x/1e6:.2f}M"),
                textposition="outside"
            ))
            fig_units.update_layout(title="Annual Units Sold", yaxis_title="Units Sold")
            apply_theme(fig_units)
            st.plotly_chart(fig_units, use_container_width=True)

        with col2:
            fig_rev = go.Figure()
            fig_rev.add_trace(go.Bar(
                x=yearly["Year"], y=yearly["revenue_b"],
                marker_color="#3b82f6",
                marker_line_color="#1d4ed8",
                marker_line_width=1,
                name="Revenue (€B)",
                text=yearly["revenue_b"].apply(lambda x: f"€{x:.1f}B"),
                textposition="outside"
            ))
            fig_rev.update_layout(title="Annual Revenue (EUR Billions)", yaxis_title="Revenue (€B)")
            apply_theme(fig_rev)
            st.plotly_chart(fig_rev, use_container_width=True)

        st.divider()
        st.subheader("Monthly Sales Trend Over Time")

        monthly = con.execute("""
            SELECT Date, SUM(Units_Sold) as total_units, SUM(Revenue_EUR)/1e9 as revenue_b
            FROM sales
            WHERE Year BETWEEN ? AND ?
              AND Region IN (SELECT UNNEST(?::VARCHAR[]))
              AND Model IN (SELECT UNNEST(?::VARCHAR[]))
            GROUP BY Date ORDER BY Date
        """, [year_range[0], year_range[1], selected_regions, selected_models]).df()

        fig_monthly = go.Figure()
        fig_monthly.add_trace(go.Scatter(
            x=monthly["Date"], y=monthly["total_units"],
            mode="lines+markers",
            line=dict(color="#1d4ed8", width=2),
            marker=dict(size=4, color="#3b82f6"),
            name="Monthly Units",
            fill="tozeroy",
            fillcolor="rgba(29,78,216,0.08)"
        ))
        fig_monthly.update_layout(title="Monthly Units Sold", yaxis_title="Units Sold", xaxis_title="")
        apply_theme(fig_monthly, 400)
        st.plotly_chart(fig_monthly, use_container_width=True)

    # ──────────────────────────────────────────
    # TAB 2: Regional Analysis
    # ──────────────────────────────────────────
    with tab_regional:
        st.subheader("Sales by Region")

        col_r1, col_r2 = st.columns(2)

        region_totals = con.execute("""
            SELECT Region,
                   SUM(Units_Sold) as total_units,
                   SUM(Revenue_EUR)/1e9 as revenue_b
            FROM sales
            WHERE Year BETWEEN ? AND ?
              AND Region IN (SELECT UNNEST(?::VARCHAR[]))
              AND Model IN (SELECT UNNEST(?::VARCHAR[]))
            GROUP BY Region ORDER BY total_units DESC
        """, [year_range[0], year_range[1], selected_regions, selected_models]).df()

        with col_r1:
            colors = [REGION_COLORS.get(r, "#6b7280") for r in region_totals["Region"]]
            fig_pie = go.Figure(data=[go.Pie(
                labels=region_totals["Region"],
                values=region_totals["total_units"],
                hole=0.45,
                marker=dict(colors=colors, line=dict(color="#ffffff", width=2)),
                textinfo="label+percent",
                textfont=dict(size=13)
            )])
            fig_pie.update_layout(title="Units Sold Share by Region")
            apply_theme(fig_pie)
            st.plotly_chart(fig_pie, use_container_width=True)

        with col_r2:
            fig_rev_region = px.bar(
                region_totals, x="Region", y="revenue_b",
                color="Region",
                color_discrete_map=REGION_COLORS,
                title="Total Revenue by Region (€B)",
                text=region_totals["revenue_b"].apply(lambda x: f"€{x:.1f}B")
            )
            fig_rev_region.update_layout(showlegend=False)
            apply_theme(fig_rev_region)
            st.plotly_chart(fig_rev_region, use_container_width=True)

        st.divider()
        st.subheader("Regional Trend Over Years")

        region_yearly = con.execute("""
            SELECT Year, Region, SUM(Units_Sold) as total_units
            FROM sales
            WHERE Year BETWEEN ? AND ?
              AND Region IN (SELECT UNNEST(?::VARCHAR[]))
              AND Model IN (SELECT UNNEST(?::VARCHAR[]))
            GROUP BY Year, Region ORDER BY Year, Region
        """, [year_range[0], year_range[1], selected_regions, selected_models]).df()

        fig_region_trend = px.line(
            region_yearly, x="Year", y="total_units", color="Region",
            color_discrete_map=REGION_COLORS,
            title="Annual Units Sold by Region",
            markers=True
        )
        fig_region_trend.update_layout(yaxis_title="Units Sold", xaxis_title="")
        apply_theme(fig_region_trend, 420)
        st.plotly_chart(fig_region_trend, use_container_width=True)

        st.divider()
        st.subheader("Average Price by Region")
        avg_price_region = con.execute("""
            SELECT Region, Year, AVG(Avg_Price_EUR) as avg_price
            FROM sales
            WHERE Year BETWEEN ? AND ?
              AND Region IN (SELECT UNNEST(?::VARCHAR[]))
              AND Model IN (SELECT UNNEST(?::VARCHAR[]))
            GROUP BY Region, Year ORDER BY Year
        """, [year_range[0], year_range[1], selected_regions, selected_models]).df()

        fig_price_region = px.line(
            avg_price_region, x="Year", y="avg_price", color="Region",
            color_discrete_map=REGION_COLORS,
            title="Average Vehicle Price by Region Over Time",
            markers=True
        )
        fig_price_region.update_layout(yaxis_title="Average Price (EUR)", xaxis_title="")
        apply_theme(fig_price_region, 400)
        st.plotly_chart(fig_price_region, use_container_width=True)

    # ──────────────────────────────────────────
    # TAB 3: Model Deep-Dive
    # ──────────────────────────────────────────
    with tab_models:
        st.subheader("Model Performance Comparison")

        model_totals = con.execute("""
            SELECT Model,
                   SUM(Units_Sold) as total_units,
                   SUM(Revenue_EUR)/1e9 as revenue_b,
                   AVG(Avg_Price_EUR) as avg_price
            FROM sales
            WHERE Year BETWEEN ? AND ?
              AND Region IN (SELECT UNNEST(?::VARCHAR[]))
              AND Model IN (SELECT UNNEST(?::VARCHAR[]))
            GROUP BY Model ORDER BY total_units DESC
        """, [year_range[0], year_range[1], selected_regions, selected_models]).df()

        col_m1, col_m2 = st.columns(2)

        with col_m1:
            colors = [MODEL_COLORS.get(m, "#6b7280") for m in model_totals["Model"]]
            fig_model_bar = go.Figure(data=[go.Bar(
                x=model_totals["Model"], y=model_totals["total_units"],
                marker_color=colors,
                text=model_totals["total_units"].apply(lambda x: f"{x/1e6:.2f}M"),
                textposition="outside"
            )])
            fig_model_bar.update_layout(title="Total Units Sold by Model", yaxis_title="Units Sold")
            apply_theme(fig_model_bar)
            st.plotly_chart(fig_model_bar, use_container_width=True)

        with col_m2:
            colors_rev = [MODEL_COLORS.get(m, "#6b7280") for m in model_totals["Model"]]
            fig_model_rev = go.Figure(data=[go.Bar(
                x=model_totals["Model"], y=model_totals["revenue_b"],
                marker_color=colors_rev,
                text=model_totals["revenue_b"].apply(lambda x: f"€{x:.1f}B"),
                textposition="outside"
            )])
            fig_model_rev.update_layout(title="Total Revenue by Model (€B)", yaxis_title="Revenue (€B)")
            apply_theme(fig_model_rev)
            st.plotly_chart(fig_model_rev, use_container_width=True)

        st.divider()
        st.subheader("Model Sales Trend Over Years")

        model_yearly = con.execute("""
            SELECT Year, Model, SUM(Units_Sold) as total_units
            FROM sales
            WHERE Year BETWEEN ? AND ?
              AND Region IN (SELECT UNNEST(?::VARCHAR[]))
              AND Model IN (SELECT UNNEST(?::VARCHAR[]))
            GROUP BY Year, Model ORDER BY Year, Model
        """, [year_range[0], year_range[1], selected_regions, selected_models]).df()

        fig_model_trend = px.line(
            model_yearly, x="Year", y="total_units", color="Model",
            color_discrete_map=MODEL_COLORS,
            title="Annual Units Sold by Model",
            markers=True
        )
        fig_model_trend.update_layout(yaxis_title="Units Sold", xaxis_title="")
        apply_theme(fig_model_trend, 420)
        st.plotly_chart(fig_model_trend, use_container_width=True)

        st.divider()
        st.subheader("Model × Region Heatmap")

        heatmap_data = con.execute("""
            SELECT Model, Region, SUM(Units_Sold) as total_units
            FROM sales
            WHERE Year BETWEEN ? AND ?
              AND Region IN (SELECT UNNEST(?::VARCHAR[]))
              AND Model IN (SELECT UNNEST(?::VARCHAR[]))
            GROUP BY Model, Region
        """, [year_range[0], year_range[1], selected_regions, selected_models]).df()

        pivot = heatmap_data.pivot(index="Model", columns="Region", values="total_units").fillna(0)

        fig_heatmap = go.Figure(data=go.Heatmap(
            z=pivot.values,
            x=pivot.columns.tolist(),
            y=pivot.index.tolist(),
            colorscale=[[0, "#eff6ff"], [0.5, "#3b82f6"], [1, "#1e3a5f"]],
            text=[[f"{int(v):,}" for v in row] for row in pivot.values],
            texttemplate="%{text}",
            textfont=dict(size=11),
            hovertemplate="Model: %{y}<br>Region: %{x}<br>Units: %{text}<extra></extra>"
        ))
        fig_heatmap.update_layout(title="Units Sold: Model × Region", xaxis_title="Region", yaxis_title="Model")
        apply_theme(fig_heatmap, 420)
        st.plotly_chart(fig_heatmap, use_container_width=True)

    # ──────────────────────────────────────────
    # TAB 4: EV & Market Trends
    # ──────────────────────────────────────────
    with tab_ev:
        st.subheader("Electric Vehicle (BEV) Share Trend")

        bev_yearly = con.execute("""
            SELECT Year, AVG(BEV_Share)*100 as avg_bev
            FROM sales
            WHERE Year BETWEEN ? AND ?
              AND Region IN (SELECT UNNEST(?::VARCHAR[]))
              AND Model IN (SELECT UNNEST(?::VARCHAR[]))
            GROUP BY Year ORDER BY Year
        """, [year_range[0], year_range[1], selected_regions, selected_models]).df()

        col_e1, col_e2 = st.columns(2)

        with col_e1:
            fig_bev = go.Figure()
            fig_bev.add_trace(go.Scatter(
                x=bev_yearly["Year"], y=bev_yearly["avg_bev"],
                mode="lines+markers+text",
                line=dict(color="#0ea5e9", width=3),
                marker=dict(size=10, color="#0ea5e9", line=dict(color="#ffffff", width=2)),
                text=bev_yearly["avg_bev"].apply(lambda x: f"{x:.1f}%"),
                textposition="top center",
                fill="tozeroy",
                fillcolor="rgba(14,165,233,0.1)",
                name="BEV Share"
            ))
            fig_bev.update_layout(title="Average BEV Share Over Years", yaxis_title="BEV Share (%)")
            apply_theme(fig_bev)
            st.plotly_chart(fig_bev, use_container_width=True)

        with col_e2:
            bev_region = con.execute("""
                SELECT Region, Year, AVG(BEV_Share)*100 as avg_bev
                FROM sales
                WHERE Year BETWEEN ? AND ?
                  AND Region IN (SELECT UNNEST(?::VARCHAR[]))
                  AND Model IN (SELECT UNNEST(?::VARCHAR[]))
                GROUP BY Region, Year ORDER BY Year
            """, [year_range[0], year_range[1], selected_regions, selected_models]).df()

            fig_bev_region = px.line(
                bev_region, x="Year", y="avg_bev", color="Region",
                color_discrete_map=REGION_COLORS,
                title="BEV Share by Region Over Time",
                markers=True
            )
            fig_bev_region.update_layout(yaxis_title="BEV Share (%)")
            apply_theme(fig_bev_region)
            st.plotly_chart(fig_bev_region, use_container_width=True)

        st.divider()
        st.subheader("Macro-Economic Indicators")

        col_m1, col_m2 = st.columns(2)

        with col_m1:
            gdp_data = con.execute("""
                SELECT Year, Region, AVG(GDP_Growth) as avg_gdp
                FROM sales
                WHERE Year BETWEEN ? AND ?
                  AND Region IN (SELECT UNNEST(?::VARCHAR[]))
                  AND Model IN (SELECT UNNEST(?::VARCHAR[]))
                GROUP BY Year, Region ORDER BY Year
            """, [year_range[0], year_range[1], selected_regions, selected_models]).df()

            fig_gdp = px.line(
                gdp_data, x="Year", y="avg_gdp", color="Region",
                color_discrete_map=REGION_COLORS,
                title="GDP Growth by Region",
                markers=True
            )
            fig_gdp.update_layout(yaxis_title="GDP Growth (%)")
            apply_theme(fig_gdp)
            st.plotly_chart(fig_gdp, use_container_width=True)

        with col_m2:
            fuel_data = con.execute("""
                SELECT Year, Region, AVG(Fuel_Price_Index) as avg_fuel
                FROM sales
                WHERE Year BETWEEN ? AND ?
                  AND Region IN (SELECT UNNEST(?::VARCHAR[]))
                  AND Model IN (SELECT UNNEST(?::VARCHAR[]))
                GROUP BY Year, Region ORDER BY Year
            """, [year_range[0], year_range[1], selected_regions, selected_models]).df()

            fig_fuel = px.line(
                fuel_data, x="Year", y="avg_fuel", color="Region",
                color_discrete_map=REGION_COLORS,
                title="Fuel Price Index by Region",
                markers=True
            )
            fig_fuel.update_layout(yaxis_title="Fuel Price Index")
            apply_theme(fig_fuel)
            st.plotly_chart(fig_fuel, use_container_width=True)

        st.divider()
        st.subheader("Premium Share Trend")

        premium_data = con.execute("""
            SELECT Year, Region, AVG(Premium_Share)*100 as avg_premium
            FROM sales
            WHERE Year BETWEEN ? AND ?
              AND Region IN (SELECT UNNEST(?::VARCHAR[]))
              AND Model IN (SELECT UNNEST(?::VARCHAR[]))
            GROUP BY Year, Region ORDER BY Year
        """, [year_range[0], year_range[1], selected_regions, selected_models]).df()

        fig_premium = px.area(
            premium_data, x="Year", y="avg_premium", color="Region",
            color_discrete_map=REGION_COLORS,
            title="Average Premium Share by Region Over Time"
        )
        fig_premium.update_layout(yaxis_title="Premium Share (%)")
        apply_theme(fig_premium, 400)
        st.plotly_chart(fig_premium, use_container_width=True)

    # ──────────────────────────────────────────
    # TAB 5: Raw Data
    # ──────────────────────────────────────────
    with tab_data:
        st.subheader("Filtered Dataset")
        st.markdown(f"<div class='floating-card'>Showing <b>{len(filtered_df):,}</b> records matching your filter criteria.</div>", unsafe_allow_html=True)

        display_df = filtered_df[["Year", "Month_Name", "Region", "Model", "Units_Sold", "Avg_Price_EUR", "Revenue_EUR", "BEV_Share", "Premium_Share", "GDP_Growth", "Fuel_Price_Index"]].copy()
        display_df = display_df.rename(columns={"Month_Name": "Month"})
        display_df = display_df.sort_values(by=["Year", "Region", "Model"]).reset_index(drop=True)
        display_df.index += 1

        st.dataframe(display_df, use_container_width=True, height=500)

        # Download button
        csv = filtered_df.to_csv(index=False)
        st.download_button(
            label="📥 Download Filtered Data as CSV",
            data=csv,
            file_name="bmw_sales_filtered.csv",
            mime="text/csv"
        )

    # ──────────────────────────────────────────
    # Key Insights
    # ──────────────────────────────────────────
    st.divider()
    st.subheader("💡 Key Insights")

    insights = []

    # Top region
    top_region = filtered_df.groupby("Region")["Units_Sold"].sum().idxmax()
    top_region_units = filtered_df.groupby("Region")["Units_Sold"].sum().max()
    insights.append(f"🌍 <b>Top Market:</b> <b>{top_region}</b> leads with <b>{top_region_units:,.0f}</b> total units sold in the selected period.")

    # Top model
    top_model = filtered_df.groupby("Model")["Units_Sold"].sum().idxmax()
    top_model_units = filtered_df.groupby("Model")["Units_Sold"].sum().max()
    insights.append(f"🚘 <b>Best-Selling Model:</b> The <b>{top_model}</b> is the top seller with <b>{top_model_units:,.0f}</b> units.")

    # Revenue share of top model
    total_rev = filtered_df["Revenue_EUR"].sum()
    top_model_rev = filtered_df[filtered_df["Model"] == top_model]["Revenue_EUR"].sum()
    rev_share = top_model_rev / total_rev * 100 if total_rev > 0 else 0
    insights.append(f"💰 <b>Revenue Concentration:</b> The <b>{top_model}</b> accounts for <b>{rev_share:.1f}%</b> of total revenue.")

    # BEV trend
    bev_first = filtered_df[filtered_df["Year"] == filtered_df["Year"].min()]["BEV_Share"].mean() * 100
    bev_last = filtered_df[filtered_df["Year"] == filtered_df["Year"].max()]["BEV_Share"].mean() * 100
    bev_change = bev_last - bev_first
    direction = "increased" if bev_change > 0 else "decreased"
    insights.append(f"⚡ <b>EV Transition:</b> Average BEV share has {direction} from <b>{bev_first:.1f}%</b> to <b>{bev_last:.1f}%</b> ({bev_change:+.1f} pp).")

    # Most expensive model
    expensive_model = filtered_df.groupby("Model")["Avg_Price_EUR"].mean().idxmax()
    expensive_price = filtered_df.groupby("Model")["Avg_Price_EUR"].mean().max()
    insights.append(f"💎 <b>Premium Leader:</b> The <b>{expensive_model}</b> commands the highest average price at <b>€{expensive_price:,.0f}</b>.")

    insights_html = "<div class='insight-card'><ul style='line-height: 1.9; margin-bottom: 0; font-size: 1.02rem;'>"
    for insight in insights:
        insights_html += f"<li style='margin-bottom: 8px;'>{insight}</li>"
    insights_html += "</ul></div>"
    st.markdown(insights_html, unsafe_allow_html=True)

else:
    st.warning("⚠️ No data matches the selected filters. Please adjust the sidebar filters.")

# Footer
st.divider()
st.caption("© 2026 Idzharul Huda | Built with Streamlit, Plotly, and DuckDB")
