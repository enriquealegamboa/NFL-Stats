import requests
from postgrest.exceptions import APIError

# ESPN seasons endpoint base (used to look up a season's start/end dates).
SEASONS_URL = "https://sports.core.api.espn.com/v2/sports/football/leagues/nfl/seasons"


def add_record_chunk(supabase, table_name, records, conflict_column=None):
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


def ensure_season(supabase, year):
    existing = supabase.table("season").select("season_id").eq("season_id", year).execute()
    if existing.data:
        return
    r = requests.get(f"{SEASONS_URL}/{year}")
    if r.status_code != 200:
        print(f"Could not fetch season {year} info from ESPN -- season row not added")
        return
    data = r.json()
    start_date = data["startDate"][:10]   # "2025-07-31T07:00Z" -> "2025-07-31"
    end_date = data["endDate"][:10]
    add_record_chunk(supabase, "season", [{
        "season_id": year,
        "start_date": start_date,
        "end_date": end_date
    }], "season_id")
    print(f"Added season {year}: {start_date} to {end_date}")
