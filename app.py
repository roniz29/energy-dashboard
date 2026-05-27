
import pandas as pd
import plotly.express as px
import streamlit as st

# ── Page config ────────────────────────────────────────────
st.set_page_config(
    page_title="Global Energy Transition 2000–2020",
    page_icon="⚡",
    layout="wide"
)

# ── Load data ──────────────────────────────────────────────
@st.cache_data
def load_data():
    df = pd.read_csv(r"C:\Users\mroni\OneDrive\Documents\Assessment3_Task2\data\global-data-on-sustainable-energy.csv")
    # Remove non-country aggregates
    remove = ["World", "Asia", "Europe", "Africa", "Americas",
              "North America", "South America", "European Union",
              "High-income countries", "Low-income countries",
              "Upper-middle-income countries", "Lower-middle-income countries"]
    df = df[~df["Entity"].isin(remove)]
    return df

df = load_data()

# ── Sidebar filters ────────────────────────────────────────
st.sidebar.title("⚡ Filters")
st.sidebar.markdown("---")

year_range = st.sidebar.slider(
    "Select Year Range",
    min_value=2000, max_value=2020,
    value=(2000, 2020), step=1
)

all_countries = sorted(df["Entity"].unique().tolist())
selected_countries = st.sidebar.multiselect(
    "Select Countries (for trend charts)",
    options=all_countries,
    default=["China", "United States", "India", "Germany", "Brazil"]
)

st.sidebar.markdown("---")
st.sidebar.markdown("**Dataset:** Global Sustainable Energy Indicators")
st.sidebar.markdown("**Source:** Our World in Data / UN Statistics")
st.sidebar.markdown("**Period:** 2000–2020")

# ── Filter data ────────────────────────────────────────────
df_filtered = df[(df["Year"] >= year_range[0]) & (df["Year"] <= year_range[1])]
df_countries = df_filtered[df_filtered["Entity"].isin(selected_countries)] if selected_countries else df_filtered

# ── Title ──────────────────────────────────────────────────
st.title("⚡ The Global Energy Transition: Progress, Gaps & Countries Left Behind")
st.markdown("*Exploring sustainable energy indicators across 173 countries from 2000 to 2020*")
st.markdown("---")

# ── KPI Row ────────────────────────────────────────────────
col1, col2, col3, col4 = st.columns(4)

latest = df[df["Year"] == 2020]
earliest = df[df["Year"] == 2000]

avg_access_2020 = latest["Access to electricity (% of population)"].mean()
avg_access_2000 = earliest["Access to electricity (% of population)"].mean()
avg_renew_2020 = latest["Renewable energy share in the total final energy consumption (%)"].mean()
countries_count = df["Entity"].nunique()

col1.metric("🌍 Countries Tracked", f"{countries_count}")
col2.metric("⚡ Avg Electricity Access (2020)", f"{avg_access_2020:.1f}%", f"+{avg_access_2020 - avg_access_2000:.1f}% since 2000")
col3.metric("🌱 Avg Renewable Share (2020)", f"{avg_renew_2020:.1f}%")
col4.metric("📅 Years Covered", "2000–2020")

st.markdown("---")

# ── ROW 1: Map + Line chart ────────────────────────────────
st.subheader("1. Where Are People Still Without Electricity?")
col_map, col_line = st.columns([1.5, 1])

with col_map:
    map_year = st.select_slider("Select year for map", options=list(range(2000, 2021)), value=2020)
    df_map = df[df["Year"] == map_year].dropna(subset=["Access to electricity (% of population)"])
    fig_map = px.choropleth(
        df_map,
        locations="Entity",
        locationmode="country names",
        color="Access to electricity (% of population)",
        color_continuous_scale=["#d73027", "#fee08b", "#1a9850"],
        range_color=[0, 100],
        title=f"Access to Electricity by Country ({map_year})",
        labels={"Access to electricity (% of population)": "Access (%)"},
    )
    fig_map.update_layout(
        margin=dict(l=0, r=0, t=40, b=0),
        coloraxis_colorbar=dict(title="Access (%)"),
        height=380
    )
    st.plotly_chart(fig_map, use_container_width=True)

with col_line:
    st.markdown("#### Global Avg Electricity Access Over Time")
    df_global = df.groupby("Year")["Access to electricity (% of population)"].mean().reset_index()
    df_global.columns = ["Year", "Avg Access (%)"]
    fig_access = px.line(
        df_global, x="Year", y="Avg Access (%)",
        title="Global Average Electricity Access (2000–2020)",
        markers=True,
        color_discrete_sequence=["#1a9850"]
    )
    fig_access.update_layout(height=350, margin=dict(l=0, r=0, t=40, b=0))
    fig_access.add_annotation(
        x=2020, y=df_global[df_global["Year"]==2020]["Avg Access (%)"].values[0],
        text="85% in 2020", showarrow=True, arrowhead=2,
        font=dict(size=11, color="green")
    )
    st.plotly_chart(fig_access, use_container_width=True)

st.markdown("---")

# ── ROW 2: Fossil vs Renewables + Scatter ─────────────────
st.subheader("2. Is the World Actually Transitioning to Clean Energy?")
col_trend, col_scatter = st.columns(2)

