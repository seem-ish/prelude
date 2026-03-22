<template>
  <div class="p-shell">
    <!-- Sidebar -->
    <aside class="p-sidebar">
      <div class="p-logo" @click="$router.push('/prelude')" style="cursor:pointer">Prelude</div>
      <nav class="p-nav">
        <router-link to="/prelude" class="p-nav-item">
          <span class="p-nav-icon">⊞</span> Dashboard
        </router-link>
        <router-link to="/prelude/brief" class="p-nav-item">
          <span class="p-nav-icon">✦</span> New Experiment
        </router-link>
      </nav>
    </aside>

    <!-- Main -->
    <main class="p-main">
      <!-- Top bar with back link and progress -->
      <div class="p-topbar-row">
        <button class="p-back-btn" @click="$router.push(`/prelude/sim/${id}`)">← Simulation</button>
        <div class="p-progress-bar">
          <div class="p-progress-step done"><span class="p-progress-dot"></span><span class="p-progress-label">Brief</span></div>
          <div class="p-progress-step done"><span class="p-progress-dot"></span><span class="p-progress-label">Personas</span></div>
          <div class="p-progress-step done"><span class="p-progress-dot"></span><span class="p-progress-label">Simulation</span></div>
          <div class="p-progress-step active"><span class="p-progress-dot"></span><span class="p-progress-label">Results</span></div>
        </div>
      </div>

      <!-- Scrolling report -->
      <div class="r-report">

        <!-- ═══════ Section 1: The Verdict ═══════ -->
        <section class="r-section r-hero">
          <div class="r-hero-verdict">Variant A is predicted to win</div>
          <p class="r-hero-explain">
            Guided onboarding reduces abandonment by removing the "how long will this take?"
            hesitation at step 1. Users who see a progress indicator commit earlier and
            complete setup at nearly double the rate.
          </p>
          <div class="r-hero-confidence">
            <span class="r-conf-dots">
              <span class="r-conf-dot filled"></span>
              <span class="r-conf-dot filled"></span>
              <span class="r-conf-dot filled"></span>
              <span class="r-conf-dot empty"></span>
            </span>
            <span class="r-conf-label">HIGH</span>
          </div>
          <div class="r-hero-actions">
            <button class="p-btn-secondary" @click="shareReport">Share</button>
            <button class="p-btn-primary" @click="copySummary">
              {{ copyLabel }}
            </button>
          </div>
        </section>

        <!-- ═══════ Section 2: Segment Breakdown ═══════ -->
        <section class="r-section">
          <h2 class="r-section-title">Segment Breakdown</h2>
          <div class="r-segment-table">
            <div
              v-for="(seg, i) in segments"
              :key="seg.name"
              class="r-seg-row"
              :class="{ expanded: expandedSegment === i }"
              @click="expandedSegment = expandedSegment === i ? null : i"
            >
              <div class="r-seg-header">
                <span class="r-seg-name">{{ seg.name }}</span>
                <span class="r-seg-pct">{{ seg.pct }}% of users</span>
                <span class="r-seg-pref" :class="prefClass(seg.pref)">{{ seg.pref }}</span>
                <span class="r-seg-chevron">{{ expandedSegment === i ? '−' : '+' }}</span>
              </div>
              <transition name="expand">
                <div v-if="expandedSegment === i" class="r-seg-detail">
                  <p class="r-seg-narrative">{{ seg.narrative }}</p>
                  <blockquote class="r-seg-quote">"{{ seg.quote }}"</blockquote>
                </div>
              </transition>
            </div>
          </div>
        </section>

        <!-- ═══════ Section 3: Friction Heatmap ═══════ -->
        <section class="r-section">
          <h2 class="r-section-title">Friction Heatmap</h2>
          <div class="r-heatmap">
            <div class="r-heatmap-row" v-for="step in frictionSteps" :key="step.label">
              <div class="r-heatmap-label">{{ step.label }}</div>
              <div class="r-heatmap-bars">
                <div class="r-heatmap-bar-wrap">
                  <span class="r-bar-tag">A</span>
                  <div class="r-heatmap-bar">
                    <div
                      class="r-heatmap-fill"
                      :style="{ width: step.a + '%', background: frictionColor(step.a) }"
                    ></div>
                  </div>
                  <span class="r-bar-val">{{ step.a }}%</span>
                </div>
                <div class="r-heatmap-bar-wrap">
                  <span class="r-bar-tag">B</span>
                  <div class="r-heatmap-bar">
                    <div
                      class="r-heatmap-fill"
                      :style="{ width: step.b + '%', background: frictionColor(step.b) }"
                    ></div>
                  </div>
                  <span class="r-bar-val">{{ step.b }}%</span>
                </div>
              </div>
            </div>
          </div>
          <div class="r-auto-insight">
            Step 2 ("About You") causes 3x more friction in Variant B. Users reported
            feeling overwhelmed by the number of fields without knowing how much remained.
          </div>
        </section>

        <!-- ═══════ Section 4: Sentiment Arc ═══════ -->
        <section class="r-section">
          <h2 class="r-section-title">Sentiment Arc</h2>
          <div class="r-sentiment-chart">
            <div class="r-sent-y-axis">
              <span>1.0</span>
              <span>0.5</span>
              <span>0.0</span>
              <span>−0.5</span>
            </div>
            <div class="r-sent-canvas">
              <!-- Grid lines -->
              <div class="r-sent-gridline" style="top: 0%"></div>
              <div class="r-sent-gridline" style="top: 33.3%"></div>
              <div class="r-sent-gridline" style="top: 66.6%"></div>
              <div class="r-sent-gridline" style="top: 100%"></div>

              <!-- SVG lines -->
              <svg class="r-sent-svg" viewBox="0 0 300 150" preserveAspectRatio="none">
                <!-- Variant A line -->
                <polyline
                  :points="sentimentPointsA"
                  fill="none"
                  stroke="#4AE89A"
                  stroke-width="2.5"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                />
                <!-- Variant B line -->
                <polyline
                  :points="sentimentPointsB"
                  fill="none"
                  stroke="#F07858"
                  stroke-width="2.5"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-dasharray="6,4"
                />
                <!-- Dots A -->
                <circle
                  v-for="(pt, i) in sentimentDotsA"
                  :key="'a'+i"
                  :cx="pt.x"
                  :cy="pt.y"
                  r="4"
                  fill="#4AE89A"
                />
                <!-- Dots B -->
                <circle
                  v-for="(pt, i) in sentimentDotsB"
                  :key="'b'+i"
                  :cx="pt.x"
                  :cy="pt.y"
                  r="4"
                  fill="#F07858"
                />
              </svg>

              <!-- X-axis labels -->
              <div class="r-sent-x-labels">
                <span v-for="s in journeySteps" :key="s">{{ s }}</span>
              </div>
            </div>
          </div>
          <div class="r-sent-legend">
            <span class="r-legend-item"><span class="r-legend-swatch" style="background:#4AE89A"></span> Variant A</span>
            <span class="r-legend-item"><span class="r-legend-swatch r-legend-dashed" style="background:#F07858"></span> Variant B</span>
          </div>
          <div class="r-auto-insight">
            Variant A maintains positive sentiment throughout the journey. Variant B drops
            sharply at the skip button, where users interpret the option as a signal that the
            process isn't worth completing.
          </div>
        </section>

        <!-- ═══════ Section 5: Agent Stories ═══════ -->
        <section class="r-section">
          <h2 class="r-section-title">Agent Stories</h2>
          <div class="r-stories">
            <div v-for="agent in agentStories" :key="agent.name" class="r-story-card">
              <div class="r-story-top">
                <span class="r-story-name">{{ agent.name }}</span>
                <span
                  class="r-story-outcome"
                  :class="agent.outcome === 'Completed' ? 'r-outcome-good' : 'r-outcome-bad'"
                >{{ agent.outcome }}</span>
              </div>
              <div class="r-story-blend">
                <span
                  v-for="tag in agent.blend"
                  :key="tag.label"
                  class="r-blend-tag"
                  :style="{ background: tag.color + '18', color: tag.color }"
                >{{ tag.label }}</span>
              </div>
              <p class="r-story-text">{{ agent.story }}</p>
            </div>
          </div>
        </section>

        <!-- ═══════ Section 6: Mechanism + Risk + Watch ═══════ -->
        <section class="r-section">
          <div class="r-analysis-block">
            <h3 class="r-analysis-label">WHY A WINS</h3>
            <p class="r-analysis-body">
              Variant A's progress indicator creates a completion contract: once users see "Step 1 of 4,"
              they mentally commit to the sequence. This anchoring effect reduces the cognitive overhead of
              deciding whether to continue at each screen. The guided flow also front-loads lightweight
              questions (name, age), building momentum before asking for the harder commitment (goals, plan
              selection). Variant B's open-ended form triggers decision fatigue in the first 30 seconds.
            </p>
          </div>

          <div class="r-analysis-block">
            <h3 class="r-analysis-label r-analysis-label--risk">KEY RISK</h3>
            <p class="r-analysis-body">
              Power users (Early Adopters) find the step-by-step flow patronizing. If your user base skews
              toward experienced fitness app users, the guided flow may increase time-to-value without
              improving retention. Consider offering a "Quick setup" escape hatch at step 1 for returning users.
            </p>
          </div>

          <div class="r-analysis-block">
            <h3 class="r-analysis-label">THREE THINGS TO WATCH</h3>
            <ol class="r-watch-list">
              <li>
                <strong>Step 2 completion rate:</strong> If "About You" drops below 65% in Variant A,
                the form fields need trimming — the progress bar alone won't carry users past bad UX.
              </li>
              <li>
                <strong>Time-to-first-workout:</strong> Measure whether Variant A's higher onboarding
                completion actually translates to a first logged workout within 48 hours. Completion
                without activation is a vanity metric.
              </li>
              <li>
                <strong>Day-7 retention by variant:</strong> The real test. If Variant A users churn at
                the same rate by day 7, the onboarding improvement is cosmetic — you've delayed the drop,
                not prevented it.
              </li>
            </ol>
          </div>
        </section>

        <!-- ═══════ Section 7: Recommended Modification ═══════ -->
        <section class="r-section">
          <h2 class="r-section-title">Recommended Modification to Variant A</h2>
          <div class="r-recommendation">
            <p>
              Add an estimated time remaining label at the top of each step (e.g., "About 2 min left").
              Our simulation showed that even users who committed to the 4-step flow experienced micro-hesitations
              at step 3 ("Goals"), where the questions became more personal. An explicit time anchor reduces
              this friction by 40% in our model. Additionally, consider making the "Goals" step optional with
              smart defaults — pre-fill based on the age and activity level captured in step 2, and let users
              edit later from their profile.
            </p>
          </div>
        </section>

        <!-- ═══════ Section 8: Calibration Log ═══════ -->
        <section class="r-section r-section-last">
          <h2 class="r-section-title">Log Real Outcome</h2>
          <p class="r-cal-subtitle">
            When your A/B test completes, come back and log what actually happened.
            This builds your team's prediction accuracy score.
          </p>

          <div class="r-cal-form">
            <div class="r-cal-field">
              <label class="r-cal-label">Experiment ran?</label>
              <div class="r-radio-group">
                <label class="r-radio"><input type="radio" v-model="calibration.ran" value="yes" /><span class="r-radio-custom"></span> Yes</label>
                <label class="r-radio"><input type="radio" v-model="calibration.ran" value="no" /><span class="r-radio-custom"></span> Not yet</label>
              </div>
            </div>

            <template v-if="calibration.ran === 'yes'">
              <div class="r-cal-field">
                <label class="r-cal-label">Actual winner</label>
                <div class="r-radio-group">
                  <label class="r-radio"><input type="radio" v-model="calibration.winner" value="a" /><span class="r-radio-custom"></span> Variant A</label>
                  <label class="r-radio"><input type="radio" v-model="calibration.winner" value="b" /><span class="r-radio-custom"></span> Variant B</label>
                  <label class="r-radio"><input type="radio" v-model="calibration.winner" value="inconclusive" /><span class="r-radio-custom"></span> Inconclusive</label>
                </div>
              </div>

              <div class="r-cal-field">
                <label class="r-cal-label">Notes</label>
                <textarea
                  v-model="calibration.notes"
                  class="r-cal-textarea"
                  rows="4"
                  placeholder="What happened? Any surprises?"
                ></textarea>
              </div>
            </template>

            <button
              class="p-btn-primary"
              :disabled="!canSaveCalibration"
              @click="saveCalibration"
            >
              {{ calibrationSaved ? 'Saved' : 'Save outcome' }}
            </button>
          </div>
        </section>

      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, reactive, computed } from 'vue'

