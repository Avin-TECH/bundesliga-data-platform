-- Fact table: one row per team per season with derived metrics
-- Joins staging models and adds calculated business metrics

with teams as (
    select * from {{ ref('stg_teams') }}
),

standings as (
    select * from {{ ref('stg_standings') }}
)

select
    s.standing_id,
    s.team_id,
    t.team_name,
    t.team_code,
    s.season,
    s.position,
    s.played_games,
    s.games_won,
    s.games_drawn,
    s.games_lost,
    s.points,
    s.goals_for,
    s.goals_against,
    s.goal_difference,

    -- Derived metrics
    round(s.points::numeric / nullif(s.played_games, 0), 2) as points_per_game,
    round(s.games_won::numeric / nullif(s.played_games, 0) * 100, 1) as win_percentage,
    round(s.goals_for::numeric / nullif(s.played_games, 0), 2) as goals_per_game,
    round(s.goals_against::numeric / nullif(s.played_games, 0), 2) as goals_conceded_per_game,

    -- Tier classification
    case
        when s.position <= 4 then 'Champions League'
        when s.position <= 6 then 'Europa League'
        when s.position >= 16 then 'Relegation Zone'
        else 'Mid-Table'
    end as season_tier,

    s.recorded_at

from standings s
join teams t on s.team_id = t.team_id
order by s.position
