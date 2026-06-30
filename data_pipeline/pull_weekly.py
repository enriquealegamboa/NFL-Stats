import requests
import os
from supabase import create_client, Client
import time
from datetime import datetime, timezone
from postgrest.exceptions import APIError
from pipeline_utils import add_record_chunk, ensure_season


SEASON_YEAR = None
ATHLETES_URL = "https://sports.core.api.espn.com/v2/sports/football/leagues/nfl/seasons/{year}/athletes"
PLAYER_SEASON_URL = "https://site.web.api.espn.com/apis/common/v3/sports/football/nfl/athletes"
SCOREBOARD_URL = "https://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard"
EVENT_URL = "https://sports.core.api.espn.com/v2/sports/football/leagues/nfl/events"
BOXSCORE_URL = "https://cdn.espn.com/core/nfl/boxscore?xhr=1&"

_original_get = requests.get


class _FailedResponse:
    status_code = 599

    def json(self):
        return {}


def paused_get(url, *args, retries=3, **kwargs):
    kwargs.setdefault("timeout", 30)
    time.sleep(1.1)
    last = None
    for attempt in range(retries):
        try:
            last = _original_get(url, *args, **kwargs)
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
        ath_bio_url = f"{ATHLETES_URL.format(year=SEASON_YEAR)}/{athlete["player_id"]}?lang=en&region=us"
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
                "season_id" : SEASON_YEAR,
                "player_id" : player_id,
                "is_regular_season" : regular
            })
            player_stats.players_added.add(player_id)
    else:
        if player_id not in player_stats.players_added_post:
            player_stats.season_player_stats.append({
                "season_id" : SEASON_YEAR,
                "player_id" : player_id,
                "is_regular_season" : regular
            })
            player_stats.players_added_post.add(player_id)

def season_values(category):
    latest = category["statistics"][-1]
    return latest["season"]["year"], dict(zip(category["names"], latest["stats"]))

