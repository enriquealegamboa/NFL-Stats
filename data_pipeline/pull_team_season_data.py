import requests
import pandas as pd
import os
import time
from supabase import create_client, Client
from pipeline_utils import add_record_chunk, ensure_season



POST_SEASON_CHECK_URL = "https://site.api.espn.com/apis/site/v2/sports/football/nfl/teams"
TEAM_SEASON_URL = "https://sports.core.api.espn.com/v2/sports/football/leagues/nfl/seasons"

session = requests.Session()


class _FailedResponse:
    # Stand-in returned when every retry failed. Callers only check
    # .status_code (treating anything != 200 as a failure and skipping).
    status_code = 599

    def json(self):
        return {}


def paused_get(url, *args, retries=3, **kwargs):
    # Pace requests (ESPN rate-limits us) and retry transient failures with
    # exponential backoff so a single blip doesn't silently drop data.
    kwargs.setdefault("timeout", 30)
    time.sleep(1.1)
    last = None
    for attempt in range(retries):
        try:
            last = session.get(url, *args, **kwargs)
            if last.status_code == 200:
                return last
        except requests.RequestException as e:
            print(f"Request error: {e}")
            last = None
        if attempt < retries - 1:
            wait = 2 ** attempt   # back off: 1s, then 2s
            print(f"Retry {attempt + 1}/{retries - 1} in {wait}s -> {url}")
            time.sleep(wait)
    return last if last is not None else _FailedResponse()

requests.get = paused_get

def get_all_season_team_stats(year: int):

    team_df = pd.read_csv('teams_df.csv')
    team_id = team_df["espn_team_id"]

    season_team_stats = []

    count = 1
    for id in team_id:
        url = f"{POST_SEASON_CHECK_URL}/{id}/schedule?season={year}&seasontype=3"
        r = requests.get(url)

        if r.status_code != 200:
            print("Post Season Event Page Request Failed for " + str(id))
            continue

        data = r.json()
        post = False
        if len(data["events"]) != 0:
            post = True
        append_team_stats(season_team_stats, True, id, year)
        if post:
            append_team_stats(season_team_stats, False, id, year)
        
        print(f"{count} of {len(team_id)} teams complete")
        count+=1
    
    return season_team_stats

def get_value(array, name, default_missing_value=0):
    if array is None:
        return default_missing_value
    for element in array:
        if element["name"] == name:
            return int(element["value"]) if element["value"] is not None else default_missing_value
    print(f"value not found for {name}, returning default")
    return default_missing_value

def get_categorie(array, name):
    for element in array:
        if element["name"] == name:
            return element["stats"] if element["stats"] is not None else None
    print(f"category not found: {name}")
    return None

def append_team_stats(season_team_stats, regular, id, year:int):
    url = f"{TEAM_SEASON_URL}/{year}/types/3/teams/{id}/statistics"
    if regular:
        url = f"{TEAM_SEASON_URL}/{year}/types/2/teams/{id}/statistics"
    r = requests.get(url)

    if r.status_code != 200:
        print(f"Regular Season Stats Page Failed {id}")
        return

    data = r.json()

    categories = data["splits"]["categories"]

    scoring = get_categorie(categories, "scoring")
    miscellaneous = get_categorie(categories, "miscellaneous")
    passing = get_categorie(categories, "passing")
    rushing = get_categorie(categories, "rushing")
    returning = get_categorie(categories, "returning")
    interception = get_categorie(categories, "defensiveInterceptions")
    punting = get_categorie(categories, "punting")
    kicking = get_categorie(categories, "kicking")
    general = get_categorie(categories, "general")
    
    season_team_stats.append({
        "team_id" : id,
        "season_id" : year,
        "regular_season" : regular,
        "total_points" : get_value(scoring, "totalPoints"),
        "total_touchdowns" : get_value(scoring, "totalTouchdowns"),
        "first_downs_rushing" : get_value(miscellaneous, "firstDownsRushing"),
        "first_downs_passing" : get_value(miscellaneous, "firstDownsPassing"),
        "first_downs_penalty" : get_value(miscellaneous, "firstDownsPenalty"),
        "third_down_attempts" : get_value(miscellaneous, "thirdDownAttempts"),
        "third_down_conversions" : get_value(miscellaneous, "thirdDownConvs"),
        "fourth_down_attempts" : get_value(miscellaneous, "fourthDownAttempts"),
        "fourth_down_conversions" : get_value(miscellaneous, "fourthDownConvs"),
        "pass_completions" : get_value(passing, "completions"),
        "pass_attempts" : get_value(passing, "passingAttempts"),
        "net_passing_yards" : get_value(passing, "netPassingYards"),
        "passing_touchdowns" : get_value(passing, "passingTouchdowns"),
        "interceptions_thrown" : get_value(passing, "interceptions"),
        "sacks" : get_value(passing, "sacks"),
        "sack_yards_lost" : get_value(passing, "sackYardsLost"),
        "rushing_attempts" : get_value(rushing, "rushingAttempts"),
        "rushing_yards" : get_value(rushing, "rushingYards"),
        "rushing_touchdowns" : get_value(rushing, "rushingTouchdowns"),
        "offensive_plays" : get_value(passing, "totalOffensivePlays"),
        "total_yards" : get_value(passing, "totalYards"),
        "kickoff_returns" : get_value(returning, "kickReturns"),
        "kickoff_return_yards" : get_value(returning, "kickReturnYards"),
        "punt_returns" : get_value(returning, "puntReturns"),
        "punt_return_yards" : get_value(returning, "puntReturnYards"),
        "interception_returns" : get_value(interception, "interceptions"),
        "interception_return_yards" : get_value(interception, "interceptionYards"),
        "punts" : get_value(punting, "punts"),
        "punt_total_yards" : get_value(punting, "puntYards"),
        "field_goals_made" : get_value(kicking, "fieldGoalsMade"),
        "field_goals_attempted" : get_value(kicking, "fieldGoalAttempts"),
        "touchbacks" : get_value(kicking, "touchbacks"),
        "penalties_count" : get_value(general, "totalPenalties"),
        "penalty_yards" : get_value(general, "totalPenaltyYards"),
        "possession_time_seconds" : get_value(miscellaneous, "possessionTimeSeconds"),
        "fumbles" : get_value(general, "fumbles"),
        "fumbles_lost" : get_value(general, "fumblesLost"),
        "turnovers" : get_value(miscellaneous, "turnOverDifferential")
    })

def main():
    url: str = os.environ["SUPABASE_URL"]
    key: str = os.environ["SUPABASE_SECRET_KEY"]
    supabase: Client = create_client(url, key)

    for x in range(2011, 2026):
        ensure_season(supabase, x)
        season_team_stats = get_all_season_team_stats(x)
        add_record_chunk(supabase, "season_team_stats", season_team_stats,
                         "team_id,season_id,regular_season")
        print(f"Data complete for {x}")
    print("Completed import")

main()