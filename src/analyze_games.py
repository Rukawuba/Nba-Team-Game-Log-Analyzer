import sqlite3
from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt

DB_PATH = Path("data/team_games.db")


def load_games():
    conn = sqlite3.connect(DB_PATH)
    query = """
        SELECT
            GAME_DATE,
            GAME_NUMBER,
            WL,
            HOME_AWAY,
            OPPONENT,
            PTS,
            PTS_OPP,
            POINT_DIFF
        FROM team_games
        ORDER BY GAME_DATE
    """
    df = pd.read_sql_query(query, conn, parse_dates=["GAME_DATE"])
    conn.close()
    return df


def basic_summary(df: pd.DataFrame):
    total_games = len(df)
    wins = (df["WL"] == "W").sum()
    losses = (df["WL"] == "L").sum()
    print(f"Total games: {total_games} | Wins: {wins} | Losses: {losses}")

    # Home / Away record
    home = df[df["HOME_AWAY"] == "HOME"]
    away = df[df["HOME_AWAY"] == "AWAY"]

    home_wins = (home["WL"] == "W").sum()
    home_losses = (home["WL"] == "L").sum()
    away_wins = (away["WL"] == "W").sum()
    away_losses = (away["WL"] == "L").sum()

    print(f"Home record: {home_wins}-{home_losses}")
    print(f"Away record: {away_wins}-{away_losses}")

    # Average points for / against
    print(f"Average PTS: {df['PTS'].mean():.1f}")
    print(f"Average PTS OPP: {df['PTS_OPP'].mean():.1f}")
    print(f"Average point diff: {df['POINT_DIFF'].mean():.1f}")


def plot_points_over_time(df: pd.DataFrame):

        # Suns colors
    suns_orange = "#E56020"
    suns_purple = "#1D1160"

    plt.figure(figsize=(10, 5))
    plt.plot(df["GAME_NUMBER"], df["PTS"], label="Points Scored")
    plt.plot(df["GAME_NUMBER"], df["PTS_OPP"], label="Points Allowed")
    plt.xlabel("Game Number")
    plt.ylabel("Points")
    plt.title("Points Scored vs Points Allowed Over Season")
    plt.legend()
    plt.tight_layout()
    plt.show()


def plot_point_diff_moving_avg(df: pd.DataFrame, window: int = 5):
    df = df.copy()
    df["POINT_DIFF_MA"] = df["POINT_DIFF"].rolling(window=window, min_periods=1).mean()

    plt.figure(figsize=(10, 5))
    plt.plot(
        df["GAME_NUMBER"],
        df["POINT_DIFF"],
        marker="o",
        linestyle="none",
        label="Point Diff (single game)",
    )
    plt.plot(
        df["GAME_NUMBER"],
        df["POINT_DIFF_MA"],
        label=f"{window}-Game Moving Avg",
    )
    plt.axhline(0, linestyle="--")
    plt.xlabel("Game Number")
    plt.ylabel("Point Differential")
    plt.title(f"Point Differential & {window}-Game Moving Average")
    plt.legend()
    plt.tight_layout()
    plt.show()


def main():
    df = load_games()
    print(df.head())

    basic_summary(df)
    plot_points_over_time(df)
    plot_point_diff_moving_avg(df, window=5)


if __name__ == "__main__":
    main()

plt.savefig("figures/points_over_time.png", dpi=200)
