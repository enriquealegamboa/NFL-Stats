import requests
import pandas as pd
import os
from supabase import create_client, Client
import time
from postgrest.exceptions import APIError
import maskpass


ATHLETES_URL = "https://sports.core.api.espn.com/v2/sports/football/leagues/nfl/seasons/2025/athletes"
PLAYER_SEASON_URL = "https://site.web.api.espn.com/apis/common/v3/sports/football/nfl/athletes"
SCOREBOARD_URL = "https://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard"
EVENT_URL = "https://sports.core.api.espn.com/v2/sports/football/leagues/nfl/events"
BOXSCORE_URL = "https://cdn.espn.com/core/nfl/boxscore?xhr=1&"
POST_SEASON_CHECK_URL = "https://site.api.espn.com/apis/site/v2/sports/football/nfl/teams"
TEAM_SEASON_URL = "https://sports.core.api.espn.com/v2/sports/football/leagues/nfl/seasons/2025"

_original_get = requests.get

def paused_get(url, *args, **kwargs):
    time.sleep(1.1)
    return _original_get(url, *args, **kwargs)

requests.get = paused_get

def get_all_season_team_stats():

    team_df = pd.read_csv('teams_df.csv')
    team_id = team_df["espn_team_id"]

    season_team_stats = []

    count = 1
    for id in team_id:
        url = f"{POST_SEASON_CHECK_URL}/{id}/schedule?season=2025&seasontype=3"
        r = requests.get(url)

        if r.status_code != 200:
            print("Post Season Event Page Request Failed for " + str(id))
            continue

        data = r.json()
        post = False
        if len(data["events"]) != 0:
            post = True
        append_team_stats(season_team_stats, True, id)
        if post:
            append_team_stats(season_team_stats, False, id)
        
        print(f"{count} of {len(team_id)} teams complete")
        count+=1
    
    return season_team_stats

def get_value(array, position, name, default_missing_value=0):
    if position < len(array) and array[position]["name"] == name:
        return int(array[position]["value"]) if array[position]["value"] != None else default_missing_value
    
    print(f"wrong position: {name}")
    for element in array:
        if name == element["name"]:
            return int(element["value"]) if element["value"] != None else default_missing_value
    
    print(f"value not found for {name} returning default value")
    return default_missing_value

