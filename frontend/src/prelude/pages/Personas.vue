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
        <button class="p-back-btn" @click="goBack">← {{ mode === 'build' ? 'Brief' : 'Back' }}</button>
        <div class="p-progress-bar">
          <div class="p-progress-step done"><span class="p-progress-dot"></span><span class="p-progress-label">Brief</span></div>
          <div class="p-progress-step active"><span class="p-progress-dot"></span><span class="p-progress-label">Personas</span></div>
          <div class="p-progress-step"><span class="p-progress-dot"></span><span class="p-progress-label">Simulation</span></div>
          <div class="p-progress-step"><span class="p-progress-dot"></span><span class="p-progress-label">Results</span></div>
        </div>
      </div>

      <!-- ═══════ BUILD MODE ═══════ -->
      <template v-if="mode === 'build'">
        <h1 class="p-page-title">Who will react to your feature?</h1>
        <p class="p-page-sub">We've suggested a starting population. Adjust as needed.</p>

        <!-- Mode toggle -->
        <div class="p-mode-toggle">
          <button class="p-mode-btn active">Build</button>
          <button class="p-mode-btn" @click="mode = 'browse'">Browse All</button>
        </div>

        <!-- Loading state -->
        <div v-if="buildLoading" class="p-build-loading">
          Analyzing your brief and selecting personas...
        </div>

        <!-- Population list -->
        <div v-else class="p-build-section">
          <div class="p-build-header">
            <span class="p-build-count">SUGGESTED ({{ population.length }} of 40 personas)</span>
            <span class="p-build-agents">Total: {{ agentCount }} agents</span>
          </div>

          <div class="p-population-list">
            <div
              v-for="(p, idx) in population"
              :key="p.slug"
              class="p-pop-row"
            >
              <span class="p-pop-dot">●</span>
              <span class="p-pop-name" @click="openPersonaDetail(p.slug)">{{ p.name }}</span>
              <span class="p-cluster-badge p-cluster-badge--sm" :style="{ background: clusterColor(p.cluster) + '22', color: clusterColor(p.cluster) }">
                {{ clusterLabel(p.cluster) }}
              </span>
              <div class="p-weight-slider-wrap">
                <input
                  type="range"
                  class="p-weight-slider"
                  min="1"
                  max="100"
                  :value="Math.round(p.weight * 100)"
                  @input="onWeightChange(idx, $event)"
                />
              </div>
              <span class="p-pop-weight">{{ Math.round(p.weight * 100) }}%</span>
              <button class="p-pop-remove" @click="removePersona(idx)" title="Remove">✕</button>
            </div>
          </div>

          <!-- Actions -->
          <div class="p-build-actions">
            <button class="p-btn-secondary" @click="showAddPersona = true">+ Add persona</button>
            <button class="p-btn-secondary" @click="regenerateSuggestion">Regenerate suggestion</button>
          </div>

          <!-- Hybrid blending info -->
          <div class="p-blend-info">
            <p>Hybrid blending: each agent blends 2-3 personas</p>
            <button class="p-btn-secondary" @click="previewSampleAgent">Preview a sample agent</button>
          </div>

          <!-- Run Simulation CTA -->
          <button class="p-btn-primary p-run-btn" @click="runSimulation" :disabled="building">
            {{ building ? 'Building agents...' : 'Run Simulation →' }}
          </button>
        </div>
      </template>

      <!-- ═══════ BROWSE MODE ═══════ -->
      <template v-else>
        <h1 class="p-page-title">Who could react to your feature?</h1>
        <p class="p-page-sub">40 persona archetypes across 6 behavioral clusters. Filter, search, and explore.</p>

        <!-- Mode toggle (only show if we have an experiment) -->
        <div v-if="id" class="p-mode-toggle">
          <button class="p-mode-btn" @click="mode = 'build'">Build</button>
          <button class="p-mode-btn active">Browse All</button>
        </div>

        <!-- Filters -->
        <div class="p-filters">
          <button
            v-for="f in filterOptions"
            :key="f.value"
            class="p-filter-btn"
            :class="{ active: activeCluster === f.value }"
            :style="activeCluster === f.value ? { background: f.color + '22', color: f.color, borderColor: f.color + '44' } : {}"
            @click="activeCluster = activeCluster === f.value ? null : f.value"
          >{{ f.label }}</button>
          <div class="p-search-wrap">
            <input
              v-model="searchQuery"
              class="p-search"
              placeholder="Search personas..."
              type="text"
            />
          </div>
        </div>

        <!-- Persona grid -->
        <div class="p-persona-grid">
          <div
            v-for="p in filteredPersonas"
            :key="p.slug"
            class="p-persona-card"
            :class="{ selected: selectedPersona?.slug === p.slug }"
            @click="selectedPersona = p"
          >
            <div class="p-persona-top">
              <span class="p-cluster-badge" :style="{ background: clusterColor(p.cluster) + '22', color: clusterColor(p.cluster) }">
                {{ clusterLabel(p.cluster) }}
              </span>
            </div>
            <h3 class="p-persona-name">{{ p.name }}</h3>
            <p class="p-persona-short">{{ p.short_desc }}</p>
            <!-- Top 3 traits as mini bars -->
            <div class="p-trait-bars">
              <div v-for="t in topTraits(p)" :key="t.name" class="p-trait-row">
                <span class="p-trait-label">{{ t.name }}</span>
                <div class="p-trait-track">
                  <div class="p-trait-fill" :style="{ width: (t.value * 100) + '%', background: clusterColor(p.cluster) }"></div>
                </div>
              </div>
            </div>
            <!-- Motivation & fear -->
            <div class="p-persona-hints">
              <div class="p-hint"><span class="p-hint-icon">↑</span>{{ p.motivations[0] }}</div>
              <div class="p-hint"><span class="p-hint-icon">↓</span>{{ p.fears[0] }}</div>
            </div>
          </div>

          <!-- Empty state -->
          <div v-if="filteredPersonas.length === 0" class="p-empty-personas">
            No personas match your search.
          </div>
        </div>
      </template>

    </main>

    <!-- Detail panel — teleported to escape scroll stacking context -->
    <Teleport to="#app">
      <transition name="panel-slide">
        <div v-if="selectedPersona" class="p-detail-backdrop" @click="selectedPersona = null"></div>
      </transition>
      <transition name="panel-slide">
        <div v-if="selectedPersona" class="p-detail-panel">
            <div class="p-detail-header">
              <div>
                <span class="p-cluster-badge p-cluster-badge--lg" :style="{ background: clusterColor(selectedPersona.cluster) + '22', color: clusterColor(selectedPersona.cluster) }">
                  {{ clusterLabel(selectedPersona.cluster) }}
                </span>
                <h2 class="p-detail-name">{{ selectedPersona.name }}</h2>
              </div>
              <button class="p-detail-close" @click="selectedPersona = null">✕</button>
            </div>

            <p class="p-detail-desc">{{ selectedPersona.description }}</p>

            <div class="p-detail-quote">"{{ selectedPersona.representative_quote }}"</div>

            <!-- All traits -->
            <div class="p-detail-section">
              <h4 class="p-detail-section-title">Traits</h4>
              <div class="p-trait-bars p-trait-bars--full">
                <div v-for="(val, key) in selectedPersona.traits" :key="key" class="p-trait-row">
                  <span class="p-trait-label">{{ formatTrait(key) }}</span>
                  <div class="p-trait-track">
                    <div class="p-trait-fill" :style="{ width: (val * 100) + '%', background: clusterColor(selectedPersona.cluster) }"></div>
                  </div>
                  <span class="p-trait-val">{{ Math.round(val * 100) }}</span>
                </div>
              </div>
            </div>

            <!-- Motivations -->
            <div class="p-detail-section">
              <h4 class="p-detail-section-title">Motivations</h4>
              <ul class="p-detail-list">
                <li v-for="m in selectedPersona.motivations" :key="m">{{ m }}</li>
              </ul>
            </div>

            <!-- Fears -->
            <div class="p-detail-section">
              <h4 class="p-detail-section-title">Fears</h4>
              <ul class="p-detail-list p-detail-list--fear">
                <li v-for="f in selectedPersona.fears" :key="f">{{ f }}</li>
              </ul>
            </div>

            <!-- Triggers -->
            <div class="p-detail-section">
              <h4 class="p-detail-section-title">Triggers</h4>
              <ul class="p-detail-list p-detail-list--trigger">
                <li v-for="t in selectedPersona.triggers" :key="t">{{ t }}</li>
              </ul>
            </div>

            <!-- Abandonment signals -->
            <div class="p-detail-section">
              <h4 class="p-detail-section-title">Abandonment Signals</h4>
              <ul class="p-detail-list p-detail-list--abandon">
                <li v-for="a in selectedPersona.abandonment_signals" :key="a">{{ a }}</li>
              </ul>
            </div>

            <!-- Journey pattern -->
            <div class="p-detail-section">
              <h4 class="p-detail-section-title">Typical Journey</h4>
              <p class="p-detail-journey">{{ selectedPersona.journey_pattern }}</p>
            </div>

            <!-- Domain relevance -->
            <div class="p-detail-section">
              <h4 class="p-detail-section-title">Domain Relevance</h4>
              <div class="p-relevance-bars">
                <div v-for="(val, domain) in selectedPersona.category_relevance" :key="domain" class="p-relevance-row">
                  <span class="p-relevance-label">{{ formatDomain(domain) }}</span>
                  <div class="p-trait-track">
                    <div class="p-trait-fill" :style="{ width: (val * 100) + '%', background: domainColor(domain) }"></div>
                  </div>
                  <span class="p-trait-val">{{ Math.round(val * 100) }}%</span>
                </div>
              </div>
            </div>

            <!-- Add to population button (in browse mode with experiment) -->
            <button
              v-if="mode === 'browse' && id && !isInPopulation(selectedPersona.slug)"
              class="p-btn-primary p-add-to-pop"
              @click="addToPopulation(selectedPersona); selectedPersona = null"
            >
              + Add to Population
            </button>
          </div>
        </transition>

      <!-- Add persona picker modal -->
      <transition name="panel-slide">
        <div v-if="showAddPersona" class="p-detail-backdrop" @click="showAddPersona = false"></div>
      </transition>
      <transition name="panel-slide">
        <div v-if="showAddPersona" class="p-detail-panel p-add-panel">
          <div class="p-detail-header">
            <h2 class="p-detail-name">Add Persona</h2>
            <button class="p-detail-close" @click="showAddPersona = false">✕</button>
          </div>
          <input
            v-model="addSearchQuery"
            class="p-search p-add-search"
            placeholder="Search personas to add..."
            type="text"
          />
          <div class="p-add-list">
            <div
              v-for="p in addablePersonas"
              :key="p.slug"
              class="p-add-item"
              @click="addToPopulation(p); showAddPersona = false"
            >
              <span class="p-cluster-badge p-cluster-badge--sm" :style="{ background: clusterColor(p.cluster) + '22', color: clusterColor(p.cluster) }">
                {{ clusterLabel(p.cluster) }}
              </span>
              <span class="p-add-item-name">{{ p.name }}</span>
              <span class="p-add-item-desc">{{ p.short_desc }}</span>
            </div>
          </div>
        </div>
      </transition>

      <!-- Sample agent preview modal -->
      <transition name="panel-slide">
        <div v-if="sampleAgent" class="p-detail-backdrop" @click="sampleAgent = null"></div>
      </transition>
      <transition name="panel-slide">
        <div v-if="sampleAgent" class="p-detail-panel p-sample-panel">
          <div class="p-detail-header">
            <h2 class="p-detail-name">Sample Agent: {{ sampleAgent.name }}</h2>
            <button class="p-detail-close" @click="sampleAgent = null">✕</button>
          </div>

          <div class="p-sample-blend">
            <div v-for="(comp, i) in sampleAgent.persona_blend" :key="comp.slug" class="p-sample-comp">
              <span class="p-sample-role">{{ i === 0 ? 'Primary' : i === 1 ? 'Secondary' : 'Tertiary' }}:</span>
              <span class="p-sample-persona">{{ personaNameBySlug(comp.slug) }}</span>
              <span class="p-sample-pct">{{ Math.round(comp.influence * 100) }}%</span>
            </div>
          </div>

          <div class="p-detail-quote">"{{ sampleAgent.backstory }}"</div>

          <div class="p-detail-section">
            <h4 class="p-detail-section-title">Blended Traits</h4>
            <div class="p-trait-bars p-trait-bars--full">
              <div v-for="(val, key) in sampleAgent.traits" :key="key" class="p-trait-row">
                <span class="p-trait-label">{{ formatTrait(key) }}</span>
                <div class="p-trait-track">
                  <div class="p-trait-fill" :style="{ width: (val * 100) + '%', background: '#4AE89A' }"></div>
                </div>
                <span class="p-trait-val">{{ Math.round(val * 100) }}</span>
              </div>
            </div>
          </div>

          <button class="p-btn-secondary p-gen-another" @click="previewSampleAgent">Generate another</button>
        </div>
      </transition>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'

