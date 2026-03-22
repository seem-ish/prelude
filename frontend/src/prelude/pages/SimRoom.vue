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
        <button class="p-back-btn" @click="$router.push(`/prelude/personas/${id}`)">← Personas</button>
        <div class="p-progress-bar">
          <div class="p-progress-step done"><span class="p-progress-dot"></span><span class="p-progress-label">Brief</span></div>
          <div class="p-progress-step done"><span class="p-progress-dot"></span><span class="p-progress-label">Personas</span></div>
          <div class="p-progress-step active"><span class="p-progress-dot"></span><span class="p-progress-label">Simulation</span></div>
          <div class="p-progress-step"><span class="p-progress-dot"></span><span class="p-progress-label">Results</span></div>
        </div>
      </div>

      <!-- Status bar -->
      <div class="sim-status-bar">
        <template v-if="!simComplete">
          <span class="sim-status-dot sim-status-dot--running"></span>
          <span class="sim-status-text">Running</span>
          <span class="sim-status-sep">·</span>
          <span>Variant A: {{ variantAProgress }}%</span>
          <span class="sim-status-sep">·</span>
          <span>Variant B: {{ variantBProgress }}%</span>
          <span class="sim-status-sep">·</span>
          <span class="sim-status-time">~{{ remainingMin }} min remaining</span>
          <div class="sim-status-actions">
            <button class="sim-btn-ghost" @click="togglePause">{{ paused ? 'Resume' : 'Pause' }}</button>
            <button class="sim-btn-ghost sim-btn-ghost--danger" @click="cancelSim">Cancel</button>
          </div>
        </template>
        <template v-else>
          <span class="sim-status-dot sim-status-dot--complete"></span>
          <span class="sim-status-text">Simulation complete. Generating your prediction...</span>
          <div class="sim-status-actions">
            <button class="p-btn-primary" @click="$router.push(`/prelude/readout/${id}`)">View Results →</button>
          </div>
        </template>
      </div>

      <!-- Three-panel layout -->
      <div class="sim-panels">
        <!-- Left: Live Agent Feed -->
        <div class="sim-panel sim-panel--feed">
          <div class="sim-panel-header">
            <h2 class="sim-panel-title">LIVE FEED</h2>
            <div class="sim-filter-btns">
              <button
                class="sim-filter-btn"
                :class="{ active: feedFilter === 'a' }"
                @click="feedFilter = feedFilter === 'a' ? 'both' : 'a'"
              >A</button>
              <button
                class="sim-filter-btn"
                :class="{ active: feedFilter === 'b' }"
                @click="feedFilter = feedFilter === 'b' ? 'both' : 'b'"
              >B</button>
              <button
                class="sim-filter-btn"
                :class="{ active: feedFilter === 'both' }"
                @click="feedFilter = 'both'"
              >Both</button>
            </div>
          </div>

          <div class="sim-feed-list" ref="feedListRef">
            <transition-group name="feed-item" tag="div">
              <div
                v-for="ev in filteredEvents"
                :key="ev.id"
                class="sim-feed-item"
                :class="{ expanded: expandedEvent === ev.id }"
                @click="expandedEvent = expandedEvent === ev.id ? null : ev.id"
              >
                <div class="sim-feed-row">
                  <div class="sim-avatar" :style="{ background: clusterColor(ev.agent.cluster) }">
                    {{ initials(ev.agent.name) }}
                  </div>
                  <div class="sim-feed-body">
                    <div class="sim-feed-meta">
                      <span class="sim-feed-name">{{ ev.agent.name }}</span>
                      <span class="sim-feed-persona">{{ ev.agent.primaryPersona }}</span>
                    </div>
                    <div class="sim-feed-content">{{ ev.content }}</div>
                  </div>
                  <div class="sim-feed-indicators">
                    <span class="sim-sentiment-dot" :style="{ background: sentimentColor(ev.sentiment) }"></span>
                    <span class="sim-variant-badge" :class="`sim-variant-badge--${ev.variant}`">{{ ev.variant.toUpperCase() }}</span>
                  </div>
                </div>

                <!-- Expanded details -->
                <div v-if="expandedEvent === ev.id" class="sim-feed-detail">
                  <div class="sim-detail-row">
                    <span class="sim-detail-label">Persona blend</span>
                    <span class="sim-detail-value">{{ ev.agent.blend }}</span>
                  </div>
                  <div class="sim-detail-row">
                    <span class="sim-detail-label">Backstory</span>
                    <span class="sim-detail-value">{{ ev.agent.backstory }}</span>
                  </div>
                  <div class="sim-detail-row">
                    <span class="sim-detail-label">Reasoning</span>
                    <span class="sim-detail-value">{{ ev.reasoning }}</span>
                  </div>
                </div>
              </div>
            </transition-group>

            <!-- Empty state -->
            <div v-if="filteredEvents.length === 0 && !simComplete" class="sim-feed-empty">
              <span class="sim-feed-empty-dots">
                <span class="sim-dot-bounce"></span>
                <span class="sim-dot-bounce"></span>
                <span class="sim-dot-bounce"></span>
              </span>
              Waiting for agents...
            </div>
          </div>
        </div>

        <!-- Center: Variant Comparison -->
        <div class="sim-panel sim-panel--compare">
          <h2 class="sim-panel-title">VARIANT COMPARISON</h2>

          <div class="sim-compare-grid">
            <!-- Variant A -->
            <div class="sim-compare-col">
              <div class="sim-compare-header">
                <span class="sim-variant-badge sim-variant-badge--a">A</span>
                <span class="sim-compare-label">Variant A</span>
              </div>
              <div class="sim-compare-progress">
                <div class="sim-compare-bar">
                  <div class="sim-compare-fill sim-compare-fill--a" :style="{ width: variantAProgress + '%' }"></div>
                </div>
                <span class="sim-compare-pct">{{ variantAProgress }}%</span>
              </div>

              <!-- Sentiment arc -->
              <div class="sim-sentiment-arc">
                <div class="sim-sentiment-arc-label">Sentiment over time</div>
                <div class="sim-arc-bars">
                  <div
                    v-for="(val, i) in sentimentArcA"
                    :key="'a-' + i"
                    class="sim-arc-bar"
                    :style="{ height: arcBarHeight(val), background: sentimentColor(val) }"
                  ></div>
                </div>
              </div>

              <!-- Early signals -->
              <div class="sim-signals" v-if="signalsA.length">
                <div class="sim-signal-label">Early signals</div>
                <div v-for="(sig, i) in signalsA" :key="'sa-' + i" class="sim-signal-item">
                  <span class="sim-signal-icon">{{ sig.positive ? '▲' : '▼' }}</span>
                  {{ sig.text }}
                </div>
              </div>
            </div>

            <!-- Variant B -->
            <div class="sim-compare-col">
              <div class="sim-compare-header">
                <span class="sim-variant-badge sim-variant-badge--b">B</span>
                <span class="sim-compare-label">Variant B</span>
              </div>
              <div class="sim-compare-progress">
                <div class="sim-compare-bar">
                  <div class="sim-compare-fill sim-compare-fill--b" :style="{ width: variantBProgress + '%' }"></div>
                </div>
                <span class="sim-compare-pct">{{ variantBProgress }}%</span>
              </div>

              <!-- Sentiment arc -->
              <div class="sim-sentiment-arc">
                <div class="sim-sentiment-arc-label">Sentiment over time</div>
                <div class="sim-arc-bars">
                  <div
                    v-for="(val, i) in sentimentArcB"
                    :key="'b-' + i"
                    class="sim-arc-bar"
                    :style="{ height: arcBarHeight(val), background: sentimentColor(val) }"
                  ></div>
                </div>
              </div>

              <!-- Early signals -->
              <div class="sim-signals" v-if="signalsB.length">
                <div class="sim-signal-label">Early signals</div>
                <div v-for="(sig, i) in signalsB" :key="'sb-' + i" class="sim-signal-item">
                  <span class="sim-signal-icon">{{ sig.positive ? '▲' : '▼' }}</span>
                  {{ sig.text }}
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Right: Population Map -->
        <div class="sim-panel sim-panel--pop">
          <h2 class="sim-panel-title">WHO'S REACTED SO FAR</h2>

          <div class="sim-pop-list">
            <div v-for="cluster in clusterProgress" :key="cluster.key" class="sim-pop-row">
              <div class="sim-pop-label">
                <span class="sim-pop-dot" :style="{ background: cluster.color }"></span>
                {{ cluster.label }}
              </div>
              <div class="sim-pop-bar-wrap">
                <div class="sim-pop-bar">
                  <div class="sim-pop-fill" :style="{ width: cluster.pct + '%', background: cluster.color }"></div>
                </div>
                <span class="sim-pop-pct">{{ cluster.pct }}%</span>
              </div>
            </div>
          </div>

          <div class="sim-moments" v-if="keyMoments.length">
            <h3 class="sim-moments-title">KEY MOMENTS</h3>
            <div v-for="(m, i) in keyMoments" :key="'m-' + i" class="sim-moment-item">
              <span class="sim-moment-icon">{{ m.icon }}</span>
              <span class="sim-moment-text">{{ m.text }}</span>
            </div>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, nextTick, watch } from 'vue'
