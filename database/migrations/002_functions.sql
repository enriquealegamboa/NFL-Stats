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

CREATE OR REPLACE FUNCTION validate_player_in_game()
RETURNS TRIGGER AS $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM "season_player_stats" pgs
        WHERE pgs."game_id" = NEW."game_id"
          AND pgs."player_id" = NEW."player_id"
          AND pgs."is_regular_season" = NEW."is_regular_season"
    ) THEN
        RAISE EXCEPTION 'Player % did NOT play in "game" % (season type: %)',
            NEW."player_id", NEW."game_id", NEW."is_regular_season";
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;