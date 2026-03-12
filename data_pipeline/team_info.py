import os
from supabase import create_client, Client
import pandas as pd


def add_entries_to_team_table(supabase, team_df):
    main_list = []
    for row in team_df.itertuples(index=False):
        value = {'team_id': row.espn_team_id, 'team_name': row.name,
                'abbreviation': row.abbreviation, 'conference': row.conference,
                'division': row.division}
        main_list.append(value)
    supabase.table('team').upsert(
            main_list,
            on_conflict= 'team_id'
            ).execute()

def main():
    team_df = pd.read_csv('teams_df.csv')
    url: str = os.environ.get("SUPABASE_URL")
    key: str = os.environ.get("SUPABASE_KEY")
    supabase: Client = create_client(url, key)
    add_entries_to_team_table(supabase, team_df)

main()
