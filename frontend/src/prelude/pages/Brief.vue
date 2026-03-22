<template>
  <div class="p-shell">
    <!-- Sidebar (shared layout) -->
    <aside class="p-sidebar">
      <div class="p-logo" @click="$router.push('/prelude')" style="cursor:pointer">Prelude</div>
      <nav class="p-nav">
        <router-link to="/prelude" class="p-nav-item">
          <span class="p-nav-icon">⊞</span> Dashboard
        </router-link>
        <router-link to="/prelude/brief" class="p-nav-item router-link-active">
          <span class="p-nav-icon">✦</span> New Experiment
        </router-link>
      </nav>
    </aside>

    <!-- Main -->
    <main class="p-main">
      <!-- Top progress bar -->
      <div class="p-progress-bar">
        <div
          v-for="(label, i) in steps"
          :key="i"
          class="p-progress-step"
          :class="{ active: i === step, done: i < step }"
          @click="i < step && (step = i)"
        >
          <span class="p-progress-dot"></span>
          <span class="p-progress-label">{{ label }}</span>
        </div>
      </div>

      <!-- Step forms -->
      <div class="p-brief-body">

        <!-- ── Step 0: Product context ─────────────────────────── -->
        <transition name="slide" mode="out-in">
        <div v-if="step === 0" key="0" class="p-step">
          <h2 class="p-step-title">What are you working on?</h2>

          <div class="p-category-grid">
            <button
              v-for="cat in categories"
              :key="cat.value"
              class="p-cat-btn"
              :class="{ selected: form.category === cat.value }"
              @click="form.category = cat.value"
            >
              <span class="p-cat-icon">{{ cat.icon }}</span>
              <span class="p-cat-label">{{ cat.label }}</span>
            </button>
          </div>

          <!-- Use-case presets (filtered by category) -->
          <div v-if="presetsForCategory.length" class="p-presets">
            <label class="p-label" style="margin-top:20px">Or start from a use case:</label>
            <div class="p-preset-list">
              <button
                v-for="preset in presetsForCategory"
                :key="preset.label"
                class="p-preset-btn"
                @click="applyPreset(preset)"
              >{{ preset.label }}</button>
            </div>
          </div>

          <div class="p-field" style="margin-top:28px">
            <label class="p-label">What's your product?</label>
            <input
              v-model="form.product_context"
              class="p-input"
              placeholder="e.g. Fashion e-commerce checkout flow"
              @input="autosave"
            />
          </div>

          <div class="p-step-actions">
            <button class="p-btn-primary" :disabled="!form.category" @click="step++">
              Continue →
            </button>
          </div>
        </div>
        </transition>

        <!-- ── Step 1: The problem ─────────────────────────────── -->
        <transition name="slide" mode="out-in">
        <div v-if="step === 1" key="1" class="p-step">
          <h2 class="p-step-title">What problem are you solving?</h2>
          <p class="p-step-hint">
            Be specific. "Users don't activate" is too vague.
            "40% of new users never complete profile setup" is useful.
          </p>

          <div class="p-field">
            <textarea
              v-model="form.problem"
              class="p-textarea"
              rows="5"
              placeholder="Describe the specific problem with numbers if you have them…"
              @input="autosave"
            ></textarea>
            <div class="p-assist-row">
              <button
                class="p-btn-assist"
                :class="{ loading: assistLoading.problem }"
                :disabled="!form.product_context || assistLoading.problem"
                @click="assist('problem')"
              >
                {{ assistLoading.problem ? 'Thinking…' : '✦ Help me write this' }}
              </button>
              <span class="p-char-count">{{ form.problem.length }} chars</span>
            </div>
          </div>

          <div class="p-step-actions">
            <button class="p-btn-ghost" @click="step--">← Back</button>
            <button class="p-btn-primary" :disabled="form.problem.length < 20" @click="step++">
              Continue →
            </button>
          </div>
        </div>
        </transition>

        <!-- ── Step 2: Variants ────────────────────────────────── -->
        <transition name="slide" mode="out-in">
        <div v-if="step === 2" key="2" class="p-step">
          <h2 class="p-step-title">Describe both variants.</h2>
          <p class="p-step-hint">
            The more distinct, the more useful the prediction.
          </p>

          <div class="p-variants-grid">
            <div class="p-field">
              <label class="p-label">
                <span class="p-variant-tag-lg">A</span> Variant A
              </label>
              <textarea
                v-model="form.variant_a"
                class="p-textarea"
                rows="4"
                placeholder="Describe what Variant A looks/feels like…"
                @input="autosave"
              ></textarea>
              <button
                class="p-btn-assist"
                :class="{ loading: assistLoading.variant_a }"
                :disabled="!form.problem || assistLoading.variant_a"
                @click="assist('variant_a')"
              >
                {{ assistLoading.variant_a ? 'Thinking…' : '✦ Suggest a variant' }}
              </button>
            </div>

            <div class="p-field">
              <label class="p-label">
                <span class="p-variant-tag-lg">B</span> Variant B
              </label>
              <textarea
                v-model="form.variant_b"
                class="p-textarea"
                rows="4"
                placeholder="Describe what Variant B looks/feels like…"
                @input="autosave"
              ></textarea>
              <button
                class="p-btn-assist"
                :class="{ loading: assistLoading.variant_b }"
                :disabled="!form.problem || assistLoading.variant_b"
                @click="assist('variant_b')"
              >
                {{ assistLoading.variant_b ? 'Thinking…' : '✦ Suggest a variant' }}
              </button>
            </div>
          </div>

          <div class="p-step-actions">
            <button class="p-btn-ghost" @click="step--">← Back</button>
            <button
              class="p-btn-primary"
              :disabled="form.variant_a.length < 10 || form.variant_b.length < 10"
              @click="step++"
            >
              Continue →
            </button>
          </div>
        </div>
        </transition>

        <!-- ── Step 3: Target user + success ──────────────────── -->
        <transition name="slide" mode="out-in">
        <div v-if="step === 3" key="3" class="p-step">
          <h2 class="p-step-title">Who's the target user?</h2>

          <div class="p-field">
            <label class="p-label">Target user</label>
            <textarea
              v-model="form.target_user"
              class="p-textarea"
              rows="3"
              placeholder="e.g. New signups in the first 7 days, mobile users, 25–45"
              @input="autosave"
            ></textarea>
          </div>

          <div class="p-field">
            <label class="p-label">What does success look like?</label>
            <input
              v-model="form.success_metric"
              class="p-input"
              placeholder="e.g. Profile completion within 24 hours of signup"
              @input="autosave"
            />
          </div>

          <div class="p-run-estimate">
            Estimated run time: ~15 minutes for 200 agents
          </div>

          <div class="p-step-actions">
            <button class="p-btn-ghost" @click="step--">← Back</button>
            <button
              class="p-btn-primary p-btn-submit"
              :disabled="form.target_user.length < 5 || form.success_metric.length < 5 || submitting"
              @click="submit"
            >
              <span v-if="submitting">Setting up your experiment…</span>
              <span v-else>Set up experiment →</span>
            </button>
          </div>
        </div>
        </transition>

      </div><!-- /p-brief-body -->
    </main>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import axios from 'axios'

