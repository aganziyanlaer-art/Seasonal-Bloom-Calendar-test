import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.title("🌸 Seasonal Bloom Calendar with Color Filter")

# Load plant CSV (make sure this file is in your GitHub repo / Streamlit cloud project)
plants = pd.read_csv("plants.csv")

# Sidebar filter
flower_colors = plants["Flower Color"].unique().tolist()
selected_colors = st.sidebar.multiselect("Filter by Flower Color:", flower_colors, default=flower_colors)

# Filter dataset by color
filtered_plants = plants[plants["Flower Color"].isin(selected_colors)]

# Map seasons to months
season_to_months = {
    "Summer": [12, 1, 2],
    "Autumn": [3, 4, 5],
    "Winter": [6, 7, 8],
    "Spring": [9, 10, 11],
}

# Expand dataset into months
expanded_data = []
for _, row in filtered_plants.iterrows():
    for season in row["Blooming Season"].split("-"):
        months = season_to_months.get(season.strip(), [])
        for m in months:
            expanded_data.append({
                "Plant": row["Common Name"],
                "Month": m,
                "Color": row["Flower Color"]
            })

df = pd.DataFrame(expanded_data)

# Plot
if not df.empty:
    fig, ax = plt.subplots(figsize=(12, 8))

    for plant in df["Plant"].unique():
        plant_data = df[df["Plant"] == plant]
        months = plant_data["Month"].tolist()
        color = plant_data["Color"].iloc[0].lower()  # use flower color for bar color
        ax.barh(plant, [1]*len(months), left=[m-0.5 for m in months], height=0.6, color=color)

    ax.set_xticks(range(1, 13))
    ax.set_xticklabels(["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"])
    ax.set_xlabel("Month")
    ax.set_ylabel("Plant")
    ax.set_title("🌸 Seasonal Bloom Calendar (Filtered by Flower Color)")

    st.pyplot(fig)

    # Export option
    fig.savefig("bloom_calendar.png")
    with open("bloom_calendar.png", "rb") as f:
        st.download_button("Download Bloom Calendar", f, file_name="bloom_calendar.png")
else:
    st.warning("⚠️ No plants match your selected flower colors.")