const props = defineProps({ id: String })
const router = useRouter()

// ─── State ────────────────────────────────────────────────────────────────────
const personas = ref([])
const loading = ref(false)
const activeCluster = ref(null)
const searchQuery = ref('')
const selectedPersona = ref(null)

// Build mode state
const mode = ref(props.id ? 'build' : 'browse')
const experiment = ref(null)
const population = ref([])       // [{slug, name, cluster, weight, relevance_score}, ...]
const buildLoading = ref(false)
const building = ref(false)
const agentCount = ref(200)
const sampleAgent = ref(null)
const showAddPersona = ref(false)
const addSearchQuery = ref('')

// ─── Cluster config ───────────────────────────────────────────────────────────
const clusterColors = {
  value_driven: '#F0A843',
  convenience_driven: '#3BC4A0',
  trust_driven: '#5BADEE',
  identity_driven: '#A78BFA',
  situational: '#F07858',
  resistance: '#F05858',
}

const clusterLabels = {
  value_driven: 'Value',
  convenience_driven: 'Convenience',
  trust_driven: 'Trust',
  identity_driven: 'Identity',
  situational: 'Situational',
  resistance: 'Resistance',
}

const filterOptions = [
  { value: null, label: 'All', color: '#4AE89A' },
  { value: 'value_driven', label: 'Value', color: '#F0A843' },
  { value: 'convenience_driven', label: 'Convenience', color: '#3BC4A0' },
  { value: 'trust_driven', label: 'Trust', color: '#5BADEE' },
  { value: 'identity_driven', label: 'Identity', color: '#A78BFA' },
  { value: 'situational', label: 'Situational', color: '#F07858' },
  { value: 'resistance', label: 'Resistance', color: '#F05858' },
]

