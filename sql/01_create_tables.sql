-- =====================================================
-- Bundesliga Data Platform - Schema v1
-- Creates tables: teams, standings
-- =====================================================

-- Drop tables if they exist (for clean re-runs during development)
DROP TABLE IF EXISTS standings;
DROP TABLE IF EXISTS teams;

-- =====================================================
-- Table: teams
-- =====================================================
CREATE TABLE teams (
    team_id      INTEGER PRIMARY KEY,
    name         TEXT NOT NULL,
    short_name   TEXT,
    tla          TEXT,
    crest_url    TEXT,
    created_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- Table: standings
-- =====================================================
CREATE TABLE standings (
    standing_id      SERIAL PRIMARY KEY,
    team_id          INTEGER NOT NULL REFERENCES teams(team_id),
    season           INTEGER NOT NULL,
    position         INTEGER NOT NULL,
    played_games     INTEGER NOT NULL,
    won              INTEGER NOT NULL,
    draw             INTEGER NOT NULL,
    lost             INTEGER NOT NULL,
    points           INTEGER NOT NULL,
    goals_for        INTEGER NOT NULL,
    goals_against    INTEGER NOT NULL,
    goal_difference  INTEGER NOT NULL,
    recorded_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index for quick lookups by team and season
CREATE INDEX idx_standings_team_season ON standings(team_id, season);