const router = useRouter()
const route  = useRoute()
const expId  = route.params.id || null

// ─── Steps ────────────────────────────────────────────────────────────────────
const steps = ['Brief', 'Personas', 'Simulation', 'Results']
const step  = ref(0)

// ─── Form state ───────────────────────────────────────────────────────────────
const form = reactive({
  title:           '',
  category:        '',
  product_context: '',
  problem:         '',
  variant_a:       '',
  variant_b:       '',
  target_user:     '',
  success_metric:  '',
})

const categories = [
  { value: 'grocery',             icon: '🛒', label: 'Grocery'              },
  { value: 'grocery_loyalty',     icon: '💳', label: 'Grocery — Loyalty'    },
  { value: 'grocery_subscription',icon: '📦', label: 'Grocery — Subscription'},
  { value: 'fashion',             icon: '👗', label: 'Fashion'              },
  { value: 'fashion_launch',      icon: '✨', label: 'Fashion — Launch'     },
  { value: 'fashion_returns',     icon: '↩️', label: 'Fashion — Returns'    },
]

// ─── Retail use-case presets ─────────────────────────────────────────────────
const USE_CASE_PRESETS = [
  {
    label: 'Checkout abandonment recovery',
    category: 'fashion',
    product_context: 'Fashion e-commerce checkout flow',
    problem: '70% of users who add items to cart abandon at the payment step. Highest drop-off is between shipping cost reveal and payment entry.',
    variant_a: 'Recovery email 1 hour after abandonment: "Your cart is reserved for 2 hours. Free shipping unlocked — no minimum." Removes the #1 friction point with urgency.',
    variant_b: 'Recovery email 1 hour after abandonment: "Still thinking? Here\'s 10% off your first order. Code: COMEBACK10." Discount-led recovery with no urgency.',
    target_user: 'Urban shoppers 22-38, mobile-first, fashion-conscious, price-sensitive, abandoned a cart in the last 7 days',
    success_metric: 'Checkout completion within 2 hours of recovery email',
  },
  {
    label: 'Loyalty program upsell',
    category: 'grocery_loyalty',
    product_context: 'Grocery chain loyalty membership program',
    problem: 'Only 12% of weekly shoppers have joined the loyalty program. Those who join spend 35% more per visit, but the signup funnel converts at just 4%.',
    variant_a: 'Points-based program: "Earn 1 point per £1 spent. 500 points = £5 off." Simple, transparent, no tier complexity. Shown at self-checkout after payment.',
    variant_b: 'Tier-based membership: "Join Silver free → unlock Gold at £50/month spend for 10% off fresh produce." Aspirational, gamified, shown via in-app push notification.',
    target_user: 'Weekly grocery shoppers spending £60-120 per visit, mix of families and singles, price-aware but not extreme coupon users',
    success_metric: 'Loyalty program signup within 2 weeks of first exposure',
  },
  {
    label: 'New collection launch',
    category: 'fashion_launch',
    product_context: 'Mid-range fashion brand seasonal collection drop',
    problem: 'New collections generate 80% of traffic in the first 48 hours but only 15% of that traffic converts. Most visitors browse but don\'t buy — "I\'ll wait for the sale" is the dominant sentiment.',
    variant_a: 'Early access email to existing customers: "Shop the Spring collection 24 hours before everyone else. No discount — just first pick." Exclusivity-driven, no price lever.',
    variant_b: 'Launch week push notification: "Spring is here — 15% off your first piece from the new collection. Code: SPRING15." Discount-driven, broader audience.',
    target_user: 'Existing customers who purchased in the last 6 months, fashion-engaged, follow the brand on social media, 25-40',
    success_metric: 'First purchase from new collection within 72 hours of launch',
  },
  {
    label: 'Subscription bundle introduction',
    category: 'grocery_subscription',
    product_context: 'Online grocery delivery subscription box',
    problem: 'Average order frequency is 1.2x/month. Customers order reactively when they run out. A subscription model could increase frequency to 4x/month but previous attempts felt inflexible.',
    variant_a: 'Fixed weekly essentials box (£25): milk, bread, eggs, fruit, veg — curated by the algorithm based on past purchases. Cancel or skip any week.',
    variant_b: 'Build-your-own weekly box: pick 10-15 items from a curated list of 50 essentials, locked in for 4 weeks at a 12% discount. Modify items each week.',
    target_user: 'Households ordering groceries online at least 2x/month, £80+ average basket, have used the platform for 3+ months',
    success_metric: 'Subscription activation and retention through week 4 (no cancel/skip)',
  },
  {
    label: 'Returns experience redesign',
    category: 'fashion_returns',
    product_context: 'Fashion e-commerce returns and exchange flow',
    problem: '32% of fashion orders are returned. The current returns process takes 3-5 days to get a refund. 40% of returners never purchase again — returns are a churn event.',
    variant_a: 'Pre-printed free returns label in the box + instant refund on courier scan. Zero friction, maximum trust, but expensive at scale.',
    variant_b: 'QR code drop-off at partner locations (convenience stores) + exchange-first flow: "Swap for a different size?" before offering refund. Lower cost, attempts save.',
    target_user: 'Online fashion buyers who have returned at least one item in the last 3 months, 22-45, buy 2+ items per order',
    success_metric: 'Repurchase within 30 days of return completion',
  },
]

