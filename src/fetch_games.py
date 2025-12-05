import os
import sqlite3
from pathlib import Path

import pandas as pd

from nba_api.stats.static import teams
from nba_api.stats.endpoints import teamgamelogs


# ==== CONFIG ====
TEAM_NAME = "Phoenix Suns"    # change later if you want
SEASON = "2024-25"            # NBA format (YYYY-YY)
DB_PATH = Path("data/team_games.db")
RAW_CSV_PATH = Path("data/raw") / f"{TEAM_NAME.replace(' ', '_').lower()}_{SEASON}_gamelog_raw.csv"
# =================


def get_team_id(team_name: str) -> int:
    nba_teams = teams.get_teams()
    matches = [t for t in nba_teams if t["full_name"] == team_name]
    if not matches:
        raise ValueError(f"Team '{team_name}' not found in NBA team list.")
    return matches[0]["id"]


def fetch_team_gamelog(team_id: int, season: str) -> pd.DataFrame:
    # Use TeamGameLogs (plural) endpoint
    gl = teamgamelogs.TeamGameLogs(
        team_id_nullable=str(team_id),
        season_nullable=season,
        season_type_nullable="Regular Season",
    )
    df = gl.get_data_frames()[0]
    # Optional: see what columns are there
    print("Columns from nba_api:", df.columns.tolist())
    return df


def transform_gamelog(df: pd.DataFrame, team_name: str, season: str, team_id: int) -> pd.DataFrame:
    """
    Keep + derive only what we need.
    """
    # Use the actual column names from TeamGameLogs endpoint
    cols_needed = ["GAME_ID", "GAME_DATE", "MATCHUP", "WL", "PTS", "PLUS_MINUS"]
    df = df[cols_needed].copy()

    # Normalize date
    df["GAME_DATE"] = pd.to_datetime(df["GAME_DATE"])

    # Derive opponent points from PTS and PLUS_MINUS:
    # plus_minus = team_pts - opp_pts  => opp_pts = team_pts - plus_minus
    df["PTS_OPP"] = df["PTS"] - df["PLUS_MINUS"]
    df["POINT_DIFF"] = df["PTS"] - df["PTS_OPP"]

    # Home / Away + opponent name from MATCHUP (e.g. "PHX vs LAL" or "PHX @ LAL")
    def parse_matchup(matchup: str):
        parts = matchup.split(" ")  # ["PHX", "vs", "LAL"]
        sep = parts[1]              # "vs" or "@"
        opp_abbr = parts[2]

        home_away = "HOME" if sep.lower() == "vs" else "AWAY"
        return home_away, opp_abbr

    df["HOME_AWAY"], df["OPPONENT"] = zip(*df["MATCHUP"].map(parse_matchup))

    # Sort by date and assign game_number
    df = df.sort_values("GAME_DATE").reset_index(drop=True)
    df["GAME_NUMBER"] = df.index + 1

    # Add season + team info
    df["SEASON"] = season
    df["TEAM_ID"] = team_id
    df["TEAM_NAME"] = team_name

    # Reorder columns to match schema
    df_out = df[
        [
            "GAME_ID",
            "SEASON",
            "TEAM_ID",
            "TEAM_NAME",
            "GAME_DATE",
            "GAME_NUMBER",
            "MATCHUP",
            "HOME_AWAY",
            "OPPONENT",
            "WL",
            "PTS",
            "PTS_OPP",
            "POINT_DIFF",
        ]
    ].copy()

    return df_out




def init_db(db_path: Path):
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    with open("sql/schema.sql", "r") as f:
        schema_sql = f.read()
    conn.executescript(schema_sql)
    conn.commit()
    conn.close()


def load_to_sqlite(df: pd.DataFrame, db_path: Path):
    conn = sqlite3.connect(db_path)
    # Use REPLACE in case you re-run script
    df.to_sql("team_games", conn, if_exists="replace", index=False)
    conn.close()


def main():
    # Ensure folders exist
    RAW_CSV_PATH.parent.mkdir(parents=True, exist_ok=True)
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    team_id = get_team_id(TEAM_NAME)
    print(f"Found team_id={team_id} for {TEAM_NAME}")

    print("Fetching game log from nba_api...")
    df_raw = fetch_team_gamelog(team_id, SEASON)
    print(f"Fetched {len(df_raw)} games.")

    # Save raw
    df_raw.to_csv(RAW_CSV_PATH, index=False)
    print(f"Saved raw game log to {RAW_CSV_PATH}")

    # Transform
    df_clean = transform_gamelog(df_raw, TEAM_NAME, SEASON, team_id)
    print("Transformed game log; preview:")
    print(df_clean.head())

    # Init DB + load
    init_db(DB_PATH)
    load_to_sqlite(df_clean, DB_PATH)
    print(f"Loaded {len(df_clean)} rows into SQLite at {DB_PATH}")


if __name__ == "__main__":
    main()