-- Staging model: cleaned standings data
-- Source: public.standings (loaded by Python ingestion)

with source as (
    select * from public.standings
)

select
    standing_id,
    team_id,
    season,
    position,
    played_games,
    won as games_won,
    draw as games_drawn,
    lost as games_lost,
    points,
    goals_for,
    goals_against,
    goal_difference,
    recorded_at
from source
