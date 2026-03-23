-- Prelude v1 Migration: Add feature_signals and voc_output columns
-- Run: psql $PRELUDE_DB_URL -f backend/prelude/migrations/v1_add_feature_signals_and_voc.sql

-- Feature signals extracted from variant descriptions at brief time
ALTER TABLE experiments ADD COLUMN IF NOT EXISTS feature_signals JSONB;

-- Voice of Customer structured output from LLM-driven simulation
ALTER TABLE run_signals ADD COLUMN IF NOT EXISTS voc_output JSONB;