const props = defineProps({
  id: { type: String, required: true }
})

// ─── Copy Summary ──────────────────────────────────────────────────────────────

const copyLabel = ref('Copy summary')

function copySummary() {
  const text = `VERDICT: Variant A is predicted to win (HIGH confidence)

Guided onboarding reduces abandonment by removing the "how long will this take?" hesitation at step 1. Users who see a progress indicator commit earlier and complete setup at nearly double the rate.

WHY A WINS: Variant A's progress indicator creates a completion contract: once users see "Step 1 of 4," they mentally commit to the sequence. This anchoring effect reduces the cognitive overhead of deciding whether to continue at each screen. The guided flow also front-loads lightweight questions (name, age), building momentum before asking for the harder commitment (goals, plan selection). Variant B's open-ended form triggers decision fatigue in the first 30 seconds.`

  navigator.clipboard.writeText(text).then(() => {
    copyLabel.value = 'Copied!'
    setTimeout(() => { copyLabel.value = 'Copy summary' }, 2000)
  })
}

function shareReport() {
  if (navigator.share) {
    navigator.share({
      title: 'Prelude Prediction: Variant A wins',
      text: 'Guided onboarding reduces abandonment by removing the "how long will this take?" hesitation.',
      url: window.location.href
    })
  } else {
    navigator.clipboard.writeText(window.location.href).then(() => {
      alert('Link copied to clipboard')
    })
  }
}

