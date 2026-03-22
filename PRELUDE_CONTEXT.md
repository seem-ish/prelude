# Prelude — Project Context & Handoff

> Consumer behavior simulation platform for product managers.
> Built on a fork of MiroFish. Retail-focused (Grocery + Fashion).
> GitHub: `git@github.com:seem-ish/prelude.git`

---

## What Prelude Does

A PM enters a brief describing a feature they want to test (e.g. "checkout abandonment recovery — free shipping vs. discount code"). Prelude simulates how 200 synthetic consumer agents react to each variant and returns a prediction with segment-level breakdowns, before any real A/B test is run.

**The core value:** distribution over point estimate. Instead of "ChatGPT says Variant A wins," you get "Deal Hunters break 78% for A, Brand Loyalists split 61/39, here's why."

---

## Stack

| Layer | Technology |
|---|---|
| Frontend | Vue 3 (`<script setup>`) + Vite, port 3000 |
| Backend | Flask (Python) with Blueprints, port 5001 |
| Database | PostgreSQL (`prelude` DB) via psycopg2 |
| Dev runner | `npm run dev` (concurrently — starts both) |
| LLM (optional) | Claude via Anthropic API (`LLM_API_KEY` in `.env`) |

---

## Repository Structure

```
prelude/
├── backend/
│   └── prelude/
│       ├── app.py                  # Flask app factory, mounts /api/prelude
│       ├── db.py                   # psycopg2 helpers: query(), execute(), execute_returning()
│       ├── api/
│       │   ├── router.py           # All blueprints registered here
│       │   ├── experiments.py      # CRUD for experiments
│       │   ├── brief.py            # Brief save + LLM assist endpoint
│       │   ├── personas.py         # List/filter/get personas
│       │   ├── population.py       # Population generate/build/preview
│       │   ├── simulation.py       # Start simulation, SSE event stream
│       │   ├── prediction.py       # Prediction + log real outcome
│       │   └── calibration.py      # Calibration log + team stats
│       └── agents/
│           ├── persona_library.py  # 40 persona definitions (1803 lines)
│           ├── population_generator.py  # Algorithmic persona scoring
│           └── hybrid_builder.py   # Build 200 hybrid agents from personas
├── frontend/
│   └── src/prelude/
│       ├── pages/
│       │   ├── Dashboard.vue       # Experiment list, status, calibration score
│       │   ├── Brief.vue           # 4-step brief form
│       │   ├── Personas.vue        # Persona browser + Population builder (1011 lines)
│       │   ├── SimRoom.vue         # Simulation room, live event stream (1171 lines)
│       │   └── Readout.vue         # Prediction readout + log real outcome (1220 lines)
│       └── router/index.js         # Routes: /prelude, /prelude/brief, etc.
├── .env                            # Never commit — see env vars below
└── package.json                    # npm run dev starts both servers
```

---

## Environment Variables (`.env`)

```bash
LLM_API_KEY=your_anthropic_key          # Required for LLM assist + backstories
LLM_BASE_URL=https://api.anthropic.com/v1
LLM_MODEL_NAME=claude-sonnet-4-20250514
PRELUDE_DB_URL=postgresql://localhost:5432/prelude
PRELUDE_ENV=development
FLASK_HOST=0.0.0.0
FLASK_PORT=5001
FLASK_DEBUG=true
```

---

## API Endpoints (all under `/api/prelude`)

```
GET    /health

# Experiments
GET    /experiments                              # list all
POST   /experiments                              # create from brief
GET    /experiments/:id                          # get one
PATCH  /experiments/:id                          # update

# Brief
POST   /experiments/assist                       # LLM assist for any field

# Personas
GET    /personas                                 # all 40
GET    /personas?cluster=value_driven            # filtered
GET    /personas/:slug                           # single persona

# Population (per experiment)
POST   /experiments/:id/population/generate      # suggest population from brief
POST   /experiments/:id/population/build         # build 200 agents
GET    /experiments/:id/population               # get population + sample agents
POST   /experiments/:id/population/preview-agent # preview one hybrid agent

# Simulation
POST   /experiments/:id/simulation/start         # start simulation run
GET    /experiments/:id/simulation/stream        # SSE event stream
GET    /experiments/:id/simulation/status        # run status + progress

# Prediction
GET    /experiments/:id/prediction               # get prediction readout
POST   /experiments/:id/outcome                  # log real A/B result

# Calibration
GET    /experiments/:id/calibration              # single experiment calibration
GET    /team/calibration                         # team-wide calibration stats
```

