-- 005_daily_puzzle_cron.sql
--
-- Schedules a daily job that picks the NEXT day's puzzle and writes it into
-- daily_puzzle. Generating a day ahead means the row is always in place before
-- its day begins, so there is no gap right after midnight. It runs entirely
-- inside Supabase via pg_cron (Postgres' built-in scheduler) -- no external
-- service required.
--
-- The selection is a random REGULAR-SEASON row from season_team_stats. The
-- composite foreign key on daily_puzzle guarantees the chosen (team, season)
-- actually has a regular-season stat line.
--
-- Applied automatically on push to main by .github/workflows/migrate.yml.

-- 1. Enable pg_cron. Safe to run if it is already enabled.
--    If this line fails with a permissions error, enable "pg_cron" once from the
--    Supabase dashboard (Database -> Extensions), then re-run the migration.
create extension if not exists pg_cron;

-- 2. The selection logic, wrapped in a function so it is easy to re-deploy
--    (create or replace) and to test by hand: select public.pick_daily_puzzle();
create or replace function public.pick_daily_puzzle()
returns void
language plpgsql
as $fn$
declare
    -- Prepare TOMORROW's puzzle so it is ready before the day starts. "Tomorrow"
    -- is computed in America/New_York to match the API (app.daily.zone); the DB's
    -- own CURRENT_DATE is UTC and can differ by a day, so we must NOT use it here.
    target_date date := (now() at time zone 'America/New_York')::date + 1;  -- tomorrow (NY)
begin
    insert into public.daily_puzzle (puzzle_date, team_id, season_id, regular_season)
    select
        target_date,
        s.team_id,
        s.season_id,
        true                       -- always a regular-season stat line
    from public.season_team_stats s
    where s.regular_season = true
      -- Don't repeat the exact (team, season) puzzle within the last 90 days.
      and not exists (
          select 1
          from public.daily_puzzle d
          where d.puzzle_date >= target_date - 90
            and d.team_id   = s.team_id
            and d.season_id = s.season_id
      )
      -- ...and don't repeat the same team (any season) within the last 10 days.
      and not exists (
          select 1
          from public.daily_puzzle d
          where d.puzzle_date >= target_date - 10
            and d.team_id = s.team_id
      )
    order by random()
    limit 1
    -- If today's puzzle already exists (job re-ran, or it was seeded by hand),
    -- leave it untouched instead of erroring or replacing it.
    on conflict (puzzle_date) do nothing;
end;
$fn$;

-- 3. Schedule the function to run once a day at 03:00 US Eastern. pg_cron reads
--    schedules in UTC and cannot track DST, so we pin it to 07:00 UTC = 03:00 EDT
--    (summer) / 02:00 EST (winter). Running in the small hours (well within one
--    NY day) keeps "tomorrow" unambiguous, so each run prepares the following
--    day's puzzle. Unschedule any prior copy first so re-applying this file is safe.
select cron.unschedule('pick-daily-puzzle')
where exists (select 1 from cron.job where jobname = 'pick-daily-puzzle');

select cron.schedule(
    'pick-daily-puzzle',
    '0 7 * * *',
    'select public.pick_daily_puzzle();'
);
