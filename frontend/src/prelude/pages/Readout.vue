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

      <!-- Loading state -->
      <div v-if="loading" class="r-loading">
        <div class="r-loading-spinner"></div>
        <p>Generating prediction readout...</p>
      </div>
      <div v-if="loadError" class="r-error">
        <p>{{ loadError }}</p>
        <button class="p-btn-primary" @click="loadPrediction">Retry</button>
      </div>

      <!-- Scrolling report -->
      <div v-if="!loading && prediction" class="r-report">

        <!-- ═══════ Section 1: The Verdict ═══════ -->
        <section class="r-section r-hero">
          <div class="r-hero-verdict">Variant {{ prediction.winner?.toUpperCase() }} is predicted to win</div>
          <p class="r-hero-explain">
            {{ prediction.confidence_rationale }}
          </p>
          <div class="r-hero-confidence">
            <span class="r-conf-dots">
              <span class="r-conf-dot" :class="prediction.confidence !== 'low' ? 'filled' : 'empty'"></span>
              <span class="r-conf-dot" :class="prediction.confidence !== 'low' ? 'filled' : 'empty'"></span>
              <span class="r-conf-dot" :class="prediction.confidence === 'high' ? 'filled' : 'empty'"></span>
              <span class="r-conf-dot empty"></span>
            </span>
            <span class="r-conf-label">{{ (prediction.confidence || 'medium').toUpperCase() }}</span>
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
          <div v-if="frictionSteps.length" class="r-auto-insight">
            {{ frictionSteps.reduce((worst, s) => Math.abs(s.a - s.b) > Math.abs(worst.a - worst.b) ? s : worst, frictionSteps[0]).label }}
            shows the largest friction gap between variants
            (A: {{ frictionSteps.reduce((worst, s) => Math.abs(s.a - s.b) > Math.abs(worst.a - worst.b) ? s : worst, frictionSteps[0]).a }}%
             vs B: {{ frictionSteps.reduce((worst, s) => Math.abs(s.a - s.b) > Math.abs(worst.a - worst.b) ? s : worst, frictionSteps[0]).b }}%).
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
          <div v-if="sentimentA.length" class="r-auto-insight">
            {{ (() => {
              const avgA = sentimentA.reduce((s, v) => s + v, 0) / sentimentA.length
              const avgB = sentimentB.length ? sentimentB.reduce((s, v) => s + v, 0) / sentimentB.length : 0
              return avgA > avgB
                ? `Variant A maintains higher overall sentiment (${avgA.toFixed(2)}) vs Variant B (${avgB.toFixed(2)}), suggesting stronger positive reception across the journey.`
                : `Variant B shows stronger sentiment (${avgB.toFixed(2)}) vs Variant A (${avgA.toFixed(2)}), indicating the new approach resonates better with agents.`
            })() }}
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
                  :class="agent.outcome === 'Positive' ? 'r-outcome-good' : agent.outcome === 'Negative' ? 'r-outcome-bad' : ''"
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

        <!-- ═══════ Section 6: Voice of Customer (v1) ═══════ -->
        <section v-if="voc && voc.highlight_quotes && voc.highlight_quotes.length" class="r-section">
          <h2 class="r-section-title">
            Voice of Customer
            <span class="r-voc-badge">v1 — LLM-driven</span>
          </h2>

          <!-- Highlight quotes -->
          <div class="r-voc-highlights">
            <div
              v-for="(q, i) in voc.highlight_quotes.slice(0, 6)"
              :key="i"
              class="r-voc-quote-card"
              :class="q.sentiment > 0.2 ? 'r-voc-positive' : q.sentiment < -0.2 ? 'r-voc-negative' : 'r-voc-neutral'"
            >
              <div class="r-voc-quote-top">
                <span class="r-voc-agent">{{ q.agent }}</span>
                <span class="r-voc-variant" :class="'r-voc-variant-' + q.variant">{{ q.variant?.toUpperCase() }}</span>
              </div>
              <blockquote class="r-voc-text">"{{ q.quote }}"</blockquote>
              <div class="r-voc-meta">
                <span class="r-voc-step">{{ (q.step || '').replace(/_/g, ' ') }}</span>
                <span class="r-voc-sentiment" :class="q.sentiment > 0 ? 'r-voc-sent-pos' : 'r-voc-sent-neg'">
                  {{ q.sentiment > 0 ? '+' : '' }}{{ q.sentiment?.toFixed(2) }}
                </span>
              </div>
            </div>
          </div>

          <!-- Segment preference summary -->
          <div v-if="voc.summary" class="r-voc-summary">
            <div class="r-voc-summary-stat">
              <span class="r-voc-summary-num">{{ voc.summary.segments_preferring_a }}</span>
              <span class="r-voc-summary-label">segments prefer A</span>
            </div>
            <div class="r-voc-summary-stat">
              <span class="r-voc-summary-num">{{ voc.summary.segments_preferring_b }}</span>
              <span class="r-voc-summary-label">segments prefer B</span>
            </div>
            <div class="r-voc-summary-stat">
              <span class="r-voc-summary-num">{{ voc.summary.total_quotes_a + voc.summary.total_quotes_b }}</span>
              <span class="r-voc-summary-label">total VoC quotes</span>
            </div>
          </div>

          <!-- Segment-level VoC (expandable) -->
          <div class="r-voc-segments">
            <div
              v-for="(seg, key) in voc.by_segment"
              :key="key"
              class="r-voc-seg-row"
              :class="{ expanded: expandedVocSeg === key }"
              @click="expandedVocSeg = expandedVocSeg === key ? null : key"
            >
              <div class="r-voc-seg-header">
                <span class="r-voc-seg-name">{{ seg.name }}</span>
                <span class="r-voc-seg-pref" :class="'r-voc-pref-' + seg.preference">
                  {{ seg.preference === 'a' ? 'Prefers A' : seg.preference === 'b' ? 'Prefers B' : 'Split' }}
                </span>
                <span class="r-voc-seg-scores">
                  A: {{ seg.avg_sentiment_a?.toFixed(2) }} / B: {{ seg.avg_sentiment_b?.toFixed(2) }}
                </span>
                <span class="r-voc-seg-chevron">{{ expandedVocSeg === key ? '−' : '+' }}</span>
              </div>
              <transition name="expand">
                <div v-if="expandedVocSeg === key" class="r-voc-seg-detail">
                  <div class="r-voc-seg-cols">
                    <div class="r-voc-seg-col">
                      <h4 class="r-voc-col-title">Variant A</h4>
                      <blockquote
                        v-for="(q, qi) in (seg.quotes_a || []).slice(0, 3)"
                        :key="'a'+qi"
                        class="r-voc-seg-quote"
                      >"{{ q.quote }}" <span class="r-voc-seg-quote-sent" :class="q.sentiment > 0 ? 'r-voc-sent-pos' : 'r-voc-sent-neg'">{{ q.sentiment?.toFixed(2) }}</span></blockquote>
                    </div>
                    <div class="r-voc-seg-col">
                      <h4 class="r-voc-col-title">Variant B</h4>
                      <blockquote
                        v-for="(q, qi) in (seg.quotes_b || []).slice(0, 3)"
                        :key="'b'+qi"
                        class="r-voc-seg-quote"
                      >"{{ q.quote }}" <span class="r-voc-seg-quote-sent" :class="q.sentiment > 0 ? 'r-voc-sent-pos' : 'r-voc-sent-neg'">{{ q.sentiment?.toFixed(2) }}</span></blockquote>
                    </div>
                  </div>
                </div>
              </transition>
            </div>
          </div>
        </section>

        <!-- ═══════ Section 7: Mechanism + Risk + Watch ═══════ -->
        <section class="r-section">
          <div class="r-analysis-block">
            <h3 class="r-analysis-label">WHY {{ prediction.winner?.toUpperCase() }} WINS</h3>
            <p class="r-analysis-body">
              {{ prediction.mechanism }}
            </p>
          </div>

          <div class="r-analysis-block">
            <h3 class="r-analysis-label r-analysis-label--risk">KEY RISK</h3>
            <p class="r-analysis-body">
              {{ prediction.key_risk }}
            </p>
          </div>

          <div class="r-analysis-block">
            <h3 class="r-analysis-label">THREE THINGS TO WATCH</h3>
            <ol class="r-watch-list">
              <li v-for="(item, i) in (prediction.watch_items || [])" :key="i">
                {{ item }}
              </li>
            </ol>
          </div>
        </section>

        <!-- ═══════ Section 7: Recommended Modification ═══════ -->
        <section class="r-section">
          <h2 class="r-section-title">Recommended Modification</h2>
          <div class="r-recommendation">
            <p>{{ prediction.recommended_mod }}</p>
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
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'