// ─── Preset helpers ──────────────────────────────────────────────────────────
const presetsForCategory = computed(() => {
  if (!form.category) return []
  return USE_CASE_PRESETS.filter(p => p.category === form.category)
})

function applyPreset(preset) {
  Object.assign(form, {
    category: preset.category,
    product_context: preset.product_context,
    problem: preset.problem,
    variant_a: preset.variant_a,
    variant_b: preset.variant_b,
    target_user: preset.target_user,
    success_metric: preset.success_metric,
  })
  step.value = 3  // Jump to the final step since all fields are filled
  autosave()
}

// ─── Assist state ─────────────────────────────────────────────────────────────
const assistLoading = reactive({ problem: false, variant_a: false, variant_b: false })

// ─── Submit state ─────────────────────────────────────────────────────────────
const submitting = ref(false)

// ─── Auto-save ────────────────────────────────────────────────────────────────
const STORAGE_KEY = `prelude_brief_draft_${expId || 'new'}`
let saveTimer = null

function autosave() {
  clearTimeout(saveTimer)
  saveTimer = setTimeout(() => {
    localStorage.setItem(STORAGE_KEY, JSON.stringify({ step: step.value, form: { ...form } }))
  }, 500)
}

watch(step, () => autosave())

function loadDraft() {
  try {
    const saved = localStorage.getItem(STORAGE_KEY)
    if (saved) {
      const { step: s, form: f } = JSON.parse(saved)
      Object.assign(form, f)
      step.value = s
    }
  } catch {}
}

