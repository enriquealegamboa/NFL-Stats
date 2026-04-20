CREATE TRIGGER team_must_play_in_game
BEFORE INSERT OR UPDATE ON game_team_stats
FOR EACH ROW
EXECUTE FUNCTION validate_team_in_game();

CREATE TRIGGER trg_player_defense_stats_check
BEFORE INSERT OR UPDATE ON "game_player_defense_stats"
FOR EACH ROW
EXECUTE FUNCTION validate_player_in_game();

CREATE TRIGGER trg_player_fumble_stats_check
BEFORE INSERT OR UPDATE ON "game_player_fumble_stats"
FOR EACH ROW
EXECUTE FUNCTION validate_player_in_game();

CREATE TRIGGER trg_player_interception_stats_check
BEFORE INSERT OR UPDATE ON "game_player_interception_stats"
FOR EACH ROW
EXECUTE FUNCTION validate_player_in_game();

CREATE TRIGGER trg_player_kicking_stats_check
BEFORE INSERT OR UPDATE ON "game_player_kicking_stats"
FOR EACH ROW
EXECUTE FUNCTION validate_player_in_game();

CREATE TRIGGER trg_player_passing_stats_check
BEFORE INSERT OR UPDATE ON "game_player_passing_stats"
FOR EACH ROW
EXECUTE FUNCTION validate_player_in_game();

CREATE TRIGGER trg_player_punting_stats_check
BEFORE INSERT OR UPDATE ON "game_player_punting_stats"
FOR EACH ROW
EXECUTE FUNCTION validate_player_in_game();

CREATE TRIGGER trg_player_receiving_stats_check
BEFORE INSERT OR UPDATE ON "game_player_receiving_stats"
FOR EACH ROW
EXECUTE FUNCTION validate_player_in_game();

CREATE TRIGGER trg_player_return_stats_check
BEFORE INSERT OR UPDATE ON "game_player_return_stats"
FOR EACH ROW
EXECUTE FUNCTION validate_player_in_game();

CREATE TRIGGER trg_player_rushing_stats_check
BEFORE INSERT OR UPDATE ON "game_player_rushing_stats"
FOR EACH ROW
EXECUTE FUNCTION validate_player_in_game();