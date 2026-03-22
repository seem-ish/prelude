<template>
  <div class="p-shell">
    <!-- Sidebar -->
    <aside class="p-sidebar">
      <div class="p-logo">Prelude</div>

      <nav class="p-nav">
        <router-link to="/prelude" class="p-nav-item active">
          <span class="p-nav-icon">⊞</span> Dashboard
        </router-link>
        <router-link to="/prelude/brief" class="p-nav-item">
          <span class="p-nav-icon">✦</span> Library
        </router-link>
      </nav>

      <div class="p-sidebar-footer">
        <div class="p-calibration-mini" v-if="calibrationStats.total > 0">
          <div class="p-calibration-label">Prediction accuracy</div>
          <div class="p-calibration-pct">{{ calibrationStats.pct }}%</div>
          <div class="p-calibration-sub">{{ calibrationStats.total }} logged</div>
        </div>
      </div>
    </aside>

    <!-- Main -->
    <main class="p-main">
      <header class="p-topbar">
        <h1 class="p-page-title">Your Experiments</h1>
        <button class="p-btn-primary" @click="$router.push('/prelude/brief')">
          + New Experiment
        </button>
      </header>

      <!-- Loading skeletons -->
      <div class="p-grid" v-if="loading">
        <div class="p-card p-card-skeleton" v-for="i in 3" :key="i">
          <div class="skel skel-title"></div>
          <div class="skel skel-line"></div>
          <div class="skel skel-line skel-short"></div>
        </div>
      </div>

      <!-- Error state -->
      <div class="p-empty" v-else-if="error">
        <div class="p-empty-icon">⚠</div>
        <div class="p-empty-title">Couldn't load experiments</div>
        <div class="p-empty-sub">{{ error }}</div>
        <button class="p-btn-primary" @click="load">Retry</button>
      </div>

      <!-- Empty state -->
      <div class="p-empty" v-else-if="experiments.length === 0">
        <div class="p-empty-icon">◎</div>
        <div class="p-empty-title">Run your first simulation.</div>
        <div class="p-empty-sub">It takes 10 minutes.</div>
        <button class="p-btn-primary" @click="$router.push('/prelude/brief')">
          Start an experiment
        </button>
      </div>

      <!-- Experiment grid -->
      <div class="p-grid" v-else>
        <div
          v-for="exp in experiments"
          :key="exp.id"
          class="p-card"
          :class="`p-card--${exp.status}`"
          @click="openExperiment(exp)"
        >
          <div class="p-card-top">
            <span class="p-badge p-badge--status" :class="`p-badge--${exp.status}`">
              {{ statusLabel(exp.status) }}
            </span>
            <span class="p-badge p-badge--category" v-if="exp.category">
              {{ exp.category }}
            </span>
          </div>

          <h3 class="p-card-title">{{ exp.title }}</h3>

          <div class="p-card-variants" v-if="exp.variant_a">
            <div class="p-variant-row">
              <span class="p-variant-tag">A</span>
              <span class="p-variant-text">{{ truncate(exp.variant_a, 60) }}</span>
            </div>
            <div class="p-variant-row" v-if="exp.variant_b">
              <span class="p-variant-tag">B</span>
              <span class="p-variant-text">{{ truncate(exp.variant_b, 60) }}</span>
            </div>
          </div>

          <div class="p-card-footer">
            <span class="p-card-date">{{ formatDate(exp.created_at) }}</span>
            <span
              class="p-winner-badge"
              v-if="exp.status === 'complete' && exp.winner"
            >
              {{ exp.winner === 'a' ? 'A wins' : exp.winner === 'b' ? 'B wins' : 'Inconclusive' }}
              <span class="p-winner-conf" v-if="exp.confidence">· {{ exp.confidence }}</span>
            </span>
          </div>
        </div>
      </div>

      <!-- Calibration score panel -->
      <section class="p-calibration" v-if="calibrationStats.total > 0">
        <h2 class="p-section-title">Calibration Score</h2>
        <div class="p-calibration-bar">
          <div class="p-calibration-fill" :style="{ width: calibrationStats.pct + '%' }"></div>
        </div>
        <p class="p-calibration-text">
          {{ calibrationStats.correct }}/{{ calibrationStats.total }} predictions correct
          ({{ calibrationStats.pct }}%)
        </p>
      </section>
    </main>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