// ─── Segment Breakdown ─────────────────────────────────────────────────────────

const expandedSegment = ref(null)

const segments = [
  {
    name: 'Decision Deferrer',
    pct: 31,
    pref: 'Strongly prefers A',
    narrative: 'Decision Deferrers are paralyzed by open-ended choices. The 4-step guided flow removes ambiguity about what to do next. They reported feeling "relieved" when they saw a clear numbered sequence instead of a blank form.',
    quote: 'I almost closed the app, but then I saw it was only 4 steps. That felt doable.'
  },
  {
    name: 'Passive Subscriber',
    pct: 24,
    pref: 'Prefers A',
    narrative: 'Passive Subscribers have low motivation and need external structure. Variant A\'s step-by-step flow acts as a gentle nudge system, keeping them moving forward without requiring self-direction.',
    quote: 'I liked that it told me what to do next. I didn\'t have to think about it.'
  },
  {
    name: 'Complexity Avoider',
    pct: 18,
    pref: 'Slightly prefers A',
    narrative: 'Complexity Avoiders scan for signs of effort before committing. The progress bar in Variant A signals a bounded, manageable experience. Variant B\'s single long form triggered their "this looks like work" reflex.',
    quote: 'Four steps? Fine. But if I\'d seen all those fields at once, I would have noped out.'
  },
  {
    name: 'One-Click Converter',
    pct: 12,
    pref: 'Neutral',
    narrative: 'One-Click Converters care about speed above all. Both variants felt roughly equivalent — Variant A had more screens but less per screen, while Variant B had one screen but more density. A slight edge to A for perceived simplicity.',
    quote: 'Just let me start working out. I don\'t care how you ask the questions.'
  },
  {
    name: 'Early Adopter',
    pct: 8,
    pref: 'Prefers B',
    narrative: 'Early Adopters are confident and want control. The guided flow felt slow and unnecessary. They preferred Variant B\'s single form where they could fill everything at their own pace and skip what they didn\'t care about.',
    quote: 'The step-by-step thing felt like a children\'s app. Just give me the form.'
  },
  {
    name: 'Brand Loyalist',
    pct: 4,
    pref: 'Neutral',
    narrative: 'Brand Loyalists are already committed to the product. Onboarding friction barely registers because their motivation is high enough to push through either variant. They completed both flows at similar rates.',
    quote: 'I heard about this app from a friend. I was going to finish setup no matter what.'
  },
  {
    name: 'Skeptic',
    pct: 3,
    pref: 'Prefers B',
    narrative: 'Skeptics distrust structured flows because they feel manipulated. The progress bar in Variant A triggered suspicion ("what are they collecting and why?"). Variant B\'s transparency — showing everything upfront — felt more honest.',
    quote: 'When apps break things into steps, I always wonder what they\'re hiding in step 4.'
  }
]

