CREATE UNIQUE INDEX one_game_per_week_home_team
  ON "game" ("season_id", "week", "home_team_id");

CREATE UNIQUE INDEX one_game_per_week_away_team
  ON "game" ("season_id", "week", "away_team_id");

CREATE UNIQUE INDEX one_active_record_per_id
  ON "roster" ("player_id")
  WHERE end_date IS NULL;