// ─── State ────────────────────────────────────────────────────────────────────

const loading = ref(false)
const error   = ref(null)

// Mock data — replaced with real API in step 1.C
const experiments = ref([
  {
    id: 'sample-1',
    title: 'Fitness App — Onboarding Completion',
    status: 'complete',
    category: 'fitness',
    variant_a: 'Guided 3-step onboarding with progress bar and estimated time…',
    variant_b: 'Single long-scroll page with skip button prominent at top…',
    created_at: '2024-01-10T00:00:00Z',
    winner: 'a',
    confidence: 'high'
  },
  {
    id: 'sample-2',
    title: 'Grocery Delivery — Trial to Paid',
    status: 'complete',
    category: 'retail',
    variant_a: 'Personalized savings email: "Your free deliveries saved you $47…"',
    variant_b: 'Feature unlock email: "Upgrade to unlock exclusive member prices…"',
    created_at: '2024-01-12T00:00:00Z',
    winner: 'a',
    confidence: 'medium'
  },
  {
    id: 'draft-1',
    title: 'New experiment',
    status: 'draft',
    category: null,
    variant_a: null,
    variant_b: null,
    created_at: '2024-01-15T00:00:00Z',
    winner: null,
    confidence: null
  }
])

// ─── Calibration (mock) ───────────────────────────────────────────────────────

const calibrationStats = computed(() => {
  const complete = experiments.value.filter(e => e.status === 'complete' && e.winner)
  return {
    total:   complete.length,
    correct: complete.length, // mock: all correct for demo
    pct:     complete.length ? 100 : 0
  }
})

// ─── Actions ──────────────────────────────────────────────────────────────────

async function load() {
  // Step 1.C: replaced with real API call
}

function openExperiment(exp) {
  if (exp.status === 'complete') {
    router.push(`/prelude/readout/${exp.id}`)
  } else {
    router.push(`/prelude/brief/${exp.id}`)
  }
}

// ─── Helpers ──────────────────────────────────────────────────────────────────

function truncate(str, n) {
  if (!str) return ''
  return str.length > n ? str.slice(0, n) + '…' : str
}

function formatDate(iso) {
  if (!iso) return ''
  return new Date(iso).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
}

function statusLabel(s) {
  return { draft: 'Draft', running: 'Running', complete: 'Complete' }[s] || s
}

onMounted(load)
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
.p-nav-item.active {
  background: #1A1F1D;
  color: #E8EAE9;
}
.p-nav-item.router-link-active {
  background: #1A1F1D;
  color: #E8EAE9;
}
.p-nav-icon {
  font-size: 13px;
  opacity: 0.7;
}

.p-sidebar-footer {
  padding: 20px 20px 0;
}

.p-calibration-mini {
  background: #161A18;
  border: 1px solid #1E2421;
  border-radius: 10px;
  padding: 14px 16px;
}
.p-calibration-label {
  font-size: 11px;
  color: #5A6460;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  margin-bottom: 6px;
}
.p-calibration-pct {
  font-size: 26px;
  font-weight: 600;
  color: #4AE89A;
  line-height: 1;
}
.p-calibration-sub {
  font-size: 12px;
  color: #5A6460;
  margin-top: 4px;
}

/* ─── Main ───────────────────────────────────────────────────────────────────── */
.p-main {
  flex: 1;
  padding: 40px 48px;
  max-width: 1100px;
}

.p-topbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 36px;
}

.p-page-title {
  font-family: 'DM Serif Display', serif;
  font-size: 32px;
  font-weight: 400;
  color: #E8EAE9;
  letter-spacing: -0.5px;
  margin: 0;
}

/* ─── Button ─────────────────────────────────────────────────────────────────── */
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

/* ─── Grid ───────────────────────────────────────────────────────────────────── */
.p-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 16px;
}

