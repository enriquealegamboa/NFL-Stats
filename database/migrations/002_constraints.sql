-- Functions, triggers, and unique indexes that guard data integrity.
-- Runs after 001_schema.sql (the tables must exist first).

-- ---------------------------------------------------------------------------
-- Functions
-- ---------------------------------------------------------------------------

-- A team's game stats may only be recorded if that team actually played in the game.
CREATE OR REPLACE FUNCTION validate_team_in_game()
RETURNS TRIGGER AS $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM "game" g
        WHERE g."game_id" = NEW."game_id"
          AND (g.home_team_id = NEW."team_id"
               OR g.away_team_id = NEW."team_id")
    ) THEN
        RAISE EXCEPTION
            'Team % did NOT play in "game" %',
            NEW."team_id", NEW."game_id";
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- A player's per-stat-category rows may only be recorded if the player is
-- registered as having played in that game (a row in game_player_stats).
CREATE OR REPLACE FUNCTION validate_player_in_game()
RETURNS TRIGGER AS $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM "game_player_stats" pgs
        WHERE pgs."game_id" = NEW."game_id"
          AND pgs."player_id" = NEW."player_id"
    ) THEN
        RAISE EXCEPTION 'Player % did NOT play in "game" % ',
            NEW."player_id", NEW."game_id";
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- ---------------------------------------------------------------------------
-- Triggers
-- ---------------------------------------------------------------------------

CREATE OR REPLACE TRIGGER team_must_play_in_game
BEFORE INSERT OR UPDATE ON game_team_stats
FOR EACH ROW
EXECUTE FUNCTION validate_team_in_game();

CREATE OR REPLACE TRIGGER trg_player_defense_stats_check
BEFORE INSERT OR UPDATE ON "game_player_defense_stats"
FOR EACH ROW
EXECUTE FUNCTION validate_player_in_game();

CREATE OR REPLACE TRIGGER trg_player_fumble_stats_check
BEFORE INSERT OR UPDATE ON "game_player_fumble_stats"
FOR EACH ROW
EXECUTE FUNCTION validate_player_in_game();

CREATE OR REPLACE TRIGGER trg_player_interception_stats_check
BEFORE INSERT OR UPDATE ON "game_player_interception_stats"
FOR EACH ROW
EXECUTE FUNCTION validate_player_in_game();

CREATE OR REPLACE TRIGGER trg_player_kicking_stats_check
BEFORE INSERT OR UPDATE ON "game_player_kicking_stats"
FOR EACH ROW
EXECUTE FUNCTION validate_player_in_game();

CREATE OR REPLACE TRIGGER trg_player_passing_stats_check
BEFORE INSERT OR UPDATE ON "game_player_passing_stats"
FOR EACH ROW
EXECUTE FUNCTION validate_player_in_game();

CREATE OR REPLACE TRIGGER trg_player_punting_stats_check
BEFORE INSERT OR UPDATE ON "game_player_punting_stats"
FOR EACH ROW
EXECUTE FUNCTION validate_player_in_game();

CREATE OR REPLACE TRIGGER trg_player_receiving_stats_check
BEFORE INSERT OR UPDATE ON "game_player_receiving_stats"
FOR EACH ROW
EXECUTE FUNCTION validate_player_in_game();

CREATE OR REPLACE TRIGGER trg_player_return_stats_check
BEFORE INSERT OR UPDATE ON "game_player_return_stats"
FOR EACH ROW
EXECUTE FUNCTION validate_player_in_game();

CREATE OR REPLACE TRIGGER trg_player_rushing_stats_check
BEFORE INSERT OR UPDATE ON "game_player_rushing_stats"
FOR EACH ROW
EXECUTE FUNCTION validate_player_in_game();

-- ---------------------------------------------------------------------------
-- Unique indexes
-- ---------------------------------------------------------------------------

-- A team can only play one game per week (as home, and as away) in a season.
CREATE UNIQUE INDEX IF NOT EXISTS one_game_per_week_home_team
  ON "game" ("season_id", "week", "home_team_id");

CREATE UNIQUE INDEX IF NOT EXISTS one_game_per_week_away_team
  ON "game" ("season_id", "week", "away_team_id");

-- A player can have at most one active (end_date IS NULL) roster record.
CREATE UNIQUE INDEX IF NOT EXISTS one_active_record_per_id
  ON "roster" ("player_id")
  WHERE end_date IS NULL;