// ─── LLM Assist ───────────────────────────────────────────────────────────────
async function assist(field) {
  assistLoading[field] = true
  try {
    const { data } = await axios.post('/api/prelude/experiments/assist', {
      field,
      context: { ...form }
    })
    if (data.suggestion) form[field] = data.suggestion
  } catch (e) {
    // If no API key yet, show a placeholder
    const placeholders = {
      problem:   `${form.product_context ? form.product_context + ': ' : ''}[Add API key to enable AI suggestions]`,
      variant_a: '[Add API key to enable AI suggestions]',
      variant_b: '[Add API key to enable AI suggestions]',
    }
    form[field] = form[field] || placeholders[field]
  } finally {
    assistLoading[field] = false
  }
}

// ─── Submit ───────────────────────────────────────────────────────────────────
async function submit() {
  submitting.value = true
  try {
    const title = form.product_context
      ? `${form.product_context} — ${form.category}`
      : `New experiment`

    let id = expId
    if (!id) {
      const { data } = await axios.post('/api/prelude/experiments', {
        ...form,
        title,
        status: 'draft',
      })
      id = data.id
    } else {
      await axios.patch(`/api/prelude/experiments/${id}`, { ...form, title })
    }

    // Clear draft
    localStorage.removeItem(STORAGE_KEY)

    // Navigate to personas
    router.push(`/prelude/personas/${id}`)
  } catch (e) {
    alert('Failed to save experiment. Is the backend running?')
  } finally {
    submitting.value = false
  }
}

