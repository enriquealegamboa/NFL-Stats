import requests
import pandas as pd
import os
from supabase import create_client, Client

BASE_URL = "https://site.api.espn.com/apis/site/v2/sports/football/nfl/teams"

def get_all_players(team_id):

    players = []
    for id in team_id:

        url = f"{BASE_URL}/{id}/roster"
        r = requests.get(url)

        if r.status_code != 200:
            print("Request failed")
            break

        data = r.json()

        athletes = data.get("athletes", [])

        if not athletes:
            break

        for athlete_data in athletes:
            items = athlete_data.get("items")
            if items:
                for item in items:
                    position = None
                    name = None
                    team_id = id
                    player_id = None
                    position = item["position"]["abbreviation"]
                    name = item["fullName"]
                    player_id = item["id"]    
                    players.append({
                        "player_id": player_id,
                        "player_name": name,
                        "position": position,
                        "current_team_id": team_id
                    })

        print(f"Finished team: {id}")

    return players


def add_entries_to_player_table(supabase, player_df):
    main_list = []
    for row in player_df.itertuples(index=False):
        value = {'player_id': row.player_id, 'full_name': row.player_name,
                'position': row.position, 'current_team': row.current_team_id}
        main_list.append(value)
    supabase.table('player').upsert(
            main_list,
            on_conflict= 'player_id'
            ).execute()

def main():

    print("Pulling all NFL players from team rosters...")

    team_df = pd.read_csv('teams_df.csv')
    team_id = team_df["espn_team_id"]

    players = get_all_players(team_id)

    url: str = os.environ.get("SUPABASE_URL")
    key: str = os.environ.get("SUPABASE_KEY")
    supabase: Client = create_client(url, key)


    player_df = pd.DataFrame(players)

    #df.to_csv("players_df.csv", index=False)
    add_entries_to_player_table(supabase, player_df)

    print(f"Saved {len(player_df)} players")


main()