function prefClass(pref) {
  if (pref.includes('Strongly prefers A') || pref.includes('Prefers A')) return 'r-pref-a'
  if (pref.includes('Prefers B')) return 'r-pref-b'
  return 'r-pref-neutral'
}

// ─── Friction Heatmap ──────────────────────────────────────────────────────────

const frictionSteps = [
  { label: 'First Screen', a: 15, b: 22 },
  { label: 'About You',    a: 28, b: 84 },
  { label: 'Goals',        a: 35, b: 45 },
  { label: 'Plan Setup',   a: 20, b: 38 }
]

function frictionColor(val) {
  if (val <= 25) return '#4AE89A'
  if (val <= 50) return '#F0A843'
  return '#F05858'
}

// ─── Sentiment Arc ─────────────────────────────────────────────────────────────

const journeySteps = ['First Screen', 'About You', 'Goals', 'Plan Setup']

const sentimentA = [0.3, 0.6, 0.7, 0.8]
const sentimentB = [0.3, 0.4, -0.1, 0.3]

function sentToY(val) {
  // Range: -0.5 to 1.0, mapped to 150 (bottom) to 0 (top)
  return 150 - ((val + 0.5) / 1.5) * 150
}

function sentToX(i) {
  return 37.5 + i * 75
}

const sentimentPointsA = computed(() =>
  sentimentA.map((v, i) => `${sentToX(i)},${sentToY(v)}`).join(' ')
)
const sentimentPointsB = computed(() =>
  sentimentB.map((v, i) => `${sentToX(i)},${sentToY(v)}`).join(' ')
)
const sentimentDotsA = computed(() =>
  sentimentA.map((v, i) => ({ x: sentToX(i), y: sentToY(v) }))
)
const sentimentDotsB = computed(() =>
  sentimentB.map((v, i) => ({ x: sentToX(i), y: sentToY(v) }))
)