def get_season_single_player_stats(player_stats, player_id, regular):
    if regular:
        url = f"{PLAYER_SEASON_URL}/{player_id}/stats?seasontype=2&season={SEASON_YEAR}"
    else:
        url = f"{PLAYER_SEASON_URL}/{player_id}/stats?seasontype=3&season={SEASON_YEAR}"
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
                year_val, vals = season_values(categorie)
                if year_val == SEASON_YEAR:
                    check_if_in_season(player_id, player_stats, regular)
                    player_stats.passing.append({
                        "season_id" : SEASON_YEAR,
                        "player_id" : player_id,
                        "is_regular_season" : regular,
                        "gp" : vals["gamesPlayed"],
                        "cmp" : vals["completions"],
                        "att": vals["passingAttempts"],
                        "cmp_pct" : vals["completionPct"],
                        "yds" : vals["passingYards"].replace(",",""),
                        "avg" : vals["yardsPerPassAttempt"],
                        "td" : vals["passingTouchdowns"],
                        "int_" : vals["interceptions"],
                        "lng" : vals["longPassing"],
                        "sack" : vals["sacks"],
                        "rtg" : vals["QBRating"],
                        "qbr" : vals["adjQBR"]
                    })
                break
            case "rushing" : 
                year_val, vals = season_values(categorie)
                if year_val == SEASON_YEAR:
                    check_if_in_season(player_id, player_stats, regular)
                    player_stats.rushing.append({
                        "season_id" : SEASON_YEAR,
                        "player_id" : player_id,
                        "is_regular_season" : regular,
                        "gp" : vals["gamesPlayed"],
                        "car" : vals["rushingAttempts"],
                        "yds": vals["rushingYards"].replace(",",""),
                        "avg" : vals["yardsPerRushAttempt"],
                        "td" : vals["rushingTouchdowns"],
                        "lng" : vals["longRushing"],
                        "fd" : vals["rushingFirstDowns"],
                        "fum" : vals["rushingFumbles"],
                        "lst" : vals["rushingFumblesLost"]
                    })
                break
            case "receiving" : 
                year_val, vals = season_values(categorie)
                if year_val == SEASON_YEAR:
                    check_if_in_season(player_id, player_stats, regular)
                    player_stats.receiving.append({
                        "season_id" : SEASON_YEAR,
                        "player_id" : player_id,
                        "is_regular_season" : regular,
                        "gp" : vals["gamesPlayed"],
                        "rec" : vals["receptions"],
                        "tgts": vals["receivingTargets"],
                        "yds" : vals["receivingYards"].replace(",", ""),
                        "avg" : vals["yardsPerReception"],
                        "td" : vals["receivingTouchdowns"],
                        "lng" : vals["longReception"],
                        "fd" : vals["receivingFirstDowns"],
                        "fum" : vals["receivingFumbles"],
                        "lst" : vals["receivingFumblesLost"]
                    })
                break
            case "kicking" : 
                year_val, vals = season_values(categorie)
                if year_val == SEASON_YEAR:
                    check_if_in_season(player_id, player_stats, regular)
                    fgm_1_19 , fga_1_19 = vals["fieldGoalsMade1_19-fieldGoalAttempts1_19"].split("-")
                    fgm_20_29, fga_20_29 = vals["fieldGoalsMade20_29-fieldGoalAttempts20_29"].split("-")
                    fgm_30_39, fga_30_39 = vals["fieldGoalsMade30_39-fieldGoalAttempts30_39"].split("-")
                    fgm_40_49, fga_40_49 = vals["fieldGoalsMade40_49-fieldGoalAttempts40_49"].split("-")
                    fgm_50_plus, fga_50_plus = vals["fieldGoalsMade50-fieldGoalAttempts50"].split("-")
                    player_stats.kicking.append({
                        "season_id" : SEASON_YEAR,
                        "player_id" : player_id,
                        "is_regular_season" : regular,
                        "gp" : vals["gamesPlayed"],
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
                        "lng" : vals["longFieldGoalMade"],
                        "xpm" : vals["extraPointsMade"],
                        "xpa" : vals["extraPointAttempts"],
                        "pts" : vals["totalKickingPoints"]
                    })
                break
            case "punting" : 
                year_val, vals = season_values(categorie)
                if year_val == SEASON_YEAR:
                    check_if_in_season(player_id, player_stats, regular)
                    player_stats.punting.append({
                        "season_id" : SEASON_YEAR,
                        "player_id" : player_id,
                        "is_regular_season" : regular,
                        "gp" : vals["gamesPlayed"],
                        "punts" : vals["punts"],
                        "avg": vals["grossAvgPuntYards"],
                        "lng" : vals["longPunt"],
                        "yds" : vals["puntYards"].replace(",",""),
                        "tb" : vals["touchbacks"],
                        "tb_pct" : vals["touchbackPct"],
                        "in20" : vals["puntsInside20"],
                        "in20_pct" : vals["puntsInside20Pct"],
                        "att" : vals["puntReturns"],
                        "att_yds" : vals["puntReturnYards"],
                        "att_avg" : vals["avgPuntReturnYards"],
                        "net" : vals["netAvgPuntYards"]
                    })
                break
            case "returning" : 
                year_val, vals = season_values(categorie)
                if year_val == SEASON_YEAR:
                    check_if_in_season(player_id, player_stats, regular)
                    player_stats.returning.append({
                        "season_id" : SEASON_YEAR,
                        "player_id" : player_id,
                        "is_regular_season" : regular,
                        "gp" : vals["gamesPlayed"],
                        "p_att" : vals["puntReturns"],
                        "p_yds": vals["puntReturnYards"].replace(",",""),
                        "p_td" : vals["puntReturnTouchdowns"],
                        "p_fc" : vals["puntReturnFairCatches"],
                        "p_lng" : vals["longPuntReturn"],
                        "k_att" : vals["kickReturns"],
                        "k_yds" : vals["kickReturnYards"].replace(",", ""),
                        "k_td" : vals["kickReturnTouchdowns"],
                        "k_fc" : vals["kickReturnFairCatches"],
                        "k_lng" : vals["longKickReturn"]
                    })
                break
            case "defensive" : 
                year_val, vals = season_values(categorie)
                if year_val == SEASON_YEAR:
                    check_if_in_season(player_id, player_stats, regular)
                    player_stats.defense.append({
                        "season_id" : SEASON_YEAR,
                        "player_id" : player_id,
                        "is_regular_season" : regular,
                        "gp" : vals["gamesPlayed"],
                        "tot" : vals["totalTackles"],
                        "solo": vals["soloTackles"],
                        "ast" : vals["assistTackles"],
                        "sack" : vals["sacks"],
                        "ff" : vals["fumblesForced"],
                        "fr" : vals["fumblesRecovered"],
                        "yds" : int(vals["fumblesRecoveredYards"])+int(vals["interceptionYards"]),
                        "int_" : vals["interceptions"],
                        "avg" : vals["avgInterceptionYards"],
                        "td" : vals["interceptionTouchdowns"],
                        "lng" : vals["longInterception"],
                        "pd" : vals["passesDefended"],
                        "stf" : vals["stuffs"],
                        "stfyds" : vals["stuffYards"],
                        "kb" : vals["kicksBlocked"]
                    })
                break
            case "scoring" : 
                year_val, vals = season_values(categorie)
                if year_val == SEASON_YEAR:
                    check_if_in_season(player_id, player_stats, regular)
                    player_stats.scoring.append({
                        "season_id" : SEASON_YEAR,
                        "player_id" : player_id,
                        "is_regular_season" : regular,
                        "gp" : vals["gamesPlayed"],
                        "pass" : vals["passingTouchdowns"],
                        "rush": vals["rushingTouchdowns"],
                        "rec" : vals["receivingTouchdowns"],
                        "ret" : vals["returnTouchdowns"],
                        "td" : vals["totalTouchdowns"],
                        "two_pt" : vals["totalTwoPointConvs"],
                        "pat" : vals["kickExtraPoints"],
                        "fg" : vals["fieldGoals"],
                        "pts" : vals["totalPoints"]
                    })
                break
    return True        