/* ─── Card ───────────────────────────────────────────────────────────────────── */
.p-card {
  background: #111413;
  border: 1px solid #1E2421;
  border-radius: 14px;
  padding: 22px 22px 18px;
  cursor: pointer;
  transition: border-color 0.15s, transform 0.12s;
  display: flex;
  flex-direction: column;
  gap: 14px;
}
.p-card:hover {
  border-color: #2E3D37;
  transform: translateY(-1px);
}
.p-card--complete { border-left: 3px solid #4AE89A; }
.p-card--running  { border-left: 3px solid #F0A843; }
.p-card--draft    { border-left: 3px solid #2E3D37; }

/* ─── Skeleton card ──────────────────────────────────────────────────────────── */
.p-card-skeleton { cursor: default; pointer-events: none; }
.skel {
  background: linear-gradient(90deg, #1A1F1D 25%, #212825 50%, #1A1F1D 75%);
  background-size: 200% 100%;
  animation: shimmer 1.4s infinite;
  border-radius: 6px;
}
.skel-title { height: 20px; width: 70%; }
.skel-line  { height: 13px; width: 90%; margin-top: 8px; }
.skel-short { width: 55%; }
@keyframes shimmer {
  0%   { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}

/* ─── Card internals ─────────────────────────────────────────────────────────── */
.p-card-top {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.p-badge {
  font-size: 11px;
  font-weight: 600;
  padding: 3px 9px;
  border-radius: 20px;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}
.p-badge--complete { background: #0D2E1E; color: #4AE89A; }
.p-badge--running  { background: #2E2005; color: #F0A843; }
.p-badge--draft    { background: #1A1F1D; color: #5A6460; }
.p-badge--category { background: #161A18; color: #8A9490; }

.p-card-title {
  font-size: 16px;
  font-weight: 600;
  color: #E8EAE9;
  margin: 0;
  line-height: 1.35;
  letter-spacing: -0.2px;
}

.p-card-variants {
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.p-variant-row {
  display: flex;
  align-items: flex-start;
  gap: 8px;
}
.p-variant-tag {
  font-size: 10px;
  font-weight: 700;
  color: #0D0F0E;
  background: #3A4440;
  width: 18px;
  height: 18px;
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  margin-top: 1px;
}
.p-variant-text {
  font-size: 13px;
  color: #6A7870;
  line-height: 1.4;
}

.p-card-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: auto;
  padding-top: 4px;
  border-top: 1px solid #1A1F1D;
}
.p-card-date {
  font-size: 12px;
  color: #4A5450;
}
.p-winner-badge {
  font-size: 12px;
  font-weight: 700;
  color: #4AE89A;
  background: #0D2E1E;
  padding: 3px 10px;
  border-radius: 20px;
}
.p-winner-conf {
  font-weight: 400;
  opacity: 0.7;
  text-transform: capitalize;
}

/* ─── Empty state ────────────────────────────────────────────────────────────── */
.p-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 80px 20px;
  gap: 12px;
  text-align: center;
}
.p-empty-icon {
  font-size: 36px;
  color: #2E3D37;
  margin-bottom: 4px;
}
.p-empty-title {
  font-family: 'DM Serif Display', serif;
  font-size: 24px;
  color: #E8EAE9;
}
.p-empty-sub {
  font-size: 15px;
  color: #5A6460;
  margin-bottom: 8px;
}

/* ─── Calibration panel ──────────────────────────────────────────────────────── */
.p-calibration {
  margin-top: 48px;
  padding: 28px 32px;
  background: #111413;
  border: 1px solid #1E2421;
  border-radius: 14px;
  max-width: 480px;
}
.p-section-title {
  font-family: 'DM Serif Display', serif;
  font-size: 18px;
  font-weight: 400;
  color: #E8EAE9;
  margin: 0 0 16px;
}
.p-calibration-bar {
  height: 6px;
  background: #1E2421;
  border-radius: 10px;
  overflow: hidden;
  margin-bottom: 10px;
}
.p-calibration-fill {
  height: 100%;
  background: #4AE89A;
  border-radius: 10px;
  transition: width 0.6s ease;
}
.p-calibration-text {
  font-size: 14px;
  color: #6A7870;
  margin: 0;
}
</style>
