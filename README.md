# NBA Team Game Log Analyzer

End-to-end project to using **SQL**, **Python (pandas/matplotlib)**, and **Git/GitHub** using real NBA data.

## Project Overview

- Fetches a single NBA team's regular season game logs using `nba_api`
- Stores cleaned data in a **SQLite** database (`data/team_games.db`)
- Runs basic analysis:
  - Overall record, home/away record
  - Average points scored / allowed
  - Point differential
- Visualizes:
  - Points scored vs points allowed over the season
  - Point differential with a moving average

## Tech Stack

- Python (pandas, matplotlib)
- nba_api
- SQLite
- Git/GitHub

## How to Run

```bash
git clone <this-repo-url>
cd nba-team-game-log-analyzer
python -m venv venv
source venv/bin/activate         # Windows: venv\Scripts\activate
pip install -r requirements.txt

# 1. Fetch data & populate SQLite
python src/fetch_games.py

# 2. Run analysis & view plots
python src/analyze_games.py


Can check points over time below
![Points Over Time](figures/points_over_time.png)


Extra:
To analyze other team/season, update TEAM_NAME and SEASOn in src/fetch_games.py