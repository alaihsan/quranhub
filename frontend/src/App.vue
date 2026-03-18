<script setup>
import { onMounted } from 'vue'
import { useQuranStore } from '@/stores/quran'
import AppHeader from '@/components/AppHeader.vue'
import AppSidebar from '@/components/AppSidebar.vue'

const store = useQuranStore()

onMounted(() => {
  document.documentElement.setAttribute('data-theme', store.settings.theme)
  store.fetchChapters()
})
</script>

<template>
  <div class="app-layout">
    <AppHeader />
    <div class="app-body">
      <AppSidebar />
      <main class="app-main">
        <router-view v-slot="{ Component }">
          <transition name="page-fade" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </main>
    </div>
  </div>
</template>

<style scoped>
.app-layout {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.app-body {
  display: flex;
  flex: 1;
  margin-top: var(--header-height);
}

.app-main {
  flex: 1;
  min-height: calc(100vh - var(--header-height));
  overflow-y: auto;
}

.page-fade-enter-active,
.page-fade-leave-active {
  transition: opacity 0.2s ease;
}

.page-fade-enter-from,
.page-fade-leave-to {
  opacity: 0;
}

@media (max-width: 768px) {
  .app-body {
    flex-direction: column;
  }
}
</style>
