"""
Prelude sample data seed.
Creates two pre-built experiments with full prediction readouts.
Idempotent — safe to run multiple times.

Usage:
    python3 backend/prelude/seed_sample_data.py
"""

import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), "../../.env"))

from prelude.db import get_conn
import psycopg2.extras

# ---------------------------------------------------------------------------
# Sample experiments
# ---------------------------------------------------------------------------

SAMPLE_EXPERIMENTS = [
    {
        "title": "Fitness App — Onboarding Completion",
        "problem": (
            "55% of new users never complete the 4-step onboarding survey "
            "that unlocks their personalized workout plan. We lose them before "
            "they experience any core value."
        ),
        "variant_a": (
            "Guided 3-step onboarding with a progress bar, estimated time "
            "('2 min'), and a preview of what they'll unlock. Each step is "
            "one focused question."
        ),
        "variant_b": (
            "Single long-scroll onboarding page with all questions visible "
            "at once. Skip button prominent at the top."
        ),
        "target_user": (
            "Health-conscious adults 25–45, mix of first-time fitness app "
            "users and people switching from a competitor. Mobile-first."
        ),
        "success_metric": "Onboarding completion within 24 hours of signup",
        "product_context": "A fitness tracking app with free and paid tiers",
        "category": "fitness",
        "status": "complete",
    },
    {
        "title": "Grocery Delivery — Trial to Paid Conversion",
        "problem": (
            "70% of free trial users don't convert when the trial ends, "
            "despite high engagement during the trial period. They use the "
            "product but don't pay for it."
        ),
        "variant_a": (
            "Personalized savings email: 'Your free deliveries saved you $47 "
            "this month. Keep saving for $9.99/month.'"
        ),
        "variant_b": (
            "Feature unlock email: 'Upgrade to unlock exclusive member prices "
            "and priority delivery slots.'"
        ),
        "target_user": (
            "Urban adults 28–45, primary household grocery shopper, used "
            "4+ deliveries during trial period."
        ),
        "success_metric": "Paid subscription activation within 7 days of trial expiry",
        "product_context": "A grocery delivery subscription service",
        "category": "retail",
        "status": "complete",
    },
]

# ---------------------------------------------------------------------------
# Pre-built prediction readouts
# ---------------------------------------------------------------------------