import { useRouter } from 'vue-router'

const props = defineProps({
  id: { type: String, required: true }
})

const router = useRouter()

// ─── Cluster colors ──────────────────────────────────────────────────────────
const CLUSTER_COLORS = {
  value_driven: '#F0A843',
  convenience_driven: '#3BC4A0',
  trust_driven: '#5BADEE',
  identity_driven: '#A78BFA',
  situational: '#F07858',
  resistance: '#F05858'
}

const CLUSTER_LABELS = {
  value_driven: 'Value-Driven',
  convenience_driven: 'Convenience-Driven',
  trust_driven: 'Trust-Driven',
  identity_driven: 'Identity-Driven',
  situational: 'Situational',
  resistance: 'Resistance'
}

function clusterColor(c) {
  return CLUSTER_COLORS[c] || '#5A6460'
}

// ─── Mock agents ──────────────────────────────────────────────────────────────
const AGENTS = [
  { name: 'Jordan', cluster: 'value_driven', primaryPersona: 'Budget Optimizer', blend: 'Value-Driven 70% / Convenience 30%', backstory: 'Freelance designer who tracks every subscription. Canceled three fitness apps last year for not proving ROI.' },
  { name: 'Priya', cluster: 'convenience_driven', primaryPersona: 'Quick-Start User', blend: 'Convenience 80% / Trust 20%', backstory: 'Product manager at a startup. Has 4 minutes to decide if an app is worth keeping.' },
  { name: 'Marcus', cluster: 'trust_driven', primaryPersona: 'Privacy Guardian', blend: 'Trust 75% / Identity 25%', backstory: 'Security engineer. Reads privacy policies before sign-up. Will delete app if data feels misused.' },
  { name: 'Wei', cluster: 'identity_driven', primaryPersona: 'Community Builder', blend: 'Identity 65% / Value 35%', backstory: 'Runs a local running club. Apps are tools for connecting, not just tracking.' },
  { name: 'Amara', cluster: 'situational', primaryPersona: 'New Year Resolver', blend: 'Situational 60% / Convenience 40%', backstory: 'Signed up in January with high motivation. Historically loses interest by February.' },
  { name: 'Sofia', cluster: 'resistance', primaryPersona: 'Skeptical Switcher', blend: 'Resistance 70% / Trust 30%', backstory: 'Burned by three apps with bait-and-switch pricing. Defaults to distrust.' },
  { name: 'Kenji', cluster: 'value_driven', primaryPersona: 'Feature Comparator', blend: 'Value 55% / Convenience 45%', backstory: 'Spreadsheet enthusiast. Compared 12 fitness apps before choosing the last one.' },
  { name: 'Fatima', cluster: 'convenience_driven', primaryPersona: 'Mobile-First User', blend: 'Convenience 85% / Situational 15%', backstory: 'Works two jobs. If onboarding takes more than 3 taps, she is gone.' },
  { name: 'Liam', cluster: 'trust_driven', primaryPersona: 'Data Ownership Advocate', blend: 'Trust 80% / Value 20%', backstory: 'Educator who writes about digital rights. Has exported and deleted data from 20+ apps.' },
  { name: 'Valentina', cluster: 'identity_driven', primaryPersona: 'Lifestyle Integrator', blend: 'Identity 60% / Convenience 40%', backstory: 'Yoga instructor. Wants the app to feel like an extension of her practice, not a separate chore.' }
]