---

## The 40 Personas

All defined in `backend/prelude/agents/persona_library.py`. Three domains of relevance: **retail**, **social_media**, **fintech**.

### Clusters (6)

| Cluster | Count | Color | Key Personas |
|---|---|---|---|
| `value_driven` | 7 | Amber `#F0A843` | deal_hunter, coupon_stacker, bulk_buyer |
| `convenience_driven` | 6 | Teal `#3BC4A0` | time_starved_parent, one_click_converter |
| `trust_driven` | 7 | Blue `#5BADEE` | brand_loyalist, skeptic, review_reader |
| `identity_driven` | 6 | Purple `#A78BFA` | status_signaler, early_adopter, premium_seeker |
| `situational` | 7 | Coral `#F07858` | seasonal_shopper, lapsed_returner, gift_recipient |
| `resistance` | 7 | Red `#F05858` | price_shock_abandoner, decision_deferrer, active_canceler |

### All 40 Slugs

```
VALUE (7):         deal_hunter, meticulous_optimizer, coupon_stacker,
                   comparison_shopper, sunk_cost_holder, free_trial_maximizer, bulk_buyer

CONVENIENCE (6):   time_starved_parent, passive_subscriber, one_click_converter,
                   repeat_habit_user, low_effort_decider, auto_renewer

TRUST (7):         brand_loyalist, social_proof_seeker, influencer_follower,
                   review_reader, word_of_mouth_converter, skeptic, privacy_conscious

IDENTITY (6):      status_signaler, early_adopter, premium_seeker,
                   conscious_consumer, community_member, power_user

SITUATIONAL (7):   gift_recipient, corporate_user, seasonal_shopper,
                   life_event_trigger, reluctant_subscriber, lapsed_returner, trial_convert

RESISTANCE (7):    active_canceler, passive_churner, price_shock_abandoner,
                   complexity_avoider, decision_deferrer, silent_dissatisfied, feature_mismatcher
```

### Persona Data Shape

```python
{
  "slug": "deal_hunter",
  "name": "The Deal Hunter",
  "cluster": "value_driven",
  "short_desc": "Calculates ROI on everything. Won't commit without proof of savings.",
  "description": "...",
  "traits": {
    "price_sensitivity":     0.95,   # all 0–1
    "trust_baseline":        0.40,
    "decision_speed":        0.30,
    "tech_comfort":          0.65,
    "frustration_threshold": 0.55,
    "research_depth":        0.90,
    "social_influence":      0.20,
    "risk_tolerance":        0.30
  },
  "motivations":          ["...", "...", "..."],
  "fears":                ["...", "...", "..."],
  "triggers":             ["...", "...", "..."],
  "abandonment_signals":  ["...", "...", "..."],
  "journey_pattern":      "Reads everything → calculates → compares alternatives → decides or leaves",
  "representative_quote": "I need to know exactly what I'm getting and whether the math works out.",
  "category_relevance": {
    "retail":       0.95,
    "social_media": 0.30,
    "fintech":      0.90
  }
}
```

---

## How Agents Are Built (No LLM Required)

### 1. Population Scoring (`population_generator.py`)

Each persona is scored against the experiment brief using:

```
final_score = 0.6 * keyword_overlap + 0.4 * category_relevance[domain]
```

Top 8–12 personas are selected. Weights are assigned inversely proportional to rank, then normalized to sum to 1.0.

### 2. Hybrid Agent Building (`hybrid_builder.py`)

200 agents are built from the weighted persona set:

```
Agent = Primary persona (65%) + Secondary (25%) + optional Tertiary (10%)
Trait vector = weighted average of component persona traits
Name = randomly drawn from 120+ culturally diverse name pool
Backstory = template-filled from persona data (no LLM)
```

To use real LLM backstories: replace `_generate_backstory()` in `hybrid_builder.py` with an Anthropic API call — the function signature and return type don't change.

