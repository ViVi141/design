import { createRouter, createWebHistory, RouteRecordRaw } from 'vue-router'

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    redirect: '/dashboard'
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: () => import('@/views/dashboard/DashboardView.vue')
  },
  {
    path: '/map',
    name: 'Map',
    component: () => import('@/views/map/MapView.vue')
  },
  {
    path: '/planner',
    name: 'Planner',
    component: () => import('@/views/planner/PlannerViewV3.vue')
  },
  {
    path: '/chat',
    name: 'Chat',
    component: () => import('@/views/chat/ChatView.vue')
  },
  {
    path: '/trips',
    name: 'Trips',
    component: () => import('@/views/trip/TripList.vue')
  },
  {
    path: '/trips/:id',
    name: 'TripDetail',
    component: () => import('@/views/trip/TripDetail.vue')
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router