// ─── Mock events ─────────────────────────────────────────────────────────────
const MOCK_EVENTS = [
  { variant: 'a', agentIdx: 0, step: 1, event_type: 'impression', content: 'Opened the app and noticed the free trial badge immediately. Feels upfront about cost.', sentiment: 0.6, reasoning: 'Jordan responds well to transparent pricing cues. The free trial reduces perceived risk.' },
  { variant: 'b', agentIdx: 1, step: 1, event_type: 'impression', content: 'Three-step onboarding loaded fast. Already past the first screen.', sentiment: 0.8, reasoning: 'Priya values speed. Variant B minimal onboarding matches her mental model.' },
  { variant: 'a', agentIdx: 2, step: 1, event_type: 'concern', content: 'Asked for health data access before explaining why. Hesitating on the permission screen.', sentiment: -0.4, reasoning: 'Marcus sees early data requests as a red flag without context about data usage.' },
  { variant: 'b', agentIdx: 3, step: 2, event_type: 'engagement', content: 'Found the community challenges tab and immediately shared with running club group chat.', sentiment: 0.9, reasoning: 'Wei is driven by social connection. Community features trigger sharing behavior.' },
  { variant: 'a', agentIdx: 4, step: 2, event_type: 'impression', content: 'Goal-setting wizard feels motivating. Selected "Run a 5K" as the target.', sentiment: 0.5, reasoning: 'Amara is engaged when initial goal-setting aligns with her resolution energy.' },
  { variant: 'b', agentIdx: 5, step: 2, event_type: 'concern', content: '"Upgrade to Pro" banner appeared on the second screen. Already suspicious.', sentiment: -0.7, reasoning: 'Sofia has been burned by upsells before. Early monetization triggers distrust pattern.' },
  { variant: 'a', agentIdx: 6, step: 3, event_type: 'engagement', content: 'Found the feature comparison chart between free and paid tiers. Screenshotted it.', sentiment: 0.7, reasoning: 'Kenji is a comparator. Clear feature differentiation feeds his decision-making process.' },
  { variant: 'b', agentIdx: 7, step: 3, event_type: 'engagement', content: 'Completed onboarding in under 90 seconds. Already logging first workout.', sentiment: 0.85, reasoning: 'Fatima responds to ultra-fast flows. She is already past the activation threshold.' },
  { variant: 'a', agentIdx: 8, step: 3, event_type: 'concern', content: 'Noticed "personalized recommendations" but no explanation of what data feeds them.', sentiment: -0.3, reasoning: 'Liam wants transparency about algorithmic personalization before he trusts it.' },
  { variant: 'b', agentIdx: 9, step: 4, event_type: 'engagement', content: 'The daily intention prompt feels aligned with her practice. Set a mindfulness reminder.', sentiment: 0.75, reasoning: 'Valentina connects with holistic framing. The intention feature resonated.' },
  { variant: 'a', agentIdx: 1, step: 4, event_type: 'engagement', content: 'Variant A walkthrough has more steps but Priya skipped to the dashboard. Found it easily.', sentiment: 0.4, reasoning: 'Priya adapts; she skipped the tutorial but found what she needed.' },
  { variant: 'b', agentIdx: 0, step: 4, event_type: 'concern', content: 'No pricing info visible yet. Jordan is looking for cost transparency before investing time.', sentiment: -0.2, reasoning: 'Jordan needs pricing clarity early. Variant B delays this information.' },
  { variant: 'a', agentIdx: 3, step: 5, event_type: 'engagement', content: 'Created a group challenge and invited club members. Six people joined within minutes.', sentiment: 0.85, reasoning: 'Wei activates social loops. Group challenges in Variant A drove viral invites.' },
  { variant: 'b', agentIdx: 2, step: 5, event_type: 'impression', content: 'Found the privacy dashboard after some searching. Feels somewhat reassured.', sentiment: 0.3, reasoning: 'Marcus located privacy controls. Presence helps but discoverability could be better.' },
  { variant: 'a', agentIdx: 5, step: 5, event_type: 'dropout', content: 'Closed the app after the third upsell prompt. Not coming back.', sentiment: -0.9, reasoning: 'Sofia hit her tolerance limit. Three monetization touchpoints exceeded her threshold.' },
  { variant: 'b', agentIdx: 4, step: 6, event_type: 'engagement', content: 'Completed first workout and got a streak badge. Posted it to Instagram.', sentiment: 0.7, reasoning: 'Amara is in her motivation window. Quick wins reinforce the new-year energy.' },
  { variant: 'a', agentIdx: 7, step: 6, event_type: 'concern', content: 'Workout log screen has too many fields. Fatima abandoned it mid-entry.', sentiment: -0.5, reasoning: 'Fatima needs minimal friction. Variant A workout log is too complex for her use case.' },
  { variant: 'b', agentIdx: 6, step: 6, event_type: 'impression', content: 'Variant B lacks the detailed comparison view. Kenji feeling uncertain about tier differences.', sentiment: -0.1, reasoning: 'Kenji cannot do his comparison analysis. Missing feature tables creates friction.' },
  { variant: 'a', agentIdx: 9, step: 7, event_type: 'engagement', content: 'Yoga integration section found. Customized workout plan to include flexibility days.', sentiment: 0.8, reasoning: 'Valentina found deep customization that aligns with her practice philosophy.' },
  { variant: 'b', agentIdx: 8, step: 7, event_type: 'engagement', content: 'Data export option found on the settings page. Liam is tentatively satisfied.', sentiment: 0.5, reasoning: 'Liam values data portability. Variant B makes export accessible.' },
  { variant: 'a', agentIdx: 4, step: 8, event_type: 'dropout', content: 'Reminder notifications feel generic. Amara turned them off and engagement is dropping.', sentiment: -0.4, reasoning: 'Amara needs personalized nudges. Generic reminders accelerate her usual drop-off.' },
  { variant: 'b', agentIdx: 3, step: 8, event_type: 'engagement', content: 'Club leaderboard live. Members are competing on weekly distance. Wei is thrilled.', sentiment: 0.9, reasoning: 'Wei social dynamics fully engaged. Leaderboard creates ongoing community engagement.' },
  { variant: 'a', agentIdx: 8, step: 9, event_type: 'impression', content: 'Privacy policy link now visible on settings. Liam reads it and finds it acceptable.', sentiment: 0.4, reasoning: 'Liam completed his due diligence. Variant A privacy policy passed his standards.' },
  { variant: 'b', agentIdx: 5, step: 9, event_type: 'impression', content: 'Sofia notices the app hasn\'t pushed any upsells in 5 minutes. Cautiously exploring features.', sentiment: 0.2, reasoning: 'Sofia\'s guard is lowering. Variant B delayed monetization is working for this archetype.' },
  { variant: 'a', agentIdx: 6, step: 10, event_type: 'conversion', content: 'Kenji upgraded to paid tier after confirming the feature list matched his needs.', sentiment: 0.9, reasoning: 'Kenji converted through informed decision-making. Feature clarity drove the upgrade.' }
]

