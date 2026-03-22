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

      <!-- Loading / Error states -->
      <div v-if="simRunning" class="sim-loading">
        <div class="sim-loading-spinner"></div>
        <p>Running simulation — analyzing 200 agents across both variants...</p>
        <p class="sim-loading-sub">This takes 5-15 seconds</p>
      </div>
      <div v-if="simError" class="sim-error">
        <p>Simulation failed: {{ simError }}</p>
        <button class="p-btn-primary" @click="runSimulation">Retry</button>
      </div>

      <!-- Three-panel layout -->
      <div v-if="!simRunning" class="sim-panels">
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
import axios from 'axios'

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

// ─── Agent lookup (loaded from API) ─────────────────────────────────────────
const agentsById = ref({})

// ─── State ───────────────────────────────────────────────────────────────────
const events = ref([])
const feedFilter = ref('both')
const expandedEvent = ref(null)
const paused = ref(false)
const simComplete = ref(false)
const simRunning = ref(false)
const simError = ref(null)
const feedListRef = ref(null)
const allRawEvents = ref([])   // Full event list from API (replayed by timer)
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

const totalEventsExpected = computed(() => allRawEvents.value.length || 50)

const variantAProgress = computed(() => {
  const totalA = allRawEvents.value.filter(e => e.variant === 'a').length || 1
  return Math.min(100, Math.round((variantAEvents.value.length / totalA) * 100))
})

const variantBProgress = computed(() => {
  const totalB = allRawEvents.value.filter(e => e.variant === 'b').length || 1
  return Math.min(100, Math.round((variantBEvents.value.length / totalB) * 100))
})

const remainingMin = computed(() => {
  const done = events.value.length
  const total = totalEventsExpected.value
  const remaining = total - done
  return Math.max(1, Math.round((remaining * 1.5) / 60))
})

// Sentiment arcs
const sentimentArcA = computed(() => variantAEvents.value.map(e => e.sentiment))
const sentimentArcB = computed(() => variantBEvents.value.map(e => e.sentiment))

function arcBarHeight(val) {
  const pct = Math.round(((val + 1) / 2) * 80 + 10)
  return pct + '%'
}

// Early signals — derived from real event data
const signalsA = computed(() => {
  const sigs = []
  const aEvts = variantAEvents.value
  if (aEvts.length >= 3) {
    const avgSentiment = aEvts.reduce((s, e) => s + e.sentiment, 0) / aEvts.length
    if (avgSentiment > 0.2) sigs.push({ positive: true, text: `Positive momentum — avg sentiment ${avgSentiment.toFixed(2)}` })
    if (avgSentiment < -0.1) sigs.push({ positive: false, text: `Friction building — avg sentiment ${avgSentiment.toFixed(2)}` })
    const abandonments = aEvts.filter(e => e.content.toLowerCase().includes('abandon'))
    if (abandonments.length > 0) sigs.push({ positive: false, text: `${abandonments.length} abandonment signal(s)` })
    const positive = aEvts.filter(e => e.sentiment > 0.5)
    if (positive.length >= 3) sigs.push({ positive: true, text: `${positive.length} strongly positive reactions` })
  }
  return sigs
})

const signalsB = computed(() => {
  const sigs = []
  const bEvts = variantBEvents.value
  if (bEvts.length >= 3) {
    const avgSentiment = bEvts.reduce((s, e) => s + e.sentiment, 0) / bEvts.length
    if (avgSentiment > 0.2) sigs.push({ positive: true, text: `Positive momentum — avg sentiment ${avgSentiment.toFixed(2)}` })
    if (avgSentiment < -0.1) sigs.push({ positive: false, text: `Friction building — avg sentiment ${avgSentiment.toFixed(2)}` })
    const abandonments = bEvts.filter(e => e.content.toLowerCase().includes('abandon'))
    if (abandonments.length > 0) sigs.push({ positive: false, text: `${abandonments.length} abandonment signal(s)` })
    const positive = bEvts.filter(e => e.sentiment > 0.5)
    if (positive.length >= 3) sigs.push({ positive: true, text: `${positive.length} strongly positive reactions` })
  }
  return sigs
})

// Cluster progress
const clusterProgress = computed(() => {
  const clusterCounts = {}
  const totalPerCluster = Math.max(1, Math.floor(events.value.length / Object.keys(CLUSTER_COLORS).length))

  for (const key of Object.keys(CLUSTER_COLORS)) {
    clusterCounts[key] = 0
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
    pct: Math.min(100, Math.round((clusterCounts[key] / Math.max(totalPerCluster, 1)) * 100))
  }))
})

