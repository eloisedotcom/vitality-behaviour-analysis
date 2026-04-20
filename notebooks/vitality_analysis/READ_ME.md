# Vitality Behaviour Analysis

Given all data available by Wednesday 23:59, what is the probability that total weekly points (Sat-Fri) will reach >= 900 by Friday midnight?

Personal project analysing my Strava activities (2014–) to **estimate Discovery Vitality fitness points** and **predict by Wednesday** whether I will close my weekly **Active Rewards** exercise goal by **Friday**. 
The Active Rewards exercise week runs **Saturday → Friday**. Only **one exercise session per day** counts towards the weekly goal, with points awarded based on **average heart‑rate (HR) zone** and **duration**. 
References: Vitality fitness points table (HR zones and one‑per‑day rule) and the Active Rewards benefit guide (weekly window and Saturday→Friday timeline). [2](https://www.discovery.co.za/wcm/discoverycoza/assets/vitality/vitality-news/vitality-fitness-points-table.pdf)[3](https://www.discoveryhealthmedicalscheme.co.za/wcm/discoverycoza/assets/vitality/benefit-rules/vitality-active-rewards-benefit-guide-new.pdf)

---

## Problem & Decision

- **Target**: `will_close_week = 1` if total points earned between **Saturday 00:00** and **Friday 23:59** ≥ **900**; else `0`. (900 treated as configurable project default.) [4](https://forum.bikehub.co.za/topic/194953-discovery-vitality-weekly-goal-cap/) 
- **Prediction time**: **Wednesday 23:59**. 
- **Decision**: If the model predicts I will **not** close the week, I can plan a Thu/Fri workout (what‑if estimates included).

> Note: Vitality goals are personalised and can vary; endurance members may use **1 200**. This repo uses **900** as the default threshold (configurable in `PointsPolicy`). [4](https://forum.bikehub.co.za/topic/194953-discovery-vitality-weekly-goal-cap/)

---

## Data

- **Inputs**: Strava export (`.fit`, `.fit.gz`, `.fit.zip`, `.gpx`). HR comes from FIT files; GPX may lack HR. 
- **Privacy**: Raw exports are **not** committed. A small **synthetic sample** is provided for pipeline tests. 
- **Granularity**:
  - **Daily**: points are computed via **one‑activity‑per‑day** rule (take the highest‑scoring session that day). 
  - **Weekly**: weeks end on **Friday** (`W-FRI`) so that the window is **Sat→Fri**. [3](https://www.discoveryhealthmedicalscheme.co.za/wcm/discoverycoza/assets/vitality/benefit-rules/vitality-active-rewards-benefit-guide-new.pdf)

---

## Scoring Rules (encoded)

- **HR‑based points** (age‑related max HR): 
  - **Light**: 60–69% of max HR, 30+ min → **100 pts** 
  - **Moderate**: 70–79%, 30–59 min → **200 pts**; 60+ min → **300 pts** 
  - **Vigorous**: ≥80%, 30+ min → **300 pts** 
- **One exercise session per day counts**; we **take the max** eligible points for that day. 
- **Daily cap** for HR workouts used here: **300 pts**. 
Source: Discovery’s official points table and guidance (see link). [2](https://www.discovery.co.za/wcm/discoverycoza/assets/vitality/vitality-news/vitality-fitness-points-table.pdf)

---

## Repository Structure












Limitations & Assumptions

HR-based points estimation assumes accurate heart rate data from FIT files; GPX activities (no HR) contribute 0 points in this model.
Only the highest-scoring activity per day is considered (per official Vitality rules), but this implementation sums across days without daily max grouping in all visuals.
Max HR is estimated as 220 - age — replace with your actual tested max HR for better accuracy.
Non-HR activities (e.g., steps-only, swimming without HR monitor) are not awarded points here.
Model does not yet account for other point sources (sleep, nutrition, weekly challenges, etc.).

Key Insights

High-effort workouts (≥200 estimated points) frequently feature structured training terms such as interval, tempo, hill, repeats, and VO2 — suggesting that deliberate, intensity-focused sessions drive the most Vitality points.
Mid-week consistency (strong points by Wednesday) is a strong predictor of weekly goal achievement in historical data.
Longer-term trends may reveal shifts in training volume/intensity across life stages (e.g., post-graduation, career changes, or family phases).

Business Value
This project demonstrates how personal fitness data can power predictive analytics to estimate the probability of reaching the 900-point weekly Vitality Active Rewards goal based on Wednesday progress.
Early-week forecasting enables proactive interventions — such as mid-week motivational nudges, personalized alerts, or gamified reminders — which can improve adherence, reinforce healthy behavior change, and increase long-term member engagement and retention for Discovery.
By transforming raw Strava exports into actionable, behavior-motivating insights, the model aligns directly with Discovery’s core purpose: helping people live healthier, longer lives through data-driven wellness.
Future Work & Extensions

Implement daily max points grouping to fully match Vitality’s “highest activity per day” rule
Add time-series forecasting (e.g., Prophet, ARIMA, or LSTM) to predict end-of-week points trajectory
Incorporate NLP analysis on activity titles/descriptions/notes (word clouds → topic modeling → sentiment)
Explore LLM integration for natural-language summaries of weekly performance (e.g., via local Llama-3 or Ollama)
Deploy as an interactive Streamlit / Dash dashboard showing personal trends, goal probability, and motivational feedback
Extend to SQL-based reporting (e.g., load cleaned DataFrame into SQLite/PostgreSQL for BI-style queries: SELECT week, AVG(estimated_points), SUM(duration_min) FROM activities GROUP BY week)

Technical Note – SQL Context
In my day-to-day work, I regularly build and maintain SQL reports for data extraction, aggregation, and business intelligence.
This project uses pandas for flexible prototyping and data wrangling, but the cleaned DataFrame can be loaded into a relational database (SQLite or PostgreSQL) for more structured querying, e.g.:
SQLSELECT 
    week,
    AVG(estimated_points) AS avg_points,
    SUM(duration_min) AS total_duration_min,
    COUNT(*) AS num_activities
FROM activities
GROUP BY week
ORDER BY week DESC;
Hypothetical LLM Prompt Example
(Demonstrates awareness of modern NLP/LLM capabilities)
Pythonprint("""
Hypothetical LLM Prompt (e.g., for a local model such as Llama-3 via Ollama or Hugging Face):

You are a supportive Discovery Vitality coach analyzing a member's weekly fitness data.

Given:
- Total weekly points: {total_points}
- Points accumulated by Wednesday: {points_by_wed}
- Average heart rate across tracked activities: {avg_hr:.1f}%
- Key activity types: {top_activities}

Generate a concise, motivational 3–5 sentence summary that:
- Celebrates achievements
- Highlights patterns
- Offers one actionable suggestion to maintain or improve momentum

Example:
Total points: 1050
Points by Wednesday: 420
Average HR: 78.5%
Key activities: Interval Run, Hill Cycling, Tempo Swim

Sample output:
This week you smashed the 900-point goal with 1050 points — outstanding work! Your powerful mid-week surge (420 points by Wednesday) driven by high-intensity interval runs, hill efforts, and tempo sessions shows excellent consistency in vigorous zones. Keep front-loading structured workouts early in the week to make hitting the Active Rewards target feel effortless and sustainable.
""")