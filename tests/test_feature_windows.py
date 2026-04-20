import pandas as pd
from src.points_policy import PointsPolicy
from src.features import compute_daily_points, make_weekly_table

def test_week_boundary_and_wed_cutoff():
    policy = PointsPolicy()
    # Synthetic: Sat..Fri with points only on Mon (200) and Thu (300)
    dates = pd.date_range("2026-03-14", periods=7, freq="D")  # Sat..Fri
    df = pd.DataFrame({
        "start_time": [dates[2], dates[5]],  # Mon & Thu
        "avg_hr_bpm": [150, 170],  # arbitrary
        "duration_min": [45, 35],  # both valid
        "age": [30, 30],
    })
    daily = compute_daily_points(df, policy)
    X, y = make_weekly_table(daily, policy)
    # Wed cutoff excludes Thu, so wed_points should be 200 (Mon only)
    assert int(X.loc[0, "wed_points"]) == 200
    # Label should reflect full week total 200 + 300 = 500 < 900 ⇒ 0
    assert int(y.loc[0, "will_close_week"]) == 0