// Key moments
const keyMoments = computed(() => {
  const moments = []
  const evts = events.value

  const firstAbandon = evts.find(e => e.content.toLowerCase().includes('abandon'))
  if (firstAbandon) {
    moments.push({ icon: '⚠', text: `${firstAbandon.agent.name} showed abandonment signals (${firstAbandon.variant.toUpperCase()})` })
  }

  const highEngagement = evts.filter(e => e.sentiment > 0.6)
  if (highEngagement.length >= 2) {
    moments.push({ icon: '▲', text: `${highEngagement.length} highly positive reactions` })
  }

  const negativeEvents = evts.filter(e => e.sentiment < -0.3)
  if (negativeEvents.length >= 2) {
    moments.push({ icon: '●', text: `${negativeEvents.length} friction events detected` })
  }

  // Sentiment divergence
  if (variantAEvents.value.length >= 3 && variantBEvents.value.length >= 3) {
    const avgA = variantAEvents.value.reduce((s, e) => s + e.sentiment, 0) / variantAEvents.value.length
    const avgB = variantBEvents.value.reduce((s, e) => s + e.sentiment, 0) / variantBEvents.value.length
    if (Math.abs(avgA - avgB) > 0.15) {
      const leading = avgA > avgB ? 'A' : 'B'
      moments.push({ icon: '✦', text: `Variant ${leading} pulling ahead in sentiment` })
    }
  }

  return moments
})

// ─── Helpers ─────────────────────────────────────────────────────────────────
function initials(name) {
  if (!name) return '??'
  return name.split(' ').map(w => w[0]).join('').toUpperCase().slice(0, 2)
}

function sentimentColor(val) {
  if (val >= 0.3) return '#4AE89A'
  if (val >= -0.3) return '#F0A843'
  return '#F05858'
}

function _resolveAgentInfo(agentId) {
  const agent = agentsById.value[agentId]
  if (!agent) return { name: 'Agent', cluster: 'value_driven', primaryPersona: 'Unknown', blend: '', backstory: '' }
  const blend = agent.persona_blend || []
  const primary = blend.length ? blend.reduce((a, b) => (a.influence || 0) > (b.influence || 0) ? a : b, blend[0]) : {}
  // Determine cluster from primary persona slug
  const clusterMap = {
    deal_hunter: 'value_driven', meticulous_optimizer: 'value_driven', coupon_stacker: 'value_driven',
    comparison_shopper: 'value_driven', sunk_cost_holder: 'value_driven', free_trial_maximizer: 'value_driven', bulk_buyer: 'value_driven',
    time_starved_parent: 'convenience_driven', passive_subscriber: 'convenience_driven', one_click_converter: 'convenience_driven',
    repeat_habit_user: 'convenience_driven', low_effort_decider: 'convenience_driven', auto_renewer: 'convenience_driven',
    brand_loyalist: 'trust_driven', social_proof_seeker: 'trust_driven', influencer_follower: 'trust_driven',
    review_reader: 'trust_driven', word_of_mouth_converter: 'trust_driven', skeptic: 'trust_driven', privacy_conscious: 'trust_driven',
    status_signaler: 'identity_driven', early_adopter: 'identity_driven', premium_seeker: 'identity_driven',
    conscious_consumer: 'identity_driven', community_member: 'identity_driven', power_user: 'identity_driven',
    gift_recipient: 'situational', corporate_user: 'situational', seasonal_shopper: 'situational',
    life_event_trigger: 'situational', reluctant_subscriber: 'situational', lapsed_returner: 'situational', trial_convert: 'situational',
    active_canceler: 'resistance', passive_churner: 'resistance', price_shock_abandoner: 'resistance',
    complexity_avoider: 'resistance', decision_deferrer: 'resistance', silent_dissatisfied: 'resistance', feature_mismatcher: 'resistance',
  }
  const primarySlug = primary.slug || ''
  const cluster = clusterMap[primarySlug] || 'value_driven'
  const blendStr = blend.map(b => `${(b.slug || '').replace(/_/g, ' ')} ${Math.round((b.influence || 0) * 100)}%`).join(' / ')
  return {
    name: agent.name || 'Agent',
    cluster,
    primaryPersona: (primarySlug || '').replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()),
    blend: blendStr,
    backstory: agent.backstory || '',
  }
}

// ─── Simulation control ──────────────────────────────────────────────────────