const props = defineProps({
  id: { type: String, required: true }
})

const router = useRouter()

// ─── Loading state ──────────────────────────────────────────────────────────────
const loading = ref(true)
const loadError = ref(null)
const prediction = ref(null)
const experiment = ref(null)
const signals = ref(null)
const voc = ref(null)
const expandedVocSeg = ref(null)

// ─── Copy Summary ──────────────────────────────────────────────────────────────

const copyLabel = ref('Copy summary')

function copySummary() {
  if (!prediction.value) return
  const p = prediction.value
  const text = `VERDICT: Variant ${p.winner?.toUpperCase()} is predicted to win (${(p.confidence || '').toUpperCase()} confidence)

${p.confidence_rationale || ''}

WHY ${p.winner?.toUpperCase()} WINS: ${p.mechanism || ''}`

  navigator.clipboard.writeText(text).then(() => {
    copyLabel.value = 'Copied!'
    setTimeout(() => { copyLabel.value = 'Copy summary' }, 2000)
  })
}

function shareReport() {
  const p = prediction.value
  const title = p ? `Prelude Prediction: Variant ${p.winner?.toUpperCase()} wins` : 'Prelude Prediction'
  if (navigator.share) {
    navigator.share({ title, text: p?.confidence_rationale || '', url: window.location.href })
  } else {
    navigator.clipboard.writeText(window.location.href).then(() => {
      alert('Link copied to clipboard')
    })
  }
}

