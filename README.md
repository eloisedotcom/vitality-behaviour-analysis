Vitality Behaviour Analysis
Personal project analyzing exported Strava fitness activities to estimate Discovery Vitality Active Rewards points and predict weekly goal achievement (900 points standard).

Main Notebook: vitality_analysis.ipynb
This Jupyter Notebook contains the core workflow:

Data Loading — Reads mixed Strava export formats:

.gpx files (tracks, distance, duration)
.fit / .fit.gz / .fit.zip files (adds heart rate, cadence, speed for points estimation)
Data Preparation — Cleans timestamps, calculates duration/distance, adds weekday/week columns

Vitality Points Estimation — Uses heart rate zones (based on official Discovery rules as of 2026):

Light (60–69% max HR): 100–300 pts depending on duration
Moderate (70–79%): 100–300 pts
Vigorous (80%+): 300 pts for 30+ min
Only highest points per day count (partial implementation)
Visual Insights:

Workout frequency & average duration by day of week
Weekly total duration trends (2014–2026)
Estimated points trends (FIT data only)
Early-Week Prediction — Simple logistic regression to estimate chance of hitting 900 pts based on Wednesday progress

How to Run
Clone or download this repo
Install dependencies: pip install pandas numpy matplotlib seaborn fitparse gpxpy
Update the folder path in the notebook to point to your Strava activities export
Run cells sequentially
Limitations & Notes
GPX activities contribute to duration/distance but not points (no HR data)
Points are estimates — actual Vitality awarding may differ slightly
Focused on HR-based rules; does not include sleep/steps/other bonuses
See the notebook for full details, code, and plots.

Feedback welcome!

Limitations & Assumptions

HR-based points estimation assumes accurate heart rate data from FIT files; GPX activities (no HR) contribute 0 points in this model. Only the highest-scoring activity per day is considered (per official Vitality rules), but this implementation sums across days without daily max grouping in all visuals. Max HR is estimated as 220 - age — replace with your actual tested max HR for better accuracy. Non-HR activities (e.g., steps-only, swimming without HR monitor) are not awarded points here. Model does not yet account for other point sources (sleep, nutrition, weekly challenges, etc.).

Technical Note – SQL Context In my day-to-day work, I regularly build and maintain SQL reports for data extraction, aggregation, and business intelligence. This project uses pandas for flexible prototyping and data wrangling, but the cleaned DataFrame can be loaded into a relational database (SQLite or PostgreSQL) for more structured querying, e.g.: SQLSELECT week, AVG(estimated_points) AS avg_points, SUM(duration_min) AS total_duration_min, COUNT(*) AS num_activities FROM activities GROUP BY week ORDER BY week DESC; Hypothetical LLM Prompt Example

Pythonprint(""" Hypothetical LLM Prompt (e.g., for a local model such as Llama-3 via Ollama or Hugging Face):

You are a supportive Discovery Vitality coach analyzing a member's weekly fitness data.

Given:

Total weekly points: {total_points}
Points accumulated by Wednesday: {points_by_wed}
Average heart rate across tracked activities: {avg_hr:.1f}%
Key activity types: {top_activities}
Generate a concise, motivational 3–5 sentence summary that:

Celebrates achievements
Highlights patterns
Offers one actionable suggestion to maintain or improve momentum
Example: Total points: 1050 Points by Wednesday: 420 Average HR: 78.5% Key activities: Interval Run, Hill Cycling, Tempo Swim

Sample output: This week you smashed the 900-point goal with 1050 points — outstanding work! Your powerful mid-week surge (420 points by Wednesday) driven by high-intensity interval runs, hill efforts, and tempo sessions shows excellent consistency in vigorous zones. Keep front-loading structured workouts early in the week to make hitting the Active Rewards target feel effortless and sustainable. """)