function emitNextEvent() {
  if (eventIndex >= allRawEvents.value.length) {
    simComplete.value = true
    clearInterval(timer)
    // Trigger prediction generation
    triggerPrediction()
    return
  }

  const raw = allRawEvents.value[eventIndex]
  const agentInfo = _resolveAgentInfo(raw.agent_id)

  events.value.push({
    id: ++eventIdCounter,
    variant: raw.variant,
    agent: agentInfo,
    step: raw.step || raw.journey_step || '',
    event_type: raw.event_type,
    content: raw.content,
    sentiment: parseFloat(raw.sentiment) || 0,
    reasoning: `Disposition-driven ${raw.event_type} at step "${raw.step || raw.journey_step || '?'}"`
  })

  eventIndex++

  nextTick(() => {
    if (feedListRef.value) {
      feedListRef.value.scrollTop = feedListRef.value.scrollHeight
    }
  })
}

async function triggerPrediction() {
  try {
    await axios.post(`/api/prelude/experiments/${props.id}/predict`)
  } catch (e) {
    console.warn('Prediction generation failed:', e)
  }
}

async function runSimulation() {
  simRunning.value = true
  simError.value = null
  try {
    // 1. Load agents for this experiment
    const { data: popData } = await axios.get(`/api/prelude/experiments/${props.id}/population`)
    const agentList = popData.agents || popData.sample_agents || []
    // Also get full agent list from DB if population endpoint returns samples
    if (popData.all_agents) {
      for (const a of popData.all_agents) { agentsById.value[String(a.id)] = a }
    }
    for (const a of agentList) { agentsById.value[String(a.id)] = a }

    // 2. Trigger simulation (synchronous — returns events for both variants)
    const { data: simData } = await axios.post(`/api/prelude/experiments/${props.id}/simulation/simulate`)

    // 3. Load full event list from DB
    const { data: evtData } = await axios.get(`/api/prelude/experiments/${props.id}/simulation/events`)

    // Also load agents if we didn't get them from population
    if (Object.keys(agentsById.value).length === 0) {
      // Fallback: extract agent info from events
      for (const ev of (evtData.events || [])) {
        if (ev.agent_id && !agentsById.value[String(ev.agent_id)]) {
          agentsById.value[String(ev.agent_id)] = {
            id: ev.agent_id,
            name: ev.agent_name || 'Agent',
            persona_blend: ev.persona_blend || [],
            traits: ev.traits || {},
            backstory: '',
          }
        }
      }
    }

    // 4. Build interleaved event list for replay
    const rawEvents = (evtData.events || []).map(ev => ({
      ...ev,
      variant: ev.variant || 'a',
      step: ev.journey_step || ev.step || '',
    }))

    allRawEvents.value = rawEvents
    simRunning.value = false

    // 5. Start replaying events with timer
    startReplay()

  } catch (e) {
    simError.value = e.response?.data?.error || e.message || 'Simulation failed'
    simRunning.value = false
    console.error('Simulation error:', e)
  }
}

async function loadExistingRun() {
  // Check if simulation already ran — load events from DB
  try {
    const { data: evtData } = await axios.get(`/api/prelude/experiments/${props.id}/simulation/events`)
    if (evtData.events && evtData.events.length > 0) {
      // Load agents
      const { data: popData } = await axios.get(`/api/prelude/experiments/${props.id}/population`)
      const agentList = popData.all_agents || popData.agents || popData.sample_agents || []
      for (const a of agentList) { agentsById.value[String(a.id)] = a }
      for (const ev of evtData.events) {
        if (ev.agent_id && !agentsById.value[String(ev.agent_id)]) {
          agentsById.value[String(ev.agent_id)] = {
            id: ev.agent_id, name: ev.agent_name || 'Agent',
            persona_blend: ev.persona_blend || [], traits: ev.traits || {},
          }
        }
      }

      allRawEvents.value = evtData.events.map(ev => ({
        ...ev, variant: ev.variant || 'a', step: ev.journey_step || ev.step || '',
      }))
      startReplay()
      return true
    }
  } catch {}
  return false
}

function startReplay() {
  timer = setInterval(() => {
    if (!paused.value) emitNextEvent()
  }, 800)  // Faster replay for real data
}

function togglePause() {
  paused.value = !paused.value
}

function cancelSim() {
  clearInterval(timer)
  router.push(`/prelude/personas/${props.id}`)
}

onMounted(async () => {
  // First check if simulation already ran
  const existing = await loadExistingRun()
  if (!existing) {
    // Run fresh simulation
    await runSimulation()
  }
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

/* ─── Loading / Error ────────────────────────────────────────────────────────── */
.sim-loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  flex: 1;
  gap: 16px;
  color: #8A9490;
  font-size: 15px;
}
.sim-loading-spinner {
  width: 36px;
  height: 36px;
  border: 3px solid #1E2421;
  border-top-color: #4AE89A;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }
.sim-loading-sub {
  font-size: 13px;
  color: #5A6460;
}
.sim-error {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
  padding: 40px;
  color: #F05858;
  font-size: 14px;
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
