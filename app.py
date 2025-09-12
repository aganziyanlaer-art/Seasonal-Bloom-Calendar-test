import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Title
st.title("🌸 Seasonal Bloom Calendar with Color Filter")

# Load plant data
plants = pd.read_csv("plants.csv")

# Preview table to check if CSV loads correctly
st.subheader("Plant Data Preview")
st.write(plants.head())

# Sidebar filters
st.sidebar.header("Filter Options")

# Color filter
flower_colors = plants["Flower Color"].dropna().unique().tolist()
selected_color = st.sidebar.selectbox("Select Flower Color", ["All"] + flower_colors)

# Season filter
seasons = ["All", "Winter", "Spring", "Summer", "Autumn"]
selected_season = st.sidebar.selectbox("Select Blooming Season", seasons)

# Apply filters
filtered = plants.copy()

if selected_color != "All":
    filtered = filtered[filtered["Flower Color"].str.contains(selected_color, case=False, na=False)]

if selected_season != "All":
    filtered = filtered[filtered["Blooming Season"].str.contains(selected_season, case=False, na=False)]

# Display filtered results
st.subheader("Filtered Plant List")
st.dataframe(filtered)

# Bloom calendar chart
st.subheader("Blooming Season Overview")

if not filtered.empty:
    season_counts = filtered["Blooming Season"].value_counts()

    fig, ax = plt.subplots()
    season_counts.plot(kind="bar", ax=ax)
    ax.set_ylabel("Number of Plants")
    ax.set_xlabel("Season(s)")
    ax.set_title("Blooming Season Distribution")

    st.pyplot(fig)
else:
    st.warning("No plants match the selected filters.")
