import pandas as pd
import streamlit as st

st.set_page_config(page_title="Rangers FC Historical Seasons", layout="wide")


@st.cache_data
def load_rangers_data() -> pd.DataFrame:
  overview = pd.read_csv("data/seasons_overview.csv")
  metrics = pd.read_csv("data/season_metrics.csv")

  merged = pd.merge(
      overview,
      metrics,
      on=["Season", "season_start_year"],
      how="inner",
      validate="one_to_one",
  )
  return merged.sort_values("season_start_year").reset_index(drop=True)


df = load_rangers_data()

st.title("Rangers FC Historical Seasons (1890–91 to 2025–26)")
st.caption(
    "Relational join between `data/seasons_overview.csv` and"
    " `data/season_metrics.csv` on `Season` and `season_start_year`."
)

min_yr = int(df["season_start_year"].min())
max_yr = int(df["season_start_year"].max())
year_range = st.sidebar.slider(
    "Season start year range",
    min_value=min_yr,
    max_value=max_yr,
    value=(min_yr, max_yr),
)

divisions = sorted(df["Division"].dropna().unique().tolist())
selected_divs = st.sidebar.multiselect(
    "Division(s)",
    options=divisions,
    default=divisions,
)

filtered = df[
    (df["season_start_year"] >= year_range[0])
    & (df["season_start_year"] <= year_range[1])
    & (df["Division"].isin(selected_divs))
]

c1, c2, c3, c4 = st.columns(4)
c1.metric("Seasons Shown", len(filtered))
c2.metric(
    "Avg 3-Pt PPG",
    f"{filtered['ppg_3pt_norm'].mean():.2f}" if len(filtered) else "—",
)
c3.metric(
    "Avg Win %",
    f"{filtered['win_pct'].mean():.1f}%" if len(filtered) else "—",
)
c4.metric(
    "Avg Goal Diff",
    f"{filtered['goal_diff'].mean():.1f}" if len(filtered) else "—",
)

display_cols = [
    "Season",
    "Division",
    "Pos",
    "Pld",
    "W",
    "D",
    "L",
    "GF",
    "GA",
    "goal_diff",
    "Pts",
    "points_per_win_rule",
    "ppg_3pt_norm",
    "win_pct",
]
present_cols = [col for col in display_cols if col in filtered.columns]
st.dataframe(filtered[present_cols], width="stretch", hide_index=True)

if len(filtered) > 0:
  st.subheader("3-Point Normalized PPG Across Selected Seasons")
  st.line_chart(filtered.set_index("Season")[["ppg_3pt_norm"]])