// ─── Segment Breakdown ─────────────────────────────────────────────────────────

const expandedSegment = ref(null)

const segments = computed(() => {
  if (!prediction.value?.segment_story) return []
  const story = prediction.value.segment_story
  return (Array.isArray(story) ? story : []).map(seg => ({
    name: (seg.persona || '').replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()),
    pct: seg.pct || 0,
    pref: (seg.preference || 'neutral').replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()),
    narrative: seg.narrative || '',
    quote: seg.quote || '',
  }))
})

function prefClass(pref) {
  const lower = pref.toLowerCase()
  if (lower.includes('a')) return 'r-pref-a'
  if (lower.includes('b')) return 'r-pref-b'
  return 'r-pref-neutral'
}

// ─── Friction Heatmap ──────────────────────────────────────────────────────────

const frictionSteps = computed(() => {
  if (!signals.value?.friction_heatmap) return []
  const heatmap = signals.value.friction_heatmap
  return (Array.isArray(heatmap) ? heatmap : []).map(s => ({
    label: (s.step || '').replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()),
    a: Math.round((s.a_friction || 0) * 100),
    b: Math.round((s.b_friction || 0) * 100),
  }))
})

function frictionColor(val) {
  if (val <= 25) return '#4AE89A'
  if (val <= 50) return '#F0A843'
  return '#F05858'
}

// ─── Sentiment Arc ─────────────────────────────────────────────────────────────

const journeySteps = computed(() => {
  if (!signals.value?.friction_heatmap) return []
  return signals.value.friction_heatmap.map(s =>
    (s.step || '').replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())
  )
})

const sentimentA = computed(() => signals.value?.sentiment_arc?.a || [])
const sentimentB = computed(() => signals.value?.sentiment_arc?.b || [])

function sentToY(val) {
  return 150 - ((val + 0.5) / 1.5) * 150
}

function sentToX(i, total) {
  const count = total || 4
  const spacing = 300 / (count + 1)
  return spacing * (i + 1)
}