### 3. Simulation Events (`simulation.py`)

Events are generated algorithmically from trait math:

```python
disposition = (trust_baseline * 0.4) + (frustration_threshold * 0.3) + (openness * 0.3)
# Each step: sentiment drifts based on disposition + stimulus + noise
# Low disposition agents abandon mid-journey
```

Streamed to the frontend via SSE (`/simulation/stream`).

---

## Scope: Retail Only (Grocery + Fashion)

This build is scoped to **retail** with two sub-domains:

| Sub-domain | Key Personas | Top Use Cases |
|---|---|---|
| **Grocery** | bulk_buyer, repeat_habit_user, time_starved_parent, low_effort_decider | Loyalty programs, subscription bundles, click-and-collect, private label switching |
| **Fashion** | status_signaler, price_shock_abandoner, conscious_consumer, brand_loyalist | Checkout abandonment, new collection launch, size/fit friction, returns experience |

### Top 5 Retail Use Cases

1. **Checkout abandonment recovery** — Free shipping vs. discount code (works for both grocery + fashion)
2. **Loyalty program upsell** — Points-based vs. tier-based membership (grocery dominant)
3. **New collection/product launch** — Early access email vs. in-app push (fashion dominant)
4. **Subscription bundle introduction** — Fixed bundle vs. build-your-own (grocery dominant)
5. **Returns experience redesign** — Free returns label in box vs. drop-off QR code (fashion dominant)

---

## Build Slices — Completion Status

| Slice | Name | Status | Commit |
|---|---|---|---|
| 0 | Foundation (Flask + Vue + Postgres) | ✅ Done | `chore(s0)` |
| 1 | Dashboard | ✅ Done | `feat(s1)` |
| 2 | Brief Builder | ✅ Done | `feat(s2)` |
| 3 | Persona Browser | ✅ Done | `feat(s3)` |
| 4 | Population Builder | ✅ Done | `feat(s4)` |
| 5 | Simulation Room | ✅ Done | `feat(s5-s7)` |
| 6 | Prediction Readout | ✅ Done | `feat(s5-s7)` |
| 7 | Calibration Log | ✅ Done | `feat(s5-s7)` |

All 8 slices shipped. Full end-to-end flow works without an LLM API key (algorithmic simulation + template backstories). Wire `LLM_API_KEY` for LLM-assisted brief writing and richer backstories.

---

## Running Locally

```bash
# 1. Clone
git clone git@github.com:seem-ish/prelude.git
cd prelude

# 2. Create .env (copy from above, fill in PRELUDE_DB_URL at minimum)
cp .env.example .env

# 3. Create Postgres DB
createdb prelude

# 4. Install deps
npm install
pip install -r backend/requirements.txt  # or: cd backend && pip install -e .

# 5. Run (starts Flask on :5001 and Vite on :3000)
npm run dev

# 6. Open
open http://localhost:3000/prelude
```

---

## Key Vue Architecture Notes

- **`Teleport to="#app"`** is used in `Personas.vue` and `SimRoom.vue` for overlay panels. This is required because `overflow-y: auto` on `.p-main` creates a CSS stacking context that traps `position: fixed` children. Teleporting to `#app` escapes this.
- **Unscoped `<style>` block** alongside scoped styles — teleported elements lose Vue's scoped attribute, so their styles must be in a separate unscoped `<style>` block.
- **Props-based routing** — `Personas.vue` accepts `id` (experiment ID) prop. When `id` is present, it starts in Build mode (Population Builder). Without `id`, it's in Browse mode.

---

## Design System

| Token | Value |
|---|---|
| Background | `#0D0F0E` (near-black) |
| Primary accent | `#4AE89A` (green) |
| Heading font | DM Serif Display |
| Body font | DM Sans |
| Sidebar width | 220px |
| Card border | `rgba(255,255,255,0.06)` |

---

## What's Not Built Yet

- Real LLM reasoning per agent step (currently algorithmic)
- Agent-to-agent interaction / social graph (currently independent)
- Multi-team / org support
- Export to PDF / Confluence
- Slack integration for prediction delivery
- Fine-tuned calibration weighting (currently linear)

---

*Last updated: March 2026. All 8 slices complete. Retail-scoped (grocery + fashion).*
