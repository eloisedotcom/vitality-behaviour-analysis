# --- add at the very top of src/features.py ---
# Support running this file directly: ensure repo root is on sys.path
import os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # repo root
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
# --- end bootstrap ---

from src.points_policy import PointsPolicy  # keep absolute import

import pandas as pd
from typing import Tuple
from src.points_policy import PointsPolicy

def assign_week_period(dates: pd.Series) -> pd.PeriodIndex:
    """
    Return a weekly PeriodIndex with weeks ending on Friday (so weeks run Sat→Fri).
    """
    return dates.dt.to_period("W-FRI")

def compute_daily_points(df_activities: pd.DataFrame, policy: PointsPolicy) -> pd.DataFrame:
    """
    Input columns expected:
      ['start_time','date','avg_hr_bpm','duration_min','age']
    Returns a DataFrame with one row per date: ['date','daily_points']
    """
    # Ensure date is normalized to date (no time)
    df = df_activities.copy()
    df["date"] = pd.to_datetime(df["start_time"]).dt.tz_convert(None).dt.date
    df["date"] = pd.to_datetime(df["date"])
    daily = (
        df.groupby("date", as_index=False)
          .apply(lambda g: policy.daily_points(g))
          .rename(columns={None: "daily_points"})
    )
    return daily

def make_weekly_table(
    daily_points: pd.DataFrame, policy: PointsPolicy
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Build (features, labels) tables at weekly grain with Wed cutoff.
    daily_points columns: ['date','daily_points']
    Returns:
      X: features by week (up to Wed)
      y: labels by week (Fri total >= weekly_goal_points)
    """
    d = daily_points.copy()
    d["date"] = pd.to_datetime(d["date"])
    d["week"] = assign_week_period(d["date"])
    # Get Friday (week end) as Timestamp for each week
    week_end = d["week"].dt.end_time.dt.normalize()
    # Wednesday cutoff = Friday - 2 days
    d["wed_cutoff"] = d["week"].dt.end_time - pd.Timedelta(days=2)

    # Labels: full-week totals vs policy goal
    weekly_totals = d.groupby("week", as_index=False)["daily_points"].sum()
    weekly_totals["will_close_week"] = (weekly_totals["daily_points"] >= policy.weekly_goal_points).astype(int)

    # Features up to Wed
    d["is_before_or_on_wed"] = d["date"] <= d["wed_cutoff"].dt.normalize()
    feats = (
        d[d["is_before_or_on_wed"]]
        .groupby("week")
        .agg(
            wed_points=("daily_points", "sum"),
            sat_points=("daily_points", lambda s: s[d.loc[s.index, "date"].dt.day_name().eq("Saturday")].sum()),
            sun_points=("daily_points", lambda s: s[d.loc[s.index, "date"].dt.day_name().eq("Sunday")].sum()),
            mon_points=("daily_points", lambda s: s[d.loc[s.index, "date"].dt.day_name().eq("Monday")].sum()),
            tue_points=("daily_points", lambda s: s[d.loc[s.index, "date"].dt.day_name().eq("Tuesday")].sum()),
            wed_points_day=("daily_points", lambda s: s[d.loc[s.index, "date"].dt.day_name().eq("Wednesday")].sum()),
            days_with_points=("daily_points", lambda s: (s > 0).sum()),
            best_day_points=("daily_points", "max"),
        )
        .reset_index()
    )
    feats["gap_to_goal"] = (policy.weekly_goal_points - feats["wed_points"]).clip(lower=0)
    # Merge label
    y = weekly_totals[["week", "will_close_week"]]
    X = feats.merge(y, on="week", how="left")
    return X.drop(columns=["will_close_week"]), y