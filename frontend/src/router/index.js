import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue'
import Process from '../views/MainView.vue'
import SimulationView from '../views/SimulationView.vue'
import SimulationRunView from '../views/SimulationRunView.vue'
import ReportView from '../views/ReportView.vue'
import InteractionView from '../views/InteractionView.vue'

// Prelude routes
import PreludeDashboard from '../prelude/pages/Dashboard.vue'
import PreludeBrief from '../prelude/pages/Brief.vue'
import PreludePersonas from '../prelude/pages/Personas.vue'
import PreludeSimRoom from '../prelude/pages/SimRoom.vue'
import PreludeReadout from '../prelude/pages/Readout.vue'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home
  },
  {
    path: '/process/:projectId',
    name: 'Process',
    component: Process,
    props: true
  },
  {
    path: '/simulation/:simulationId',
    name: 'Simulation',
    component: SimulationView,
    props: true
  },
  {
    path: '/simulation/:simulationId/start',
    name: 'SimulationRun',
    component: SimulationRunView,
    props: true
  },
  {
    path: '/report/:reportId',
    name: 'Report',
    component: ReportView,
    props: true
  },
  {
    path: '/interaction/:reportId',
    name: 'Interaction',
    component: InteractionView,
    props: true
  },

  // Prelude
  {
    path: '/prelude',
    name: 'PreludeDashboard',
    component: PreludeDashboard
  },
  {
    path: '/prelude/brief/:id?',
    name: 'PreludeBrief',
    component: PreludeBrief,
    props: true
  },
  {
    path: '/prelude/personas/:id',
    name: 'PreludePersonas',
    component: PreludePersonas,
    props: true
  },
  {
    path: '/prelude/sim/:id',
    name: 'PreludeSimRoom',
    component: PreludeSimRoom,
    props: true
  },
  {
    path: '/prelude/readout/:id',
    name: 'PreludeReadout',
    component: PreludeReadout,
    props: true
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
