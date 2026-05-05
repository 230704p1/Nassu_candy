import streamlit as st
import pandas as pd
import plotly.express as px

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(layout="wide")

# =========================
# HEADER
# =========================
st.markdown("""
<h1 style='font-size:48px; font-weight:800; color:#F5F5F5;'>
Nassau Candy Route Intelligence Dashboard
</h1>
<p style='color:#A0A0A0; font-size:22px;'>
Advanced analytics platform for optimizing logistics, improving delivery efficiency, and maximizing profitability.
</p>
""", unsafe_allow_html=True)

# =========================
# LOAD DATA
# =========================
df = pd.read_csv("processed_data.csv")
df['Ship Mode'] = df['Ship Mode'].str.strip().str.title()

# =========================
# SIDEBAR (CLEAN)
# =========================
st.sidebar.header("Control Panel")

region = st.sidebar.multiselect(
    "Region",
    df["Region"].unique(),
    default=df["Region"].unique()
)

ship_mode = st.sidebar.multiselect(
    "Ship Mode",
    df["Ship Mode"].unique(),
    default=df["Ship Mode"].unique()
)

product = st.sidebar.multiselect(
    "Product",
    df["Product Name"].unique(),
    default=df["Product Name"].unique()
)

shipping_range = st.sidebar.slider(
    "Shipping Time (Days)",
    int(df["shipping_time"].min()),
    int(df["shipping_time"].max()),
    (1, 7)
)

# =========================
# FILTER DATA
# =========================
filtered_df = df[
    (df["Region"].isin(region)) &
    (df["Ship Mode"].isin(ship_mode)) &
    (df["Product Name"].isin(product)) &
    (df["shipping_time"].between(shipping_range[0], shipping_range[1]))
].copy()

if filtered_df.empty:
    st.warning("⚠️ No data found!")
    st.stop()

# ------------------------------- 
#  KPI CARDS 
# ------------------------------- 

# REQUIRED VARIABLES
filtered_df['Late'] = filtered_df['shipping_time'] > 5
late_orders = filtered_df['Late'].sum()
risk_profit = filtered_df[filtered_df['Late']]['Gross Profit'].sum()

st.markdown(""" 
<style> 
.card {
    background: linear-gradient(135deg, #1f2937, #111827); 
    padding: 20px; 
    border-radius: 15px; 
    box-shadow: 0 4px 20px rgba(0,0,0,0.5); 
    text-align: left; 
    transition: 0.3s; 
    margin-bottom:20px; 
    border:2px solid white; 
} 
.card:hover { 
    transform: scale(1.05); 
} 
.card-title { 
    font-size: 20px; 
    color: white; 
    font-weight: bold; 
} 
.card-value { 
    font-size: 30px;
    font-weight: bold; 
    color: white;
} 
</style> 
""", unsafe_allow_html=True) 

col1, col2, col3, col4, col5, col6 = st.columns(6) 

col1.markdown(f"""
<div class='card'>
<div class='card-title'>Sales</div>
<div class='card-value'>${filtered_df['Sales'].sum():,.0f}</div>
</div>
""", unsafe_allow_html=True)

col2.markdown(f"""
<div class='card'>
<div class='card-title'>Profit</div>
<div class='card-value'>${filtered_df['Gross Profit'].sum():,.0f}</div>
</div>
""", unsafe_allow_html=True)

col3.markdown(f"""
<div class='card'>
<div class='card-title'>Orders</div>
<div class='card-value'>{filtered_df.shape[0]}</div>
</div>
""", unsafe_allow_html=True)

col4.markdown(f"""
<div class='card'>
<div class='card-title'>Avg Time</div>
<div class='card-value'>{filtered_df['shipping_time'].mean():.1f} d</div>
</div>
""", unsafe_allow_html=True)

col5.markdown(f"""
<div class='card'>
<div class='card-title'>Late Orders</div>
<div class='card-value'>{late_orders}</div>
</div>
""", unsafe_allow_html=True)

col6.markdown(f"""
<div class='card'>
<div class='card-title'>Risk Impact</div>
<div class='card-value'>${risk_profit:,.0f}</div>
</div>
""", unsafe_allow_html=True)
# =========================
# TREND CHART
# =========================
st.subheader("📈 Revenue vs Profit Trend")