SAMPLE_PREDICTIONS = [
    {
        # Fitness — Onboarding
        "winner": "a",
        "confidence": "high",
        "confidence_rationale": (
            "Both variants are clearly differentiated. Fitness category personas "
            "are well-specified, and the primary abandonment driver (ambiguity about "
            "time investment) is directly addressed by Variant A."
        ),
        "segment_story": [
            {
                "persona": "Decision Deferrer",
                "weight": 0.31,
                "preference": "strongly_a",
                "narrative": (
                    "Decision Deferrer agents were the primary beneficiaries of "
                    "Variant A's progress indicator. Seeing '1 of 3 · About 2 "
                    "minutes' immediately resolved their core hesitation — 'how "
                    "long is this going to take?' — and allowed them to commit to "
                    "starting. In Variant B, 67% of Decision Deferrer agents clicked "
                    "the skip button without completing a single field."
                ),
                "best_quote": (
                    "I can see there are only 3 steps and it says 2 minutes. "
                    "That I can do right now."
                ),
            },
            {
                "persona": "Passive Subscriber",
                "weight": 0.24,
                "preference": "prefers_a",
                "narrative": (
                    "Passive Subscriber agents responded well to the structured "
                    "format of Variant A. The clear progression reduced the cognitive "
                    "load of deciding 'how much of this do I have to do.' Most "
                    "completed steps 1 and 2 automatically, carried by momentum."
                ),
                "best_quote": "Oh, that's it? I thought it would be longer.",
            },
            {
                "persona": "One-Click Converter",
                "weight": 0.12,
                "preference": "neutral",
                "narrative": (
                    "One-Click Converters completed both variants at similar rates. "
                    "They were motivated enough to get through onboarding regardless "
                    "of format. Variant B's skip option was briefly tempting, but "
                    "most proceeded anyway."
                ),
                "best_quote": "I just want to get to the workout plan already.",
            },
            {
                "persona": "Early Adopter",
                "weight": 0.08,
                "preference": "prefers_b",
                "narrative": (
                    "Early Adopter agents preferred seeing the full scope upfront. "
                    "Variant B's long-scroll felt more transparent and less patronizing "
                    "to this segment. However, their small population share (8%) "
                    "means this preference doesn't affect the overall outcome."
                ),
                "best_quote": (
                    "I actually like seeing everything at once — I can decide "
                    "what matters to me."
                ),
            },
            {
                "persona": "Complexity Avoider",
                "weight": 0.18,
                "preference": "strongly_a",
                "narrative": (
                    "Complexity Avoider agents abandoned Variant B at the skip button "
                    "at an 82% rate. For this segment, a visible skip option reads as "
                    "a signal that the content is optional and burdensome — permission "
                    "to disengage. Variant A's focused single-question format felt "
                    "manageable by comparison."
                ),
                "best_quote": (
                    "There's a skip button so I can always come back to it later. "
                    "[never returns]"
                ),
            },
        ],
        "mechanism": (
            "Variant A wins by removing the primary abandonment trigger for the "
            "Fitness category: ambiguity about time investment. The progress bar "
            "and '2 minutes' label address the single most common question in "
            "agents' minds before they've started — 'how long is this going to "
            "take?' — before it can become a reason to leave."
        ),
        "key_risk": (
            "This prediction assumes users trust the '2 minutes' estimate. If "
            "onboarding consistently takes longer than 3 minutes in production, "
            "the broken promise in step 2 will erode trust and drive abandonment "
            "— potentially worse than the Variant B baseline."
        ),
        "watch_items": [
            {
                "item": "Time-to-complete for Variant A",
                "metric": "Median completion time. Flag if >3.5 minutes.",
                "rationale": (
                    "The '2 min' label is Variant A's key conversion lever. "
                    "If it's a lie, it becomes a liability."
                ),
            },
            {
                "item": "One-Click Converter drop-off by variant",
                "metric": "Completion rate for One-Click Converters in A vs B.",
                "rationale": (
                    "This segment found Variant A 'patronizing' in simulation. "
                    "Watch whether they complete at lower rates than the overall."
                ),
            },
            {
                "item": "Step 2 friction in both variants",
                "metric": "Drop-off rate at step 2 ('About You') vs other steps.",
                "rationale": (
                    "Step 2 showed elevated friction in both simulations. "
                    "Regardless of winner, this step warrants a follow-up experiment."
                ),
            },
        ],
        "recommended_mod": (
            "Add a 'Save and continue later' option at the bottom of each step "
            "in Variant A. Decision Deferrer agents who feel time pressure from "
            "committing to all 3 steps will benefit from an explicit 'I'll come "
            "back' path — reducing full abandonment to partial completion that "
            "can be resumed."
        ),
    },
    {
        # Grocery — Trial to Paid
        "winner": "a",
        "confidence": "medium",
        "confidence_rationale": (
            "Variant A shows a clear edge, but the grocery retail category has "
            "meaningful representation from both value-driven and convenience-driven "
            "segments that split on variant preference. Confidence is medium because "
            "the winning margin is real but not decisive."
        ),
        "segment_story": [
            {
                "persona": "Deal Hunter",
                "weight": 0.28,
                "preference": "strongly_a",
                "narrative": (
                    "Deal Hunter agents responded strongly to Variant A's specific "
                    "dollar figure ($47). This segment calculates ROI before every "
                    "commitment, and a concrete savings number does that math for "
                    "them. Variant B's 'exclusive member prices' was too vague — "
                    "'exclusive compared to what?' was a recurring objection."
                ),
                "best_quote": (
                    "$47 saved last month means the $9.99 fee pays for itself in "
                    "less than a quarter of a delivery. That's straightforward."
                ),
            },
            {
                "persona": "Free Trial Maximizer",
                "weight": 0.22,
                "preference": "prefers_a",
                "narrative": (
                    "Free Trial Maximizer agents — those who use free trials "
                    "strategically — were moved by the retrospective framing of "
                    "Variant A. Showing what they already extracted made the "
                    "transition feel like protecting existing gains rather than "
                    "starting a new cost relationship."
                ),
                "best_quote": (
                    "I didn't realize I'd gotten that much value out of it. "
                    "Okay, $10 a month seems reasonable."
                ),
            },
            {
                "persona": "Convenience Driven Parent",
                "weight": 0.20,
                "preference": "prefers_b",
                "narrative": (
                    "Convenience-driven segments responded more to Variant B's "
                    "feature framing — 'priority delivery slots' spoke directly "
                    "to their core need (reliability and speed). The savings "
                    "calculation in Variant A required mental effort this segment "
                    "was reluctant to invest."
                ),
                "best_quote": (
                    "Priority slots would actually be useful for me. I hate "
                    "having to plan around 4-hour windows."
                ),
            },
            {
                "persona": "Passive Subscriber",
                "weight": 0.18,
                "preference": "prefers_a",
                "narrative": (
                    "Passive Subscribers responded to social proof and retrospective "
                    "value. The '$47 saved' frame made the subscription feel like "
                    "a continuation of something already working, not a new decision. "
                    "This reduced the activation energy to convert."
                ),
                "best_quote": "I already use it all the time. I guess I should just pay for it.",
            },
            {
                "persona": "Price Shock Abandoner",
                "weight": 0.12,
                "preference": "neutral",
                "narrative": (
                    "Price Shock Abandoner agents didn't convert well on either "
                    "variant. For this segment, the conversion barrier isn't "
                    "framing — it's the $9.99 price point itself. Neither "
                    "message resolved the objection."
                ),
                "best_quote": "$10 a month is still $120 a year. I'm not sure I want that commitment.",
            },
        ],
        "mechanism": (
            "Variant A wins by anchoring the value decision in past behavior "
            "rather than future promises. '$47 saved' is a verified, personal "
            "number — it requires no trust in marketing claims. Variant B asks "
            "users to imagine future value ('exclusive prices'), which is a "
            "higher cognitive and trust burden. For a category where value-driven "
            "segments dominate (50% of this population), concrete retrospective "
            "data outperforms aspirational feature language."
        ),
        "key_risk": (
            "The $47 figure is only compelling if it's personalized and accurate. "
            "If the savings calculation uses average order value rather than the "
            "individual's actual orders, the number may feel generic or "
            "implausible — and a wrong specific number is worse than a vague "
            "general claim."
        ),
        "watch_items": [
            {
                "item": "Personalization accuracy of the savings figure",
                "metric": (
                    "% of Variant A emails where displayed savings match "
                    "user's actual order history within 10%."
                ),
                "rationale": (
                    "The entire mechanism depends on the number being credible. "
                    "Audit the calculation before launch."
                ),
            },
            {
                "item": "Conversion rate for Convenience-Driven segment",
                "metric": "Trial-to-paid conversion for users with 6+ orders in trial.",
                "rationale": (
                    "Heavy users (likely convenience-driven) showed stronger "
                    "response to Variant B. Consider a segmented send."
                ),
            },
            {
                "item": "Price Shock Abandoner fallout",
                "metric": "Unsubscribe rate post-conversion email for both variants.",
                "rationale": (
                    "Neither variant converts price-sensitive users. Watch for "
                    "backlash (unsubscribes, spam reports) from this segment."
                ),
            },
        ],
        "recommended_mod": (
            "Test a hybrid variant: lead with the personal savings figure "
            "('$47 saved'), then add the feature hook as secondary ("
            "'Plus: unlock priority delivery slots'). This captures Variant A's "
            "proven value anchor while addressing the Convenience-Driven "
            "segment's primary motivation."
        ),
    },
]


