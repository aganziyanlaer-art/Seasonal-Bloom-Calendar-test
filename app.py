import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO

st.set_page_config(page_title="Bloom Calendar", layout="wide")

# -------------------------
# Load Data
# -------------------------
@st.cache_data
def load_data():
    try:
        df = pd.read_csv("plants.csv")
    except FileNotFoundError:
        st.error("❌ Could not find `plants.csv`. Make sure it's in the same folder as `app.py`.")
        return None

    # Normalize column names (lowercase + underscores)
    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]

    required = ["scientific_name", "common_name", "sun", "soil_type",
                "drought_tolerant", "mature_size_(m)", "flower_color", "blooming_season"]
    missing = [col for col in required if col not in df.columns]

    if missing:
        st.error(f"❌ Missing columns in plants.csv: {missing}")
        return None

    return df

plants = load_data()
if plants is None:
    st.stop()

# -------------------------
# Sidebar Filters
# -------------------------
st.sidebar.header("🌿 Filter Plants")

sun_options = sorted(plants["sun"].dropna().unique().tolist())
soil_options = sorted(plants["soil_type"].dropna().unique().tolist())
color_options = sorted(plants["flower_color"].dropna().unique().tolist())
drought_options = sorted(plants["drought_tolerant"].dropna().unique().tolist())

selected_sun = st.sidebar.multiselect("☀️ Sun", sun_options, default=sun_options)
selected_soil = st.sidebar.multiselect("🌱 Soil Type", soil_options, default=soil_options)
selected_color = st.sidebar.multiselect("🎨 Flower Color", color_options, default=color_options)
selected_drought = st.sidebar.multiselect("💧 Drought Tolerant", drought_options, default=drought_options)

# -------------------------
# Apply Filters
# -------------------------
filtered = plants[
    plants["sun"].isin(selected_sun) &
    plants["soil_type"].isin(selected_soil) &
    plants["flower_color"].isin(selected_color) &
    plants["drought_tolerant"].isin(selected_drought)
]

st.write(f"### Showing {len(filtered)} plant(s)")

def expand_seasons(season_str):
    # Convert something like "Winter-Spring" into ["Winter", "Spring"]
    seasons_order = ["Spring", "Summer", "Autumn", "Winter"]
    season_str = str(season_str)
    result = []

    # Split by comma first
    parts = season_str.split(",")
    for part in parts:
        part = part.strip()
        if "-" in part:
            start, end = part.split("-")
            start = start.strip()
            end = end.strip()
            # Find index in seasons_order
            try:
                start_idx = seasons_order.index(start)
                end_idx = seasons_order.index(end)
                # Add all seasons from start to end (inclusive)
                if start_idx <= end_idx:
                    result.extend(seasons_order[start_idx:end_idx+1])
                else:
                    # Wrap around year end
                    result.extend(seasons_order[start_idx:] + seasons_order[:end_idx+1])
            except ValueError:
                pass
        else:
            result.append(part)
    return result

# -------------------------
# Bloom Calendar Plot
# -------------------------
seasons = ["Spring", "Summer", "Autumn", "Winter"]
y_labels = filtered["scientific_name"].tolist()

fig, ax = plt.subplots(figsize=(10, 6))

for i, row in filtered.iterrows():
    bloom_seasons = expand_seasons(row["blooming_season"])
    for season in bloom_seasons:
        if season in seasons:
            x = seasons.index(season)
            y = y_labels.index(row["scientific_name"])
            ax.scatter(x, y, color=row["flower_color"], s=200, edgecolor="black")

ax.set_xticks(range(len(seasons)))
ax.set_xticklabels(seasons)
ax.set_yticks(range(len(y_labels)))
ax.set_yticklabels(y_labels)
ax.set_title("🌸 Seasonal Bloom Calendar", fontsize=16)
plt.tight_layout()

st.pyplot(fig)

# -------------------------
# Download Button
# -------------------------
buf = BytesIO()
fig.savefig(buf, format="png")
st.download_button(
    label="⬇️ Download Bloom Calendar as PNG",
    data=buf.getvalue(),
    file_name="bloom_calendar.png",
    mime="image/png"
)
