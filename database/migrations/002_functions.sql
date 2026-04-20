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