// ─── State ───────────────────────────────────────────────────────────────────
const events = ref([])
const feedFilter = ref('both')
const expandedEvent = ref(null)
const paused = ref(false)
const simComplete = ref(false)
const feedListRef = ref(null)
let timer = null
let eventIndex = 0
let eventIdCounter = 0

// ─── Computed ────────────────────────────────────────────────────────────────
const filteredEvents = computed(() => {
  if (feedFilter.value === 'both') return events.value
  return events.value.filter(e => e.variant === feedFilter.value)
})

const variantAEvents = computed(() => events.value.filter(e => e.variant === 'a'))
const variantBEvents = computed(() => events.value.filter(e => e.variant === 'b'))

const totalAgents = 200

const variantAProgress = computed(() => {
  const aCount = variantAEvents.value.length
  return Math.min(100, Math.round((aCount / 13) * 100))
})

const variantBProgress = computed(() => {
  const bCount = variantBEvents.value.length
  return Math.min(100, Math.round((bCount / 12) * 100))
})

const remainingMin = computed(() => {
  const done = events.value.length
  const total = MOCK_EVENTS.length
  const remaining = total - done
  return Math.max(1, Math.round((remaining * 1.5) / 60))
})

// Sentiment arcs (rolling average of last N events per variant)
const sentimentArcA = computed(() => variantAEvents.value.map(e => e.sentiment))
const sentimentArcB = computed(() => variantBEvents.value.map(e => e.sentiment))