// ─── Load existing experiment if editing ──────────────────────────────────────
onMounted(async () => {
  if (expId) {
    try {
      const { data } = await axios.get(`/api/prelude/experiments/${expId}`)
      Object.assign(form, {
        category:        data.category        || '',
        product_context: data.product_context || '',
        problem:         data.problem         || '',
        variant_a:       data.variant_a       || '',
        variant_b:       data.variant_b       || '',
        target_user:     data.target_user     || '',
        success_metric:  data.success_metric  || '',
      })
      return
    } catch {}
  }
  loadDraft()
})
</script>

<style scoped>
/* Shared shell/sidebar styles duplicated from Dashboard for now */
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
.p-nav { display: flex; flex-direction: column; gap: 2px; padding: 0 12px; }
.p-nav-item {
  display: flex; align-items: center; gap: 10px;
  padding: 9px 12px; border-radius: 8px;
  font-size: 14px; font-weight: 500; color: #8A9490; text-decoration: none;
  transition: background 0.15s, color 0.15s;
}
.p-nav-item:hover, .p-nav-item.router-link-active {
  background: #1A1F1D; color: #E8EAE9;
}
.p-nav-icon { font-size: 13px; opacity: 0.7; }

/* Main */
.p-main {
  flex: 1;
  padding: 40px 0;
  display: flex;
  flex-direction: column;
  align-items: center;
}