const sentimentPointsA = computed(() =>
  sentimentA.value.map((v, i) => `${sentToX(i, sentimentA.value.length)},${sentToY(v)}`).join(' ')
)
const sentimentPointsB = computed(() =>
  sentimentB.value.map((v, i) => `${sentToX(i, sentimentB.value.length)},${sentToY(v)}`).join(' ')
)
const sentimentDotsA = computed(() =>
  sentimentA.value.map((v, i) => ({ x: sentToX(i, sentimentA.value.length), y: sentToY(v) }))
)
const sentimentDotsB = computed(() =>
  sentimentB.value.map((v, i) => ({ x: sentToX(i, sentimentB.value.length), y: sentToY(v) }))
)

// ─── Agent Stories (from top quotes) ──────────────────────────────────────────

const clusterColors = {
  value_driven: '#F0A843',
  convenience_driven: '#3BC4A0',
  trust_driven: '#5BADEE',
  identity_driven: '#A78BFA',
  situational: '#F07858',
  resistance: '#F05858'
}

const agentStories = computed(() => {
  if (!signals.value?.top_quotes) return []
  return signals.value.top_quotes.slice(0, 5).map(q => ({
    name: q.agent || 'Agent',
    blend: [
      { label: `Variant ${(q.variant || 'a').toUpperCase()}`, color: q.variant === 'b' ? '#F07858' : '#4AE89A' }
    ],
    story: q.content || '',
    outcome: q.sentiment > 0.3 ? 'Positive' : q.sentiment < -0.3 ? 'Negative' : 'Neutral',
  }))
})

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

async function saveCalibration() {
  try {
    await axios.post(`/api/prelude/experiments/${props.id}/calibration`, {
      predicted_winner: prediction.value?.winner || 'unknown',
      actual_winner: calibration.winner || 'inconclusive',
      direction_correct: prediction.value?.winner === calibration.winner,
      segment_correct: true,  // simplified for now
      friction_correct: true,
      notes: calibration.notes,
    })
    calibrationSaved.value = true
    setTimeout(() => { calibrationSaved.value = false }, 3000)
  } catch (e) {
    alert('Failed to save calibration: ' + (e.response?.data?.error || e.message))
  }
}

// ─── Data loading ─────────────────────────────────────────────────────────────

async function loadPrediction() {
  loading.value = true
  loadError.value = null
  try {
    // Load experiment info
    const { data: expData } = await axios.get(`/api/prelude/experiments/${props.id}`)
    experiment.value = expData

    // Try to get existing prediction
    try {
      const { data: predData } = await axios.get(`/api/prelude/experiments/${props.id}/prediction`)
      prediction.value = predData
    } catch (e) {
      if (e.response?.status === 404) {
        // Generate prediction if it doesn't exist
        const { data: predData } = await axios.post(`/api/prelude/experiments/${props.id}/predict`)
        prediction.value = predData
      } else {
        throw e
      }
    }

    // Load run signals + VoC
    const { data: runData } = await axios.get(`/api/prelude/experiments/${props.id}/simulation/runs`)
    if (runData.signals) {
      signals.value = runData.signals
      // Parse JSONB fields if they're strings
      for (const field of ['adoption_by_segment', 'friction_heatmap', 'sentiment_arc', 'top_quotes', 'behavioral_patterns']) {
        if (typeof signals.value[field] === 'string') {
          signals.value[field] = JSON.parse(signals.value[field])
        }
      }
    }
    // VoC data (v1 mode)
    if (runData.voc) {
      voc.value = typeof runData.voc === 'string' ? JSON.parse(runData.voc) : runData.voc
    }

  } catch (e) {
    loadError.value = e.response?.data?.error || e.message || 'Failed to load prediction'
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadPrediction()
})
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