with col_trend:
    df_energy = df.groupby("Year")[
        ["Electricity from fossil fuels (TWh)", "Electricity from renewables (TWh)"]
    ].sum().reset_index()
    fig_trend = px.line(
        df_energy, x="Year",
        y=["Electricity from fossil fuels (TWh)", "Electricity from renewables (TWh)"],
        title="Global Fossil Fuels vs Renewables Electricity Generation (TWh)",
        color_discrete_map={
            "Electricity from fossil fuels (TWh)": "#d73027",
            "Electricity from renewables (TWh)": "#1a9850"
        },
        markers=True
    )
    fig_trend.update_layout(
        height=380, margin=dict(l=0, r=0, t=40, b=0),
        legend=dict(title="Source", orientation="h", y=-0.2)
    )
    fig_trend.add_annotation(
        x=2020, y=df_energy[df_energy["Year"]==2020]["Electricity from fossil fuels (TWh)"].values[0],
        text="Fossils still<br>dominate", showarrow=True,
        arrowhead=2, font=dict(size=10, color="#d73027")
    )
    st.plotly_chart(fig_trend, use_container_width=True)

with col_scatter:
    df_scatter = df[df["Year"] == year_range[1]].dropna(
        subset=["gdp_per_capita",
                "Renewable energy share in the total final energy consumption (%)"]
    )
    fig_scatter = px.scatter(
        df_scatter,
        x="gdp_per_capita",
        y="Renewable energy share in the total final energy consumption (%)",
        hover_name="Entity",
        size="Primary energy consumption per capita (kWh/person)",
        color="Renewable energy share in the total final energy consumption (%)",
        color_continuous_scale=["#d73027", "#fee08b", "#1a9850"],
        title=f"Renewable Share vs GDP per Capita ({year_range[1]})",
        labels={
            "gdp_per_capita": "GDP per Capita (USD)",
            "Renewable energy share in the total final energy consumption (%)": "Renewable Share (%)"
        }
    )
    fig_scatter.update_layout(height=380, margin=dict(l=0, r=0, t=40, b=0))
    fig_scatter.add_annotation(
        x=5000, y=85,
        text="Poor countries lead<br>in renewables — but<br>mostly biomass, not solar",
        showarrow=False,
        font=dict(size=10, color="#333"),
        bgcolor="#fff3cd", bordercolor="#e6a817", borderwidth=1
    )
    st.plotly_chart(fig_scatter, use_container_width=True)

st.markdown("---")

# ── ROW 3: Top CO2 emitters + Country trends ──────────────
st.subheader("3. Who Emits the Most — and Are They Changing?")
col_bar, col_multi = st.columns(2)

with col_bar:
    co2_year = min(year_range[1], 2019)
    df_co2 = df[df["Year"] == co2_year].dropna(
        subset=["Value_co2_emissions_kt_by_country"]
    )
    df_co2 = df_co2[df_co2["Value_co2_emissions_kt_by_country"] > 0]
    df_co2 = df_co2.nlargest(10, "Value_co2_emissions_kt_by_country").copy()
    df_co2["CO2_Mt"] = df_co2["Value_co2_emissions_kt_by_country"] / 1000
    fig_co2 = px.bar(
        df_co2,
        x="CO2_Mt",
        y="Entity",
        orientation="h",
        title=f"Top 10 CO₂ Emitters ({co2_year})",
        labels={"CO2_Mt": "CO₂ Emissions (Mt)", "Entity": "Country"},
        color="CO2_Mt",
        color_continuous_scale=["#fee08b", "#d73027"]
    )
    fig_co2.update_layout(
        height=380, margin=dict(l=0, r=0, t=40, b=0),
        yaxis=dict(autorange="reversed"),
        showlegend=False
    )
    st.plotly_chart(fig_co2, use_container_width=True)

with col_multi:
    if selected_countries:
        df_multi = df_countries.dropna(subset=["Renewable energy share in the total final energy consumption (%)"])
        fig_multi = px.line(
            df_multi,
            x="Year",
            y="Renewable energy share in the total final energy consumption (%)",
            color="Entity",
            title="Renewable Energy Share Over Time (Selected Countries)",
            markers=True,
            labels={"Renewable energy share in the total final energy consumption (%)": "Renewable Share (%)"}
        )
        fig_multi.update_layout(
            height=380, margin=dict(l=0, r=0, t=40, b=0),
            legend=dict(title="Country", orientation="h", y=-0.25)
        )
        st.plotly_chart(fig_multi, use_container_width=True)
    else:
        st.info("Please select at least one country in the sidebar to see trends.")

st.markdown("---")

# ── ROW 4: Low carbon electricity bar ─────────────────────
st.subheader("4. Which Regions Lead in Low-Carbon Electricity?")

df_lowcarbon = df[df["Year"] == year_range[1]].dropna(
    subset=["Low-carbon electricity (% electricity)"]
).nlargest(15, "Low-carbon electricity (% electricity)")

fig_lowcarbon = px.bar(
    df_lowcarbon,
    x="Entity",
    y="Low-carbon electricity (% electricity)",
    title=f"Top 15 Countries by Low-Carbon Electricity Share ({year_range[1]})",
    labels={"Low-carbon electricity (% electricity)": "Low-Carbon Electricity (%)", "Entity": "Country"},
    color="Low-carbon electricity (% electricity)",
    color_continuous_scale=["#fee08b", "#1a9850"]
)
fig_lowcarbon.update_layout(
    height=380, margin=dict(l=0, r=0, t=40, b=0),
    xaxis_tickangle=-35
)
st.plotly_chart(fig_lowcarbon, use_container_width=True)

st.markdown("---")
st.caption("Data source: Our World in Data — Global Sustainable Energy Indicators (2000–2020)")