/* Progress bar */
.p-progress-bar {
  display: flex;
  gap: 0;
  margin-bottom: 56px;
  width: 100%;
  max-width: 560px;
  padding: 0 24px;
  position: relative;
}
.p-progress-bar::before {
  content: '';
  position: absolute;
  top: 9px;
  left: 48px;
  right: 48px;
  height: 1px;
  background: #1E2421;
}
.p-progress-step {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  position: relative;
  cursor: default;
}
.p-progress-step.done { cursor: pointer; }
.p-progress-dot {
  width: 18px;
  height: 18px;
  border-radius: 50%;
  background: #1E2421;
  border: 2px solid #2E3D37;
  transition: background 0.2s, border-color 0.2s;
  position: relative;
  z-index: 1;
}
.p-progress-step.done .p-progress-dot {
  background: #4AE89A;
  border-color: #4AE89A;
}
.p-progress-step.active .p-progress-dot {
  background: #0D0F0E;
  border-color: #4AE89A;
  box-shadow: 0 0 0 3px rgba(74,232,154,0.15);
}
.p-progress-label {
  font-size: 11px;
  color: #3A4A44;
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}
.p-progress-step.active .p-progress-label { color: #4AE89A; }
.p-progress-step.done  .p-progress-label { color: #5A7A6A; }

/* Step body */
.p-brief-body {
  width: 100%;
  max-width: 640px;
  padding: 0 24px;
}
.p-step { display: flex; flex-direction: column; gap: 20px; }

.p-step-title {
  font-family: 'DM Serif Display', serif;
  font-size: 28px;
  font-weight: 400;
  color: #E8EAE9;
  margin: 0;
  letter-spacing: -0.4px;
}
.p-step-hint {
  font-size: 14px;
  color: #5A6460;
  margin: -8px 0 0;
  line-height: 1.6;
}

/* Category grid */
.p-category-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 10px;
}
.p-cat-btn {
  background: #111413;
  border: 1px solid #1E2421;
  border-radius: 10px;
  padding: 16px 12px;
  cursor: pointer;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  transition: border-color 0.15s, background 0.15s;
  color: #8A9490;
}
.p-cat-btn:hover { border-color: #2E3D37; color: #E8EAE9; }
.p-cat-btn.selected {
  border-color: #4AE89A;
  background: #0D2E1E;
  color: #4AE89A;
}
.p-cat-icon { font-size: 24px; }
.p-cat-label { font-size: 13px; font-weight: 500; }

/* Preset buttons */
.p-presets { margin-top: 4px; }
.p-preset-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 8px;
}
.p-preset-btn {
  background: #111413;
  border: 1px solid #1E2421;
  border-radius: 8px;
  color: #8A9490;
  padding: 8px 14px;
  font-size: 13px;
  font-family: 'DM Sans', sans-serif;
  cursor: pointer;
  transition: all 0.15s;
}
.p-preset-btn:hover {
  border-color: #4AE89A;
  color: #4AE89A;
  background: #0D2E1E;
}

/* Fields */
.p-field { display: flex; flex-direction: column; gap: 8px; }
.p-label {
  font-size: 13px;
  font-weight: 600;
  color: #6A7870;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  display: flex;
  align-items: center;
  gap: 8px;
}
.p-input {
  background: #111413;
  border: 1px solid #1E2421;
  border-radius: 10px;
  padding: 14px 16px;
  font-size: 15px;
  color: #E8EAE9;
  font-family: 'DM Sans', sans-serif;
  transition: border-color 0.15s;
  outline: none;
  width: 100%;
  box-sizing: border-box;
}
.p-input:focus { border-color: #3A4A44; }
.p-textarea {
  background: #111413;
  border: 1px solid #1E2421;
  border-radius: 10px;
  padding: 14px 16px;
  font-size: 15px;
  color: #E8EAE9;
  font-family: 'DM Sans', sans-serif;
  resize: vertical;
  transition: border-color 0.15s;
  outline: none;
  width: 100%;
  box-sizing: border-box;
  line-height: 1.6;
}
.p-textarea:focus { border-color: #3A4A44; }

.p-assist-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.p-char-count { font-size: 12px; color: #3A4A44; }

.p-btn-assist {
  background: none;
  border: 1px solid #2E3D37;
  border-radius: 8px;
  padding: 7px 14px;
  font-size: 13px;
  font-weight: 500;
  color: #4AE89A;
  cursor: pointer;
  font-family: 'DM Sans', sans-serif;
  transition: background 0.15s, opacity 0.15s;
}
.p-btn-assist:hover:not(:disabled) { background: #0D2E1E; }
.p-btn-assist:disabled { opacity: 0.4; cursor: not-allowed; }
.p-btn-assist.loading { opacity: 0.6; }

/* Variants two-column */
.p-variants-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}
.p-variant-tag-lg {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 20px;
  height: 20px;
  background: #2E3D37;
  color: #4AE89A;
  font-size: 11px;
  font-weight: 700;
  border-radius: 4px;
}

/* Run estimate */
.p-run-estimate {
  font-size: 13px;
  color: #3A4A44;
  background: #111413;
  border: 1px solid #1E2421;
  border-radius: 8px;
  padding: 12px 16px;
}

/* Step actions */
.p-step-actions {
  display: flex;
  gap: 12px;
  align-items: center;
  margin-top: 8px;
}
.p-btn-primary {
  background: #4AE89A;
  color: #0D0F0E;
  border: none;
  border-radius: 8px;
  padding: 12px 22px;
  font-family: 'DM Sans', sans-serif;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: opacity 0.15s;
}
.p-btn-primary:hover:not(:disabled) { opacity: 0.85; }
.p-btn-primary:disabled { opacity: 0.35; cursor: not-allowed; }
.p-btn-primary.p-btn-submit { padding: 13px 28px; }
.p-btn-ghost {
  background: none;
  border: 1px solid #2E3D37;
  border-radius: 8px;
  padding: 12px 18px;
  font-family: 'DM Sans', sans-serif;
  font-size: 15px;
  font-weight: 500;
  color: #6A7870;
  cursor: pointer;
  transition: border-color 0.15s, color 0.15s;
}
.p-btn-ghost:hover { border-color: #4AE89A; color: #E8EAE9; }

/* Slide transition */
.slide-enter-active,
.slide-leave-active {
  transition: opacity 0.2s ease, transform 0.2s ease;
}
.slide-enter-from { opacity: 0; transform: translateX(20px); }
.slide-leave-to   { opacity: 0; transform: translateX(-20px); }
</style>