# ---------------------------------------------------------------------------
# Seed logic
# ---------------------------------------------------------------------------

def seed():
    print("Seeding Prelude sample data...")
    with get_conn() as conn:
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        # Ensure a default team exists
        cur.execute("SELECT id FROM teams WHERE name = 'Demo Team' LIMIT 1")
        row = cur.fetchone()
        if row:
            team_id = row["id"]
            print(f"  Team already exists: {team_id}")
        else:
            cur.execute(
                "INSERT INTO teams (name, category) VALUES (%s, %s) RETURNING id",
                ("Demo Team", "mixed"),
            )
            team_id = cur.fetchone()["id"]
            print(f"  Created team: {team_id}")

        for exp_data, pred_data in zip(SAMPLE_EXPERIMENTS, SAMPLE_PREDICTIONS):
            # Idempotency: check by title
            cur.execute(
                "SELECT id FROM experiments WHERE title = %s LIMIT 1",
                (exp_data["title"],),
            )
            row = cur.fetchone()
            if row:
                exp_id = row["id"]
                print(f"  Experiment already exists: {exp_data['title'][:40]}...")
            else:
                cur.execute(
                    """
                    INSERT INTO experiments
                      (team_id, title, problem, variant_a, variant_b,
                       target_user, success_metric, product_context, category, status)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING id
                    """,
                    (
                        team_id,
                        exp_data["title"],
                        exp_data["problem"],
                        exp_data["variant_a"],
                        exp_data["variant_b"],
                        exp_data["target_user"],
                        exp_data["success_metric"],
                        exp_data["product_context"],
                        exp_data["category"],
                        exp_data["status"],
                    ),
                )
                exp_id = cur.fetchone()["id"]
                print(f"  Created experiment: {exp_data['title'][:40]}...")

            # Seed prediction (idempotent via UNIQUE constraint)
            import json
            cur.execute(
                "SELECT id FROM predictions WHERE experiment_id = %s LIMIT 1",
                (exp_id,),
            )
            if cur.fetchone():
                print(f"  Prediction already exists for: {exp_data['title'][:40]}...")
            else:
                cur.execute(
                    """
                    INSERT INTO predictions
                      (experiment_id, winner, confidence, confidence_rationale,
                       segment_story, mechanism, key_risk, watch_items, recommended_mod)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """,
                    (
                        exp_id,
                        pred_data["winner"],
                        pred_data["confidence"],
                        pred_data["confidence_rationale"],
                        json.dumps(pred_data["segment_story"]),
                        pred_data["mechanism"],
                        pred_data["key_risk"],
                        json.dumps(pred_data["watch_items"]),
                        pred_data["recommended_mod"],
                    ),
                )
                print(f"  Created prediction for: {exp_data['title'][:40]}...")

        conn.commit()
        cur.close()

    print("Done. Sample data seeded successfully.")


if __name__ == "__main__":
    seed()
