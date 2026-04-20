
"""
Encode Discovery Vitality HR-based Active Rewards points rules.
Assumptions:
-one eligible activity per day counts (the one with highest points)
-900 points is treated as the weekly goal 
-age-adjusted HR zones are applied per activity date
"""
#src/points_policy.py
from dataclasses import dataclass
from typing import Optional
import pandas as pd

@dataclass
class PointsPolicy:
    policy_version: str = "2026-01"
    # Age-related max HR = 220 - age (simplified per Discovery tip)
    # You may replace with tested max HR if available.
    weekly_goal_points: int = 900  # configurable; endurance members may use 1200
    min_session_minutes: int = 30  # minimum tracked session that can earn HR-based points
    daily_max_points_from_exercise: int = 300  # HR-based workouts cap at 300 per day

    # HR zones as % of max HR (lower bound inclusive)
    zone_light_low: float = 0.60
    zone_moderate_low: float = 0.70
    zone_vigorous_low: float = 0.80

    def activity_points(self, avg_hr_bpm: float, age: int, duration_min: float) -> int:
        """Return points for a single activity based on average HR% and duration."""
        if duration_min < self.min_session_minutes or pd.isna(avg_hr_bpm):
            return 0
        hr_max = 220 - age
        hr_pct = avg_hr_bpm / hr_max
        # Light: 60–69% (30+ min) → 100
        if self.zone_light_low <= hr_pct < self.zone_moderate_low and duration_min >= 30:
            return 100
        # Moderate: 70–79%
        if self.zone_moderate_low <= hr_pct < self.zone_vigorous_low:
            if duration_min >= 60:
                return 300
            elif 30 <= duration_min < 60:
                return 200
        # Vigorous: ≥80% (30+ min) → 300
        if hr_pct >= self.zone_vigorous_low and duration_min >= 30:
            return 300
        return 0

    def daily_points(self, day_activities: pd.DataFrame) -> int:
        """
        Given all activities for a single calendar day with columns:
        ['avg_hr_bpm','age','duration_min'], return the highest eligible points
        (only one exercise session per day counts).
        """
        if day_activities.empty:
            return 0
        pts = day_activities.apply(
            lambda r: self.activity_points(r["avg_hr_bpm"], int(r["age"]), float(r["duration_min"])),
            axis=1,
        )
        return int(min(self.daily_max_points_from_exercise, pts.max() if len(pts) else 0))

