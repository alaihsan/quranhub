import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: () => import('@/views/HomeView.vue')
  },
  {
    path: '/surah/:id',
    name: 'Surah',
    component: () => import('@/views/SurahView.vue'),
    props: true
  },
  {
    path: '/page/:number',
    name: 'Page',
    component: () => import('@/views/PageView.vue'),
    props: true
  },
  {
    path: '/juz/:number',
    name: 'Juz',
    component: () => import('@/views/JuzView.vue'),
    props: true
  },
  {
    path: '/settings',
    name: 'Settings',
    component: () => import('@/views/SettingsView.vue')
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) return savedPosition
    return { top: 0 }
  }
})

export default router