const domainColors = {
  retail: '#4AE89A',
  social_media: '#5BADEE',
  fintech: '#F0A843',
}

// ─── Computed ─────────────────────────────────────────────────────────────────
const filteredPersonas = computed(() => {
  let result = personas.value
  if (activeCluster.value) {
    result = result.filter(p => p.cluster === activeCluster.value)
  }
  if (searchQuery.value.trim()) {
    const q = searchQuery.value.toLowerCase()
    result = result.filter(p =>
      p.name.toLowerCase().includes(q) ||
      p.short_desc.toLowerCase().includes(q) ||
      p.description.toLowerCase().includes(q) ||
      p.slug.toLowerCase().includes(q)
    )
  }
  return result
})

const populationSlugs = computed(() => new Set(population.value.map(p => p.slug)))

const addablePersonas = computed(() => {
  const q = addSearchQuery.value.toLowerCase().trim()
  return personas.value.filter(p => {
    if (populationSlugs.value.has(p.slug)) return false
    if (!q) return true
    return p.name.toLowerCase().includes(q) ||
           p.short_desc.toLowerCase().includes(q) ||
           p.cluster.toLowerCase().includes(q)
  })
})

// ─── Helpers ──────────────────────────────────────────────────────────────────
function clusterColor(c) { return clusterColors[c] || '#5A6460' }
function clusterLabel(c) { return clusterLabels[c] || c }
function domainColor(d) { return domainColors[d] || '#5A6460' }

