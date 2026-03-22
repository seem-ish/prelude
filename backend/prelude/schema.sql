-- Prelude Database Schema
-- Run: psql $PRELUDE_DB_URL -f backend/prelude/schema.sql

CREATE EXTENSION IF NOT EXISTS "pgcrypto";

CREATE TABLE IF NOT EXISTS teams (
  id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name       TEXT NOT NULL,
  category   TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS persona_definitions (
  id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  slug                TEXT UNIQUE NOT NULL,
  name                TEXT NOT NULL,
  cluster             TEXT NOT NULL,
  short_desc          TEXT,
  description         TEXT,
  traits              JSONB,
  motivations         JSONB,
  fears               JSONB,
  triggers            JSONB,
  abandonment_signals JSONB,
  journey_pattern     TEXT,
  representative_quote TEXT,
  category_relevance  JSONB
);

CREATE TABLE IF NOT EXISTS team_personas (
  id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  team_id       UUID REFERENCES teams(id),
  base_persona  TEXT REFERENCES persona_definitions(slug),
  custom_name   TEXT,
  custom_traits JSONB,
  notes         TEXT,
  created_at    TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS experiments (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  team_id         UUID REFERENCES teams(id),
  title           TEXT NOT NULL,
  problem         TEXT,
  variant_a       TEXT,
  variant_b       TEXT,
  target_user     TEXT,
  success_metric  TEXT,
  product_context TEXT,
  category        TEXT,
  status          TEXT DEFAULT 'draft',
  created_at      TIMESTAMPTZ DEFAULT NOW(),
  updated_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS agents (
  id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  experiment_id UUID REFERENCES experiments(id),
  name          TEXT,
  persona_blend JSONB,
  traits        JSONB,
  backstory     TEXT,
  created_at    TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS simulation_runs (
  id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  experiment_id UUID REFERENCES experiments(id),
  variant       TEXT NOT NULL,
  agent_count   INTEGER,
  status        TEXT DEFAULT 'queued',
  started_at    TIMESTAMPTZ,
  completed_at  TIMESTAMPTZ,
  raw_output    JSONB,
  error_log     TEXT
);

CREATE TABLE IF NOT EXISTS agent_events (
  id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  run_id       UUID REFERENCES simulation_runs(id),
  agent_id     UUID REFERENCES agents(id),
  event_type   TEXT,
  content      TEXT,
  sentiment    NUMERIC,
  journey_step TEXT,
  created_at   TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS run_signals (
  id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  run_id              UUID REFERENCES simulation_runs(id) UNIQUE,
  adoption_by_segment JSONB,
  friction_heatmap    JSONB,
  sentiment_arc       JSONB,
  top_quotes          JSONB,
  behavioral_patterns JSONB,
  created_at          TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS predictions (
  id                   UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  experiment_id        UUID REFERENCES experiments(id) UNIQUE,
  winner               TEXT,
  confidence           TEXT,
  confidence_rationale TEXT,
  segment_story        JSONB,
  mechanism            TEXT,
  key_risk             TEXT,
  watch_items          JSONB,
  recommended_mod      TEXT,
  created_at           TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS calibration_log (
  id                UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  experiment_id     UUID REFERENCES experiments(id) UNIQUE,
  predicted_winner  TEXT,
  actual_winner     TEXT,
  direction_correct BOOLEAN,
  segment_correct   BOOLEAN,
  friction_correct  BOOLEAN,
  notes             TEXT,
  logged_at         TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_experiments_team  ON experiments(team_id);
CREATE INDEX IF NOT EXISTS idx_agents_experiment ON agents(experiment_id);
CREATE INDEX IF NOT EXISTS idx_events_run        ON agent_events(run_id);