function arcBarHeight(val) {
  // Map -1..1 to 10%..100%
  const pct = Math.round(((val + 1) / 2) * 80 + 10)
  return pct + '%'
}

// Early signals
const signalsA = computed(() => {
  const sigs = []
  const aEvts = variantAEvents.value
  if (aEvts.length >= 3) {
    const avgSentiment = aEvts.reduce((s, e) => s + e.sentiment, 0) / aEvts.length
    if (avgSentiment > 0.3) sigs.push({ positive: true, text: 'Strong positive engagement from value-driven users' })
    if (avgSentiment < 0) sigs.push({ positive: false, text: 'Trust-driven users showing friction with data requests' })
    const dropouts = aEvts.filter(e => e.event_type === 'dropout')
    if (dropouts.length > 0) sigs.push({ positive: false, text: `${dropouts.length} dropout(s) detected` })
    const conversions = aEvts.filter(e => e.event_type === 'conversion')
    if (conversions.length > 0) sigs.push({ positive: true, text: `${conversions.length} conversion(s) recorded` })
  }
  return sigs
})

const signalsB = computed(() => {
  const sigs = []
  const bEvts = variantBEvents.value
  if (bEvts.length >= 3) {
    const avgSentiment = bEvts.reduce((s, e) => s + e.sentiment, 0) / bEvts.length
    if (avgSentiment > 0.3) sigs.push({ positive: true, text: 'Convenience-driven users activating quickly' })
    if (bEvts.some(e => e.event_type === 'concern')) sigs.push({ positive: false, text: 'Some users missing feature comparison info' })
    const engagements = bEvts.filter(e => e.event_type === 'engagement')
    if (engagements.length >= 4) sigs.push({ positive: true, text: 'High engagement rate from community-oriented users' })
  }
  return sigs
})

// Cluster progress
const clusterProgress = computed(() => {
  const clusterCounts = {}
  const clusterTotals = {}

  for (const key of Object.keys(CLUSTER_COLORS)) {
    clusterCounts[key] = 0
    clusterTotals[key] = Math.floor(totalAgents / Object.keys(CLUSTER_COLORS).length)
  }

  for (const ev of events.value) {
    if (ev.agent.cluster) {
      clusterCounts[ev.agent.cluster] = (clusterCounts[ev.agent.cluster] || 0) + 1
    }
  }

  return Object.keys(CLUSTER_COLORS).map(key => ({
    key,
    label: CLUSTER_LABELS[key],
    color: CLUSTER_COLORS[key],
    pct: Math.min(100, Math.round((clusterCounts[key] / clusterTotals[key]) * 100))
  }))
})