/* ─── Loading / Error ────────────────────────────────────────────────────────── */
.r-loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  flex: 1;
  gap: 16px;
  color: #8A9490;
  font-size: 15px;
  padding: 80px 0;
}
.r-loading-spinner {
  width: 36px;
  height: 36px;
  border: 3px solid #1E2421;
  border-top-color: #4AE89A;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }
.r-error {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
  padding: 80px 0;
  color: #F05858;
  font-size: 14px;
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

/* ─── Voice of Customer (v1) ─────────────────────────────────────────────── */
.r-voc-badge {
  font-size: 10px;
  font-weight: 700;
  color: #0D0F0E;
  background: #4AE89A;
  padding: 2px 8px;
  border-radius: 20px;
  margin-left: 10px;
  vertical-align: middle;
  letter-spacing: 0.05em;
  text-transform: uppercase;
}

.r-voc-highlights {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 14px;
  margin-bottom: 28px;
}

.r-voc-quote-card {
  background: #161A18;
  border-radius: 10px;
  padding: 16px 18px;
  border-left: 3px solid #3A4440;
  transition: border-color 0.2s;
}
.r-voc-positive { border-left-color: #4AE89A; }
.r-voc-negative { border-left-color: #F07858; }
.r-voc-neutral  { border-left-color: #F0A843; }

.r-voc-quote-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}
.r-voc-agent {
  font-size: 12px;
  font-weight: 600;
  color: #E8EAE9;
}
.r-voc-variant {
  font-size: 10px;
  font-weight: 700;
  padding: 2px 8px;
  border-radius: 20px;
  text-transform: uppercase;
}
.r-voc-variant-a { background: #0D2E1E; color: #4AE89A; }
.r-voc-variant-b { background: #2E1A14; color: #F07858; }

.r-voc-text {
  font-size: 14px;
  color: #C0C4C2;
  line-height: 1.6;
  margin: 0 0 10px;
  font-style: italic;
}

.r-voc-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.r-voc-step {
  font-size: 11px;
  color: #5A6460;
  text-transform: capitalize;
}
.r-voc-sentiment {
  font-size: 12px;
  font-weight: 700;
  font-family: 'DM Mono', monospace;
}
.r-voc-sent-pos { color: #4AE89A; }
.r-voc-sent-neg { color: #F07858; }

/* VoC summary stats */
.r-voc-summary {
  display: flex;
  gap: 24px;
  margin-bottom: 28px;
  padding: 18px 24px;
  background: #111413;
  border-radius: 10px;
  border: 1px solid #1E2421;
}
.r-voc-summary-stat {
  display: flex;
  flex-direction: column;
  align-items: center;
  flex: 1;
}
.r-voc-summary-num {
  font-size: 28px;
  font-weight: 700;
  color: #4AE89A;
}
.r-voc-summary-label {
  font-size: 12px;
  color: #5A6460;
  margin-top: 4px;
}

/* VoC segment rows */
.r-voc-segments {
  display: flex;
  flex-direction: column;
  gap: 2px;
}
.r-voc-seg-row {
  background: #161A18;
  border-radius: 8px;
  cursor: pointer;
  transition: background 0.15s;
}
.r-voc-seg-row:hover { background: #1A1F1D; }
.r-voc-seg-row.expanded { background: #1A1F1D; }

.r-voc-seg-header {
  display: flex;
  align-items: center;
  padding: 14px 18px;
  gap: 12px;
}
.r-voc-seg-name {
  font-size: 14px;
  font-weight: 600;
  color: #E8EAE9;
  flex: 1;
}
.r-voc-seg-pref {
  font-size: 11px;
  font-weight: 700;
  padding: 3px 10px;
  border-radius: 20px;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}
.r-voc-pref-a { background: #0D2E1E; color: #4AE89A; }
.r-voc-pref-b { background: #2E1A14; color: #F07858; }
.r-voc-pref-split { background: #1E2421; color: #8A9490; }

.r-voc-seg-scores {
  font-size: 12px;
  font-family: 'DM Mono', monospace;
  color: #5A6460;
}
.r-voc-seg-chevron {
  font-size: 18px;
  color: #5A6460;
  width: 20px;
  text-align: center;
}

.r-voc-seg-detail {
  padding: 0 18px 18px;
}
.r-voc-seg-cols {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 18px;
}
.r-voc-col-title {
  font-size: 11px;
  font-weight: 700;
  color: #5A6460;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  margin: 0 0 12px;
}
.r-voc-seg-quote {
  font-size: 13px;
  color: #8A9490;
  line-height: 1.6;
  font-style: italic;
  margin: 0 0 10px;
  padding-left: 12px;
  border-left: 2px solid #1E2421;
}
.r-voc-seg-quote-sent {
  font-size: 11px;
  font-weight: 700;
  font-family: 'DM Mono', monospace;
  font-style: normal;
}
</style>