function formatTrait(key) {
  return key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())
}

function formatDomain(d) {
  return d.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())
}

function topTraits(persona) {
  const entries = Object.entries(persona.traits)
  entries.sort((a, b) => b[1] - a[1])
  return entries.slice(0, 3).map(([name, value]) => ({
    name: formatTrait(name),
    value,
  }))
}

function isInPopulation(slug) {
  return populationSlugs.value.has(slug)
}

function personaNameBySlug(slug) {
  const p = personas.value.find(x => x.slug === slug)
  return p ? p.name : slug
}

function goBack() {
  if (mode.value === 'build' && props.id) {
    router.push(`/prelude/brief/${props.id}`)
  } else {
    router.back()
  }
}

// ─── Weight management ───────────────────────────────────────────────────────
function onWeightChange(idx, event) {
  const newVal = parseInt(event.target.value) / 100
  population.value[idx].weight = newVal
  rebalanceWeights(idx)
}

function rebalanceWeights(changedIdx) {
  const changed = population.value[changedIdx].weight
  const others = population.value.filter((_, i) => i !== changedIdx)
  const remaining = Math.max(0, 1 - changed)
  const otherTotal = others.reduce((sum, p) => sum + p.weight, 0)

  if (otherTotal > 0) {
    for (let i = 0; i < population.value.length; i++) {
      if (i !== changedIdx) {
        population.value[i].weight = Math.max(0.01, (population.value[i].weight / otherTotal) * remaining)
      }
    }
  }
  // Normalize to exactly 1.0
  const total = population.value.reduce((s, p) => s + p.weight, 0)
  if (total > 0) {
    population.value.forEach(p => { p.weight = p.weight / total })
  }
}

function removePersona(idx) {
  population.value.splice(idx, 1)
  if (population.value.length > 0) {
    const total = population.value.reduce((s, p) => s + p.weight, 0)
    population.value.forEach(p => { p.weight = p.weight / total })
  }
}

function addToPopulation(persona) {
  if (isInPopulation(persona.slug)) return
  // Add with small weight, rebalance
  const newWeight = 0.05
  const scale = 1 - newWeight
  population.value.forEach(p => { p.weight *= scale })
  population.value.push({
    slug: persona.slug,
    name: persona.name,
    cluster: persona.cluster,
    weight: newWeight,
    relevance_score: 0,
  })
}

function openPersonaDetail(slug) {
  const p = personas.value.find(x => x.slug === slug)
  if (p) selectedPersona.value = p
}