// Key moments
const keyMoments = computed(() => {
  const moments = []
  const evts = events.value

  const firstDropout = evts.find(e => e.event_type === 'dropout')
  if (firstDropout) {
    moments.push({ icon: '⚠', text: `${firstDropout.agent.name} dropped out (${firstDropout.variant.toUpperCase()})` })
  }

  const firstConversion = evts.find(e => e.event_type === 'conversion')
  if (firstConversion) {
    moments.push({ icon: '✦', text: `${firstConversion.agent.name} converted (${firstConversion.variant.toUpperCase()})` })
  }

  const highEngagement = evts.filter(e => e.sentiment > 0.8)
  if (highEngagement.length >= 2) {
    moments.push({ icon: '▲', text: `${highEngagement.length} highly positive reactions so far` })
  }

  const concerns = evts.filter(e => e.event_type === 'concern')
  if (concerns.length >= 3) {
    moments.push({ icon: '●', text: `${concerns.length} concern events flagged across both variants` })
  }

  return moments
})

// ─── Helpers ─────────────────────────────────────────────────────────────────
function initials(name) {
  return name.split(' ').map(w => w[0]).join('').toUpperCase().slice(0, 2)
}

function sentimentColor(val) {
  if (val >= 0.3) return '#4AE89A'
  if (val >= -0.3) return '#F0A843'
  return '#F05858'
}

// ─── Simulation control ──────────────────────────────────────────────────────
function emitEvent() {
  if (eventIndex >= MOCK_EVENTS.length) {
    simComplete.value = true
    clearInterval(timer)
    return
  }

  const mock = MOCK_EVENTS[eventIndex]
  const agent = AGENTS[mock.agentIdx]

  events.value.push({
    id: ++eventIdCounter,
    variant: mock.variant,
    agent: { ...agent },
    step: mock.step,
    event_type: mock.event_type,
    content: mock.content,
    sentiment: mock.sentiment,
    reasoning: mock.reasoning
  })

  eventIndex++

  // Auto-scroll feed
  nextTick(() => {
    if (feedListRef.value) {
      feedListRef.value.scrollTop = feedListRef.value.scrollHeight
    }
  })
}

function startSim() {
  timer = setInterval(() => {
    if (!paused.value) emitEvent()
  }, 1500)
}

function togglePause() {
  paused.value = !paused.value
}

function cancelSim() {
  clearInterval(timer)
  router.push(`/prelude/personas/${props.id}`)
}

onMounted(() => {
  startSim()
})

onUnmounted(() => {
  if (timer) clearInterval(timer)
})
</script>

<style scoped>
/* ─── Shell ─────────────────────────────────────────────────────────────────── */
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
  padding: 24px 32px;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