trend = filtered_df.copy()
trend['Order Date'] = pd.to_datetime(trend['Order Date'], errors='coerce')

trend = trend.groupby(
    trend['Order Date'].dt.to_period("M")
)[["Sales", "Gross Profit"]].sum().reset_index()

trend['Order Date'] = trend['Order Date'].astype(str)

fig = px.line(
    trend,
    x="Order Date",
    y=["Sales", "Gross Profit"],
    template="plotly_dark",
    color_discrete_sequence=["#00E5FF", "#FF4081"]
)

# ✅ ANNOTATION (highest sales point)
max_row = trend.loc[trend["Sales"].idxmax()]
fig.add_annotation(
    x=max_row["Order Date"],
    y=max_row["Sales"],
    text="Peak Sales",
    showarrow=True,
    arrowhead=2
)
st.plotly_chart(fig, use_container_width=True)


# ✅ HOVER HINT
# st.caption("💡 Hover over the chart to view detailed values")

# ✅ INSIGHT
st.info("Sales and profit show an overall trend, with peak performance in highlighted period.")
# =========================
# TABS
# =========================
st.subheader("📊 Analysis Section")

tab1, tab2, tab3, tab4 = st.tabs([
    "📍 Region",
    "📦 Product",
    "🚚 Shipping",
    "🗺 Route"
])

# -------------------------
# TAB 1 - PIE
# -------------------------
# with tab1:
#     region_sales = filtered_df.groupby("Region")["Sales"].sum().reset_index()

#     fig = px.pie(
#         region_sales,
#         names="Region",
#         values="Sales",
#         hole=0.4,
#         template="plotly_dark",
#         color_discrete_sequence=px.colors.sequential.RdBu
#     )
#     fig.update_traces(
#         textfont=dict(color="white", size=14),
#         textinfo="percent+label"   # show label + %
#     )

#         # ✅ LEGEND WHITE
#     fig.update_layout(
#         legend=dict(font=dict(color="white"))
#     )

    
#     st.plotly_chart(fig, use_container_width=True)


with tab1:
    region_sales = filtered_df.groupby("Region")["Sales"].sum().reset_index()
    fig = px.pie(region_sales, names="Region", values="Sales", hole=0.4)

    max_region = region_sales.loc[region_sales["Sales"].idxmax()]
    fig.add_annotation(text=f"Top Region: {max_region['Region']}", x=0.5, y=1.1, showarrow=False)


    fig = px.pie(
    region_sales,
    names="Region",
    values="Sales",
    hole=0.4,
    template="plotly_dark",
    color_discrete_sequence=px.colors.sequential.RdBu
)
    
    fig.update_traces( 
        textfont=dict(color="white", size=14), 
        textinfo="percent"  )
    st.plotly_chart(fig, use_container_width=True)
    # st.caption("💡 Hover to see percentage")
    st.info("Top region contributes highest revenue.")

# -------------------------
# TAB 2 - PRODUCT BAR
# -------------------------
with tab2:
    product_sales = (
        filtered_df.groupby("Product Name")["Sales"]
        .sum().reset_index()
        .sort_values(by="Sales", ascending=False)
        .head(10)
    )

    fig = px.bar(
        product_sales,
        x="Sales",
        y="Product Name",
        orientation='h',
        template="plotly_dark",
        color="Sales",
        color_continuous_scale="Viridis"
    )

    top_product = product_sales.iloc[0]
    fig.add_annotation(x=top_product["Sales"], y=top_product["Product Name"],
                       text="Top Product", showarrow=True)
    st.plotly_chart(fig, use_container_width=True)
    # st.caption("💡 Hover to see values")
    st.info("Top products dominate revenue.")



# -------------------------
# TAB 3 - HISTOGRAM
# -------------------------
with tab3:
    fig = px.histogram(
        filtered_df,
        x="shipping_time",
        nbins=7,
        template="plotly_dark",
        color_discrete_sequence=["#00E5FF"]
    )

    fig.add_annotation(x=6, y=10, text="Delay Zone", showarrow=True)

    st.plotly_chart(fig, use_container_width=True)
    # st.caption("💡 Hover to analyze distribution")
    st.info("Delays above 5 days indicate inefficiency.")
