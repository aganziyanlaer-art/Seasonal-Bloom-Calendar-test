import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import io

st.title("🌸 Seasonal Bloom Calendar (Interactive Filters)")

# Load plant data
plants = pd.read_csv("plants.csv")
plants.columns = plants.columns.str.strip()

# Sidebar filters
st.sidebar.header("Filter Options")

sun_options = plants["Sun"].dropna().unique().tolist()
soil_options = plants["Soil Type"].dropna().unique().tolist()
color_options = plants["Flower Color"].dropna().unique().tolist()
drought_options = plants["Drought Tolerant"].dropna().unique().tolist()

selected_sun = st.sidebar.multiselect("Select Sun Exposure", sun_options, default=sun_options)
selected_soil = st.sidebar.multiselect("Select Soil Type", soil_options, default=soil_options)
selected_color = st.sidebar.multiselect("Select Flower Color", color_options, default=color_options)
selected_drought = st.sidebar.multiselect("Select Drought Tolerance", drought_options, default=drought_options)

# Apply filters
filtered = plants[
    plants["Sun"].isin(selected_sun) &
    plants["Soil Type"].isin(selected_soil) &
    plants["Flower Color"].isin(selected_color) &
    plants["Drought Tolerant"].isin(selected_drought)
]

st.subheader("Filtered Plant List")
st.dataframe(filtered)

# --- Bloom Calendar ---
st.subheader("🌼 Bloom Calendar Visualization")

if not filtered.empty:
    fig, ax = plt.subplots(figsize=(10, 8))

    season_order = ["Autumn", "Winter", "Spring", "Summer"]

    # Assign colors based on flower color
    color_map = {
        "Yellow": "gold",
        "Red": "red",
        "Pink": "hotpink",
        "White": "lightgray",
        "Purple": "purple",
        "Blue": "blue",
        "Orange": "darkorange",
        "Cream": "wheat"
    }

    # Draw bars for each plant
    for idx, row in filtered.iterrows():
        blooming_seasons = row["Blooming Season"].replace(",", "-").split("-")
        for season in blooming_seasons:
            season = season.strip()
            if season in season_order:
                ax.barh(
                    row["Scientific Name"],
                    1,
                    left=season_order.index(season),
                    color=color_map.get(row["Flower Color"], "skyblue"),
                    edgecolor="black"
                )

    ax.set_xticks(range(len(season_order)))
    ax.set_xticklabels(season_order)
    ax.set_xlabel("Season")
    ax.set_ylabel("Scientific Name")
    ax.set_title("Seasonal Bloom Calendar")

    # Legend
    patches = [mpatches.Patch(color=v, label=k) for k, v in color_map.items()]
    ax.legend(handles=patches, title="Flower Colors", bbox_to_anchor=(1.05, 1), loc='upper left')

    st.pyplot(fig)

    # Export button
    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight")
    st.download_button(
        label="⬇️ Download Bloom Calendar",
        data=buf.getvalue(),
        file_name="bloom_calendar.png",
        mime="image/png"
    )

else:
    st.warning("No plants match your filters.")