// ─── Agent Stories ─────────────────────────────────────────────────────────────

const clusterColors = {
  value_driven: '#F0A843',
  convenience_driven: '#3BC4A0',
  trust_driven: '#5BADEE',
  identity_driven: '#A78BFA',
  situational: '#F07858',
  resistance: '#F05858'
}

const agentStories = [
  {
    name: 'Maya, 28',
    blend: [
      { label: 'Convenience', color: clusterColors.convenience_driven },
      { label: 'Decision Deferrer', color: clusterColors.situational }
    ],
    story: 'Maya opened the app on her lunch break with 8 minutes to spare. When she saw the progress bar showing "Step 1 of 4," she figured she could knock it out before getting back to work. She breezed through the first two steps but paused at Goals — she wasn\'t sure whether to pick "lose weight" or "build strength." The progress bar reminded her she was almost done, so she picked one and moved on. She logged her first workout that evening.',
    outcome: 'Completed'
  },
  {
    name: 'Jordan, 34',
    blend: [
      { label: 'Trust', color: clusterColors.trust_driven },
      { label: 'Skeptic', color: clusterColors.resistance }
    ],
    story: 'Jordan was referred by a coworker but had been burned by fitness apps before. In Variant B, he appreciated seeing all the fields upfront — no hidden steps, no surprises. He filled out what he wanted and skipped the rest. He didn\'t love the experience, but he didn\'t distrust it either. He completed setup but hasn\'t opened the app since.',
    outcome: 'Completed (low engagement)'
  },
  {
    name: 'Priya, 22',
    blend: [
      { label: 'Identity', color: clusterColors.identity_driven },
      { label: 'Early Adopter', color: clusterColors.value_driven }
    ],
    story: 'Priya downloads every new fitness app the week it launches. She found Variant A\'s guided flow tedious — she already knew her goals, her weight, her preferred workout time. She wanted to skip to the good stuff. By step 3, she was tapping "next" without reading. She completed setup but felt the app was designed for beginners, not for her.',
    outcome: 'Completed (at risk)'
  },
  {
    name: 'Marcus, 41',
    blend: [
      { label: 'Value', color: clusterColors.value_driven },
      { label: 'Passive', color: clusterColors.convenience_driven }
    ],
    story: 'Marcus got the app because his doctor told him to exercise more. He opened it at 10pm, half-watching TV. Variant A\'s simple first step (just his name) got him started before he could talk himself out of it. Each subsequent step asked for one more thing. By step 4, he\'d built enough momentum to finish. He set a reminder for tomorrow morning.',
    outcome: 'Completed'
  },
  {
    name: 'Sam, 19',
    blend: [
      { label: 'Situational', color: clusterColors.situational },
      { label: 'Complexity Avoider', color: clusterColors.resistance }
    ],
    story: 'Sam saw an Instagram ad and impulsively downloaded the app. In Variant B, the long form hit them like a wall of text. They scrolled down, saw how many fields there were, and closed the app. They never came back. In the simulation with Variant A, Sam completed 3 of 4 steps before getting distracted — but the app saved their progress, and they finished the next day.',
    outcome: 'Abandoned (B) / Completed (A)'
  }
]

// ─── Calibration ───────────────────────────────────────────────────────────────

const calibration = reactive({
  ran: null,
  winner: null,
  notes: ''
})

const calibrationSaved = ref(false)

const canSaveCalibration = computed(() => {
  if (!calibration.ran) return false
  if (calibration.ran === 'yes' && !calibration.winner) return false
  return true
})

function saveCalibration() {
  calibrationSaved.value = true
  setTimeout(() => { calibrationSaved.value = false }, 3000)
}
</script>

<style scoped>
/* ─── Shell (matches Dashboard / Personas) ──────────────────────────────────── */
.p-shell {
  display: flex;
  min-height: 100vh;
  background: #0D0F0E;
  color: #E8EAE9;
  font-family: 'DM Sans', 'Inter', sans-serif;
}

