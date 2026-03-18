<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useQuranStore } from '@/stores/quran'

const router = useRouter()
const store = useQuranStore()
const showSearch = ref(false)
const searchQuery = ref('')

function toggleTheme() {
  const newTheme = store.settings.theme === 'light' ? 'dark' : 'light'
  store.updateSettings({ theme: newTheme })
}

function goHome() {
  router.push('/')
}

function toggleSidebar() {
  document.body.classList.toggle('sidebar-open')
}

function handleSearch() {
  if (searchQuery.value.trim()) {
    // Check if it's a verse reference like "2:255"
    const verseMatch = searchQuery.value.match(/^(\d+):(\d+)$/)
    if (verseMatch) {
      router.push(`/surah/${verseMatch[1]}`)
    }
    showSearch.value = false
    searchQuery.value = ''
  }
}
</script>

<template>
  <header class="app-header">
    <div class="header-left">
      <button class="menu-btn" @click="toggleSidebar" aria-label="Menu">
        <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round">
          <line x1="3" y1="6" x2="21" y2="6"/>
          <line x1="3" y1="12" x2="21" y2="12"/>
          <line x1="3" y1="18" x2="21" y2="18"/>
        </svg>
      </button>
      <div class="logo" @click="goHome">
        <div class="logo-icon">
          <svg width="28" height="28" viewBox="0 0 32 32" fill="none">
            <rect x="4" y="2" width="24" height="28" rx="3" fill="var(--color-primary)" opacity="0.15"/>
            <rect x="6" y="4" width="20" height="24" rx="2" stroke="var(--color-primary)" stroke-width="1.5" fill="none"/>
            <line x1="16" y1="4" x2="16" y2="28" stroke="var(--color-primary)" stroke-width="1" opacity="0.3"/>
            <circle cx="16" cy="14" r="4" stroke="var(--color-gold)" stroke-width="1.5" fill="none"/>
            <circle cx="16" cy="14" r="1.5" fill="var(--color-gold)"/>
          </svg>
        </div>
        <div class="logo-text">
          <span class="logo-title">Quran Hub</span>
          <span class="logo-subtitle">القرآن الكريم</span>
        </div>
      </div>
    </div>

    <div class="header-center">
      <div v-if="showSearch" class="search-bar">
        <input
          v-model="searchQuery"
          type="text"
          placeholder="Cari surah atau ayat (misal: 2:255)"
          @keyup.enter="handleSearch"
          @keyup.escape="showSearch = false"
          autofocus
        />
        <button @click="showSearch = false" class="search-close">✕</button>
      </div>
    </div>

    <div class="header-right">
      <button class="header-btn" @click="showSearch = !showSearch" aria-label="Cari">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round">
          <circle cx="11" cy="11" r="8"/>
          <line x1="21" y1="21" x2="16.65" y2="16.65"/>
        </svg>
      </button>
      <button class="header-btn" @click="toggleTheme" :aria-label="store.settings.theme === 'light' ? 'Mode Gelap' : 'Mode Terang'">
        <svg v-if="store.settings.theme === 'light'" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round">
          <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/>
        </svg>
        <svg v-else width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round">
          <circle cx="12" cy="12" r="5"/><line x1="12" y1="1" x2="12" y2="3"/><line x1="12" y1="21" x2="12" y2="23"/><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/><line x1="1" y1="12" x2="3" y2="12"/><line x1="21" y1="12" x2="23" y2="12"/><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/>
        </svg>
      </button>
      <router-link to="/settings" class="header-btn" aria-label="Pengaturan">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round">
          <circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06A1.65 1.65 0 0 0 4.68 15a1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06A1.65 1.65 0 0 0 9 4.68a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"/>
        </svg>
      </router-link>
    </div>
  </header>
</template>

<style scoped>
.app-header {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  height: var(--header-height);
  background: var(--color-bg-card);
  border-bottom: 1px solid var(--color-border);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 var(--space-lg);
  z-index: 100;
  backdrop-filter: blur(12px);
  background: color-mix(in srgb, var(--color-bg-card) 92%, transparent);
}

.header-left {
  display: flex;
  align-items: center;
  gap: var(--space-md);
}

.menu-btn {
  display: none;
  background: none;
  border: none;
  color: var(--color-text);
  cursor: pointer;
  padding: var(--space-xs);
  border-radius: var(--radius-sm);
}

.menu-btn:hover { background: var(--color-parchment); }

.logo {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
  cursor: pointer;
  user-select: none;
}

.logo-text {
  display: flex;
  flex-direction: column;
  line-height: 1.2;
}

.logo-title {
  font-weight: 700;
  font-size: 1.1rem;
  color: var(--color-primary);
  letter-spacing: -0.02em;
}

.logo-subtitle {
  font-family: var(--font-arabic);
  font-size: 0.8rem;
  color: var(--color-gold);
  direction: rtl;
}

.header-center {
  flex: 1;
  display: flex;
  justify-content: center;
  max-width: 480px;
  margin: 0 var(--space-lg);
}

.search-bar {
  display: flex;
  align-items: center;
  width: 100%;
  background: var(--color-parchment);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  overflow: hidden;
  animation: fadeIn 0.2s ease;
}

.search-bar input {
  flex: 1;
  border: none;
  background: none;
  padding: var(--space-sm) var(--space-md);
  font-family: var(--font-body);
  font-size: 0.9rem;
  color: var(--color-text);
  outline: none;
}

.search-bar input::placeholder {
  color: var(--color-text-muted);
}

.search-close {
  background: none;
  border: none;
  padding: var(--space-sm) var(--space-md);
  color: var(--color-text-muted);
  cursor: pointer;
  font-size: 1rem;
}

.header-right {
  display: flex;
  align-items: center;
  gap: var(--space-xs);
}

.header-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  border: none;
  background: none;
  color: var(--color-text-secondary);
  cursor: pointer;
  border-radius: var(--radius-md);
  transition: all var(--transition-fast);
  text-decoration: none;
}

.header-btn:hover {
  background: var(--color-parchment);
  color: var(--color-primary);
}

@media (max-width: 768px) {
  .menu-btn { display: flex; }
  .header-center { display: none; }
}
</style>