// ─── Build mode weight map ───────────────────────────────────────────────────
function getWeightMap() {
  const map = {}
  for (const p of population.value) {
    map[p.slug] = p.weight
  }
  return map
}

// ─── API calls ───────────────────────────────────────────────────────────────
async function loadPersonas() {
  loading.value = true
  try {
    const { data } = await axios.get('/api/prelude/personas')
    personas.value = data
  } catch (e) {
    console.error('Failed to load personas:', e)
  } finally {
    loading.value = false
  }
}

async function loadExperiment() {
  if (!props.id) return
  try {
    const { data } = await axios.get(`/api/prelude/experiments/${props.id}`)
    experiment.value = data
  } catch (e) {
    console.error('Failed to load experiment:', e)
  }
}

async function generateSuggestion() {
  if (!props.id) return
  buildLoading.value = true
  try {
    const { data } = await axios.post(`/api/prelude/experiments/${props.id}/population/generate`)
    population.value = data.personas
  } catch (e) {
    console.error('Failed to generate population:', e)
  } finally {
    buildLoading.value = false
  }
}

async function regenerateSuggestion() {
  await generateSuggestion()
}

async function previewSampleAgent() {
  if (population.value.length === 0) return
  try {
    const { data } = await axios.post(`/api/prelude/experiments/${props.id}/population/preview-agent`, {
      persona_weights: getWeightMap(),
    })
    sampleAgent.value = data.agent
  } catch (e) {
    console.error('Failed to preview agent:', e)
  }
}

async function runSimulation() {
  if (building.value || population.value.length === 0) return
  building.value = true
  try {
    await axios.post(`/api/prelude/experiments/${props.id}/population/build`, {
      persona_weights: getWeightMap(),
      agent_count: agentCount.value,
    })
    router.push(`/prelude/sim/${props.id}`)
  } catch (e) {
    console.error('Failed to build population:', e)
    alert('Failed to build agents. Is the backend running?')
  } finally {
    building.value = false
  }
}

// ─── Lifecycle ───────────────────────────────────────────────────────────────
onMounted(async () => {
  await loadPersonas()
  if (props.id) {
    await loadExperiment()
    await generateSuggestion()
  }
})
</script>