# -------------------------
# TAB 4 - MAP (FIXED)
# -------------------------
with tab4:

    usa_states = {
        "Alabama":"AL","Arizona":"AZ","Arkansas":"AR","California":"CA",
        "Colorado":"CO","Connecticut":"CT","Delaware":"DE","Florida":"FL",
        "Georgia":"GA","Illinois":"IL","Indiana":"IN","Iowa":"IA",
        "Kansas":"KS","Kentucky":"KY","Louisiana":"LA","Maine":"ME",
        "Maryland":"MD","Massachusetts":"MA","Michigan":"MI","Minnesota":"MN",
        "Mississippi":"MS","Missouri":"MO","Montana":"MT","Nebraska":"NE",
        "Nevada":"NV","New Hampshire":"NH","New Jersey":"NJ","New Mexico":"NM",
        "New York":"NY","North Carolina":"NC","North Dakota":"ND","Ohio":"OH",
        "Oklahoma":"OK","Oregon":"OR","Pennsylvania":"PA","Rhode Island":"RI",
        "South Carolina":"SC","South Dakota":"SD","Tennessee":"TN","Texas":"TX",
        "Utah":"UT","Vermont":"VT","Virginia":"VA","Washington":"WA",
        "West Virginia":"WV","Wisconsin":"WI","Wyoming":"WY","District of Columbia":"DC"
    }

    map_df = filtered_df.copy()
    map_df["StateCode"] = map_df["State/Province"].map(usa_states)

    map_df = map_df.dropna(subset=["StateCode"])

    state_avg = map_df.groupby("StateCode")["shipping_time"].mean().reset_index()

    fig = px.choropleth(
        state_avg,
        locations="StateCode",
        locationmode="USA-states",
        color="shipping_time",
        scope="usa",
        template="plotly_dark",
        color_continuous_scale="Turbo"
    )


    fig.update_layout(
    geo=dict(
        bgcolor="rgba(0,0,0,0)",   # transparent background
        lakecolor="white",
        landcolor="lightgray"

    )
)
    
    fig.update_layout(
        height=600
    )

    fig.add_annotation(text="Darker = slower delivery", x=0.5, y=0, showarrow=False)

    fig.update_traces(
        hovertemplate="State: %{location}<br>Shipping Time: %{z} days"
    )

    st.plotly_chart(fig, use_container_width=True)
    # st.caption("💡 Hover over map")
    st.info("Some states show higher delays.")
# =========================
# FACTORY SIMULATOR
# =========================
st.subheader("🏭 Factory Optimization Simulator")

factory = st.selectbox("Factory", ["A","B","C"])
effect = {"A":1,"B":2,"C":3}

# effect = {"Factory A": 1, "Factory B": 2, "Factory C": 3}

filtered_df['optimized_time'] = (filtered_df['shipping_time'] - effect[factory]).clip(lower=1)

current = filtered_df['shipping_time'].mean()
optimized = filtered_df['optimized_time'].mean()

compare_df = pd.DataFrame({
    "Scenario":["Current","Optimized"],
    "Avg Time":[current, optimized]
})

fig = px.bar(compare_df, x="Scenario", y="Avg Time")

fig.add_annotation(x="Optimized", y=optimized,
                   text="Improved", showarrow=True)

st.plotly_chart(fig)
# st.caption("💡 Compare performance")
st.info("Optimization reduces delivery time.")


# # Chart
# compare_df = pd.DataFrame({
#     "Scenario": ["Current", "Optimized"],
#     "Avg Time": [current, optimized]
# })

# fig = px.bar(
#     compare_df,
#     x="Scenario",
#     y="Avg Time",
#     template="plotly_dark",
#     color="Scenario",
#     color_discrete_sequence=["#00E5FF", "#FF4081"]
# )

# st.plotly_chart(fig, use_container_width=True)



# -------------------------------
# TABLE
# -------------------------------
st.subheader("📋 Data Preview")
st.dataframe(filtered_df)
