CREATE TABLE IF NOT EXISTS "daily_puzzle" (
    
    "puzzle_date" DATE PRIMARY KEY,

    "team_id" INT NOT NULL,

    "season_id" INT NOT NULL,

    "regular_season" BOOLEAN NOT NULL DEFAULT TRUE,

    FOREIGN KEY ("team_id", "season_id", "regular_season") 
        REFERENCES "season_team_stats"("team_id" , "season_id" , "regular_season")

)