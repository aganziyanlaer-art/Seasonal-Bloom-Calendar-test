import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from io import BytesIO
import re

st.set_page_config(page_title="Seasonal Bloom Calendar", layout="wide")

# -------------------------
# Helper functions
# -------------------------
def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    # turn headers into safe snake_case-like names
    cols = (
        df.columns
        .astype(str)
        .str.strip()
        .str.lower()
        .str.replace(r'[^\w]+', '_', regex=True)
        .str.strip('_')
    )
    df.columns = cols
    return df

def extract_seasons(text: str):
    if not isinstance(text, str):
        return []
    found = re.findall(r'(spring|summer|autumn|fall|winter)', text, flags=re.I)
    mapped = []
    for f in found:
        f_low = f.lower()
        if f_low == 'fall':
            s = 'Autumn'
        else:
            s = f_low.capitalize()
        if s not in mapped:
            mapped.append(s)
    return mapped

def map_color_token(color_text: str):
    # map common color words to matplotlib-friendly colors
    if not isinstance(color_text, str) or color_text.strip() == '':
        return 'lightgray'
    token = re.split(r'[/,;|-]', color_text)[0].strip().lower()
    token = token.split()[-1]  # take last word if "pale purple"
    color_map = {
        "yellow": "gold",
        "red": "red",
        "pink": "hotpink",
        "white": "lightgray",
        "purple": "purple",
        "blue": "blue",
        "orange": "darkorange",
        "cream": "wheat",
        "green": "green",
        "gold": "gold",
        "brown": "saddlebrown",
        "lavender": "violet",
    }
    return color_map.get(token, token)  # fallback to token (matplotlib may accept common names)

# -------------------------
# Load data
# -------------------------
def load_plants(path="plants.csv"):
    try:
        df = pd.read_csv(path)
    except FileNotFoundError:
        st.error("❌ plants.csv not found. Upload plants.csv to the repo root (same folder as app.py).")
        st.stop()

    df = normalize_columns(df)

    required = [
        "scientific_name",
        "common_name",
        "sun",
        "soil_type",
        "drought_tolerant",
        "mature_size_m",
        "flower_color",
        "blooming_season",
    ]
    missing = [c for c in required if c not in df.columns]

    if missing:
        st.error(f"❌ plants.csv is missing required column(s): {missing}")
        st.write("Detected columns:", list(df.columns))
        st.stop()
    return df

plants = load_plants()

# ensure strings are trimmed
for c in ["sun", "soil_type", "drought_tolerant", "flower_color", "blooming_season", "scientific_name"]:
    plants[c] = plants[c].astype(str).str.strip()

# -------------------------
# UI: Sidebar filters
# -------------------------
st.sidebar.header("Filter options (multiple select supported)")
sun_options = sorted(plants["sun"].dropna().unique().tolist())
soil_options = sorted(plants["soil_type"].dropna().unique().tolist())
color_options = sorted(plants["flower_color"].dropna().unique().tolist())
drought_options = sorted(plants["drought_tolerant"].dropna().unique().tolist())

selected_sun = st.sidebar.multiselect(☀️ Sun", sun_options, default=sun_options)
selected_soil = st.sidebar.multiselect("🌱 Soil Type", soil_options, default=soil_options)
selected_color = st.sidebar.multiselect("🎨 Flower Color", color_options, default=color_options)
selected_drought = st.sidebar.multiselect("💧 Drought Tolerant", drought_options, default=drought_options)

# Apply filters
filtered = plants[
    plants["sun"].isin(selected_sun) &
    plants["soil_type"].isin(selected_soil) &
    plants["flower_color"].isin(selected_color) &
    plants["drought_tolerant"].isin(selected_drought)
].reset_index(drop=True)

st.write(f"### Showing {len(filtered)} plant(s) matching filters")

# data preview
with st.expander("Preview filtered data (first 10 rows)"):
    st.dataframe(filtered.head(10))

# -------------------------
# Bloom calendar visualization
# -------------------------
st.subheader("🌼 Bloom Calendar")

if filtered.empty:
    st.warning("No plants match your filters. Adjust the filters on the left.")
else:
    # canonical season order for x-axis
    season_order = ["Spring", "Summer", "Autumn", "Winter"]
    n = len(filtered)
    fig_height = max(4, 0.35 * n + 2)
    fig, ax = plt.subplots(figsize=(10, fig_height))

    # prepare y labels (scientific names)
    y_labels = filtered["scientific_name"].tolist()

    # collect colors used (for legend)
    used_color_map = {}

    for i, row in filtered.iterrows():
        seasons = extract_seasons(row["blooming_season"])
        # if no season parsed, skip
        if not seasons:
            continue
        color = map_color_token(row["flower_color"])
        used_color_map[row["flower_color"]] = color  # store original->mapped
        for s in seasons:
            if s in season_order:
                x = season_order.index(s)
                ax.barh(
                    i,                     # y position (index)
                    0.9,                   # width (bar width across one season)
                    left=x,                # which season column
                    color=color,
                    edgecolor="black",
                    height=0.6
                )

    # set axes
    ax.set_yticks(range(len(y_labels)))
    ax.set_yticklabels(y_labels)
    ax.set_xticks(range(len(season_order)))
    ax.set_xticklabels(season_order)
    ax.set_xlim(-0.5, len(season_order) - 0.5 + 0.9)
    ax.invert_yaxis()  # so first plant appears at top
    ax.set_xlabel("Season")
    ax.set_title("Seasonal Bloom Calendar")

    # Legend based on used colors (show original label)
    patches = []
    added = set()
    for orig_label, mapped in used_color_map.items():
        key = orig_label.strip()
        if key not in added:
            patches.append(mpatches.Patch(color=mapped, label=key))
            added.add(key)
    if patches:
        ax.legend(handles=patches, title="Flower Color", bbox_to_anchor=(1.02, 1), loc='upper left')

    plt.tight_layout()
    st.pyplot(fig)

    # -------------
    # Download buttons
    # -------------
    # PNG
    buf = BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight")
    st.download_button(
        label="⬇️ Download Bloom Calendar (PNG)",
        data=buf.getvalue(),
        file_name="bloom_calendar.png",
        mime="image/png"
    )

    # CSV of filtered list
    csv_buf = BytesIO()
    csv_buf.write(filtered.to_csv(index=False).encode("utf-8"))
    st.download_button(
        label="⬇️ Download Filtered Plant List (CSV)",
        data=csv_buf.getvalue(),
        file_name="filtered_plants.csv",
        mime="text/csv"
    )
