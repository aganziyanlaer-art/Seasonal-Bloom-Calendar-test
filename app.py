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

    # Clean blooming_season: strip, lowercase, filter empty
    df["blooming_season"] = df["blooming_season"].astype(str).str.strip()
    df["blooming_season"] = df["blooming_season"].apply(
        lambda x: ",".join([s.strip().capitalize() for s in x.split(",") if s.strip()])
    )

    # Ensure flower_color is non-empty and string
    df["flower_color"] = df["flower_color"].astype(str).str.strip()

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
].reset_index(drop=True)  # Reset index to avoid misalignment!

st.write(f"### Showing {len(filtered)} plant(s)")

if len(filtered) == 0:
    st.info("🔍 No plants match your filters. Try adjusting the criteria.")
    st.stop()

# -------------------------
# Bloom Calendar Plot
# -------------------------
seasons = ["Spring", "Summer", "Autumn", "Winter"]
y_labels = filtered["scientific_name"].tolist()

fig, ax = plt.subplots(figsize=(12, max(6, len(filtered) * 0.3)))  # Dynamic height
ax.set_facecolor("#f8f9fa")  # Light background for better contrast

# Create a color-to-label mapping for legend
unique_colors = filtered["flower_color"].dropna().unique()
color_legend = {color: [] for color in unique_colors}
for _, row in filtered.iterrows():
    bloom_seasons = [s.strip().capitalize() for s in row["blooming_season"].split(",") if s.strip()]
    for season in bloom_seasons:
        if season in seasons:
            x = seasons.index(season)
            y = filtered.index.get_loc(_)  # Safe index lookup using .get_loc()
            ax.scatter(x, y, color=row["flower_color"], s=200, edgecolor="black", alpha=0.9)
            color_legend[row["flower_color"]].append(row["common_name"])

# Set ticks and labels
ax.set_xticks(range(len(seasons)))
ax.set_xticklabels(seasons, fontsize=12)
ax.set_yticks(range(len(y_labels)))
ax.set_yticklabels(y_labels, fontsize=10)
ax.set_title("🌸 Seasonal Bloom Calendar", fontsize=16, fontweight="bold", pad=20)

# Add legend (only show top 10 colors to avoid clutter)
if len(color_legend) > 10:
    st.warning("⚠️ More than 10 flower colors detected. Legend limited to first 10 for clarity.")
    color_legend = dict(list(color_legend.items())[:10])

legend_elements = [
    plt.Line2D([0], [0], marker='o', color='w', label=f"{color} ({len(names)} plants)",
               markerfacecolor=color, markersize=10, markeredgecolor='black')
    for color, names in color_legend.items()
]
if legend_elements:
    ax.legend(handles=legend_elements, loc="upper right", bbox_to_anchor=(1.4, 1), fontsize=9)

plt.tight_layout()
plt.subplots_adjust(right=0.75)  # Make room for legend

st.pyplot(fig)

# -------------------------
# Download Button
# -------------------------
buf = BytesIO()
fig.savefig(buf, format="png", dpi=150, bbox_inches="tight")
st.download_button(
    label="⬇️ Download Bloom Calendar as PNG",
    data=buf.getvalue(),
    file_name="bloom_calendar.png",
    mime="image/png"
)

# -------------------------
# Optional: Show filtered table
# -------------------------
with st.expander("📋 View Full Plant List"):
    st.dataframe(
        filtered[["scientific_name", "common_name", "sun", "soil_type", "flower_color", "blooming_season", "drought_tolerant"]],
        use_container_width=True,
        height=300
    )