def get_games(week : int):
    print(f"Extracting games for week {week}")
    games = []
    if week == 22:
        print("Skipping the Pro Bowl")
        return games
    if week < 19:
        url = f"{SCOREBOARD_URL}?week={week}&seasontype=2&year={SEASON_YEAR}"
    else:
        url = f"{SCOREBOARD_URL}?week={week-18}&seasontype=3&year={SEASON_YEAR}"
    r = requests.get(url)
    if r.status_code != 200:
        print(f"Page Request failed week {url}")
        return  games 
    data = r.json()
    events = data["events"]
    for event in events:
        # Only keep finished games -- never insert scheduled or in-progress ones.
        if not event["status"]["type"]["completed"]:
            continue
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
            "season_id" : SEASON_YEAR,
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

def stats_by_name(items):
    result = {}
    for item in items:
        result.setdefault(item["name"], item)
    return result

def values_by_key(stat_group, athlete):
    # Box-score player stats: a flat "stats" list aligned to the group's "keys".
    return dict(zip(stat_group["keys"], athlete["stats"]))

def get_game_stats(game):
    game_stats = GameStats()
    url = f"{BOXSCORE_URL}gameId={game["game_id"]}"
    r = requests.get(url)
    if r.status_code != 200:
        print("Initial Page Request for game " + str(game["game_id"]) + " failed")
        return game_stats
    data = r.json()

    for team in data['gamepackageJSON']["boxscore"]["teams"]:
        ts = stats_by_name(team["statistics"])
        third_down_conversion, third_down_attempts = ts["thirdDownEff"]["displayValue"].split("-")
        fourth_down_conversion, fourth_down_attempts = ts["fourthDownEff"]["displayValue"].split("-")
        pass_completions, pass_attempts = ts["completionAttempts"]["displayValue"].split("/")
        sacks , sack_yards_lost = ts["sacksYardsLost"]["displayValue"].split("-")
        red_zone_made, red_zone_attempts = ts["redZoneAttempts"]["displayValue"].split("-")
        penalties, penalty_yards = ts["totalPenaltiesYards"]["displayValue"].split("-")
        game_stats.teams.append({
            "game_id" : game["game_id"],
            "team_id" : team["team"]["id"],
            "first_downs_passing" : ts["firstDownsPassing"]["value"],
            "first_downs_rushing" : ts["firstDownsRushing"]["value"],
            "first_downs_penalty" : ts["firstDownsPenalty"]["value"],
            "third_down_conversions" : third_down_conversion,
            "third_down_attempts" : third_down_attempts,
            "fourth_down_conversions" : fourth_down_conversion,
            "fourth_down_attempts" : fourth_down_attempts,
            "total_plays" : ts["totalOffensivePlays"]["value"],
            "total_yards" : ts["totalYards"]["displayValue"],
            "total_drives" : ts["totalDrives"]["value"],
            "passing_yards" : ts["netPassingYards"]["value"],
            "pass_completions" : pass_completions,
            "pass_attempts" : pass_attempts,
            "interceptions_thrown" : ts["interceptions"]["value"],
            "sacks" : sacks,
            "sack_yards_lost" : sack_yards_lost,
            "rushing_yards" : ts["rushingYards"]["value"],
            "rushing_attempts" : ts["rushingAttempts"]["value"],
            "red_zone_made" : red_zone_made,
            "red_zone_attempts" : red_zone_attempts,
            "penalties_count" : penalties,
            "penalty_yards" : penalty_yards,
            "turnovers" : ts["turnovers"]["displayValue"],
            "fumbles_lost" : ts["fumblesLost"]["value"],
            "defensive_special_teams_tds" : ts["defensiveTouchdowns"]["value"],
            "possession_time_seconds" : ts["possessionTime"]["value"]
        })
    
    player_returners = []

    for players in data['gamepackageJSON']["boxscore"]["players"]:
        team_id = players["team"]["id"]
        for stat in players["statistics"]:
            match stat["name"]:
                case "passing":
                    for player in stat["athletes"]:
                        check_if_in_league(player["athlete"]["id"], player["athlete"]["displayName"], game_stats)
                        check_if_in_roster(player["athlete"]["id"], team_id, game["game_date"], game_stats.roster)
                        check_if_in_game(player["athlete"]["id"], game["game_id"], game_stats)
                        vals = values_by_key(stat, player)
                        completions, attempts = vals["completions/passingAttempts"].split("/")
                        sacks , sack_yards = vals["sacks-sackYardsLost"].split("-")
                        game_stats.passing.append({
                            "player_id" : player["athlete"]["id"],
                            "game_id" : game["game_id"],
                            "completions" : completions,
                            "attempts" : attempts,
                            "yards" : vals["passingYards"],
                            "touchdowns" : vals["passingTouchdowns"],
                            "interceptions" : vals["interceptions"],
                            "sacks" : sacks,
                            "sack_yards" : sack_yards,
                            "qbr" : vals["adjQBR"],
                            "rtg" : vals["QBRating"]
                        })

                case "rushing":
                    for player in stat["athletes"]:
                        check_if_in_league(player["athlete"]["id"], player["athlete"]["displayName"], game_stats)
                        check_if_in_roster(player["athlete"]["id"], team_id, game["game_date"], game_stats.roster)
                        check_if_in_game(player["athlete"]["id"], game["game_id"], game_stats)
                        vals = values_by_key(stat, player)
                        game_stats.rushing.append({
                            "player_id" : player["athlete"]["id"],
                            "game_id" : game["game_id"],
                            "carries" : vals["rushingAttempts"],
                            "yards" : vals["rushingYards"],
                            "touchdowns" : vals["rushingTouchdowns"],
                            "long_run" : vals["longRushing"]
                        })
                
                case "receiving":
                    for player in stat["athletes"]:
                        check_if_in_league(player["athlete"]["id"], player["athlete"]["displayName"], game_stats)
                        check_if_in_roster(player["athlete"]["id"], team_id, game["game_date"], game_stats.roster)
                        check_if_in_game(player["athlete"]["id"], game["game_id"], game_stats)
                        vals = values_by_key(stat, player)
                        game_stats.receiving.append({
                            "player_id" : player["athlete"]["id"],
                            "game_id" : game["game_id"],
                            "receptions" : vals["receptions"],
                            "yards" : vals["receivingYards"],
                            "touchdowns" : vals["receivingTouchdowns"],
                            "long_reception" : vals["longReception"],
                            "targets" : vals["receivingTargets"]
                        })

                case "fumbles":
                    for player in stat["athletes"]:
                        check_if_in_league(player["athlete"]["id"], player["athlete"]["displayName"], game_stats)
                        check_if_in_roster(player["athlete"]["id"], team_id, game["game_date"], game_stats.roster)
                        check_if_in_game(player["athlete"]["id"], game["game_id"], game_stats)
                        vals = values_by_key(stat, player)
                        game_stats.fumble.append({
                            "player_id" : player["athlete"]["id"],
                            "game_id" : game["game_id"],
                            "fumbles" : vals["fumbles"],
                            "fumbles_lost" : vals["fumblesLost"],
                            "fumbles_recovered" : vals["fumblesRecovered"]
                        })
                
                case "defensive":
                    for player in stat["athletes"]:
                        check_if_in_league(player["athlete"]["id"], player["athlete"]["displayName"], game_stats)
                        check_if_in_roster(player["athlete"]["id"], team_id, game["game_date"], game_stats.roster)
                        check_if_in_game(player["athlete"]["id"], game["game_id"], game_stats)
                        vals = values_by_key(stat, player)
                        game_stats.defense.append({
                            "player_id" : player["athlete"]["id"],
                            "game_id" : game["game_id"],
                            "total_tackles" : vals["totalTackles"],
                            "solo_tackles" : vals["soloTackles"],
                            "sacks" : vals["sacks"],
                            "tackles_for_loss" : vals["tacklesForLoss"],
                            "passes_defended" : vals["passesDefended"],
                            "qb_hits" : vals["QBHits"],
                            "touchdowns" : vals["defensiveTouchdowns"]
                        })

                case "interceptions":
                    for player in stat["athletes"]:
                        check_if_in_league(player["athlete"]["id"], player["athlete"]["displayName"], game_stats)
                        check_if_in_roster(player["athlete"]["id"], team_id, game["game_date"], game_stats.roster)
                        check_if_in_game(player["athlete"]["id"], game["game_id"], game_stats)
                        vals = values_by_key(stat, player)
                        game_stats.interception.append({
                            "player_id" : player["athlete"]["id"],
                            "game_id" : game["game_id"],
                            "interceptions" : vals["interceptions"],
                            "yards" : vals["interceptionYards"],
                            "touchdowns" : vals["interceptionTouchdowns"]
                        })

                case "kickReturns":
                    for player in stat["athletes"]:
                        vals = values_by_key(stat, player)
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
                                "kick_returns" : vals["kickReturns"],
                                "kick_return_yards" : vals["kickReturnYards"],
                                "kick_return_td" : vals["kickReturnTouchdowns"],
                                "kick_long" : vals["longKickReturn"]
                            })
                        else:
                            curr_player_returner["kick_returns"] = vals["kickReturns"]
                            curr_player_returner["kick_return_yards"] = vals["kickReturnYards"]
                            curr_player_returner["kick_return_td"] = vals["kickReturnTouchdowns"]
                            curr_player_returner["kick_long"] = vals["longKickReturn"]
                        
                case "puntReturns":
                    for player in stat["athletes"]:
                        vals = values_by_key(stat, player)
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
                                "punt_returns" : vals["puntReturns"],
                                "punt_return_yards" : vals["puntReturnYards"],
                                "punt_return_td" : vals["puntReturnTouchdowns"],
                                "punt_long" : vals["longPuntReturn"],
                                "kick_returns" : 0,
                                "kick_return_yards" : 0,
                                "kick_return_td" : 0,
                                "kick_long" : 0
                            })
                        else:
                            curr_player_returner["punt_returns"] = vals["puntReturns"]
                            curr_player_returner["punt_return_yards"] = vals["puntReturnYards"]
                            curr_player_returner["punt_return_td"] = vals["puntReturnTouchdowns"]
                            curr_player_returner["punt_long"] = vals["longPuntReturn"]

                case "kicking":
                    for player in stat["athletes"]:
                        check_if_in_league(player["athlete"]["id"], player["athlete"]["displayName"], game_stats)
                        check_if_in_roster(player["athlete"]["id"], team_id, game["game_date"], game_stats.roster)
                        check_if_in_game(player["athlete"]["id"], game["game_id"], game_stats)
                        vals = values_by_key(stat, player)
                        made , attempted = vals["fieldGoalsMade/fieldGoalAttempts"].split("/")
                        extra_made, extra_attempted = vals["extraPointsMade/extraPointAttempts"].split("/")
                        game_stats.kicking.append({
                            "player_id" : player["athlete"]["id"],
                            "game_id" : game["game_id"],
                            "field_goals_made" : made,
                            "field_goals_attempted" : attempted,
                            "longest_fg" : vals["longFieldGoalMade"],
                            "extra_points" : extra_made,
                            "extra_points_attempted" : extra_attempted,
                        })
                
                case "punting":
                    for player in stat["athletes"]:
                        check_if_in_league(player["athlete"]["id"], player["athlete"]["displayName"], game_stats)
                        check_if_in_roster(player["athlete"]["id"], team_id, game["game_date"], game_stats.roster)
                        check_if_in_game(player["athlete"]["id"], game["game_id"], game_stats)
                        vals = values_by_key(stat, player)
                        game_stats.punting.append({
                            "player_id" : player["athlete"]["id"],
                            "game_id" : game["game_id"],
                            "punts" : vals["punts"],
                            "yards" : vals["puntYards"],
                            "touchbacks" : vals["touchbacks"],
                            "inside_20" : vals["puntsInside20"],
                            "long_punt" : vals["longPunt"]                                
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

def add_game_records(supabase, weeks):
    for week in weeks:
        games = get_games(week)
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
       

def get_current_week():
    r = requests.get(SCOREBOARD_URL)
    if r.status_code != 200:
        print("Could not fetch the scoreboard from ESPN")
        return None, None
    data = r.json()
    year = data["season"]["year"]
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    calendar = data["leagues"][0]["calendar"]

    current_week = None
    latest_start = None
    for phase in calendar:
        phase_type = str(phase.get("value"))   # "1" pre, "2" regular, "3" post, "4" off
        if phase_type not in ("2", "3"):
            continue                            # only regular season + playoffs
        for wk in phase.get("entries", []):
            start = wk["startDate"][:10]        # "2026-09-09T07:00Z" -> "2026-09-09"
            if start <= today and (latest_start is None or start > latest_start):
                latest_start = start
                # internal week: 1-18 regular, +18 for playoffs (matches get_games)
                current_week = int(wk["value"]) + (18 if phase_type == "3" else 0)
    return year, current_week

def main():
    global SEASON_YEAR
    url: str = os.environ["SUPABASE_URL"]
    key: str = os.environ["SUPABASE_SECRET_KEY"]
    supabase: Client = create_client(url, key)

    year, week = get_current_week()
    if week is None:
        print("No active NFL week right now (off-season or pre-season) -- nothing to pull.")
        return
    SEASON_YEAR = year

    # Make sure the season row exists before inserting games/stats that reference it.
    ensure_season(supabase, SEASON_YEAR)

    print(f"Pulling NFL data for {SEASON_YEAR} week {week}...")

    # Game-level data for this week's games (teams, players, rosters, box scores).
    add_game_records(supabase, [week])

    # Refresh current-season player aggregate stats (they change every week).
    add_season_player_records(supabase)

    print("Completed import")

main()