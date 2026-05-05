-- Staging model: cleaned team data
-- Source: public.teams (loaded by Python ingestion)

with source as (
    select * from public.teams
)

select
    team_id,
    name as team_name,
    short_name,
    tla as team_code,
    crest_url,
    created_at
from source