<style scoped>
/* ─── Shell (matches Dashboard) ──────────────────────────────────────────── */
.p-shell {
  display: flex;
  min-height: 100vh;
  background: #0D0F0E;
  color: #E8EAE9;
  font-family: 'DM Sans', 'Inter', sans-serif;
}

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
.p-nav { display: flex; flex-direction: column; gap: 2px; padding: 0 12px; flex: 1; }
.p-nav-item {
  display: flex; align-items: center; gap: 10px; padding: 9px 12px;
  border-radius: 8px; font-size: 14px; font-weight: 500; color: #8A9490;
  text-decoration: none; transition: background 0.15s, color 0.15s;
}
.p-nav-item:hover, .p-nav-item.router-link-active { background: #1A1F1D; color: #E8EAE9; }
.p-nav-icon { font-size: 13px; opacity: 0.7; }

/* ─── Main ───────────────────────────────────────────────────────────────── */
.p-main {
  flex: 1;
  padding: 32px 40px;
}

.p-topbar-row {
  display: flex;
  align-items: center;
  gap: 24px;
  margin-bottom: 28px;
}
.p-back-btn {
  background: none; border: 1px solid #2E3D37; border-radius: 8px;
  color: #8A9490; padding: 6px 14px; font-size: 13px; cursor: pointer;
  transition: color 0.15s, border-color 0.15s;
}
.p-back-btn:hover { color: #E8EAE9; border-color: #4AE89A; }

.p-progress-bar { display: flex; gap: 0; flex: 1; }
.p-progress-step {
  display: flex; align-items: center; gap: 8px; padding: 6px 16px;
  font-size: 12px; color: #4A5450; position: relative;
}
.p-progress-step.done { color: #4AE89A; }
.p-progress-step.active { color: #E8EAE9; }
.p-progress-dot {
  width: 8px; height: 8px; border-radius: 50%;
  background: #2E3D37; flex-shrink: 0;
}
.p-progress-step.done .p-progress-dot { background: #4AE89A; }
.p-progress-step.active .p-progress-dot { background: #E8EAE9; box-shadow: 0 0 0 3px #2E3D37; }

.p-page-title {
  font-family: 'DM Serif Display', serif;
  font-size: 28px; font-weight: 400; color: #E8EAE9;
  margin: 0 0 8px; letter-spacing: -0.5px;
}
.p-page-sub { font-size: 14px; color: #6A7870; margin: 0 0 24px; }

/* ─── Mode toggle ────────────────────────────────────────────────────────── */
.p-mode-toggle {
  display: flex; gap: 4px; margin-bottom: 24px;
  background: #111413; border-radius: 10px; padding: 4px;
  width: fit-content;
}
.p-mode-btn {
  background: none; border: none; border-radius: 8px;
  padding: 7px 18px; font-size: 13px; font-weight: 500; color: #6A7870;
  cursor: pointer; transition: all 0.15s;
  font-family: 'DM Sans', sans-serif;
}
.p-mode-btn.active { background: #1A1F1D; color: #E8EAE9; }
.p-mode-btn:hover:not(.active) { color: #8A9490; }

/* ─── Build mode ─────────────────────────────────────────────────────────── */
.p-build-loading {
  text-align: center; padding: 60px 20px;
  color: #6A7870; font-size: 14px;
}
.p-build-section { max-width: 700px; }
.p-build-header {
  display: flex; justify-content: space-between; align-items: center;
  margin-bottom: 16px;
}
.p-build-count {
  font-size: 11px; font-weight: 700; color: #5A6460;
  text-transform: uppercase; letter-spacing: 0.08em;
}
.p-build-agents {
  font-size: 13px; color: #8A9490; font-weight: 500;
}

/* ─── Population list ────────────────────────────────────────────────────── */
.p-population-list {
  display: flex; flex-direction: column; gap: 2px;
  background: #111413; border: 1px solid #1E2421; border-radius: 12px;
  padding: 8px; margin-bottom: 16px;
}
.p-pop-row {
  display: flex; align-items: center; gap: 10px;
  padding: 10px 12px; border-radius: 8px;
  transition: background 0.1s;
}
.p-pop-row:hover { background: #161A18; }
.p-pop-dot { color: #4AE89A; font-size: 10px; flex-shrink: 0; }
.p-pop-name {
  font-size: 13px; font-weight: 600; color: #E8EAE9;
  min-width: 140px; cursor: pointer;
}
.p-pop-name:hover { color: #4AE89A; }
.p-cluster-badge--sm {
  font-size: 9px; font-weight: 700; padding: 2px 7px; border-radius: 20px;
  text-transform: uppercase; letter-spacing: 0.06em;
}
.p-weight-slider-wrap { flex: 1; min-width: 80px; }
.p-weight-slider {
  width: 100%; height: 4px; -webkit-appearance: none; appearance: none;
  background: #1E2421; border-radius: 4px; outline: none; cursor: pointer;
}
.p-weight-slider::-webkit-slider-thumb {
  -webkit-appearance: none; appearance: none;
  width: 14px; height: 14px; border-radius: 50%;
  background: #4AE89A; cursor: pointer; border: 2px solid #0D0F0E;
}
.p-pop-weight {
  font-size: 12px; color: #8A9490; width: 36px; text-align: right;
  font-variant-numeric: tabular-nums;
}
.p-pop-remove {
  background: none; border: none; color: #3A4440; font-size: 12px;
  cursor: pointer; padding: 2px 4px; transition: color 0.15s;
}
.p-pop-remove:hover { color: #F05858; }

/* ─── Build actions ──────────────────────────────────────────────────────── */
.p-build-actions {
  display: flex; gap: 10px; margin-bottom: 20px;
}
.p-btn-secondary {
  background: #161A18; border: 1px solid #2E3D37; border-radius: 8px;
  padding: 8px 16px; font-size: 13px; font-weight: 500; color: #8A9490;
  cursor: pointer; transition: all 0.15s;
  font-family: 'DM Sans', sans-serif;
}
.p-btn-secondary:hover { border-color: #4AE89A; color: #E8EAE9; }

.p-blend-info {
  background: #111413; border: 1px solid #1E2421; border-radius: 10px;
  padding: 16px 20px; margin-bottom: 24px;
}
.p-blend-info p {
  font-size: 13px; color: #6A7870; margin: 0 0 12px;
}

.p-btn-primary {
  background: #4AE89A; color: #0D0F0E; border: none; border-radius: 10px;
  padding: 12px 28px; font-size: 15px; font-weight: 600; cursor: pointer;
  transition: background 0.15s, transform 0.1s;
  font-family: 'DM Sans', sans-serif;
}
.p-btn-primary:hover { background: #3DD88A; transform: translateY(-1px); }
.p-btn-primary:disabled { opacity: 0.5; cursor: not-allowed; transform: none; }
.p-run-btn { width: 100%; }

.p-add-to-pop {
  width: 100%; margin-top: 16px;
}

/* ─── Filters ────────────────────────────────────────────────────────────── */
.p-filters {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 24px;
  align-items: center;
}
.p-filter-btn {
  background: #161A18; border: 1px solid #2E3D37; border-radius: 20px;
  padding: 6px 14px; font-size: 13px; font-weight: 500; color: #8A9490;
  cursor: pointer; transition: all 0.15s;
}
.p-filter-btn:hover { border-color: #4A5450; color: #E8EAE9; }
.p-filter-btn.active { font-weight: 600; }
.p-search-wrap { margin-left: auto; }
.p-search {
  background: #161A18; border: 1px solid #2E3D37; border-radius: 8px;
  padding: 7px 14px; font-size: 13px; color: #E8EAE9; width: 220px;
  outline: none; transition: border-color 0.15s;
  font-family: 'DM Sans', sans-serif;
}
.p-search:focus { border-color: #4AE89A; }
.p-search::placeholder { color: #4A5450; }

/* ─── Persona grid ───────────────────────────────────────────────────────── */
.p-persona-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 14px;
  flex: 1;
  min-width: 0;
  transition: all 0.2s;
}

.p-persona-card {
  background: #111413;
  border: 1px solid #1E2421;
  border-radius: 12px;
  padding: 18px 18px 14px;
  cursor: pointer;
  transition: border-color 0.15s, transform 0.1s;
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.p-persona-card:hover { border-color: #2E3D37; transform: translateY(-1px); }
.p-persona-card.selected { border-color: #4AE89A; background: #111a15; }

.p-persona-top { display: flex; gap: 8px; }
.p-cluster-badge {
  font-size: 10px; font-weight: 700; padding: 3px 9px; border-radius: 20px;
  text-transform: uppercase; letter-spacing: 0.06em;
}
.p-cluster-badge--lg { font-size: 11px; padding: 4px 12px; }

.p-persona-name {
  font-size: 15px; font-weight: 600; color: #E8EAE9;
  margin: 0; line-height: 1.3;
}
.p-persona-short {
  font-size: 12px; color: #6A7870; margin: 0;
  line-height: 1.45; display: -webkit-box;
  -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden;
}

/* ─── Trait bars ─────────────────────────────────────────────────────────── */
.p-trait-bars { display: flex; flex-direction: column; gap: 5px; }
.p-trait-row { display: flex; align-items: center; gap: 8px; }
.p-trait-label { font-size: 10px; color: #5A6460; width: 90px; flex-shrink: 0; text-transform: capitalize; }
.p-trait-track { flex: 1; height: 4px; background: #1E2421; border-radius: 4px; overflow: hidden; }
.p-trait-fill { height: 100%; border-radius: 4px; transition: width 0.3s; }
.p-trait-val { font-size: 10px; color: #5A6460; width: 28px; text-align: right; }

.p-trait-bars--full .p-trait-label { width: 130px; font-size: 11px; }
.p-trait-bars--full .p-trait-track { height: 5px; }

/* ─── Hint rows (motivation/fear) ────────────────────────────────────────── */
.p-persona-hints { display: flex; flex-direction: column; gap: 4px; margin-top: 2px; }
.p-hint {
  font-size: 11px; color: #5A6460; display: flex; align-items: flex-start; gap: 6px;
  line-height: 1.35;
}
.p-hint-icon { flex-shrink: 0; font-size: 10px; margin-top: 1px; }

.p-empty-personas {
  grid-column: 1 / -1; text-align: center; padding: 60px 20px;
  color: #4A5450; font-size: 14px;
}

/* ─── Scrollbar ──────────────────────────────────────────────────────────── */
.p-main::-webkit-scrollbar { width: 6px; }
.p-main::-webkit-scrollbar-track { background: transparent; }
.p-main::-webkit-scrollbar-thumb { background: #2E3D37; border-radius: 4px; }
</style>

<!-- Unscoped styles for teleported panels -->
<style>
.p-detail-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(13, 15, 14, 0.95);
  z-index: 9998;
  backdrop-filter: blur(4px);
}
.p-detail-panel {
  width: 480px;
  max-width: calc(100vw - 40px);
  background: #141817;
  border: 1px solid #2E3D37;
  border-radius: 14px;
  padding: 28px;
  max-height: calc(100vh - 80px);
  overflow-y: auto;
  position: fixed;
  right: 20px;
  top: 40px;
  z-index: 9999;
  box-shadow: -8px 0 40px rgba(0,0,0,0.7);
  font-family: 'DM Sans', 'Inter', sans-serif;
  color: #E8EAE9;
}
.p-detail-header {
  display: flex; justify-content: space-between; align-items: flex-start;
  margin-bottom: 16px;
}
.p-detail-name {
  font-family: 'DM Serif Display', serif;
  font-size: 22px; font-weight: 400; color: #E8EAE9;
  margin: 8px 0 0; letter-spacing: -0.3px;
}
.p-detail-close {
  background: none; border: none; color: #5A6460; font-size: 18px;
  cursor: pointer; padding: 4px; transition: color 0.15s;
}
.p-detail-close:hover { color: #E8EAE9; }
.p-detail-desc { font-size: 13px; color: #8A9490; line-height: 1.55; margin: 0 0 16px; }
.p-detail-quote {
  font-style: italic; font-size: 13px; color: #6A7870; line-height: 1.5;
  padding: 12px 16px; background: #161A18; border-left: 3px solid #2E3D37;
  border-radius: 0 8px 8px 0; margin-bottom: 20px;
}
.p-detail-section { margin-bottom: 18px; }
.p-detail-section-title {
  font-size: 11px; font-weight: 700; color: #5A6460;
  text-transform: uppercase; letter-spacing: 0.08em; margin: 0 0 10px;
}
.p-detail-list { list-style: none; padding: 0; margin: 0; display: flex; flex-direction: column; gap: 6px; }
.p-detail-list li {
  font-size: 12px; color: #8A9490; line-height: 1.4;
  padding-left: 14px; position: relative;
}
.p-detail-list li::before {
  content: ''; position: absolute; left: 0; top: 6px;
  width: 5px; height: 5px; border-radius: 50%; background: #4AE89A;
}
.p-detail-list--fear li::before { background: #F05858; }
.p-detail-list--trigger li::before { background: #F0A843; }
.p-detail-list--abandon li::before { background: #F07858; }
.p-detail-journey {
  font-size: 12px; color: #8A9490; line-height: 1.5; margin: 0;
  padding: 10px 14px; background: #161A18; border-radius: 8px;
}
.p-relevance-bars { display: flex; flex-direction: column; gap: 6px; }
.p-relevance-row { display: flex; align-items: center; gap: 8px; }
.p-relevance-label { font-size: 11px; color: #6A7870; width: 90px; flex-shrink: 0; }
.p-detail-panel .p-trait-bars { display: flex; flex-direction: column; gap: 5px; }
.p-detail-panel .p-trait-row { display: flex; align-items: center; gap: 8px; }
.p-detail-panel .p-trait-label { font-size: 11px; color: #5A6460; width: 130px; flex-shrink: 0; text-transform: capitalize; }
.p-detail-panel .p-trait-track { flex: 1; height: 5px; background: #1E2421; border-radius: 4px; overflow: hidden; }
.p-detail-panel .p-trait-fill { height: 100%; border-radius: 4px; transition: width 0.3s; }
.p-detail-panel .p-trait-val { font-size: 10px; color: #5A6460; width: 28px; text-align: right; }
.p-detail-panel .p-cluster-badge {
  font-size: 11px; font-weight: 700; padding: 4px 12px; border-radius: 20px;
  text-transform: uppercase; letter-spacing: 0.06em; display: inline-block;
}
.p-detail-panel::-webkit-scrollbar { width: 4px; }
.p-detail-panel::-webkit-scrollbar-track { background: transparent; }
.p-detail-panel::-webkit-scrollbar-thumb { background: #2E3D37; border-radius: 4px; }
.panel-slide-enter-active, .panel-slide-leave-active {
  transition: opacity 0.2s, transform 0.2s;
}
.panel-slide-enter-from, .panel-slide-leave-to {
  opacity: 0; transform: translateX(20px);
}

/* ─── Add persona panel ──────────────────────────────────────────────────── */
.p-add-panel { width: 420px; }
.p-add-search { width: 100%; margin-bottom: 16px; box-sizing: border-box; }
.p-add-list { display: flex; flex-direction: column; gap: 4px; max-height: 400px; overflow-y: auto; }
.p-add-item {
  display: flex; align-items: center; gap: 10px;
  padding: 10px 12px; border-radius: 8px; cursor: pointer;
  transition: background 0.1s;
}
.p-add-item:hover { background: #1A1F1D; }
.p-add-item-name { font-size: 13px; font-weight: 600; color: #E8EAE9; min-width: 120px; }
.p-add-item-desc { font-size: 11px; color: #6A7870; flex: 1; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }

/* ─── Sample agent preview ───────────────────────────────────────────────── */
.p-sample-panel { width: 460px; }
.p-sample-blend {
  background: #161A18; border-radius: 10px; padding: 14px 16px;
  margin-bottom: 16px; display: flex; flex-direction: column; gap: 8px;
}
.p-sample-comp {
  display: flex; align-items: center; gap: 10px; font-size: 13px;
}
.p-sample-role { color: #5A6460; width: 70px; font-weight: 500; }
.p-sample-persona { color: #E8EAE9; font-weight: 600; flex: 1; }
.p-sample-pct { color: #4AE89A; font-weight: 600; font-variant-numeric: tabular-nums; }
.p-gen-another { margin-top: 8px; }
</style>