def append_team_stats(season_team_stats, regular, id):
    url = f"{TEAM_SEASON_URL}/types/3/teams/{id}/statistics"
    if regular:
        url = f"{TEAM_SEASON_URL}/types/2/teams/{id}/statistics"
    r = requests.get(url)

    if r.status_code != 200:
        print("Regular Season Stats Page Failded " + str(id))
        return

    data = r.json()

    categories = data["splits"]["categories"]

    scoring = categories[9]["stats"]
    miscellaneous = categories[10]["stats"]
    passing = categories[1]["stats"]
    rushing = categories[2]["stats"]
    returning = categories[7]["stats"]
    interception = categories[5]["stats"]
    punting = categories[8]["stats"]
    kicking = categories[6]["stats"]
    general = categories[0]["stats"]
    

    season_team_stats.append({
        "team_id" : id,
        "season_id" : 2025,
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


class PlayerPosition:
    def __init__(self):
        self.players = []
        self.player_position = []
        self.position = []
        self.player_no_data = {}


def get_players_positions(players):

    player_position_rec = PlayerPosition()
    position_list = []
    count = 1

    for athlete in players:
        ath_bio_url = f"{ATHLETES_URL}/{athlete["player_id"]}?lang=en&region=us"
        r = requests.get(ath_bio_url)
        if r.status_code != 200:
            print(f"Player page request failed: {ath_bio_url}")
            continue
        athlete_bio_data = r.json()
        
        player_id = None
        pos = None

        player_id = athlete
        pos = athlete_bio_data["position"]["abbreviation"]
        if pos not in position_list:
            position_list.append(pos)
            player_position_rec.position.append({
                "position": pos
            })
        player_position_rec.player_position.append({
            "player_id" : player_id,
            "position" : pos
        })
        print(f"{count} of {len(players)}")
        count +=1
    return player_position_rec

class PlayerStats:

    def __init__(self):
        self.season_player_stats = []
        self.scoring = []
        self.passing = []
        self.rushing = []
        self.receiving = []
        self.defense = []
        self.returning = []
        self.kicking = []
        self.punting = []

        self.players_added = set()
        self.players_added_post = set()


def get_season_players_stats(players):
    season_players_stats = PlayerStats()
    print("Extracting player season stats")
    count = 1
    for player in players:
        if not get_season_single_player_stats(season_players_stats, player["player_id"], True) and not get_season_single_player_stats(season_players_stats, player["player_id"], False):
            print("no data")

        print(f"{count} of {len(players)} done")
        count+=1
    return season_players_stats

def check_if_in_season(player_id : int, player_stats : PlayerStats, regular : bool):
    if regular:
        if player_id not in player_stats.players_added:
            player_stats.season_player_stats.append({
                "season_id" : 2025,
                "player_id" : player_id,
                "is_regular_season" : regular
            })
            player_stats.players_added.add(player_id)
    else:
        if player_id not in player_stats.players_added_post:
            player_stats.season_player_stats.append({
                "season_id" : 2025,
                "player_id" : player_id,
                "is_regular_season" : regular
            })
            player_stats.players_added.add(player_id)

def get_season_single_player_stats(player_stats, player_id, regular):
    if regular:
        url = f"{PLAYER_SEASON_URL}/{player_id}/stats?seasontype=2&season=2025"
    else:
        url = f"{PLAYER_SEASON_URL}/{player_id}/stats?seasontype=3&season=2025"
    r = requests.get(url)

    if r.status_code != 200:
        print(f"Initial page request for player {player_id} failed")
        return False
    
    data = r.json()

    if not regular and not any(3 in tup for tup in data["filters"][1]["options"]):
        return False

    categories = data["categories"]
    for categorie in categories:
        match categorie["name"]:
            case "passing":
                stat = categorie["statistics"]
                if stat[len(stat)-1]["season"]["year"] == 2025:
                    check_if_in_season(player_id, player_stats, regular)
                    player_stats.passing.append({
                        "season_id" : 2025,
                        "player_id" : player_id,
                        "is_regular_season" : regular,
                        "gp" : stat[len(stat)-1]["stats"][0],
                        "cmp" : stat[len(stat)-1]["stats"][1],
                        "att": stat[len(stat)-1]["stats"][2],
                        "cmp_pct" : stat[len(stat)-1]["stats"][3],
                        "yds" : stat[len(stat)-1]["stats"][4].replace(",",""),
                        "avg" : stat[len(stat)-1]["stats"][5],
                        "td" : stat[len(stat)-1]["stats"][6],
                        "int_" : stat[len(stat)-1]["stats"][7],
                        "lng" : stat[len(stat)-1]["stats"][8],
                        "sack" : stat[len(stat)-1]["stats"][9],
                        "rtg" : stat[len(stat)-1]["stats"][10],
                        "qbr" : stat[len(stat)-1]["stats"][11]
                    })
                break
            case "rushing" : 
                stat = categorie["statistics"]
                if stat[len(stat)-1]["season"]["year"] == 2025:
                    check_if_in_season(player_id, player_stats, regular)
                    player_stats.rushing.append({
                        "season_id" : 2025,
                        "player_id" : player_id,
                        "is_regular_season" : regular,
                        "gp" : stat[len(stat)-1]["stats"][0],
                        "car" : stat[len(stat)-1]["stats"][1],
                        "yds": stat[len(stat)-1]["stats"][2].replace(",",""),
                        "avg" : stat[len(stat)-1]["stats"][3],
                        "td" : stat[len(stat)-1]["stats"][4],
                        "lng" : stat[len(stat)-1]["stats"][5],
                        "fd" : stat[len(stat)-1]["stats"][6],
                        "fum" : stat[len(stat)-1]["stats"][7],
                        "lst" : stat[len(stat)-1]["stats"][8]
                    })
                break
            case "receiving" : 
                stat = categorie["statistics"]
                if stat[len(stat)-1]["season"]["year"] == 2025:
                    check_if_in_season(player_id, player_stats, regular)
                    player_stats.receiving.append({
                        "season_id" : 2025,
                        "player_id" : player_id,
                        "is_regular_season" : regular,
                        "gp" : stat[len(stat)-1]["stats"][0],
                        "rec" : stat[len(stat)-1]["stats"][1],
                        "tgts": stat[len(stat)-1]["stats"][2],
                        "yds" : stat[len(stat)-1]["stats"][3].replace(",", ""),
                        "avg" : stat[len(stat)-1]["stats"][4],
                        "td" : stat[len(stat)-1]["stats"][5],
                        "lng" : stat[len(stat)-1]["stats"][6],
                        "fd" : stat[len(stat)-1]["stats"][7],
                        "fum" : stat[len(stat)-1]["stats"][8],
                        "lst" : stat[len(stat)-1]["stats"][9]
                    })
                break
            case "kicking" : 
                stat = categorie["statistics"]
                if stat[len(stat)-1]["season"]["year"] == 2025:
                    check_if_in_season(player_id, player_stats, regular)
                    fgm_1_19 , fga_1_19 = stat[len(stat)-1]["stats"][3].split("-")
                    fgm_20_29, fga_20_29 = stat[len(stat)-1]["stats"][4].split("-")
                    fgm_30_39, fga_30_39 = stat[len(stat)-1]["stats"][5].split("-")
                    fgm_40_49, fga_40_49 = stat[len(stat)-1]["stats"][6].split("-")
                    fgm_50_plus, fga_50_plus = stat[len(stat)-1]["stats"][7].split("-")
                    player_stats.kicking.append({
                        "season_id" : 2025,
                        "player_id" : player_id,
                        "is_regular_season" : regular,
                        "gp" : stat[len(stat)-1]["stats"][0],
                        "fgm_1_19" : fgm_1_19,
                        "fga_1_19" : fga_1_19, 
                        "fgm_20_29" : fgm_20_29,
                        "fga_20_29" : fga_20_29,
                        "fgm_30_39" : fgm_30_39,
                        "fga_30_39" : fga_30_39,
                        "fgm_40_49" : fgm_40_49,
                        "fga_40_49" : fga_40_49,
                        "fgm_50_plus" : fgm_50_plus,
                        "fga_50_plus" : fga_50_plus,
                        "lng" : stat[len(stat)-1]["stats"][8],
                        "xpm" : stat[len(stat)-1]["stats"][9],
                        "xpa" : stat[len(stat)-1]["stats"][10],
                        "pts" : stat[len(stat)-1]["stats"][11]
                    })
                break
            case "punting" : 
                stat = categorie["statistics"]
                if stat[len(stat)-1]["season"]["year"] == 2025:
                    check_if_in_season(player_id, player_stats, regular)
                    player_stats.punting.append({
                        "season_id" : 2025,
                        "player_id" : player_id,
                        "is_regular_season" : regular,
                        "gp" : stat[len(stat)-1]["stats"][0],
                        "punts" : stat[len(stat)-1]["stats"][1],
                        "avg": stat[len(stat)-1]["stats"][2],
                        "lng" : stat[len(stat)-1]["stats"][3],
                        "yds" : stat[len(stat)-1]["stats"][4].replace(",",""),
                        "tb" : stat[len(stat)-1]["stats"][5],
                        "tb_pct" : stat[len(stat)-1]["stats"][6],
                        "in20" : stat[len(stat)-1]["stats"][7],
                        "in20_pct" : stat[len(stat)-1]["stats"][8],
                        "att" : stat[len(stat)-1]["stats"][9],
                        "att_yds" : stat[len(stat)-1]["stats"][10],
                        "att_avg" : stat[len(stat)-1]["stats"][11],
                        "net" : stat[len(stat)-1]["stats"][12]
                    })
                break
            case "returning" : 
                stat = categorie["statistics"]
                if stat[len(stat)-1]["season"]["year"] == 2025:
                    check_if_in_season(player_id, player_stats, regular)
                    player_stats.returning.append({
                        "season_id" : 2025,
                        "player_id" : player_id,
                        "is_regular_season" : regular,
                        "gp" : stat[len(stat)-1]["stats"][0],
                        "p_att" : stat[len(stat)-1]["stats"][1],
                        "p_yds": stat[len(stat)-1]["stats"][2].replace(",",""),
                        "p_td" : stat[len(stat)-1]["stats"][3],
                        "p_fc" : stat[len(stat)-1]["stats"][4],
                        "p_lng" : stat[len(stat)-1]["stats"][5],
                        "k_att" : stat[len(stat)-1]["stats"][6],
                        "k_yds" : stat[len(stat)-1]["stats"][7].replace(",", ""),
                        "k_td" : stat[len(stat)-1]["stats"][8],
                        "k_fc" : stat[len(stat)-1]["stats"][9],
                        "k_lng" : stat[len(stat)-1]["stats"][10]
                    })
                break
            case "defensive" : 
                stat = categorie["statistics"]
                if stat[len(stat)-1]["season"]["year"] == 2025:
                    check_if_in_season(player_id, player_stats, regular)
                    player_stats.defense.append({
                        "season_id" : 2025,
                        "player_id" : player_id,
                        "is_regular_season" : regular,
                        "gp" : stat[len(stat)-1]["stats"][0],
                        "tot" : stat[len(stat)-1]["stats"][1],
                        "solo": stat[len(stat)-1]["stats"][2],
                        "ast" : stat[len(stat)-1]["stats"][3],
                        "sack" : stat[len(stat)-1]["stats"][4],
                        "ff" : stat[len(stat)-1]["stats"][5],
                        "fr" : stat[len(stat)-1]["stats"][6],
                        "yds" : int(stat[len(stat)-1]["stats"][7])+int(stat[len(stat)-1]["stats"][9]),
                        "int_" : stat[len(stat)-1]["stats"][8],
                        "avg" : stat[len(stat)-1]["stats"][10],
                        "td" : stat[len(stat)-1]["stats"][11],
                        "lng" : stat[len(stat)-1]["stats"][12],
                        "pd" : stat[len(stat)-1]["stats"][13],
                        "stf" : stat[len(stat)-1]["stats"][14],
                        "stfyds" : stat[len(stat)-1]["stats"][15],
                        "kb" : stat[len(stat)-1]["stats"][16]
                    })
                break
            case "scoring" : 
                stat = categorie["statistics"]
                if stat[len(stat)-1]["season"]["year"] == 2025:
                    check_if_in_season(player_id, player_stats, regular)
                    player_stats.scoring.append({
                        "season_id" : 2025,
                        "player_id" : player_id,
                        "is_regular_season" : regular,
                        "gp" : stat[len(stat)-1]["stats"][0],
                        "pass" : stat[len(stat)-1]["stats"][1],
                        "rush": stat[len(stat)-1]["stats"][2],
                        "rec" : stat[len(stat)-1]["stats"][3],
                        "ret" : stat[len(stat)-1]["stats"][4],
                        "td" : stat[len(stat)-1]["stats"][5],
                        "two_pt" : stat[len(stat)-1]["stats"][6],
                        "pat" : stat[len(stat)-1]["stats"][7],
                        "fg" : stat[len(stat)-1]["stats"][8],
                        "pts" : stat[len(stat)-1]["stats"][9]
                    })
                break
    return True        

def get_games(week : int):
    print(f"Extracting games for week {week}")
    games = []
    #24 instead of curr for normal op 
    if week == 22:
        return games
    if week < 19:
        url = f"{SCOREBOARD_URL}?week={week}&seasontype=2&year=2025"
    else:
        url = f"{SCOREBOARD_URL}?week={week-18}&seasontype=3&year=2025"
    r = requests.get(url)
    if r.status_code != 200:
        print(f"Page Request failed week {url}")
        return  games 
    data = r.json()
    events = data["events"]
    for event in events:
        game_id = event["id"]
        outside = not event["competitions"][0]["venue"]["indoor"]
        neutral = event["competitions"][0]["neutralSite"]
        game_date = event["competitions"][0]["date"][:10]
        home_id = None
        away_id = None
        home_score = 0
        away_score = 0
        if event["competitions"][0]["competitors"][0]["homeAway"] == "home":
            home_id = event["competitions"][0]["competitors"][0]["team"]["id"]
            home_score = event["competitions"][0]["competitors"][0]["score"]
            away_id = event["competitions"][0]["competitors"][1]["team"]["id"]
            away_score = event["competitions"][0]["competitors"][1]["score"]
        else:
            away_id = event["competitions"][0]["competitors"][0]["team"]["id"]
            away_score = event["competitions"][0]["competitors"][0]["score"]    
            home_id = event["competitions"][0]["competitors"][1]["team"]["id"]
            home_score = event["competitions"][0]["competitors"][1]["score"]
        games.append({
            "game_id" : game_id,
            "week" : week,
            "is_outside" : outside,
            "is_neutral" : neutral,
            "game_date" : game_date,
            "season_id" : 2025,
            "home_team_id" : home_id,
            "away_team_id" : away_id,
            "home_team_score" : home_score,
            "away_team_score" : away_score
        })
    print("Extracting games completed")
    return games

class GameStats:
    def __init__(self):
        self.teams = []
        self.players_in_game = []
        self.passing = []
        self.rushing = []
        self.receiving = []
        self.defense = []
        self.fumble = []
        self.interception = []
        self.punting = []
        self.kicking = []
        self.returning= []
        self.players_added = set()
        self.players = set()
        self.players_info = []
        self.roster = {}

def check_if_in_league(player_id, display_name , game_stats : GameStats):
    if player_id not in game_stats.players:
        game_stats.players.add(player_id)
        game_stats.players_info.append({
            "player_id" : player_id,
            "full_name" : display_name
        })

def check_if_in_game(player_id, game_id , game_stats : GameStats):
    if (player_id, game_id) not in game_stats.players_added:
        game_stats.players_in_game.append({
            "player_id" : player_id,
            "game_id" : game_id
        })
        game_stats.players_added.add((player_id, game_id))

def check_if_in_roster(player_id, team_id, date, roster):
    if (player_id, team_id) not in roster:
        roster[(player_id, team_id)] = [date,date]
    else:
        roster[(player_id,team_id)] = [roster[(player_id,team_id)][0], date]        

def get_game_stats(game):
    game_stats = GameStats()
    url = f"{BOXSCORE_URL}gameId={game["game_id"]}"
    r = requests.get(url)
    if r.status_code != 200:
        print("Initial Page Request for game " + str(game["game_id"]) + " failed")
        return game_stats
    data = r.json()

    for team in data['gamepackageJSON']["boxscore"]["teams"]:
        stats = team["statistics"]
        third_down_conversion, third_down_attempts = stats[4]["displayValue"].split("-")
        fourth_down_conversion, fourth_down_attempts = stats[5]["displayValue"].split("-")
        pass_completions, pass_attempts = stats[11]["displayValue"].split("/")
        sacks , sack_yards_lost = stats[14]["displayValue"].split("-")
        red_zone_made, red_zone_attempts = stats[18]["displayValue"].split("-")
        penalties, penalty_yards = stats[19]["displayValue"].split("-")
        game_stats.teams.append({
            "game_id" : game["game_id"],
            "team_id" : team["team"]["id"],
            "first_downs_passing" : stats[1]["value"],
            "first_downs_rushing" : stats[2]["value"],
            "first_downs_penalty" : stats[3]["value"],
            "third_down_conversions" : third_down_conversion,
            "third_down_attempts" : third_down_attempts,
            "fourth_down_conversions" : fourth_down_conversion,
            "fourth_down_attempts" : fourth_down_attempts,
            "total_plays" : stats[6]["value"],
            "total_yards" : stats[7]["displayValue"],
            "total_drives" : stats[9]["value"],
            "passing_yards" : stats[10]["value"],
            "pass_completions" : pass_completions,
            "pass_attempts" : pass_attempts,
            "interceptions_thrown" : stats[13]["value"],
            "sacks" : sacks,
            "sack_yards_lost" : sack_yards_lost,
            "rushing_yards" : stats[15]["value"],
            "rushing_attempts" : stats[16]["value"],
            "red_zone_made" : red_zone_made,
            "red_zone_attempts" : red_zone_attempts,
            "penalties_count" : penalties,
            "penalty_yards" : penalty_yards,
            "turnovers" : stats[20]["displayValue"],
            "fumbles_lost" :stats[21]["value"],
            "defensive_special_teams_tds" : stats[22]["value"],
            "possession_time_seconds" : stats[23]["value"]
        })
    
    player_returners = []

    for players in data['gamepackageJSON']["boxscore"]["players"]:
        team_id = players["team"]["id"]
        for stat in players["statistics"]:
            match stat["name"]:
                case "passing":
                    for player in stat["athletes"]:
                        player_stats = player["stats"]
                        check_if_in_league(player["athlete"]["id"], player["athlete"]["displayName"], game_stats)
                        check_if_in_roster(player["athlete"]["id"], team_id, game["game_date"], game_stats.roster)
                        check_if_in_game(player["athlete"]["id"], game["game_id"], game_stats)
                        completions, attempts = player_stats[0].split("/")
                        sacks , sack_yards = player_stats[5].split("-")
                        game_stats.passing.append({
                            "player_id" : player["athlete"]["id"],
                            "game_id" : game["game_id"],
                            #0 completion / attempts
                            "completions" : completions,
                            "attempts" : attempts,
                            "yards" : player_stats[1],
                            #2 yards per attempt
                            "touchdowns" : player_stats[3],
                            "interceptions" : player_stats[4],
                            #5 sacks-sack yards lost
                            "sacks" : sacks,
                            "sack_yards" : sack_yards,
                            "qbr" : player_stats[6],
                            "rtg" : player_stats[7]
                        })

                case "rushing":
                    for player in stat["athletes"]:
                        player_stats = player["stats"]
                        check_if_in_league(player["athlete"]["id"], player["athlete"]["displayName"], game_stats)
                        check_if_in_roster(player["athlete"]["id"], team_id, game["game_date"], game_stats.roster)
                        check_if_in_game(player["athlete"]["id"], game["game_id"], game_stats)
                        game_stats.rushing.append({
                            "player_id" : player["athlete"]["id"],
                            "game_id" : game["game_id"],
                            "carries" : player_stats[0],
                            "yards" : player_stats[1],
                            #2 yards per attempt
                            "touchdowns" : player_stats[3],
                            "long_run" : player_stats[4]
                        })
                
                case "receiving":
                    for player in stat["athletes"]:
                        player_stats = player["stats"]
                        check_if_in_league(player["athlete"]["id"], player["athlete"]["displayName"], game_stats)
                        check_if_in_roster(player["athlete"]["id"], team_id, game["game_date"], game_stats.roster)
                        check_if_in_game(player["athlete"]["id"], game["game_id"], game_stats)
                        game_stats.receiving.append({
                            "player_id" : player["athlete"]["id"],
                            "game_id" : game["game_id"],
                            "receptions" : player_stats[0],
                            "yards" : player_stats[1],
                            #2 yards per reception
                            "touchdowns" : player_stats[3],
                            "long_reception" : player_stats[4],
                            "targets" : player_stats[5]
                        })

                case "fumbles":
                    for player in stat["athletes"]:
                        player_stats = player["stats"]
                        check_if_in_league(player["athlete"]["id"], player["athlete"]["displayName"], game_stats)
                        check_if_in_roster(player["athlete"]["id"], team_id, game["game_date"], game_stats.roster)
                        check_if_in_game(player["athlete"]["id"], game["game_id"], game_stats)
                        game_stats.fumble.append({
                            "player_id" : player["athlete"]["id"],
                            "game_id" : game["game_id"],
                            "fumbles" : player_stats[0],
                            "fumbles_lost" : player_stats[1],
                            "fumbles_recovered" : player_stats[2]
                        })
                
                case "defensive":
                    for player in stat["athletes"]:
                        player_stats = player["stats"]
                        check_if_in_league(player["athlete"]["id"], player["athlete"]["displayName"], game_stats)
                        check_if_in_roster(player["athlete"]["id"], team_id, game["game_date"], game_stats.roster)
                        check_if_in_game(player["athlete"]["id"], game["game_id"], game_stats)
                        game_stats.defense.append({
                            "player_id" : player["athlete"]["id"],
                            "game_id" : game["game_id"],
                            "total_tackles" : player_stats[0],
                            "solo_tackles" : player_stats[1],
                            "sacks" : player_stats[2],
                            "tackles_for_loss" : player_stats[3],
                            "passes_defended" : player_stats[4],
                            "qb_hits" : player_stats[5],
                            "touchdowns" : player_stats[6]
                        })

                case "interceptions":
                    for player in stat["athletes"]:
                        player_stats = player["stats"]
                        check_if_in_league(player["athlete"]["id"], player["athlete"]["displayName"], game_stats)
                        check_if_in_roster(player["athlete"]["id"], team_id, game["game_date"], game_stats.roster)
                        check_if_in_game(player["athlete"]["id"], game["game_id"], game_stats)
                        game_stats.interception.append({
                            "player_id" : player["athlete"]["id"],
                            "game_id" : game["game_id"],
                            "interceptions" : player_stats[0],
                            "yards" : player_stats[1],
                            "touchdowns" : player_stats[2]
                        })

                case "kickReturns":
                    for player in stat["athletes"]:
                        player_stats = player["stats"]
                        check_if_in_league(player["athlete"]["id"], player["athlete"]["displayName"], game_stats)
                        check_if_in_roster(player["athlete"]["id"], team_id, game["game_date"], game_stats.roster)
                        check_if_in_game(player["athlete"]["id"], game["game_id"], game_stats)
                        curr_player_returner = None
                        for player_returner in player_returners:
                            if player_returner["player_id"] == player["athlete"]["id"]:
                                curr_player_returner = player_returner
                        if curr_player_returner == None:
                            player_returners.append({
                                "player_id" : player["athlete"]["id"],
                                "game_id" : game["game_id"],
                                "punt_returns" : 0,
                                "punt_return_yards" : 0,
                                "punt_return_td" : 0,
                                "punt_long" : 0,
                                "kick_returns" : player_stats[0],
                                "kick_return_yards" : player_stats[1],
                                "kick_return_td" : player_stats[4],
                                "kick_long" : player_stats[3] 
                            })
                        else:
                            curr_player_returner["kick_returns"] = player_stats[0]
                            curr_player_returner["kick_return_yards"] = player_stats[1]
                            curr_player_returner["kick_return_td"] = player_stats[4]
                            curr_player_returner["kick_long"] = player_stats[3] 
                        
                case "puntReturns":
                    for player in stat["athletes"]:
                        player_stats = player["stats"]
                        check_if_in_league(player["athlete"]["id"], player["athlete"]["displayName"], game_stats)
                        check_if_in_roster(player["athlete"]["id"], team_id, game["game_date"], game_stats.roster)
                        check_if_in_game(player["athlete"]["id"], game["game_id"], game_stats)
                        curr_player_returner = None
                        for player_returner in player_returners:
                            if player_returner["player_id"] == player["athlete"]["id"]:
                                curr_player_returner = player_returner
                        if curr_player_returner == None:
                            player_returners.append({
                                "player_id" : player["athlete"]["id"],
                                "game_id" : game["game_id"],
                                "punt_returns" : player_stats[0],
                                "punt_return_yards" : player_stats[1],
                                "punt_return_td" : player_stats[4],
                                "punt_long" : player_stats[3],
                                "kick_returns" : 0,
                                "kick_return_yards" : 0,
                                "kick_return_td" : 0,
                                "kick_long" : 0 
                            })
                        else:
                            curr_player_returner["kick_returns"] = player_stats[0]
                            curr_player_returner["kick_return_yards"] = player_stats[1]
                            curr_player_returner["kick_return_td"] = player_stats[4]
                            curr_player_returner["kick_long"] = player_stats[3] 

                case "kicking":
                    for player in stat["athletes"]:
                        player_stats = player["stats"]
                        check_if_in_league(player["athlete"]["id"], player["athlete"]["displayName"], game_stats)
                        check_if_in_roster(player["athlete"]["id"], team_id, game["game_date"], game_stats.roster)
                        check_if_in_game(player["athlete"]["id"], game["game_id"], game_stats)
                        made , attempted = player_stats[0].split("/")
                        extra_made, extra_attempted = player_stats[3].split("/")
                        game_stats.kicking.append({
                            "player_id" : player["athlete"]["id"],
                            "game_id" : game["game_id"],
                            #1 field goal made / attempted
                            "field_goals_made" : made,
                            "field_goals_attempted" : attempted,
                            #2 percent
                            "longest_fg" : player_stats[2],
                            "extra_points" : extra_made,
                            "extra_points_attempted" : extra_attempted,
                        })
                
                case "punting":
                    for player in stat["athletes"]:
                        player_stats = player["stats"]
                        check_if_in_league(player["athlete"]["id"], player["athlete"]["displayName"], game_stats)
                        check_if_in_roster(player["athlete"]["id"], team_id, game["game_date"], game_stats.roster)
                        check_if_in_game(player["athlete"]["id"], game["game_id"], game_stats)
                        game_stats.punting.append({
                            "player_id" : player["athlete"]["id"],
                            "game_id" : game["game_id"],
                            "punts" : player_stats[0],
                            "yards" : player_stats[1],
                            #2 Yds per punt
                            "touchbacks" : player_stats[3],
                            "inside_20" : player_stats[4],
                            "long_punt" : player_stats[5]                                
                        })

    for returner in player_returners:
        game_stats.returning.append(returner)   

    return game_stats

def get_roster(roster_dictionary):
    roster = []
    for player_team, start_end_date in roster_dictionary.items():
        roster.append({
            "player_id" : player_team[0],
            "team_id" : player_team[1],
            "start_date" : start_end_date[0],
            "end_date" : start_end_date[1]
        })
    return roster

def add_record_chunk(supabase, table_name, records, conflict_column = None):
    print(f"\n{table_name}")
    if len(records) < 1:
        print("No records")
        return
    try:
        response = supabase.table(table_name).upsert(
            records,
            on_conflict=conflict_column
        ).execute()
        return response.data
    except APIError as e:
        print(f"Database error: {e.message}")
        print(f"Table: {table_name}")
        print(f"HTTP Status: {e.code}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

def add_game_records(supabase):
    for week in range(1,3):
        #set to 24 when not in test
        games  = get_games(week)
        for game in games:
            print(f"\nWeek : {week}\nGame : {game["game_id"]}")
            print(f"{game["home_team_id"]} vs {game["away_team_id"]}")
            game_stats = get_game_stats(game)

            add_record_chunk(supabase, "game", game, "game_id")
            
            add_record_chunk(supabase, "game_team_stats", game_stats.teams)
            
            add_record_chunk(supabase, "player", game_stats.players_info, "player_id")

            add_record_chunk(supabase, "game_player_stats", game_stats.players_in_game, "player_id,game_id")
            

            add_record_chunk(supabase, "game_player_defense_stats", game_stats.defense, "player_id,game_id")
            add_record_chunk(supabase, "game_player_fumble_stats", game_stats.fumble, "player_id,game_id")
            add_record_chunk(supabase, "game_player_interception_stats", game_stats.interception, "player_id,game_id")
            add_record_chunk(supabase, "game_player_kicking_stats", game_stats.kicking, "player_id,game_id")
            add_record_chunk(supabase, "game_player_passing_stats", game_stats.passing, "player_id,game_id")
            add_record_chunk(supabase, "game_player_punting_stats", game_stats.punting, "player_id,game_id")
            add_record_chunk(supabase, "game_player_receiving_stats", game_stats.receiving, "player_id,game_id")
            add_record_chunk(supabase, "game_player_return_stats", game_stats.returning, "player_id,game_id")
            add_record_chunk(supabase, "game_player_rushing_stats", game_stats.rushing, "player_id,game_id")

            roster = get_roster(game_stats.roster)

            add_record_chunk(supabase, "roster", roster)

def add_season_player_records(supabase):
    batch_size  = 50 
    start = 0
    end = batch_size-1
    while True:
        try:
            
            response = supabase.table("player").select("player_id").range(start,end).execute()
            data = response.data
        except APIError as e:
            print(f"HTTP Status: {e.code}")
            print(f"Error Message: {e.message}")
            break
        if not data:
            break
            
        print("Player positions")
        players_position_rec = get_players_positions(data)
        season_players_stats = get_season_players_stats(data)

        add_record_chunk(supabase, "position", players_position_rec.position, "position")
        add_record_chunk(supabase, "player", players_position_rec.players, "player_id")
        add_record_chunk(supabase, "player_position", players_position_rec.player_position)

        add_record_chunk(supabase, "season_player_stats", season_players_stats.season_player_stats, "player_id,season_id,is_regular_season")
        add_record_chunk(supabase, "season_player_defense_stats", season_players_stats.defense, "player_id,season_id,is_regular_season")
        add_record_chunk(supabase, "season_player_kicking_stats", season_players_stats.kicking, "player_id,season_id,is_regular_season")
        add_record_chunk(supabase, "season_player_passing_stats", season_players_stats.passing, "player_id,season_id,is_regular_season") 
        add_record_chunk(supabase, "season_player_punting_stats", season_players_stats.punting, "player_id,season_id,is_regular_season")
        add_record_chunk(supabase, "season_player_receiving_stats", season_players_stats.receiving, "player_id,season_id,is_regular_season")
        add_record_chunk(supabase, "season_player_return_stats", season_players_stats.returning, "player_id,season_id,is_regular_season")
        add_record_chunk(supabase, "season_player_rushing_stats", season_players_stats.rushing, "player_id,season_id,is_regular_season")
        add_record_chunk(supabase, "season_player_scoring_stats", season_players_stats.scoring, "player_id,season_id,is_regular_season")  

        start += batch_size
        end += batch_size
       

def main():

    url: str = os.environ.get("SUPABASE_URL")
    key: str = os.environ.get("SUPABASE_SECRET_KEY")
    supabase: Client = create_client(url, key)

    admin_email = input("Email: ")
    admin_password =  maskpass.askpass(mask="*")
    try:
        admin_auth = supabase.auth.sign_in_with_password({
            "email": admin_email,
            "password": admin_password
        })
    except Exception as e:
        print("Failed to sign in")
        print(f"An error occurred: {e}")

    supabase.auth.set_session(admin_auth.session.access_token, admin_auth.session.refresh_token)

    print("Pulling all NFL data from 2025 season...")

    print("Team season stats")
    season_team_stats = get_all_season_team_stats()
    add_record_chunk(supabase, "season_team_stats", season_team_stats)

    add_game_records(supabase)

    add_season_player_records(supabase)

    print(f"Completed import")
    
main()