/* ─── Sidebar ────────────────────────────────────────────────────────────────── */
.p-sidebar {
  width: 220px;
  flex-shrink: 0;
  background: #111413;
  border-right: 1px solid #1E2421;
  display: flex;
  flex-direction: column;
  padding: 28px 0;
}
.p-logo {
  font-family: 'DM Serif Display', serif;
  font-size: 22px;
  color: #4AE89A;
  padding: 0 24px 28px;
  letter-spacing: -0.3px;
}
.p-nav {
  display: flex;
  flex-direction: column;
  gap: 2px;
  padding: 0 12px;
  flex: 1;
}
.p-nav-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 9px 12px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  color: #8A9490;
  text-decoration: none;
  transition: background 0.15s, color 0.15s;
}
.p-nav-item:hover,
.p-nav-item.router-link-active {
  background: #1A1F1D;
  color: #E8EAE9;
}
.p-nav-icon {
  font-size: 13px;
  opacity: 0.7;
}

/* ─── Main ───────────────────────────────────────────────────────────────────── */
.p-main {
  flex: 1;
  padding: 40px 48px;
  max-width: 900px;
  overflow-y: auto;
}

/* ─── Top bar ────────────────────────────────────────────────────────────────── */
.p-topbar-row {
  display: flex;
  align-items: center;
  gap: 24px;
  margin-bottom: 40px;
}
.p-back-btn {
  background: none;
  border: 1px solid #1E2421;
  color: #8A9490;
  padding: 7px 14px;
  border-radius: 8px;
  font-size: 13px;
  font-family: 'DM Sans', sans-serif;
  cursor: pointer;
  transition: color 0.15s, border-color 0.15s;
  white-space: nowrap;
}
.p-back-btn:hover {
  color: #E8EAE9;
  border-color: #3A4440;
}

/* ─── Progress bar ───────────────────────────────────────────────────────────── */
.p-progress-bar {
  display: flex;
  gap: 0;
  flex: 1;
}
.p-progress-step {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 16px;
  position: relative;
}
.p-progress-step::after {
  content: '';
  position: absolute;
  right: -1px;
  top: 50%;
  transform: translateY(-50%);
  width: 20px;
  height: 1px;
  background: #1E2421;
}
.p-progress-step:last-child::after { display: none; }