/* ─── Progress bar ───────────────────────────────────────────────────────────── */
.p-topbar-row {
  display: flex;
  align-items: center;
  gap: 20px;
  margin-bottom: 20px;
}
.p-back-btn {
  background: none;
  border: 1px solid #2E3D37;
  border-radius: 8px;
  color: #8A9490;
  padding: 6px 14px;
  font-size: 13px;
  cursor: pointer;
  transition: color 0.15s, border-color 0.15s;
  white-space: nowrap;
  font-family: 'DM Sans', sans-serif;
}
.p-back-btn:hover {
  color: #E8EAE9;
  border-color: #4AE89A;
}
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
  font-size: 12px;
  color: #4A5450;
  position: relative;
}
.p-progress-step.done { color: #4AE89A; }
.p-progress-step.active { color: #E8EAE9; }
.p-progress-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #2E3D37;
  flex-shrink: 0;
}
.p-progress-step.done .p-progress-dot { background: #4AE89A; }
.p-progress-step.active .p-progress-dot { background: #E8EAE9; box-shadow: 0 0 0 3px #2E3D37; }

/* ─── Status bar ─────────────────────────────────────────────────────────────── */
.sim-status-bar {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 18px;
  background: #111413;
  border: 1px solid #1E2421;
  border-radius: 10px;
  font-size: 13px;
  color: #8A9490;
  margin-bottom: 20px;
  flex-shrink: 0;
}
.sim-status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  flex-shrink: 0;
}
.sim-status-dot--running {
  background: #4AE89A;
  animation: pulse-dot 1.5s ease-in-out infinite;
}
.sim-status-dot--complete {
  background: #4AE89A;
}
@keyframes pulse-dot {
  0%, 100% { opacity: 1; box-shadow: 0 0 0 0 rgba(74, 232, 154, 0.4); }
  50% { opacity: 0.7; box-shadow: 0 0 0 6px rgba(74, 232, 154, 0); }
}
.sim-status-text {
  font-weight: 600;
  color: #E8EAE9;
}
.sim-status-sep {
  color: #2E3D37;
}
.sim-status-time {
  color: #6A7870;
}
.sim-status-actions {
  margin-left: auto;
  display: flex;
  gap: 8px;
}
.sim-btn-ghost {
  background: none;
  border: 1px solid #2E3D37;
  border-radius: 6px;
  color: #8A9490;
  padding: 5px 14px;
  font-size: 12px;
  font-weight: 500;
  cursor: pointer;
  font-family: 'DM Sans', sans-serif;
  transition: color 0.15s, border-color 0.15s;
}
.sim-btn-ghost:hover {
  color: #E8EAE9;
  border-color: #4AE89A;
}
.sim-btn-ghost--danger:hover {
  color: #F05858;
  border-color: #F05858;
}

.p-btn-primary {
  background: #4AE89A;
  color: #0D0F0E;
  border: none;
  border-radius: 8px;
  padding: 10px 18px;
  font-family: 'DM Sans', sans-serif;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: opacity 0.15s;
  white-space: nowrap;
}
.p-btn-primary:hover { opacity: 0.85; }

/* ─── Three-panel layout ─────────────────────────────────────────────────────── */
.sim-panels {
  display: grid;
  grid-template-columns: 320px 1fr 280px;
  gap: 16px;
  flex: 1;
  min-height: 0;
}

.sim-panel {
  background: #111413;
  border: 1px solid #1E2421;
  border-radius: 12px;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.sim-panel-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 18px 12px;
  border-bottom: 1px solid #1E2421;
  flex-shrink: 0;
}

.sim-panel-title {
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.08em;
  color: #5A6460;
  margin: 0;
  padding: 16px 18px 12px;
}

.sim-panel-header .sim-panel-title {
  padding: 0;
}

/* ─── Feed filter buttons ────────────────────────────────────────────────────── */
.sim-filter-btns {
  display: flex;
  gap: 4px;
}
.sim-filter-btn {
  width: 32px;
  height: 26px;
  border: 1px solid #2E3D37;
  border-radius: 5px;
  background: none;
  color: #5A6460;
  font-size: 11px;
  font-weight: 700;
  cursor: pointer;
  font-family: 'DM Sans', sans-serif;
  transition: all 0.15s;
}
.sim-filter-btn.active {
  background: #1E2421;
  color: #E8EAE9;
  border-color: #4AE89A;
}
.sim-filter-btn:hover:not(.active) {
  border-color: #4A5450;
  color: #8A9490;
}

/* ─── Feed list ──────────────────────────────────────────────────────────────── */
.sim-feed-list {
  flex: 1;
  overflow-y: auto;
  padding: 8px 0;
  scroll-behavior: smooth;
}
.sim-feed-list::-webkit-scrollbar {
  width: 4px;
}
.sim-feed-list::-webkit-scrollbar-track {
  background: transparent;
}
.sim-feed-list::-webkit-scrollbar-thumb {
  background: #2E3D37;
  border-radius: 4px;
}

.sim-feed-item {
  padding: 12px 18px;
  border-bottom: 1px solid #1A1F1D;
  cursor: pointer;
  transition: background 0.15s;
}
.sim-feed-item:hover {
  background: #161A18;
}

.sim-feed-row {
  display: flex;
  gap: 10px;
  align-items: flex-start;
}

.sim-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 11px;
  font-weight: 700;
  color: #0D0F0E;
  flex-shrink: 0;
}

.sim-feed-body {
  flex: 1;
  min-width: 0;
}

.sim-feed-meta {
  display: flex;
  align-items: baseline;
  gap: 6px;
  margin-bottom: 3px;
}
.sim-feed-name {
  font-size: 13px;
  font-weight: 600;
  color: #E8EAE9;
}
.sim-feed-persona {
  font-size: 11px;
  color: #5A6460;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.sim-feed-content {
  font-size: 12px;
  color: #8A9490;
  line-height: 1.45;
}

.sim-feed-indicators {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
  flex-shrink: 0;
  padding-top: 2px;
}

.sim-sentiment-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  flex-shrink: 0;
}

.sim-variant-badge {
  font-size: 10px;
  font-weight: 700;
  padding: 2px 7px;
  border-radius: 4px;
  line-height: 1;
}
.sim-variant-badge--a {
  background: #1A2F26;
  color: #4AE89A;
}
.sim-variant-badge--b {
  background: #1A2530;
  color: #5BADEE;
}

/* ─── Feed expanded detail ───────────────────────────────────────────────────── */
.sim-feed-detail {
  margin-top: 10px;
  padding: 10px 12px;
  background: #0D0F0E;
  border-radius: 8px;
  display: flex;
  flex-direction: column;
  gap: 8px;
  animation: detailIn 0.2s ease;
}
@keyframes detailIn {
  from { opacity: 0; transform: translateY(-4px); }
  to { opacity: 1; transform: translateY(0); }
}
.sim-detail-row {
  display: flex;
  flex-direction: column;
  gap: 2px;
}
.sim-detail-label {
  font-size: 10px;
  font-weight: 700;
  color: #4A5450;
  text-transform: uppercase;
  letter-spacing: 0.06em;
}
.sim-detail-value {
  font-size: 12px;
  color: #8A9490;
  line-height: 1.4;
}

