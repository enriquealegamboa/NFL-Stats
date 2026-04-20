import requests
import pandas as pd
import os
import time
from postgrest.exceptions import APIError



POST_SEASON_CHECK_URL = "https://site.api.espn.com/apis/site/v2/sports/football/nfl/teams"
TEAM_SEASON_URL = "https://sports.core.api.espn.com/v2/sports/football/leagues/nfl/seasons"

session = requests.Session()

def paused_get(url, *args, **kwargs):
    time.sleep(1.1)
    return session.get(url, *args, **kwargs)

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

def get_value(array, position, name, default_missing_value=0):
    if array == None:
        return default_missing_value

    if position < len(array) and array[position]["name"] == name:
        return int(array[position]["value"]) if array[position]["value"] != None else default_missing_value
    
    print(f"wrong position: {name}")
    for element in array:
        if name == element["name"]:
            return int(element["value"]) if element["value"] != None else default_missing_value
    
    print(f"value not found for {name} returning default value")
    return default_missing_value

def get_categorie(array, position:int, name: str):
    if position < len(array) and array[position]["name"] == name:
        return array[position]["stats"] if array[position]["stats"] != None else None
    
    print(f"wrong position: {name} for categories")
    for element in array:
        if name == element["name"]:
            return element["stats"] if element["stats"] != None else None
    
    print(f"value not found for {name} returning None")
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

    scoring = get_categorie(categories, 9, "scoring") 
    miscellaneous = get_categorie(categories, 10, "miscellaneous")
    passing = get_categorie(categories, 1, "passing")
    rushing = get_categorie(categories, 2, "rushing")
    returning = get_categorie(categories, 7, "returning")
    interception = get_categorie(categories, 5, "defensiveInterceptions")
    punting = get_categorie(categories, 8, "punting")
    kicking = get_categorie(categories, 6, "kicking")
    general = get_categorie(categories, 0, "general")
    
    season_team_stats.append({
        "team_id" : id,
        "season_id" : year,
        "regular_season" : regular,
        "total_points" : get_value(scoring, 9 , "totalPoints"),
        "total_touchdowns" : get_value(scoring, 11, "totalTouchdowns"),
        "first_downs_rushing" : get_value(miscellaneous, 4, "firstDownsRushing"),
        "first_downs_passing" : get_value(miscellaneous, 1, "firstDownsPassing"),
        "first_downs_penalty" : get_value(miscellaneous, 2, "firstDownsPenalty"),
        "third_down_attempts" : get_value(miscellaneous, 14, "thirdDownAttempts"),
        "third_down_conversions" : get_value(miscellaneous, 16, "thirdDownConvs"),
        "fourth_down_attempts" : get_value(miscellaneous, 5, "fourthDownAttempts"),
        "fourth_down_conversions" : get_value(miscellaneous, 7 , "fourthDownConvs"),
        "pass_completions" : get_value(passing, 2, "completions"),
        "pass_attempts" : get_value(passing, 12, "passingAttempts"),
        "net_passing_yards" : get_value(passing, 8, "netPassingYards"),
        "passing_touchdowns" : get_value(passing, 18, "passingTouchdowns"),
        "interceptions_thrown" : get_value(passing, 5, "interceptions"),
        "sacks" : get_value(passing, 24, "sacks"),
        "sack_yards_lost" : get_value(passing, 25, "sackYardsLost"),
        "rushing_attempts" : get_value(rushing, 6, "rushingAttempts"),
        "rushing_yards" : get_value(rushing, 12, "rushingYards"),
        "rushing_touchdowns" : get_value(rushing, 11, "rushingTouchdowns"),
        "offensive_plays" : get_value(passing, 28, "totalOffensivePlays"),
        "total_yards" : get_value(passing, 32, "totalYards"),
        "kickoff_returns" : get_value(returning, 8, "kickReturns"),
        "kickoff_return_yards" : get_value(returning, 10, "kickReturnYards"), 
        "punt_returns" : get_value(returning, 23, "puntReturns"),
        "punt_return_yards" : get_value(returning, 27, "puntReturnYards"),
        "interception_returns" : get_value(interception, 0, "interceptions"),
        "interception_return_yards" : get_value(interception, 2, "interceptionYards"),
        "punts" : get_value(punting, 7, "punts"),
        "punt_total_yards" : get_value(punting, 14, "puntYards"),
        "field_goals_made" : get_value(kicking, 21, "fieldGoalsMade"),
        "field_goals_attempted" : get_value(kicking, 9, "fieldGoalAttempts"),
        "touchbacks" : get_value(kicking, 42, "touchbacks"),
        "penalties_count" : get_value(general, 10, "totalPenalties"),
        "penalty_yards" : get_value(general, 11, "totalPenaltyYards"),
        "possession_time_seconds" : get_value(miscellaneous, 9, "possessionTimeSeconds"),
        "fumbles" : get_value(general, 0, "fumbles"),
        "fumbles_lost" : get_value(general, 1, "fumblesLost"),
        "turnovers" : get_value(miscellaneous, 22, "turnOverDifferential")
    })

def add_record_chunk(table_name, records, supabase_url, key):
    print(f"\n{table_name}")
    if len(records) < 1:
        print("No records")
        return
    try:
        url = f"{supabase_url}/rest/v1/{table_name}"
        headers = {
        "apikey": key,
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
        "Prefer": "return=representation"
        }
        response = requests.post(url, headers=headers, json=records)
        return response
    except APIError as e:
        print(f"Database error: {e.message}")
        print(f"Table: {table_name}")
        print(f"HTTP Status: {e.code}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

def main():
    url: str = os.environ.get("SUPABASE_URL")
    key: str = os.environ.get("SUPABASE_SECRET_KEY")

    for x in range(2011, 2026):
        season_team_stats = get_all_season_team_stats(x)
        add_record_chunk("season_team_stats", season_team_stats, url, key)
        print(f"Data complete complete for {x}")
    print(f"Completed import")
    
main()