.p-progress-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #2E3D37;
  flex-shrink: 0;
}
.p-progress-step.done .p-progress-dot { background: #4AE89A; }
.p-progress-step.active .p-progress-dot {
  background: #4AE89A;
  box-shadow: 0 0 0 3px rgba(74, 232, 154, 0.25);
}
.p-progress-label {
  font-size: 12px;
  color: #5A6460;
  white-space: nowrap;
}
.p-progress-step.done .p-progress-label,
.p-progress-step.active .p-progress-label {
  color: #8A9490;
}

/* ─── Report ─────────────────────────────────────────────────────────────────── */
.r-report {
  display: flex;
  flex-direction: column;
  gap: 0;
}

.r-section {
  background: #111413;
  border: 1px solid #1E2421;
  border-radius: 14px;
  padding: 36px 40px;
  margin-bottom: 20px;
}
.r-section-last {
  margin-bottom: 80px;
}

.r-section-title {
  font-family: 'DM Serif Display', serif;
  font-size: 22px;
  font-weight: 400;
  color: #E8EAE9;
  margin: 0 0 24px;
  letter-spacing: -0.3px;
}

/* ─── Hero / Verdict ─────────────────────────────────────────────────────────── */
.r-hero {
  text-align: center;
  padding: 52px 48px;
}
.r-hero-verdict {
  font-family: 'DM Serif Display', serif;
  font-size: 36px;
  color: #4AE89A;
  margin-bottom: 20px;
  letter-spacing: -0.5px;
  line-height: 1.2;
}
.r-hero-explain {
  font-size: 16px;
  color: #8A9490;
  line-height: 1.65;
  max-width: 560px;
  margin: 0 auto 28px;
}
.r-hero-confidence {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  margin-bottom: 32px;
}
.r-conf-dots {
  display: flex;
  gap: 5px;
}
.r-conf-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
}
.r-conf-dot.filled { background: #4AE89A; }
.r-conf-dot.empty {
  background: transparent;
  border: 1.5px solid #3A4440;
}
.r-conf-label {
  font-size: 12px;
  font-weight: 700;
  color: #4AE89A;
  letter-spacing: 0.1em;
}
.r-hero-actions {
  display: flex;
  justify-content: center;
  gap: 12px;
}

/* ─── Buttons ────────────────────────────────────────────────────────────────── */
.p-btn-primary {
  background: #4AE89A;
  color: #0D0F0E;
  border: none;
  border-radius: 8px;
  padding: 10px 20px;
  font-family: 'DM Sans', sans-serif;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: opacity 0.15s;
  white-space: nowrap;
}
.p-btn-primary:hover { opacity: 0.85; }
.p-btn-primary:disabled {
  opacity: 0.4;
  cursor: default;
}

.p-btn-secondary {
  background: transparent;
  color: #8A9490;
  border: 1px solid #1E2421;
  border-radius: 8px;
  padding: 10px 20px;
  font-family: 'DM Sans', sans-serif;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: color 0.15s, border-color 0.15s;
}
.p-btn-secondary:hover {
  color: #E8EAE9;
  border-color: #3A4440;
}

/* ─── Segment Breakdown ──────────────────────────────────────────────────────── */
.r-segment-table {
  display: flex;
  flex-direction: column;
  gap: 2px;
}
.r-seg-row {
  background: #161A18;
  border-radius: 10px;
  cursor: pointer;
  transition: background 0.15s;
  overflow: hidden;
}
.r-seg-row:hover { background: #1A1F1D; }
.r-seg-header {
  display: flex;
  align-items: center;
  padding: 14px 18px;
  gap: 12px;
}
.r-seg-name {
  font-size: 14px;
  font-weight: 600;
  color: #E8EAE9;
  min-width: 160px;
}
.r-seg-pct {
  font-size: 13px;
  color: #5A6460;
  min-width: 110px;
}
.r-seg-pref {
  font-size: 12px;
  font-weight: 600;
  padding: 3px 10px;
  border-radius: 20px;
  flex: 1;
  text-align: center;
}
.r-pref-a {
  background: #0D2E1E;
  color: #4AE89A;
}
.r-pref-b {
  background: #2E1A14;
  color: #F07858;
}
.r-pref-neutral {
  background: #1A1F1D;
  color: #5A6460;
}
.r-seg-chevron {
  font-size: 16px;
  color: #3A4440;
  width: 24px;
  text-align: center;
  flex-shrink: 0;
}
.r-seg-detail {
  padding: 0 18px 18px;
}
.r-seg-narrative {
  font-size: 14px;
  color: #8A9490;
  line-height: 1.6;
  margin: 0 0 12px;
}
.r-seg-quote {
  font-size: 13px;
  color: #6A7870;
  font-style: italic;
  border-left: 2px solid #2E3D37;
  padding-left: 14px;
  margin: 0;
}

/* Expand transition */
.expand-enter-active,
.expand-leave-active {
  transition: all 0.25s ease;
  max-height: 200px;
  opacity: 1;
  overflow: hidden;
}
.expand-enter-from,
.expand-leave-to {
  max-height: 0;
  opacity: 0;
  padding-top: 0;
  padding-bottom: 0;
}

/* ─── Friction Heatmap ───────────────────────────────────────────────────────── */
.r-heatmap {
  display: flex;
  flex-direction: column;
  gap: 16px;
  margin-bottom: 20px;
}
.r-heatmap-row {
  display: flex;
  align-items: center;
  gap: 16px;
}
.r-heatmap-label {
  font-size: 13px;
  color: #8A9490;
  width: 110px;
  flex-shrink: 0;
  text-align: right;
}
.r-heatmap-bars {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.r-heatmap-bar-wrap {
  display: flex;
  align-items: center;
  gap: 8px;
}
.r-bar-tag {
  font-size: 11px;
  font-weight: 700;
  color: #5A6460;
  width: 14px;
  flex-shrink: 0;
}
.r-heatmap-bar {
  flex: 1;
  height: 14px;
  background: #1A1F1D;
  border-radius: 7px;
  overflow: hidden;
}
.r-heatmap-fill {
  height: 100%;
  border-radius: 7px;
  transition: width 0.6s ease;
}
.r-bar-val {
  font-size: 12px;
  color: #5A6460;
  width: 36px;
  text-align: right;
}

.r-auto-insight {
  font-size: 14px;
  color: #8A9490;
  line-height: 1.6;
  padding: 16px 18px;
  background: #0D2E1E;
  border-left: 3px solid #4AE89A;
  border-radius: 0 8px 8px 0;
}

/* ─── Sentiment Arc ──────────────────────────────────────────────────────────── */
.r-sentiment-chart {
  display: flex;
  gap: 12px;
  margin-bottom: 16px;
  height: 200px;
}
.r-sent-y-axis {
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  font-size: 11px;
  color: #3A4440;
  padding: 4px 0 28px;
  width: 32px;
  text-align: right;
  flex-shrink: 0;
}
.r-sent-canvas {
  flex: 1;
  position: relative;
}
.r-sent-gridline {
  position: absolute;
  left: 0;
  right: 0;
  height: 1px;
  background: #1A1F1D;
}
.r-sent-svg {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: calc(100% - 28px);
}
.r-sent-x-labels {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  display: flex;
  justify-content: space-around;
  font-size: 11px;
  color: #5A6460;
  padding-top: 8px;
}
.r-sent-legend {
  display: flex;
  gap: 20px;
  margin-bottom: 20px;
}
.r-legend-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: #6A7870;
}
.r-legend-swatch {
  width: 16px;
  height: 3px;
  border-radius: 2px;
}
.r-legend-dashed {
  background: repeating-linear-gradient(
    90deg,
    #F07858 0px,
    #F07858 4px,
    transparent 4px,
    transparent 7px
  ) !important;
}

/* ─── Agent Stories ──────────────────────────────────────────────────────────── */
.r-stories {
  display: flex;
  flex-direction: column;
  gap: 14px;
}
.r-story-card {
  background: #161A18;
  border-radius: 10px;
  padding: 22px 24px;
}
.r-story-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 10px;
}
.r-story-name {
  font-size: 15px;
  font-weight: 600;
  color: #E8EAE9;
}
.r-story-outcome {
  font-size: 11px;
  font-weight: 700;
  padding: 3px 10px;
  border-radius: 20px;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}
.r-outcome-good {
  background: #0D2E1E;
  color: #4AE89A;
}
.r-outcome-bad {
  background: #2E1A14;
  color: #F07858;
}
.r-story-blend {
  display: flex;
  gap: 6px;
  margin-bottom: 12px;
}
.r-blend-tag {
  font-size: 11px;
  font-weight: 600;
  padding: 3px 9px;
  border-radius: 20px;
}
.r-story-text {
  font-size: 14px;
  color: #8A9490;
  line-height: 1.65;
  margin: 0;
}

/* ─── Analysis Block (Mechanism / Risk / Watch) ──────────────────────────────── */
.r-analysis-block {
  margin-bottom: 32px;
}
.r-analysis-block:last-child { margin-bottom: 0; }

.r-analysis-label {
  font-size: 11px;
  font-weight: 700;
  color: #4AE89A;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  margin: 0 0 12px;
}
.r-analysis-label--risk {
  color: #F0A843;
}
.r-analysis-body {
  font-size: 15px;
  color: #8A9490;
  line-height: 1.7;
  margin: 0;
}

.r-watch-list {
  font-size: 15px;
  color: #8A9490;
  line-height: 1.7;
  margin: 0;
  padding-left: 20px;
  display: flex;
  flex-direction: column;
  gap: 14px;
}
.r-watch-list strong {
  color: #E8EAE9;
  font-weight: 600;
}

/* ─── Recommendation ─────────────────────────────────────────────────────────── */
.r-recommendation {
  font-size: 15px;
  color: #8A9490;
  line-height: 1.7;
}
.r-recommendation p { margin: 0; }

/* ─── Calibration Form ───────────────────────────────────────────────────────── */
.r-cal-subtitle {
  font-size: 14px;
  color: #5A6460;
  line-height: 1.6;
  margin: -12px 0 28px;
}
.r-cal-form {
  display: flex;
  flex-direction: column;
  gap: 22px;
}
.r-cal-field {
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.r-cal-label {
  font-size: 13px;
  font-weight: 600;
  color: #8A9490;
}
.r-radio-group {
  display: flex;
  gap: 20px;
  flex-wrap: wrap;
}
.r-radio {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  color: #E8EAE9;
  cursor: pointer;
}
.r-radio input[type="radio"] {
  display: none;
}
.r-radio-custom {
  width: 16px;
  height: 16px;
  border-radius: 50%;
  border: 2px solid #3A4440;
  position: relative;
  flex-shrink: 0;
  transition: border-color 0.15s;
}
.r-radio input[type="radio"]:checked + .r-radio-custom {
  border-color: #4AE89A;
}
.r-radio input[type="radio"]:checked + .r-radio-custom::after {
  content: '';
  position: absolute;
  top: 3px;
  left: 3px;
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #4AE89A;
}

.r-cal-textarea {
  background: #161A18;
  border: 1px solid #1E2421;
  border-radius: 8px;
  padding: 12px 14px;
  font-family: 'DM Sans', sans-serif;
  font-size: 14px;
  color: #E8EAE9;
  resize: vertical;
  transition: border-color 0.15s;
}
.r-cal-textarea::placeholder { color: #3A4440; }
.r-cal-textarea:focus {
  outline: none;
  border-color: #4AE89A;
}
</style>
