# Prelude

**Predict how real users will react — before you run the test.**

Prelude is an AI-powered A/B test prediction tool built on [MiroFish](https://github.com/666ghj/MiroFish).
Give it an experiment brief, and it simulates how 200 persona-blended agents respond to each variant,
then delivers a structured prediction you can put in a PRD.

## What It Does

1. **Brief** — describe your experiment (problem, Variant A, Variant B, target user)
2. **Personas** — explore 40 user archetypes; Prelude auto-selects a relevant population
3. **Simulation** — 200 hybrid agents run both variants live via MiroFish
4. **Prediction** — winner call, segment breakdown, friction heatmap, agent stories, key risk
5. **Calibration** — log real outcomes, track prediction accuracy over time

## Tech Stack

- **Frontend**: Vue 3 + Vite + Vue Router
- **Backend**: Flask + Blueprints (Python 3.13)
- **Database**: PostgreSQL 15
- **Simulation Engine**: MiroFish (multi-agent framework)
- **LLM**: Claude (Anthropic)

## Setup

See [CHECKLIST.md](./CHECKLIST.md) for the full incremental build guide.

```bash
npm run setup:all
createdb prelude
psql $PRELUDE_DB_URL -f backend/prelude/schema.sql
python3 backend/prelude/seed_sample_data.py
npm run dev
```
