<script setup>
import { ref, computed, watch, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { useQuranStore } from '@/stores/quran'

const router = useRouter()
const store = useQuranStore()
const showSearch = ref(false)
const searchQuery = ref('')
const searchInputRef = ref(null)
const searchResults = ref([])
const showResults = ref(false)
const selectedIndex = ref(-1)

// Watch query changes for live search
watch(searchQuery, (q) => {
  if (!q.trim()) {
    searchResults.value = []
    showResults.value = false
    selectedIndex.value = -1
    return
  }
  performSearch(q.trim())
})

function performSearch(q) {
  const results = []

  // 1. Check verse reference pattern like "2:255" or "2 255"
  const verseMatch = q.match(/^(\d+)[:\s](\d+)$/)
  if (verseMatch) {
    const chId = Number(verseMatch[1])
    const verseNum = verseMatch[2]
    const ch = store.chapters.find(c => c.id === chId)
    if (ch) {
      results.push({
        type: 'verse',
        id: chId,
        verse: verseNum,
        label: `${ch.name_simple} : Ayat ${verseNum}`,
        sublabel: ch.name_arabic,
        icon: '📖'
      })
    }
  }

  // 2. Check surah number only
  const numMatch = q.match(/^(\d+)$/)
  if (numMatch) {
    const num = Number(numMatch[1])
    // Match surah number
    const ch = store.chapters.find(c => c.id === num)
    if (ch) {
      results.push({
        type: 'surah',
        id: ch.id,
        label: `${ch.id}. ${ch.name_simple}`,
        sublabel: `${ch.name_arabic} — ${ch.translated_name?.name}`,
        icon: '📗'
      })
    }
    // Also match page
    if (num >= 1 && num <= 604) {
      results.push({
        type: 'page',
        id: num,
        label: `Halaman ${num}`,
        sublabel: 'Buka halaman mushaf',
        icon: '📄'
      })
    }
    // Also match juz
    if (num >= 1 && num <= 30) {
      results.push({
        type: 'juz',
        id: num,
        label: `Juz ${num}`,
        sublabel: 'Buka juz',
        icon: '📚'
      })
    }
  }

  // 3. Search surah by name (latin, arabic, translated name)
  if (!numMatch || results.length === 0) {
    const lower = q.toLowerCase()
    const matched = store.chapters.filter(ch =>
      ch.name_simple.toLowerCase().includes(lower) ||
      ch.name_arabic.includes(q) ||
      ch.translated_name?.name?.toLowerCase().includes(lower) ||
      // Also match without diacritics: al-fatihah = fatihah = al fatihah
      ch.name_simple.toLowerCase().replace(/[^a-z]/g, '').includes(lower.replace(/[^a-z]/g, ''))
    ).slice(0, 8)

    for (const ch of matched) {
      // Avoid duplicates
      if (!results.some(r => r.type === 'surah' && r.id === ch.id)) {
        results.push({
          type: 'surah',
          id: ch.id,
          label: `${ch.id}. ${ch.name_simple}`,
          sublabel: `${ch.name_arabic} — ${ch.translated_name?.name} · ${ch.verses_count} Ayat`,
          icon: ch.revelation_place === 'makkah' || ch.revelation_place === 'makka' ? '🕋' : '🕌'
        })
      }
    }
  }

  searchResults.value = results
  showResults.value = results.length > 0
  selectedIndex.value = -1
}

function navigateResult(result) {
  if (!result) return
  switch (result.type) {
    case 'surah':
      router.push(`/surah/${result.id}`)
      break
    case 'verse':
      router.push(`/surah/${result.id}`)
      // TODO: scroll to specific verse after navigation
      break
    case 'page':
      router.push(`/page/${result.id}`)
      break
    case 'juz':
      router.push(`/juz/${result.id}`)
      break
  }
  closeSearch()
}

function handleSearchSubmit() {
  if (selectedIndex.value >= 0 && searchResults.value[selectedIndex.value]) {
    navigateResult(searchResults.value[selectedIndex.value])
    return
  }
  if (searchResults.value.length > 0) {
    navigateResult(searchResults.value[0])
    return
  }
  // Fallback: try verse pattern
  const q = searchQuery.value.trim()
  const verseMatch = q.match(/^(\d+)[:\s](\d+)$/)
  if (verseMatch) {
    router.push(`/surah/${verseMatch[1]}`)
    closeSearch()
  }
}

function handleKeydown(e) {
  if (e.key === 'ArrowDown') {
    e.preventDefault()
    selectedIndex.value = Math.min(selectedIndex.value + 1, searchResults.value.length - 1)
  } else if (e.key === 'ArrowUp') {
    e.preventDefault()
    selectedIndex.value = Math.max(selectedIndex.value - 1, -1)
  } else if (e.key === 'Enter') {
    handleSearchSubmit()
  } else if (e.key === 'Escape') {
    closeSearch()
  }
}

function openSearch() {
  showSearch.value = true
  nextTick(() => {
    searchInputRef.value?.focus()
  })
}

function closeSearch() {
  showSearch.value = false
  showResults.value = false
  searchQuery.value = ''
  searchResults.value = []
  selectedIndex.value = -1
}

function toggleTheme() {
  const newTheme = store.settings.theme === 'light' ? 'dark' : 'light'
  store.updateSettings({ theme: newTheme })
}

function goHome() {
  router.push('/')
}

function toggleSidebar() {
  store.updateSettings({ sidebarCollapsed: !store.settings.sidebarCollapsed })
}
</script>

<template>
  <header class="app-header">
    <div class="header-left">
      <button class="header-btn sidebar-toggle-btn" @click="toggleSidebar" aria-label="Toggle Sidebar" title="Show/Hide Sidebar">
        <svg v-if="!store.settings.sidebarCollapsed" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round">
          <rect x="3" y="3" width="18" height="18" rx="2"/>
          <line x1="9" y1="3" x2="9" y2="21"/>
        </svg>
        <svg v-else width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round">
          <rect x="3" y="3" width="18" height="18" rx="2"/>
          <line x1="9" y1="3" x2="9" y2="21" opacity="0.3"/>
          <polyline points="13,9 16,12 13,15"/>
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
      <div v-if="showSearch" class="search-wrapper">
        <div class="search-bar">
          <svg class="search-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
          <input
            ref="searchInputRef"
            v-model="searchQuery"
            type="text"
            placeholder="Cari surah, ayat (2:255), halaman, juz..."
            @keydown="handleKeydown"
            autocomplete="off"
          />
          <kbd v-if="!searchQuery" class="search-hint">ESC</kbd>
          <button v-else @click="closeSearch" class="search-close">✕</button>
        </div>

        <!-- Search Results Dropdown -->
        <div v-if="showResults" class="search-dropdown">
          <div
            v-for="(r, idx) in searchResults"
            :key="`${r.type}-${r.id}`"
            :class="['search-result-item', { selected: idx === selectedIndex }]"
            @click="navigateResult(r)"
            @mouseenter="selectedIndex = idx"
          >
            <span class="result-icon">{{ r.icon }}</span>
            <div class="result-text">
              <span class="result-label">{{ r.label }}</span>
              <span class="result-sublabel">{{ r.sublabel }}</span>
            </div>
            <span class="result-type">{{ r.type === 'surah' ? 'Surah' : r.type === 'verse' ? 'Ayat' : r.type === 'page' ? 'Halaman' : 'Juz' }}</span>
          </div>
        </div>

        <!-- Backdrop -->
        <div class="search-backdrop" @click="closeSearch"></div>
      </div>
    </div>

    <div class="header-right">
      <button class="header-btn" @click="openSearch" aria-label="Cari">
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
  gap: var(--space-sm);
}