/* ─── Feed empty state ───────────────────────────────────────────────────────── */
.sim-feed-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 48px 20px;
  color: #4A5450;
  font-size: 13px;
  gap: 12px;
}
.sim-feed-empty-dots {
  display: flex;
  gap: 4px;
}
.sim-dot-bounce {
  width: 6px;
  height: 6px;
  background: #4AE89A;
  border-radius: 50%;
  animation: dotBounce 1.2s ease-in-out infinite;
}
.sim-dot-bounce:nth-child(2) { animation-delay: 0.2s; }
.sim-dot-bounce:nth-child(3) { animation-delay: 0.4s; }
@keyframes dotBounce {
  0%, 80%, 100% { transform: translateY(0); opacity: 0.4; }
  40% { transform: translateY(-6px); opacity: 1; }
}

/* Feed item transitions */
.feed-item-enter-active {
  transition: all 0.3s ease;
}
.feed-item-enter-from {
  opacity: 0;
  transform: translateX(-12px);
}

/* ─── Center panel: Variant Comparison ───────────────────────────────────────── */
.sim-panel--compare {
  overflow-y: auto;
}
.sim-panel--compare::-webkit-scrollbar {
  width: 4px;
}
.sim-panel--compare::-webkit-scrollbar-thumb {
  background: #2E3D37;
  border-radius: 4px;
}

.sim-compare-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  padding: 0 18px 18px;
}

.sim-compare-col {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.sim-compare-header {
  display: flex;
  align-items: center;
  gap: 8px;
}
.sim-compare-label {
  font-size: 14px;
  font-weight: 600;
  color: #E8EAE9;
}

.sim-compare-progress {
  display: flex;
  align-items: center;
  gap: 10px;
}
.sim-compare-bar {
  flex: 1;
  height: 6px;
  background: #1E2421;
  border-radius: 6px;
  overflow: hidden;
}
.sim-compare-fill {
  height: 100%;
  border-radius: 6px;
  transition: width 0.6s ease;
}
.sim-compare-fill--a { background: #4AE89A; }
.sim-compare-fill--b { background: #5BADEE; }
.sim-compare-pct {
  font-size: 14px;
  font-weight: 700;
  color: #E8EAE9;
  min-width: 36px;
  text-align: right;
}

/* ─── Sentiment arc ──────────────────────────────────────────────────────────── */
.sim-sentiment-arc {
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.sim-sentiment-arc-label {
  font-size: 10px;
  font-weight: 600;
  color: #4A5450;
  text-transform: uppercase;
  letter-spacing: 0.06em;
}
.sim-arc-bars {
  display: flex;
  align-items: flex-end;
  gap: 3px;
  height: 48px;
  padding: 4px 0;
}
.sim-arc-bar {
  flex: 1;
  min-width: 4px;
  max-width: 14px;
  border-radius: 2px 2px 0 0;
  transition: height 0.4s ease, background 0.4s ease;
}

/* ─── Early signals ──────────────────────────────────────────────────────────── */
.sim-signals {
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.sim-signal-label {
  font-size: 10px;
  font-weight: 600;
  color: #4A5450;
  text-transform: uppercase;
  letter-spacing: 0.06em;
}
.sim-signal-item {
  font-size: 12px;
  color: #8A9490;
  display: flex;
  align-items: flex-start;
  gap: 6px;
  line-height: 1.4;
}
.sim-signal-icon {
  font-size: 10px;
  flex-shrink: 0;
  margin-top: 2px;
}

/* ─── Right panel: Population Map ────────────────────────────────────────────── */
.sim-panel--pop {
  overflow-y: auto;
}
.sim-panel--pop::-webkit-scrollbar {
  width: 4px;
}
.sim-panel--pop::-webkit-scrollbar-thumb {
  background: #2E3D37;
  border-radius: 4px;
}

.sim-pop-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding: 0 18px 18px;
}

.sim-pop-row {
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.sim-pop-label {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: #8A9490;
  font-weight: 500;
}
.sim-pop-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  flex-shrink: 0;
}
.sim-pop-bar-wrap {
  display: flex;
  align-items: center;
  gap: 8px;
}
.sim-pop-bar {
  flex: 1;
  height: 5px;
  background: #1E2421;
  border-radius: 5px;
  overflow: hidden;
}
.sim-pop-fill {
  height: 100%;
  border-radius: 5px;
  transition: width 0.6s ease;
}
.sim-pop-pct {
  font-size: 12px;
  font-weight: 600;
  color: #6A7870;
  min-width: 30px;
  text-align: right;
}

/* ─── Key Moments ────────────────────────────────────────────────────────────── */
.sim-moments {
  padding: 18px 18px;
  border-top: 1px solid #1E2421;
}
.sim-moments-title {
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.08em;
  color: #5A6460;
  margin: 0 0 12px;
}
.sim-moment-item {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  font-size: 12px;
  color: #8A9490;
  line-height: 1.4;
  margin-bottom: 8px;
}
.sim-moment-icon {
  font-size: 10px;
  flex-shrink: 0;
  margin-top: 2px;
  color: #4AE89A;
}
</style>
