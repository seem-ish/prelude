/**
 * Prelude experiment store.
 * Uses Vue 3 reactive state (no Pinia dependency — matches MiroFish's setup).
 * Slice 1 will flesh this out.
 */

import { reactive } from "vue";
import axios from "axios";

const BASE = "/api/prelude";

export const experimentStore = reactive({
  experiments: [],
  currentExperiment: null,
  loading: false,
  error: null,

  async fetchAll() {
    this.loading = true;
    this.error = null;
    try {
      const { data } = await axios.get(`${BASE}/experiments`);
      this.experiments = data;
    } catch (e) {
      this.error = e.message;
    } finally {
      this.loading = false;
    }
  },

  async fetchOne(id) {
    const { data } = await axios.get(`${BASE}/experiments/${id}`);
    this.currentExperiment = data;
    return data;
  },

  async create(payload) {
    const { data } = await axios.post(`${BASE}/experiments`, payload);
    this.experiments.unshift(data);
    return data;
  },

  async update(id, payload) {
    const { data } = await axios.patch(`${BASE}/experiments/${id}`, payload);
    const idx = this.experiments.findIndex((e) => e.id === id);
    if (idx !== -1) this.experiments[idx] = data;
    this.currentExperiment = data;
    return data;
  },
});