.sidebar-toggle-btn {
  color: var(--color-text-secondary);
}

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
  max-width: 540px;
  margin: 0 var(--space-lg);
  position: relative;
}

/* ── Search ── */
.search-wrapper {
  width: 100%;
  position: relative;
  z-index: 200;
}

.search-bar {
  display: flex;
  align-items: center;
  width: 100%;
  background: var(--color-bg-card);
  border: 2px solid var(--color-primary);
  border-radius: var(--radius-lg);
  overflow: hidden;
  animation: fadeIn 0.15s ease;
  box-shadow: var(--shadow-md);
}

.search-icon {
  margin-left: var(--space-md);
  color: var(--color-text-muted);
  flex-shrink: 0;
}

.search-bar input {
  flex: 1;
  border: none;
  background: none;
  padding: 10px var(--space-md);
  font-family: var(--font-body);
  font-size: 0.9rem;
  color: var(--color-text);
  outline: none;
}

.search-bar input::placeholder { color: var(--color-text-muted); }

.search-hint {
  font-size: 0.65rem;
  padding: 2px 6px;
  background: var(--color-parchment);
  border: 1px solid var(--color-border);
  border-radius: 4px;
  color: var(--color-text-muted);
  margin-right: var(--space-sm);
  font-family: var(--font-body);
}

.search-close {
  background: none;
  border: none;
  padding: 8px 14px;
  color: var(--color-text-muted);
  cursor: pointer;
  font-size: 1rem;
}
.search-close:hover { color: var(--color-text); }

/* Search dropdown */
.search-dropdown {
  position: absolute;
  top: calc(100% + 6px);
  left: 0;
  right: 0;
  background: var(--color-bg-card);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-lg);
  max-height: 360px;
  overflow-y: auto;
  z-index: 201;
  animation: fadeIn 0.15s ease;
}

.search-result-item {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
  padding: 10px var(--space-md);
  cursor: pointer;
  transition: background 0.1s;
  border-bottom: 1px solid var(--color-border-light);
}
.search-result-item:last-child { border-bottom: none; }
.search-result-item:hover,
.search-result-item.selected {
  background: color-mix(in srgb, var(--color-primary) 8%, transparent);
}

.result-icon { font-size: 1.2rem; flex-shrink: 0; width: 28px; text-align: center; }
.result-text { flex: 1; min-width: 0; }
.result-label { font-weight: 600; font-size: 0.9rem; color: var(--color-text); display: block; }
.result-sublabel { font-size: 0.75rem; color: var(--color-text-muted); display: block; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.result-type { font-size: 0.65rem; color: var(--color-text-muted); text-transform: uppercase; letter-spacing: 0.05em; background: var(--color-parchment); padding: 2px 8px; border-radius: 99px; flex-shrink: 0; }

.search-backdrop {
  position: fixed;
  inset: 0;
  z-index: -1;
}

/* ── Header buttons ── */
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
  .header-center { margin: 0 var(--space-sm); }
  .search-wrapper { position: fixed; left: var(--space-sm); right: var(--space-sm); top: 10px; }
  .logo-text { display: none; }
}
</style>
