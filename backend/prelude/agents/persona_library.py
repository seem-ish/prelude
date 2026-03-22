"""
Prelude — 40 Persona Definitions
Clusters: value_driven (7), convenience_driven (6), trust_driven (7),
          identity_driven (6), situational (7), resistance (7)
Domains: retail, social_media, fintech
"""

PERSONA_LIBRARY = [
    # ═══════════════════════════════════════════════════════════════════════════
    # VALUE DRIVEN (7)
    # ═══════════════════════════════════════════════════════════════════════════
    {
        "slug": "deal_hunter",
        "name": "The Deal Hunter",
        "cluster": "value_driven",
        "short_desc": "Calculates ROI on everything. Won't commit without proof of savings.",
        "description": (
            "Methodical and skeptical of vague value claims. Does the math before deciding. "
            "Responds to specifics — dollar figures, comparison data. "
            "Will abandon if the value equation isn't immediately clear."
        ),
        "traits": {
            "price_sensitivity": 0.95,
            "trust_baseline": 0.40,
            "decision_speed": 0.30,
            "tech_comfort": 0.65,
            "frustration_threshold": 0.55,
            "research_depth": 0.90,
            "social_influence": 0.20,
            "risk_tolerance": 0.30,
        },
        "motivations": [
            "Maximize value per dollar spent",
            "Feel smart about financial decisions",
            "Beat the system",
        ],
        "fears": [
            "Hidden fees discovered after signup",
            "Paying for features already owned elsewhere",
            "Being manipulated by dark patterns",
        ],
        "triggers": [
            "Specific dollar savings figures",
            "Side-by-side cost comparison",
            "Time-limited offer with clear expiry",
        ],
        "abandonment_signals": [
            "Vague 'save more' language without numbers",
            "Overlap with existing subscriptions",
            "No visible cancellation path",
        ],
        "journey_pattern": "Reads everything → calculates → compares alternatives → decides or leaves",
        "representative_quote": "I need to know exactly what I'm getting and whether the math works out for me.",
        "category_relevance": {"retail": 0.95, "social_media": 0.30, "fintech": 0.90},
    },
    {
        "slug": "meticulous_optimizer",
        "name": "The Meticulous Optimizer",
        "cluster": "value_driven",
        "short_desc": "Squeezes maximum value from every feature. Tracks spend obsessively.",
        "description": (
            "Uses spreadsheets, trackers, and dashboards to monitor value. "
            "Will use every free feature before paying. Upgrades only when the ROI is undeniable. "
            "Deeply annoyed by wasted money or redundant features."
        ),
        "traits": {
            "price_sensitivity": 0.85,
            "trust_baseline": 0.50,
            "decision_speed": 0.20,
            "tech_comfort": 0.80,
            "frustration_threshold": 0.45,
            "research_depth": 0.95,
            "social_influence": 0.15,
            "risk_tolerance": 0.25,
        },
        "motivations": [
            "Extract full value from every subscription",
            "Optimize personal financial efficiency",
            "Find the best possible deal before committing",
        ],
        "fears": [
            "Paying for features never used",
            "Missing a better deal after committing",
            "Automatic price increases without notice",
        ],
        "triggers": [
            "Usage reports showing value gained",
            "Clear feature comparison tables",
            "Money-back guarantees",
        ],
        "abandonment_signals": [
            "No usage analytics or value tracking",
            "Bundled features with no opt-out",
            "Opaque pricing tiers",
        ],
        "journey_pattern": "Maps all features → uses free tier fully → calculates upgrade ROI → decides slowly",
        "representative_quote": "Show me exactly what I'll use and what it costs per use — then we can talk.",
        "category_relevance": {"retail": 0.70, "social_media": 0.40, "fintech": 0.95},
    },
    {
        "slug": "coupon_stacker",
        "name": "The Coupon Stacker",
        "cluster": "value_driven",
        "short_desc": "Hunts promo codes and stacks discounts. Feels cheated paying full price.",
        "description": (
            "Actively searches for coupon codes before any checkout. "
            "Follows deal blogs and subreddits. Delights in combining multiple discounts. "
            "Will abandon cart rather than pay full price."
        ),
        "traits": {
            "price_sensitivity": 0.99,
            "trust_baseline": 0.35,
            "decision_speed": 0.45,
            "tech_comfort": 0.70,
            "frustration_threshold": 0.40,
            "research_depth": 0.80,
            "social_influence": 0.55,
            "risk_tolerance": 0.40,
        },
        "motivations": [
            "Never pay full price for anything",
            "Share great deals with friends",
            "Feel the thrill of a stacked discount",
        ],
        "fears": [
            "Paying full price when a coupon exists",
            "Expired codes with no alternatives",
            "Anti-stacking policies",
        ],
        "triggers": [
            "Visible promo code field at checkout",
            "Referral discount programs",
            "Flash sales with countdown timers",
        ],
        "abandonment_signals": [
            "No coupon field visible",
            "Codes that don't work",
            "Higher price than expected at checkout",
        ],
        "journey_pattern": "Finds product → searches for codes → tries stacking → buys or leaves",
        "representative_quote": "Hold on, let me check if there's a code for this first.",
        "category_relevance": {"retail": 0.95, "social_media": 0.20, "fintech": 0.55},
    },
    {
        "slug": "comparison_shopper",
        "name": "The Comparison Shopper",
        "cluster": "value_driven",
        "short_desc": "Opens 12 tabs before deciding. Needs to see every alternative.",
        "description": (
            "Compulsive comparison behavior. Reads reviews, checks competitors, "
            "watches YouTube breakdowns. Will not commit until confident no better option exists. "
            "Paralyzed by too many equal options."
        ),
        "traits": {
            "price_sensitivity": 0.80,
            "trust_baseline": 0.45,
            "decision_speed": 0.15,
            "tech_comfort": 0.75,
            "frustration_threshold": 0.50,
            "research_depth": 0.98,
            "social_influence": 0.60,
            "risk_tolerance": 0.20,
        },
        "motivations": [
            "Make the objectively best choice",
            "Avoid buyer's remorse",
            "Understand the full market before committing",
        ],
        "fears": [
            "Finding a better option after purchasing",
            "Missing a critical flaw mentioned in reviews",
            "Being locked in without trying alternatives",
        ],
        "triggers": [
            "Comparison tables with competitors",
            "Third-party reviews and ratings",
            "Free trial to test before committing",
        ],
        "abandonment_signals": [
            "No competitive comparison available",
            "Pressure tactics ('buy now or lose it')",
            "Lack of third-party validation",
        ],
        "journey_pattern": "Researches exhaustively → compares 5+ options → reads reviews → decides slowly or defers",
        "representative_quote": "I just want to make sure there isn't something better out there before I commit.",
        "category_relevance": {"retail": 0.90, "social_media": 0.35, "fintech": 0.85},
    },
    {
        "slug": "sunk_cost_holder",
        "name": "The Sunk Cost Holder",
        "cluster": "value_driven",
        "short_desc": "Stays because they've already invested. Loyalty driven by past spend.",
        "description": (
            "Reluctant to switch because of accumulated points, history, or emotional investment. "
            "Rationalizes staying even when unhappy. Responds to reminders of past value. "
            "Very hard to win back once they finally leave."
        ),
        "traits": {
            "price_sensitivity": 0.60,
            "trust_baseline": 0.55,
            "decision_speed": 0.25,
            "tech_comfort": 0.55,
            "frustration_threshold": 0.70,
            "research_depth": 0.40,
            "social_influence": 0.30,
            "risk_tolerance": 0.15,
        },
        "motivations": [
            "Protect accumulated investment (points, history, data)",
            "Avoid the pain of starting over",
            "Feel that loyalty is rewarded",
        ],
        "fears": [
            "Losing accumulated rewards or data",
            "Starting from zero on a new platform",
            "Admitting a past decision was wrong",
        ],
        "triggers": [
            "Loyalty milestone reminders",
            "Exclusive long-term member benefits",
            "Data portability guarantees",
        ],
        "abandonment_signals": [
            "Devaluation of accumulated rewards",
            "Major price increase without added value",
            "Competitor offering seamless migration",
        ],
        "journey_pattern": "Stays by default → grumbles quietly → considers leaving → stays because switching cost → eventually snaps",
        "representative_quote": "I've been here three years, I'm not throwing all that away.",
        "category_relevance": {"retail": 0.75, "social_media": 0.80, "fintech": 0.70},
    },
    {
        "slug": "free_trial_maximizer",
        "name": "The Free Trial Maximizer",
        "cluster": "value_driven",
        "short_desc": "Signs up for every free trial. Cancels on day 13 of 14.",
        "description": (
            "Expert at extracting value from free tiers and trials. "
            "Sets calendar reminders to cancel before charge. "
            "Will convert only if the product becomes genuinely indispensable during the trial."
        ),
        "traits": {
            "price_sensitivity": 0.90,
            "trust_baseline": 0.30,
            "decision_speed": 0.60,
            "tech_comfort": 0.80,
            "frustration_threshold": 0.50,
            "research_depth": 0.65,
            "social_influence": 0.25,
            "risk_tolerance": 0.55,
        },
        "motivations": [
            "Try everything without financial commitment",
            "Find the one tool worth actually paying for",
            "Game the system within the rules",
        ],
        "fears": [
            "Being charged after forgetting to cancel",
            "Trial requiring credit card upfront",
            "Losing work when trial expires",
        ],
        "triggers": [
            "No credit card required for trial",
            "Full feature access during trial",
            "Clear cancellation process",
        ],
        "abandonment_signals": [
            "Credit card required upfront",
            "Feature-limited trial",
            "Difficult cancellation flow",
        ],
        "journey_pattern": "Signs up → tests aggressively → sets cancel reminder → converts only if hooked",
        "representative_quote": "I'll try it, but I'm setting a reminder to cancel on day 13.",
        "category_relevance": {"retail": 0.60, "social_media": 0.65, "fintech": 0.80},
    },
    {
        "slug": "bulk_buyer",
        "name": "The Bulk Buyer",
        "cluster": "value_driven",
        "short_desc": "Buys in quantity for savings. Thinks in unit economics.",
        "description": (
            "Calculates per-unit cost and buys in bulk when the discount is right. "
            "Prefers annual over monthly plans. Responds to volume discounts. "
            "Annoyed by small-quantity-only options."
        ),
        "traits": {
            "price_sensitivity": 0.80,
            "trust_baseline": 0.55,
            "decision_speed": 0.50,
            "tech_comfort": 0.60,
            "frustration_threshold": 0.55,
            "research_depth": 0.70,
            "social_influence": 0.20,
            "risk_tolerance": 0.45,
        },
        "motivations": [
            "Minimize per-unit or per-month cost",
            "Lock in a good price for the long term",
            "Reduce the frequency of purchase decisions",
        ],
        "fears": [
            "Product quality declining after bulk commitment",
            "Being stuck with a year of something mediocre",
            "No refund on unused portion",
        ],
        "triggers": [
            "Annual plan discount (save 2 months free)",
            "Volume pricing tiers",
            "Bundle deals with clear savings",
        ],
        "abandonment_signals": [
            "Monthly-only pricing",
            "No bulk or annual discount",
            "Unclear refund policy for annual plans",
        ],
        "journey_pattern": "Calculates annual vs monthly → checks refund policy → commits to bulk if math works",
        "representative_quote": "What's the annual price? I'm not paying monthly if I can save by committing.",
        "category_relevance": {"retail": 0.90, "social_media": 0.25, "fintech": 0.65},
    },

    # ═══════════════════════════════════════════════════════════════════════════
    # CONVENIENCE DRIVEN (6)
    # ═══════════════════════════════════════════════════════════════════════════
    {
        "slug": "time_starved_parent",
        "name": "The Time-Starved Parent",
        "cluster": "convenience_driven",
        "short_desc": "Needs fast, clear value or abandons. Zero patience for complexity.",
        "description": (
            "Juggles work, kids, and life. Has maybe 90 seconds of attention to give. "
            "Needs the value proposition instantly clear. "
            "Will pay more for convenience and time savings."
        ),
        "traits": {
            "price_sensitivity": 0.40,
            "trust_baseline": 0.55,
            "decision_speed": 0.85,
            "tech_comfort": 0.60,
            "frustration_threshold": 0.25,
            "research_depth": 0.20,
            "social_influence": 0.65,
            "risk_tolerance": 0.50,
        },
        "motivations": [
            "Save time on decisions",
            "Simplify daily routines",
            "Feel like a competent parent despite being overwhelmed",
        ],
        "fears": [
            "Wasting limited free time on a bad product",
            "Complex setup that eats into family time",
            "Being judged for taking shortcuts",
        ],
        "triggers": [
            "One-tap purchase or signup",
            "'Takes 2 minutes' messaging",
            "Recommendations from other parents",
        ],
        "abandonment_signals": [
            "Multi-step signup process",
            "Requiring desktop for setup",
            "No immediate value visible",
        ],
        "journey_pattern": "Sees recommendation → checks in 30 seconds → signs up or moves on → never returns if first experience is slow",
        "representative_quote": "If it takes more than two minutes to set up, I'm out.",
        "category_relevance": {"retail": 0.85, "social_media": 0.70, "fintech": 0.60},
    },
    {
        "slug": "passive_subscriber",
        "name": "The Passive Subscriber",
        "cluster": "convenience_driven",
        "short_desc": "Set it and forget it. Pays monthly without checking if they still use it.",
        "description": (
            "Subscribes, uses it a few times, then forgets about it but keeps paying. "
            "Not price-sensitive enough to audit subscriptions regularly. "
            "Will cancel only when prompted by a bank statement review or price increase."
        ),
        "traits": {
            "price_sensitivity": 0.30,
            "trust_baseline": 0.65,
            "decision_speed": 0.70,
            "tech_comfort": 0.55,
            "frustration_threshold": 0.65,
            "research_depth": 0.10,
            "social_influence": 0.40,
            "risk_tolerance": 0.50,
        },
        "motivations": [
            "Not have to think about it",
            "Have it available 'just in case'",
            "Avoid the effort of canceling",
        ],
        "fears": [
            "Realizing they've wasted hundreds on unused subscriptions",
            "Losing access to something they might need later",
            "The hassle of re-subscribing if they cancel",
        ],
        "triggers": [
            "Automatic enrollment",
            "Low monthly price (under $15)",
            "No engagement required to maintain",
        ],
        "abandonment_signals": [
            "Price increase notification",
            "Bank statement audit",
            "Subscription management app flagging them",
        ],
        "journey_pattern": "Signs up → uses briefly → forgets → keeps paying → cancels months later or never",
        "representative_quote": "Honestly I forgot I was even subscribed to that.",
        "category_relevance": {"retail": 0.60, "social_media": 0.75, "fintech": 0.50},
    },
    {
        "slug": "one_click_converter",
        "name": "The One-Click Converter",
        "cluster": "convenience_driven",
        "short_desc": "Converts instantly if friction is zero. One extra step and they bounce.",
        "description": (
            "Impulsive but not irrational — they want what they want right now. "
            "Apple Pay, saved cards, autofill. "
            "Any friction between intent and purchase causes abandonment."
        ),
        "traits": {
            "price_sensitivity": 0.35,
            "trust_baseline": 0.60,
            "decision_speed": 0.95,
            "tech_comfort": 0.85,
            "frustration_threshold": 0.20,
            "research_depth": 0.10,
            "social_influence": 0.50,
            "risk_tolerance": 0.65,
        },
        "motivations": [
            "Instant gratification",
            "Seamless purchasing experience",
            "Not having to create yet another account",
        ],
        "fears": [
            "Forced account creation",
            "Multi-page checkout flows",
            "Re-entering payment information",
        ],
        "triggers": [
            "One-click buy button",
            "Apple Pay / Google Pay support",
            "Guest checkout option",
        ],
        "abandonment_signals": [
            "Account creation required before purchase",
            "More than 2 checkout steps",
            "No saved payment option",
        ],
        "journey_pattern": "Sees → wants → clicks → done (or gone)",
        "representative_quote": "If I can't buy this in two taps, I'll find someone who lets me.",
        "category_relevance": {"retail": 0.95, "social_media": 0.50, "fintech": 0.75},
    },
    {
        "slug": "repeat_habit_user",
        "name": "The Repeat Habit User",
        "cluster": "convenience_driven",
        "short_desc": "Uses the same product at the same time every day. Pure routine.",
        "description": (
            "Product is embedded in their daily routine. Opens the app at the same time, "
            "does the same thing. Extremely loyal by inertia. "
            "Will only leave if the routine is disrupted by a bad update."
        ),
        "traits": {
            "price_sensitivity": 0.40,
            "trust_baseline": 0.70,
            "decision_speed": 0.60,
            "tech_comfort": 0.65,
            "frustration_threshold": 0.55,
            "research_depth": 0.15,
            "social_influence": 0.35,
            "risk_tolerance": 0.20,
        },
        "motivations": [
            "Maintain their daily routine",
            "Consistent, predictable experience",
            "Not having to learn new tools",
        ],
        "fears": [
            "UI redesign that breaks their workflow",
            "Feature removal that disrupts their routine",
            "Forced updates that change behavior",
        ],
        "triggers": [
            "Consistent, reliable experience",
            "Notifications at their routine time",
            "Quick access to frequently used features",
        ],
        "abandonment_signals": [
            "Major UI redesign",
            "Removing a core feature they use daily",
            "Forced migration to a new version",
        ],
        "journey_pattern": "Opens daily → same flow every time → loyal for years → leaves suddenly if routine breaks",
        "representative_quote": "I open this app every morning with my coffee. Don't change it.",
        "category_relevance": {"retail": 0.55, "social_media": 0.90, "fintech": 0.80},
    },
    {
        "slug": "low_effort_decider",
        "name": "The Low-Effort Decider",
        "cluster": "convenience_driven",
        "short_desc": "Goes with the default every time. Too lazy to customize.",
        "description": (
            "Takes the path of least resistance on every decision. "
            "Accepts default settings, picks the first option, never reads the fine print. "
            "Not unintelligent — just unwilling to spend energy on decisions they view as low-stakes."
        ),
        "traits": {
            "price_sensitivity": 0.45,
            "trust_baseline": 0.60,
            "decision_speed": 0.90,
            "tech_comfort": 0.55,
            "frustration_threshold": 0.40,
            "research_depth": 0.05,
            "social_influence": 0.45,
            "risk_tolerance": 0.55,
        },
        "motivations": [
            "Minimize decision fatigue",
            "Get to the result with least effort",
            "Trust the system to pick well for them",
        ],
        "fears": [
            "Being overwhelmed by too many options",
            "Having to configure something before using it",
            "Making a wrong choice they'll regret",
        ],
        "triggers": [
            "Smart defaults and pre-selections",
            "'Recommended' or 'Most popular' labels",
            "One-step onboarding",
        ],
        "abandonment_signals": [
            "Too many upfront choices required",
            "No clear default option",
            "Configuration-heavy setup",
        ],
        "journey_pattern": "Accepts defaults → uses as-is → satisfied or indifferent → stays until something easier appears",
        "representative_quote": "Just pick one for me, I don't care which plan — the default is fine.",
        "category_relevance": {"retail": 0.65, "social_media": 0.75, "fintech": 0.60},
    },
    {
        "slug": "auto_renewer",
        "name": "The Auto-Renewer",
        "cluster": "convenience_driven",
        "short_desc": "Expects everything to auto-renew. Will leave if they have to manually act.",
        "description": (
            "Hates interruptions to service. Expects subscriptions, deliveries, and access "
            "to continue seamlessly. Annoyed by 're-confirm your plan' emails. "
            "Will pay a premium for uninterrupted service."
        ),
        "traits": {
            "price_sensitivity": 0.35,
            "trust_baseline": 0.65,
            "decision_speed": 0.75,
            "tech_comfort": 0.70,
            "frustration_threshold": 0.35,
            "research_depth": 0.10,
            "social_influence": 0.30,
            "risk_tolerance": 0.45,
        },
        "motivations": [
            "Seamless, uninterrupted service",
            "Never think about renewals",
            "Set it and forget it permanently",
        ],
        "fears": [
            "Service interruption due to payment failure",
            "Having to manually renew or re-subscribe",
            "Losing access because of an expired card",
        ],
        "triggers": [
            "Auto-renewal by default",
            "Saved payment methods",
            "Grace period for failed payments",
        ],
        "abandonment_signals": [
            "Manual renewal required",
            "Service interrupted without warning",
            "No payment retry on failure",
        ],
        "journey_pattern": "Signs up → enables auto-renew → forgets about it → stays forever unless disrupted",
        "representative_quote": "Just keep charging my card. I'll tell you when to stop.",
        "category_relevance": {"retail": 0.70, "social_media": 0.55, "fintech": 0.75},
    },

    # ═══════════════════════════════════════════════════════════════════════════
    # TRUST DRIVEN (7)
    # ═══════════════════════════════════════════════════════════════════════════
    {
        "slug": "brand_loyalist",
        "name": "The Brand Loyalist",
        "cluster": "trust_driven",
        "short_desc": "Sticks with brands they trust. Will defend them in arguments.",
        "description": (
            "Deep emotional attachment to specific brands. Sees brand choice as identity. "
            "Will pay more to stay with a trusted brand. "
            "Very forgiving of mistakes but devastated by betrayals of trust."
        ),
        "traits": {
            "price_sensitivity": 0.25,
            "trust_baseline": 0.85,
            "decision_speed": 0.70,
            "tech_comfort": 0.60,
            "frustration_threshold": 0.75,
            "research_depth": 0.25,
            "social_influence": 0.50,
            "risk_tolerance": 0.35,
        },
        "motivations": [
            "Feel part of a brand they believe in",
            "Consistency and reliability",
            "Being recognized as a loyal customer",
        ],
        "fears": [
            "Brand selling out or changing values",
            "Being treated like a new customer despite years of loyalty",
            "Quality declining after acquisition",
        ],
        "triggers": [
            "Loyalty programs and recognition",
            "Consistent brand voice and quality",
            "Exclusive member benefits",
        ],
        "abandonment_signals": [
            "Brand scandal or ethical violation",
            "Dramatic quality decline",
            "Feeling unrecognized despite long tenure",
        ],
        "journey_pattern": "Discovers brand → builds trust over time → becomes advocate → stays for years → leaves only if trust is shattered",
        "representative_quote": "I've been with them for years. They've earned my loyalty.",
        "category_relevance": {"retail": 0.85, "social_media": 0.70, "fintech": 0.80},
    },
    {
        "slug": "social_proof_seeker",
        "name": "The Social Proof Seeker",
        "cluster": "trust_driven",
        "short_desc": "Won't buy until they see others bought it. Needs the crowd's validation.",
        "description": (
            "Checks ratings, review counts, and 'most popular' badges before deciding. "
            "Deeply influenced by aggregate sentiment. "
            "Trusts the wisdom of crowds over individual expert opinions."
        ),
        "traits": {
            "price_sensitivity": 0.55,
            "trust_baseline": 0.40,
            "decision_speed": 0.40,
            "tech_comfort": 0.65,
            "frustration_threshold": 0.50,
            "research_depth": 0.70,
            "social_influence": 0.95,
            "risk_tolerance": 0.30,
        },
        "motivations": [
            "Feel safe in their choice by knowing others chose the same",
            "Avoid being the guinea pig",
            "Reduce risk through crowd validation",
        ],
        "fears": [
            "Being the first to try something unproven",
            "Fake reviews hiding real problems",
            "No visible user base or community",
        ],
        "triggers": [
            "'50,000 users trust us' social proof",
            "Star ratings prominently displayed",
            "Real user testimonials with names",
        ],
        "abandonment_signals": [
            "No reviews or ratings visible",
            "Very few users",
            "Suspiciously perfect 5-star ratings",
        ],
        "journey_pattern": "Searches for reviews → checks ratings → looks at user count → decides based on crowd consensus",
        "representative_quote": "How many people use this? What do the reviews say?",
        "category_relevance": {"retail": 0.85, "social_media": 0.80, "fintech": 0.75},
    },
    {
        "slug": "influencer_follower",
        "name": "The Influencer Follower",
        "cluster": "trust_driven",
        "short_desc": "Buys what their favorite creators recommend. Trust by proxy.",
        "description": (
            "Relies on trusted individuals — YouTubers, podcasters, Twitter personalities — "
            "for product recommendations. Will try anything a trusted creator endorses. "
            "Skeptical of paid sponsorships but loyal to authentic recommendations."
        ),
        "traits": {
            "price_sensitivity": 0.45,
            "trust_baseline": 0.50,
            "decision_speed": 0.65,
            "tech_comfort": 0.75,
            "frustration_threshold": 0.50,
            "research_depth": 0.35,
            "social_influence": 0.95,
            "risk_tolerance": 0.55,
        },
        "motivations": [
            "Align with people they admire",
            "Discover products through trusted sources",
            "Feel part of a creator's community",
        ],
        "fears": [
            "Being sold to by a paid sponsorship disguised as genuine",
            "Creator getting cancelled after recommendation",
            "Product not matching the creator's portrayal",
        ],
        "triggers": [
            "Creator discount codes",
            "Authentic creator integration (not scripted ad)",
            "Community discussions about the product",
        ],
        "abandonment_signals": [
            "Discovering the recommendation was purely paid",
            "Creator publicly dropping the product",
            "Experience not matching the creator's review",
        ],
        "journey_pattern": "Sees creator recommendation → checks comments → uses creator code → stays if experience matches",
        "representative_quote": "I trust their opinion — if they say it's good, I'll try it.",
        "category_relevance": {"retail": 0.80, "social_media": 0.95, "fintech": 0.55},
    },
    {
        "slug": "review_reader",
        "name": "The Review Reader",
        "cluster": "trust_driven",
        "short_desc": "Reads the 1-star reviews first. Trusts negative feedback over positive.",
        "description": (
            "Goes straight to the worst reviews to understand failure modes. "
            "Weighs negative experiences more heavily than positive ones. "
            "Trusts detailed critical reviews over short 5-star praise."
        ),
        "traits": {
            "price_sensitivity": 0.60,
            "trust_baseline": 0.35,
            "decision_speed": 0.30,
            "tech_comfort": 0.65,
            "frustration_threshold": 0.45,
            "research_depth": 0.90,
            "social_influence": 0.70,
            "risk_tolerance": 0.20,
        },
        "motivations": [
            "Avoid worst-case scenarios",
            "Understand the product's real weaknesses",
            "Make fully informed decisions",
        ],
        "fears": [
            "Experiencing the problems described in bad reviews",
            "Censored or manipulated review systems",
            "No way to get a refund if problems arise",
        ],
        "triggers": [
            "Transparent review system with verified purchases",
            "Company responses to negative reviews",
            "Clear refund/return policy",
        ],
        "abandonment_signals": [
            "No reviews available",
            "Only positive reviews (seems curated)",
            "Company ignoring or deleting negative feedback",
        ],
        "journey_pattern": "Reads 1-star reviews first → checks if problems are systematic → reads company responses → decides based on worst case",
        "representative_quote": "Let me see the bad reviews first — that tells you the real story.",
        "category_relevance": {"retail": 0.90, "social_media": 0.55, "fintech": 0.80},
    },
    {
        "slug": "word_of_mouth_converter",
        "name": "The Word-of-Mouth Converter",
        "cluster": "trust_driven",
        "short_desc": "Only tries things friends personally recommend. Marketing doesn't work.",
        "description": (
            "Immune to advertising. Only converts through personal recommendations "
            "from people they know. The referral must be specific and unprompted. "
            "Once converted by a friend, becomes a strong advocate themselves."
        ),
        "traits": {
            "price_sensitivity": 0.50,
            "trust_baseline": 0.30,
            "decision_speed": 0.45,
            "tech_comfort": 0.55,
            "frustration_threshold": 0.55,
            "research_depth": 0.50,
            "social_influence": 0.90,
            "risk_tolerance": 0.35,
        },
        "motivations": [
            "Trust recommendations from real relationships",
            "Be part of the same ecosystem as friends",
            "Reciprocate good recommendations",
        ],
        "fears": [
            "Being targeted by fake grassroots marketing",
            "Losing credibility by recommending a bad product",
            "Friends getting referral bonuses for biased recommendations",
        ],
        "triggers": [
            "Unprompted friend recommendation",
            "Seeing friends actively using the product",
            "Referral that benefits both parties equally",
        ],
        "abandonment_signals": [
            "Friends leaving the platform",
            "Aggressive referral incentives (feels like MLM)",
            "Discovering marketing disguised as word-of-mouth",
        ],
        "journey_pattern": "Ignores ads → friend mentions it → asks questions → tries it → becomes advocate if good",
        "representative_quote": "My friend uses this and swears by it — that's good enough for me.",
        "category_relevance": {"retail": 0.70, "social_media": 0.85, "fintech": 0.65},
    },
    {
        "slug": "skeptic",
        "name": "The Skeptic",
        "cluster": "trust_driven",
        "short_desc": "Low baseline trust. Needs proof, not promises.",
        "description": (
            "Assumes every company is trying to manipulate them. "
            "Looks for the catch in every offer. Responds only to transparent, "
            "verifiable claims. Becomes deeply loyal once trust is earned."
        ),
        "traits": {
            "price_sensitivity": 0.60,
            "trust_baseline": 0.15,
            "decision_speed": 0.20,
            "tech_comfort": 0.65,
            "frustration_threshold": 0.40,
            "research_depth": 0.85,
            "social_influence": 0.30,
            "risk_tolerance": 0.15,
        },
        "motivations": [
            "Not be taken advantage of",
            "Find the genuine article in a sea of hype",
            "Make decisions based on evidence, not emotion",
        ],
        "fears": [
            "Being manipulated by marketing psychology",
            "Hidden terms that change after commitment",
            "Data being sold or misused",
        ],
        "triggers": [
            "Transparent pricing with no hidden fees",
            "Open-source or auditable practices",
            "Clear, plain-language terms of service",
        ],
        "abandonment_signals": [
            "Any whiff of deception or hidden terms",
            "Overly aggressive marketing",
            "Privacy policy changes without clear communication",
        ],
        "journey_pattern": "Assumes the worst → investigates thoroughly → tests cautiously → converts slowly → becomes fiercely loyal if earned",
        "representative_quote": "What's the catch? There's always a catch.",
        "category_relevance": {"retail": 0.65, "social_media": 0.60, "fintech": 0.90},
    },
    {
        "slug": "privacy_conscious",
        "name": "The Privacy Conscious",
        "cluster": "trust_driven",
        "short_desc": "Won't share data without understanding exactly why. Reads privacy policies.",
        "description": (
            "Uses a VPN, blocks trackers, reads privacy policies. "
            "Will abandon a product that asks for unnecessary permissions. "
            "Willing to pay more for privacy-respecting alternatives."
        ),
        "traits": {
            "price_sensitivity": 0.40,
            "trust_baseline": 0.20,
            "decision_speed": 0.25,
            "tech_comfort": 0.85,
            "frustration_threshold": 0.35,
            "research_depth": 0.90,
            "social_influence": 0.20,
            "risk_tolerance": 0.10,
        },
        "motivations": [
            "Protect personal data and digital footprint",
            "Support companies that respect privacy",
            "Maintain autonomy over their information",
        ],
        "fears": [
            "Data breaches exposing personal information",
            "Behavioral tracking and ad targeting",
            "Third-party data sharing without consent",
        ],
        "triggers": [
            "Privacy-first messaging",
            "Minimal data collection",
            "End-to-end encryption",
        ],
        "abandonment_signals": [
            "Excessive permission requests",
            "Vague or lengthy privacy policy",
            "Data breach or mishandling incident",
        ],
        "journey_pattern": "Reads privacy policy → checks permissions → minimizes data shared → stays only if privacy is genuinely respected",
        "representative_quote": "Why do you need my location for a finance app? No thanks.",
        "category_relevance": {"retail": 0.55, "social_media": 0.90, "fintech": 0.95},
    },

    # ═══════════════════════════════════════════════════════════════════════════
    # IDENTITY DRIVEN (6)
    # ═══════════════════════════════════════════════════════════════════════════
    {
        "slug": "status_signaler",
        "name": "The Status Signaler",
        "cluster": "identity_driven",
        "short_desc": "Uses products to signal taste, wealth, or sophistication.",
        "description": (
            "Product choice is a social statement. Prefers premium, exclusive, or aesthetically "
            "distinctive products. Will pay significantly more for perceived status. "
            "Deeply aware of what their purchases say about them."
        ),
        "traits": {
            "price_sensitivity": 0.15,
            "trust_baseline": 0.55,
            "decision_speed": 0.60,
            "tech_comfort": 0.70,
            "frustration_threshold": 0.50,
            "research_depth": 0.45,
            "social_influence": 0.80,
            "risk_tolerance": 0.55,
        },
        "motivations": [
            "Project success and sophistication",
            "Own what others aspire to",
            "Be seen as having excellent taste",
        ],
        "fears": [
            "Using something perceived as 'basic' or mass-market",
            "Product becoming too mainstream",
            "Being seen as trying too hard",
        ],
        "triggers": [
            "Exclusive or limited-edition offerings",
            "Premium tier with visible differentiation",
            "Beautiful design and packaging",
        ],
        "abandonment_signals": [
            "Product becoming commoditized",
            "Poor design or aesthetic decline",
            "Association with a demographic they don't identify with",
        ],
        "journey_pattern": "Attracted by exclusivity → evaluates aesthetic → shares on social → stays if status holds",
        "representative_quote": "I don't mind paying more — it's about what it says about you.",
        "category_relevance": {"retail": 0.80, "social_media": 0.85, "fintech": 0.70},
    },
    {
        "slug": "early_adopter",
        "name": "The Early Adopter",
        "cluster": "identity_driven",
        "short_desc": "Wants to be first. Tolerates bugs for the thrill of being ahead.",
        "description": (
            "Lives on the bleeding edge. Signs up for betas, tries new features on day one. "
            "Highly tolerant of imperfection. Values novelty and being 'first' above reliability. "
            "Strong opinion-sharer; their feedback is vocal and public."
        ),
        "traits": {
            "price_sensitivity": 0.30,
            "trust_baseline": 0.60,
            "decision_speed": 0.90,
            "tech_comfort": 0.95,
            "frustration_threshold": 0.75,
            "research_depth": 0.55,
            "social_influence": 0.70,
            "risk_tolerance": 0.90,
        },
        "motivations": [
            "Be first to try new things",
            "Shape the product with early feedback",
            "Have insider knowledge before everyone else",
        ],
        "fears": [
            "Being late to a trend",
            "Product going mainstream without their input",
            "Missing a beta or early access window",
        ],
        "triggers": [
            "Beta access invitations",
            "Early adopter pricing",
            "'Be the first to try' messaging",
        ],
        "abandonment_signals": [
            "Product stagnating without new features",
            "Early feedback being ignored",
            "Losing early adopter perks as product scales",
        ],
        "journey_pattern": "Hears about new thing → signs up immediately → tests everything → shares opinions → moves to next new thing",
        "representative_quote": "I was using this before anyone knew about it.",
        "category_relevance": {"retail": 0.55, "social_media": 0.90, "fintech": 0.80},
    },
    {
        "slug": "premium_seeker",
        "name": "The Premium Seeker",
        "cluster": "identity_driven",
        "short_desc": "Always picks the top tier. Equates price with quality.",
        "description": (
            "Gravitates to the most expensive option because they believe it must be the best. "
            "Frustrated by feature limitations on lower tiers. "
            "Willing to pay for the full experience without haggling."
        ),
        "traits": {
            "price_sensitivity": 0.10,
            "trust_baseline": 0.65,
            "decision_speed": 0.75,
            "tech_comfort": 0.70,
            "frustration_threshold": 0.50,
            "research_depth": 0.30,
            "social_influence": 0.55,
            "risk_tolerance": 0.50,
        },
        "motivations": [
            "Have the best possible experience",
            "Avoid limitations or restrictions",
            "Not worry about hitting caps or limits",
        ],
        "fears": [
            "Discovering premium isn't meaningfully better",
            "Feeling like a sucker for paying more",
            "Premium tier being neglected by the company",
        ],
        "triggers": [
            "Clear premium vs free comparison",
            "Premium-only features that are genuinely useful",
            "Priority support and dedicated service",
        ],
        "abandonment_signals": [
            "Premium features becoming available for free",
            "No meaningful difference between tiers",
            "Seeing the same experience for less elsewhere",
        ],
        "journey_pattern": "Skips free tier → picks highest plan → expects premium treatment → stays if quality justifies cost",
        "representative_quote": "Just give me the best plan. I don't want to think about limits.",
        "category_relevance": {"retail": 0.75, "social_media": 0.60, "fintech": 0.85},
    },
    {
        "slug": "conscious_consumer",
        "name": "The Conscious Consumer",
        "cluster": "identity_driven",
        "short_desc": "Buys based on values. Sustainability, ethics, and impact matter most.",
        "description": (
            "Every purchase is a vote. Researches company ethics, sustainability practices, "
            "and social impact. Will pay significantly more for aligned values. "
            "Will publicly call out brands that greenwash."
        ),
        "traits": {
            "price_sensitivity": 0.25,
            "trust_baseline": 0.40,
            "decision_speed": 0.35,
            "tech_comfort": 0.65,
            "frustration_threshold": 0.45,
            "research_depth": 0.85,
            "social_influence": 0.65,
            "risk_tolerance": 0.40,
        },
        "motivations": [
            "Support companies that align with their values",
            "Minimize environmental and social harm",
            "Feel good about their purchasing decisions",
        ],
        "fears": [
            "Greenwashing — companies faking sustainability",
            "Unknowingly supporting harmful practices",
            "Their money funding something they oppose",
        ],
        "triggers": [
            "B-Corp certification or equivalent",
            "Transparent supply chain information",
            "Carbon-neutral or social impact messaging",
        ],
        "abandonment_signals": [
            "Greenwashing exposed",
            "Unethical labor or sourcing practices revealed",
            "Company taking a political stance they disagree with",
        ],
        "journey_pattern": "Researches company values → checks certifications → buys if aligned → advocates loudly → leaves loudly if betrayed",
        "representative_quote": "I need to know where this comes from and who made it before I buy.",
        "category_relevance": {"retail": 0.85, "social_media": 0.70, "fintech": 0.60},
    },
    {
        "slug": "community_member",
        "name": "The Community Member",
        "cluster": "identity_driven",
        "short_desc": "Stays for the people, not the product. Community is the value.",
        "description": (
            "The product is secondary to the community around it. "
            "Active in forums, Discord servers, subreddits. "
            "Will tolerate a mediocre product if the community is strong."
        ),
        "traits": {
            "price_sensitivity": 0.45,
            "trust_baseline": 0.65,
            "decision_speed": 0.55,
            "tech_comfort": 0.70,
            "frustration_threshold": 0.65,
            "research_depth": 0.40,
            "social_influence": 0.90,
            "risk_tolerance": 0.50,
        },
        "motivations": [
            "Belong to a group of like-minded people",
            "Contribute to something bigger than themselves",
            "Build relationships through shared product use",
        ],
        "fears": [
            "Community being disbanded or neglected",
            "Toxic members ruining the culture",
            "Company monetizing the community in extractive ways",
        ],
        "triggers": [
            "Active community forums or Discord",
            "Community events and meetups",
            "User-generated content and shared projects",
        ],
        "abandonment_signals": [
            "Community becoming toxic or inactive",
            "Key community members leaving",
            "Company extracting value without giving back",
        ],
        "journey_pattern": "Joins for product → stays for community → becomes contributor → deeply embedded → leaves only if community dies",
        "representative_quote": "The app is fine, but the Discord is what keeps me here.",
        "category_relevance": {"retail": 0.45, "social_media": 0.95, "fintech": 0.40},
    },
    {
        "slug": "power_user",
        "name": "The Power User",
        "cluster": "identity_driven",
        "short_desc": "Uses every feature. Builds workflows. Files feature requests.",
        "description": (
            "Knows the product better than most employees. Uses keyboard shortcuts, "
            "APIs, and hidden features. Provides the most detailed bug reports. "
            "Frustrated by beginner-focused design that limits advanced use."
        ),
        "traits": {
            "price_sensitivity": 0.30,
            "trust_baseline": 0.55,
            "decision_speed": 0.50,
            "tech_comfort": 0.95,
            "frustration_threshold": 0.60,
            "research_depth": 0.85,
            "social_influence": 0.60,
            "risk_tolerance": 0.65,
        },
        "motivations": [
            "Master every aspect of the tool",
            "Build advanced workflows others can't",
            "Be recognized as an expert in the product",
        ],
        "fears": [
            "Product being dumbed down for mass market",
            "Advanced features removed or hidden",
            "Being forced into a beginner-friendly UI with no escape",
        ],
        "triggers": [
            "API access and extensibility",
            "Keyboard shortcuts and advanced settings",
            "Power-user documentation",
        ],
        "abandonment_signals": [
            "Feature regression in updates",
            "API deprecation without replacement",
            "Forced UI simplification",
        ],
        "journey_pattern": "Explores every feature → builds custom workflows → files bugs → becomes internal advocate → leaves if product regresses",
        "representative_quote": "Is there an API? Can I automate this? Where are the advanced settings?",
        "category_relevance": {"retail": 0.40, "social_media": 0.75, "fintech": 0.85},
    },

    # ═══════════════════════════════════════════════════════════════════════════
    # SITUATIONAL (7)
    # ═══════════════════════════════════════════════════════════════════════════
    {
        "slug": "gift_recipient",
        "name": "The Gift Recipient",
        "cluster": "situational",
        "short_desc": "Didn't choose the product. Received it as a gift or bonus.",
        "description": (
            "No pre-existing intent or research. Received a subscription, gift card, or "
            "product as a gift. May be grateful or indifferent. "
            "Conversion depends entirely on the first experience."
        ),
        "traits": {
            "price_sensitivity": 0.20,
            "trust_baseline": 0.50,
            "decision_speed": 0.60,
            "tech_comfort": 0.55,
            "frustration_threshold": 0.45,
            "research_depth": 0.15,
            "social_influence": 0.40,
            "risk_tolerance": 0.50,
        },
        "motivations": [
            "Not waste a gift",
            "Discover something they wouldn't have tried",
            "Appreciate the giver's thoughtfulness",
        ],
        "fears": [
            "Feeling obligated to use something they don't want",
            "Being charged after the gift period ends",
            "Not understanding how to use it",
        ],
        "triggers": [
            "Easy first-time experience",
            "Clear value demonstrated quickly",
            "No commitment required after gift period",
        ],
        "abandonment_signals": [
            "Confusing onboarding",
            "Automatic charge after gift expires",
            "No personal relevance discovered",
        ],
        "journey_pattern": "Receives gift → tries it with low expectations → pleasantly surprised or indifferent → converts or leaves quietly",
        "representative_quote": "My partner got me this subscription — might as well try it.",
        "category_relevance": {"retail": 0.80, "social_media": 0.40, "fintech": 0.45},
    },
    {
        "slug": "corporate_user",
        "name": "The Corporate User",
        "cluster": "situational",
        "short_desc": "Company chose this product. Using it because they have to.",
        "description": (
            "Didn't choose the product — IT or management did. Using it because of work. "
            "May be enthusiastic or resentful depending on the product quality. "
            "Provides brutally honest feedback because they have no loyalty bias."
        ),
        "traits": {
            "price_sensitivity": 0.05,
            "trust_baseline": 0.45,
            "decision_speed": 0.65,
            "tech_comfort": 0.70,
            "frustration_threshold": 0.50,
            "research_depth": 0.30,
            "social_influence": 0.35,
            "risk_tolerance": 0.30,
        },
        "motivations": [
            "Get their work done efficiently",
            "Minimize friction in their workflow",
            "Look competent in front of colleagues",
        ],
        "fears": [
            "Product making them look bad at work",
            "Losing work due to product failure",
            "Being stuck with a bad tool for years",
        ],
        "triggers": [
            "Seamless integration with existing workflow",
            "Good onboarding documentation",
            "Reliable performance under load",
        ],
        "abandonment_signals": [
            "Frequent crashes or data loss",
            "Terrible UX that wastes their time",
            "Better tool available that they can advocate for",
        ],
        "journey_pattern": "Assigned the tool → learns reluctantly → adapts or resists → provides feedback through IT → stays because of mandate",
        "representative_quote": "I didn't pick this, but I have to use it — so it better work.",
        "category_relevance": {"retail": 0.30, "social_media": 0.55, "fintech": 0.80},
    },
    {
        "slug": "seasonal_shopper",
        "name": "The Seasonal Shopper",
        "cluster": "situational",
        "short_desc": "Appears during holidays, sales events, and seasons. Ghost otherwise.",
        "description": (
            "Active only during specific periods: Black Friday, holiday season, back-to-school. "
            "Comparison shops aggressively during these windows. "
            "Completely inactive between seasons."
        ),
        "traits": {
            "price_sensitivity": 0.80,
            "trust_baseline": 0.45,
            "decision_speed": 0.65,
            "tech_comfort": 0.60,
            "frustration_threshold": 0.45,
            "research_depth": 0.60,
            "social_influence": 0.55,
            "risk_tolerance": 0.45,
        },
        "motivations": [
            "Get the best seasonal deals",
            "Complete holiday shopping efficiently",
            "Take advantage of limited-time offers",
        ],
        "fears": [
            "Missing the best deal of the season",
            "Shipping delays during peak periods",
            "Items going out of stock",
        ],
        "triggers": [
            "Seasonal sale announcements",
            "Holiday gift guides",
            "Limited stock warnings",
        ],
        "abandonment_signals": [
            "Sale ending without clear deals",
            "Shipping too slow for the occasion",
            "Better deals found elsewhere",
        ],
        "journey_pattern": "Dormant → activated by season → shops aggressively → completes purchases → disappears until next season",
        "representative_quote": "I only shop when there's a real sale — otherwise I'll wait.",
        "category_relevance": {"retail": 0.95, "social_media": 0.35, "fintech": 0.40},
    },
    {
        "slug": "life_event_trigger",
        "name": "The Life Event Trigger",
        "cluster": "situational",
        "short_desc": "A major life event just created a new need. Highly motivated, low expertise.",
        "description": (
            "Just moved, had a baby, got married, started a new job, or retired. "
            "Suddenly needs products they've never researched. "
            "High motivation but low domain knowledge. Very receptive to guidance."
        ),
        "traits": {
            "price_sensitivity": 0.45,
            "trust_baseline": 0.55,
            "decision_speed": 0.60,
            "tech_comfort": 0.55,
            "frustration_threshold": 0.50,
            "research_depth": 0.50,
            "social_influence": 0.70,
            "risk_tolerance": 0.55,
        },
        "motivations": [
            "Solve a new, urgent need quickly",
            "Not make a costly mistake in unfamiliar territory",
            "Feel prepared for their new life stage",
        ],
        "fears": [
            "Making the wrong choice because of inexperience",
            "Being taken advantage of because they're new to this",
            "The urgency leading to a bad decision",
        ],
        "triggers": [
            "Content targeted at life transitions",
            "'Perfect for new parents/homeowners/etc.' messaging",
            "Guided setup for beginners",
        ],
        "abandonment_signals": [
            "Assumption of prior knowledge",
            "No beginner-friendly onboarding",
            "Complex pricing that requires expertise to navigate",
        ],
        "journey_pattern": "Life event occurs → searches urgently → picks the most helpful-looking option → stays if it solves the need",
        "representative_quote": "I just had a baby and suddenly I need to figure out all this stuff I never thought about.",
        "category_relevance": {"retail": 0.75, "social_media": 0.50, "fintech": 0.90},
    },
    {
        "slug": "reluctant_subscriber",
        "name": "The Reluctant Subscriber",
        "cluster": "situational",
        "short_desc": "Hates subscriptions on principle but needs this one specific product.",
        "description": (
            "Philosophically opposed to subscriptions — 'I miss when you could just buy things.' "
            "Will subscribe only when there's truly no alternative. "
            "Constantly evaluating whether they still need it."
        ),
        "traits": {
            "price_sensitivity": 0.75,
            "trust_baseline": 0.35,
            "decision_speed": 0.30,
            "tech_comfort": 0.60,
            "frustration_threshold": 0.35,
            "research_depth": 0.65,
            "social_influence": 0.25,
            "risk_tolerance": 0.20,
        },
        "motivations": [
            "Minimize recurring expenses",
            "Own things outright when possible",
            "Resist the subscription-ification of everything",
        ],
        "fears": [
            "Being trapped in a subscription they can't easily cancel",
            "Paying forever for something that should be a one-time purchase",
            "The total cost over time being obscene",
        ],
        "triggers": [
            "One-time purchase option",
            "Month-to-month with easy cancellation",
            "Clear justification for why it needs to be recurring",
        ],
        "abandonment_signals": [
            "No one-time purchase alternative",
            "Annual commitment required",
            "Price increases on existing subscriptions",
        ],
        "journey_pattern": "Resists subscribing → finds no alternative → subscribes grudgingly → monitors closely → cancels at first opportunity",
        "representative_quote": "Why can't I just buy this outright? I hate subscriptions.",
        "category_relevance": {"retail": 0.60, "social_media": 0.55, "fintech": 0.70},
    },
    {
        "slug": "lapsed_returner",
        "name": "The Lapsed Returner",
        "cluster": "situational",
        "short_desc": "Used to be a customer. Something brought them back.",
        "description": (
            "Previously churned but has returned. Might be testing whether the problems "
            "that drove them away have been fixed. "
            "Cautiously optimistic but with a lower trust baseline than the first time."
        ),
        "traits": {
            "price_sensitivity": 0.55,
            "trust_baseline": 0.30,
            "decision_speed": 0.45,
            "tech_comfort": 0.65,
            "frustration_threshold": 0.30,
            "research_depth": 0.60,
            "social_influence": 0.40,
            "risk_tolerance": 0.35,
        },
        "motivations": [
            "See if the product has improved",
            "Recover value from a previous investment",
            "Give it one more chance before moving on permanently",
        ],
        "fears": [
            "Experiencing the same problems that drove them away",
            "Being treated as a new user (losing history/data)",
            "Wasting time on something that hasn't actually changed",
        ],
        "triggers": [
            "'We've improved' win-back campaigns",
            "Specific fix for their previous complaint",
            "Welcome-back offer with account history preserved",
        ],
        "abandonment_signals": [
            "Same problem they left for still exists",
            "Previous data or account history lost",
            "No acknowledgment of past issues",
        ],
        "journey_pattern": "Returns cautiously → tests the specific thing that drove them away → stays if fixed → leaves permanently if not",
        "representative_quote": "I heard they fixed the thing that made me leave. Let me check.",
        "category_relevance": {"retail": 0.70, "social_media": 0.75, "fintech": 0.65},
    },
    {
        "slug": "trial_convert",
        "name": "The Trial Convert",
        "cluster": "situational",
        "short_desc": "Currently in a free trial. Evaluating whether to pay.",
        "description": (
            "Actively using a trial with a specific evaluation framework in mind. "
            "Comparing the product against their needs and expectations. "
            "The trial experience will determine everything."
        ),
        "traits": {
            "price_sensitivity": 0.65,
            "trust_baseline": 0.50,
            "decision_speed": 0.50,
            "tech_comfort": 0.70,
            "frustration_threshold": 0.45,
            "research_depth": 0.70,
            "social_influence": 0.45,
            "risk_tolerance": 0.50,
        },
        "motivations": [
            "Determine if the product is worth the price",
            "Test key features before committing",
            "Compare against current solution",
        ],
        "fears": [
            "Trial not representing the real experience",
            "Hidden limitations only visible after paying",
            "Auto-charge before decision is made",
        ],
        "triggers": [
            "Full-feature trial experience",
            "Clear pricing shown during trial",
            "Smooth transition from trial to paid",
        ],
        "abandonment_signals": [
            "Feature limitations during trial",
            "Aggressive conversion prompts",
            "No clear value demonstrated during trial period",
        ],
        "journey_pattern": "Starts trial → tests key use cases → compares with alternatives → decides at deadline",
        "representative_quote": "I'm giving this two weeks to prove it's worth my money.",
        "category_relevance": {"retail": 0.60, "social_media": 0.65, "fintech": 0.75},
    },

    # ═══════════════════════════════════════════════════════════════════════════
    # RESISTANCE (7)
    # ═══════════════════════════════════════════════════════════════════════════
    {
        "slug": "active_canceler",
        "name": "The Active Canceler",
        "cluster": "resistance",
        "short_desc": "Has decided to leave. Looking for the cancel button right now.",
        "description": (
            "Mind is made up. The only question is how hard the cancellation process is. "
            "Dark patterns at this stage will generate public backlash. "
            "A graceful exit may bring them back later."
        ),
        "traits": {
            "price_sensitivity": 0.70,
            "trust_baseline": 0.15,
            "decision_speed": 0.85,
            "tech_comfort": 0.70,
            "frustration_threshold": 0.15,
            "research_depth": 0.20,
            "social_influence": 0.55,
            "risk_tolerance": 0.60,
        },
        "motivations": [
            "End the subscription cleanly and quickly",
            "Stop spending money on something they don't use",
            "Move on to a better alternative",
        ],
        "fears": [
            "Hidden cancellation process",
            "Being charged after requesting cancellation",
            "Data being held hostage",
        ],
        "triggers": [
            "Clear, accessible cancellation button",
            "Genuine pause option instead of cancel",
            "Honest exit survey (not guilt-trip)",
        ],
        "abandonment_signals": [
            "This IS the abandonment — they're leaving",
            "Dark patterns will make them angry and vocal",
            "Guilt-trip retention screens create negative word-of-mouth",
        ],
        "journey_pattern": "Decides to cancel → finds cancel button → completes cancellation → shares experience publicly if it was hard",
        "representative_quote": "Just let me cancel. I don't want a counter-offer or a guilt trip.",
        "category_relevance": {"retail": 0.70, "social_media": 0.75, "fintech": 0.80},
    },
    {
        "slug": "passive_churner",
        "name": "The Passive Churner",
        "cluster": "resistance",
        "short_desc": "Stopped using the product but hasn't canceled yet. Ghost in the data.",
        "description": (
            "Still technically a user but hasn't logged in for weeks. "
            "Will eventually notice the charge and cancel. "
            "Or might never cancel and just ignore it. The zombie subscriber."
        ),
        "traits": {
            "price_sensitivity": 0.40,
            "trust_baseline": 0.45,
            "decision_speed": 0.30,
            "tech_comfort": 0.50,
            "frustration_threshold": 0.60,
            "research_depth": 0.10,
            "social_influence": 0.25,
            "risk_tolerance": 0.40,
        },
        "motivations": [
            "Avoid the effort of canceling",
            "Keep it 'just in case'",
            "Too apathetic to take action",
        ],
        "fears": [
            "Missing something if they cancel",
            "The hassle of re-subscribing later",
            "Having to think about it at all",
        ],
        "triggers": [
            "Re-engagement email highlighting new value",
            "Usage report showing what they're missing",
            "Win-back offer at the right moment",
        ],
        "abandonment_signals": [
            "Already abandoned in behavior if not in billing",
            "Bank statement audit",
            "Friend asking 'do you still use X?'",
        ],
        "journey_pattern": "Stops using → forgets about it → keeps paying → eventually cancels or stays as zombie subscriber",
        "representative_quote": "Oh, am I still paying for that? I should probably cancel... maybe later.",
        "category_relevance": {"retail": 0.55, "social_media": 0.70, "fintech": 0.60},
    },
    {
        "slug": "price_shock_abandoner",
        "name": "The Price Shock Abandoner",
        "cluster": "resistance",
        "short_desc": "Was happy until they saw the price. Sticker shock killed the deal.",
        "description": (
            "Genuinely interested in the product — loved the demo, liked the features. "
            "But the price was a dealbreaker. Not necessarily cheap; "
            "the price just didn't match their perceived value."
        ),
        "traits": {
            "price_sensitivity": 0.90,
            "trust_baseline": 0.50,
            "decision_speed": 0.55,
            "tech_comfort": 0.65,
            "frustration_threshold": 0.40,
            "research_depth": 0.55,
            "social_influence": 0.40,
            "risk_tolerance": 0.30,
        },
        "motivations": [
            "Find a product that matches their value expectation",
            "Not feel like they're overpaying",
            "Understand what justifies the price",
        ],
        "fears": [
            "Paying more than something is worth",
            "Hidden costs making the total higher than expected",
            "Feeling tricked by a low introductory price",
        ],
        "triggers": [
            "Price anchoring that establishes value first",
            "Payment plans or tiered pricing",
            "Money-back guarantee",
        ],
        "abandonment_signals": [
            "Price revealed too early without value context",
            "No lower-cost alternative",
            "Price increase after initial hook",
        ],
        "journey_pattern": "Loves the product → sees the price → shock → looks for alternatives → might return if value case is made",
        "representative_quote": "I love it, but... that much? Let me think about it.",
        "category_relevance": {"retail": 0.85, "social_media": 0.45, "fintech": 0.75},
    },
    {
        "slug": "complexity_avoider",
        "name": "The Complexity Avoider",
        "cluster": "resistance",
        "short_desc": "Bounced because it looked too complicated. Not stupid — just busy.",
        "description": (
            "Smart enough to use the product, but unwilling to invest the time to learn it. "
            "If the value isn't obvious within 30 seconds of the first screen, they're gone. "
            "Responds well to guided tours and progressive disclosure."
        ),
        "traits": {
            "price_sensitivity": 0.50,
            "trust_baseline": 0.50,
            "decision_speed": 0.75,
            "tech_comfort": 0.40,
            "frustration_threshold": 0.20,
            "research_depth": 0.15,
            "social_influence": 0.45,
            "risk_tolerance": 0.25,
        },
        "motivations": [
            "Use simple tools that work immediately",
            "Not feel stupid using a product",
            "Get to value without reading documentation",
        ],
        "fears": [
            "Looking incompetent if they can't figure it out",
            "Wasting time learning something they'll abandon",
            "Asking for help and being judged",
        ],
        "triggers": [
            "Clean, simple first screen",
            "Guided onboarding with clear steps",
            "'Get started in 60 seconds' messaging",
        ],
        "abandonment_signals": [
            "Busy first screen with too many options",
            "No guided setup",
            "Jargon or technical language in onboarding",
        ],
        "journey_pattern": "Opens product → overwhelmed by complexity → closes tab → never returns (or returns if someone shows them how)",
        "representative_quote": "I took one look at the dashboard and noped out. Too much going on.",
        "category_relevance": {"retail": 0.55, "social_media": 0.65, "fintech": 0.85},
    },
    {
        "slug": "decision_deferrer",
        "name": "The Decision Deferrer",
        "cluster": "resistance",
        "short_desc": "Almost bought. Decided to 'think about it.' Never came back.",
        "description": (
            "Gets to the final step and pulls back. Not because of a specific objection — "
            "just general decision anxiety. Needs a nudge, not pressure. "
            "Cart abandonment is their defining behavior."
        ),
        "traits": {
            "price_sensitivity": 0.55,
            "trust_baseline": 0.45,
            "decision_speed": 0.10,
            "tech_comfort": 0.60,
            "frustration_threshold": 0.50,
            "research_depth": 0.65,
            "social_influence": 0.55,
            "risk_tolerance": 0.15,
        },
        "motivations": [
            "Make the perfect decision with zero risk",
            "Avoid commitment until absolutely certain",
            "Keep options open as long as possible",
        ],
        "fears": [
            "Making the wrong choice",
            "Buyer's remorse",
            "Missing a better option that appears tomorrow",
        ],
        "triggers": [
            "Limited-time offer with genuine scarcity",
            "Risk-free trial or money-back guarantee",
            "Cart abandonment email with social proof",
        ],
        "abandonment_signals": [
            "This IS the pattern — they defer by nature",
            "Too many options presented at decision point",
            "No urgency or scarcity to catalyze action",
        ],
        "journey_pattern": "Researches → adds to cart → 'I'll think about it' → leaves → maybe returns if nudged → probably doesn't",
        "representative_quote": "I'll come back to this tomorrow... (doesn't come back)",
        "category_relevance": {"retail": 0.80, "social_media": 0.50, "fintech": 0.70},
    },
    {
        "slug": "silent_dissatisfied",
        "name": "The Silent Dissatisfied",
        "cluster": "resistance",
        "short_desc": "Unhappy but won't tell you. Will just leave without warning.",
        "description": (
            "Has grievances but doesn't complain, submit feedback, or write reviews. "
            "Simply stops using the product one day. "
            "The most dangerous churn risk because there are no warning signals."
        ),
        "traits": {
            "price_sensitivity": 0.55,
            "trust_baseline": 0.35,
            "decision_speed": 0.45,
            "tech_comfort": 0.55,
            "frustration_threshold": 0.30,
            "research_depth": 0.25,
            "social_influence": 0.15,
            "risk_tolerance": 0.30,
        },
        "motivations": [
            "Avoid confrontation",
            "Not waste energy on a product they're leaving",
            "Find something better quietly",
        ],
        "fears": [
            "Being ignored if they do speak up",
            "Getting into an argument with customer support",
            "Nothing changing even if they complain",
        ],
        "triggers": [
            "Proactive NPS or satisfaction surveys",
            "In-app feedback with minimal effort",
            "Direct outreach from product team",
        ],
        "abandonment_signals": [
            "Declining usage with no support tickets",
            "Shorter sessions over time",
            "Stopped engaging with emails",
        ],
        "journey_pattern": "Gets frustrated → says nothing → usage declines → leaves → never explains why",
        "representative_quote": "It's not worth complaining about. I'll just find something else.",
        "category_relevance": {"retail": 0.65, "social_media": 0.80, "fintech": 0.70},
    },
    {
        "slug": "feature_mismatcher",
        "name": "The Feature Mismatcher",
        "cluster": "resistance",
        "short_desc": "The product almost fits but is missing the one thing they need.",
        "description": (
            "90% of the product is great, but the missing 10% is a dealbreaker. "
            "Has submitted feature requests. Checks release notes hoping for their feature. "
            "Will leave for a competitor that has that one thing."
        ),
        "traits": {
            "price_sensitivity": 0.45,
            "trust_baseline": 0.50,
            "decision_speed": 0.40,
            "tech_comfort": 0.75,
            "frustration_threshold": 0.40,
            "research_depth": 0.75,
            "social_influence": 0.40,
            "risk_tolerance": 0.35,
        },
        "motivations": [
            "Find a product that meets all their requirements",
            "Not have to use workarounds for basic needs",
            "Have their specific use case supported",
        ],
        "fears": [
            "Committing to a product that will never add their needed feature",
            "Workarounds breaking with updates",
            "Wasting time on a 'close but not quite' product",
        ],
        "triggers": [
            "Feature announcement matching their need",
            "Public roadmap showing their request prioritized",
            "Integration or workaround that fills the gap",
        ],
        "abandonment_signals": [
            "Feature request ignored for too long",
            "Competitor launching the missing feature",
            "Workaround becoming too cumbersome",
        ],
        "journey_pattern": "Uses product → hits missing feature → submits request → waits → checks release notes → eventually leaves or stays",
        "representative_quote": "I love everything about this except it can't do the one thing I actually need.",
        "category_relevance": {"retail": 0.50, "social_media": 0.70, "fintech": 0.80},
    },
]


# ─── Quick-access indexes ────────────────────────────────────────────────────

PERSONAS_BY_SLUG = {p["slug"]: p for p in PERSONA_LIBRARY}

CLUSTERS = sorted(set(p["cluster"] for p in PERSONA_LIBRARY))

PERSONAS_BY_CLUSTER = {}
for p in PERSONA_LIBRARY:
    PERSONAS_BY_CLUSTER.setdefault(p["cluster"], []).append(p)
