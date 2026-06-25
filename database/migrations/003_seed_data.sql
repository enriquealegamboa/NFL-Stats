-- Lookup / reference data that the data pipeline depends on via foreign keys.
-- Teams reference division + conference; games and stats reference season.
-- ON CONFLICT DO NOTHING keeps this safe to re-run.

-- Conferences
INSERT INTO "conference" ("conference") VALUES
    ('AFC'),
    ('NFC')
ON CONFLICT ("conference") DO NOTHING;

-- Divisions (one per conference)
INSERT INTO "division" ("division", "conference") VALUES
    ('EAST',  'AFC'),
    ('NORTH', 'AFC'),
    ('SOUTH', 'AFC'),
    ('WEST',  'AFC'),
    ('EAST',  'NFC'),
    ('NORTH', 'NFC'),
    ('SOUTH', 'NFC'),
    ('WEST',  'NFC')
ON CONFLICT ("division", "conference") DO NOTHING;

-- 2025 season (Week 1 kickoff through Super Bowl LX)
INSERT INTO "season" ("season_id", "start_date", "end_date") VALUES
    (2025, '2025-09-04', '2026-02-08')
ON CONFLICT ("season_id") DO NOTHING;
