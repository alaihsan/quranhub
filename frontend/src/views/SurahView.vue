<script setup>
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'
import { useQuranStore } from '@/stores/quran'
import VerseCard from '@/components/VerseCard.vue'
import MushafView from '@/components/MushafView.vue'

const route = useRoute()
const store = useQuranStore()
const currentChapter = ref(null)
const loadingMore = ref(false)

const chapterId = computed(() => Number(route.params.id))

const surahName = computed(() => currentChapter.value?.name_simple || '')
const showBismillah = computed(() => currentChapter.value?.bismillah_pre !== false && chapterId.value !== 1 && chapterId.value !== 9)

// Reading mode: 'normal' or 'mushaf'
const readingMode = computed(() => store.settings.readingMode || 'normal')

function setReadingMode(mode) {
  store.updateSettings({ readingMode: mode })

  // Mushaf mode needs word-by-word data, reload if switching to mushaf
  if (mode === 'mushaf') {
    reloadWithWords()
  }
}

async function reloadWithWords() {
  await store.fetchVersesByChapter(chapterId.value, 1, true)
}

async function loadSurah(id) {
  await store.fetchChapters()
  currentChapter.value = store.chapters.find(c => c.id === id)
  const forceWords = readingMode.value === 'mushaf'
  await store.fetchVersesByChapter(id, 1, forceWords)
}

async function loadMore() {
  if (!store.pagination || !store.pagination.next_page || loadingMore.value) return
  loadingMore.value = true
  const forceWords = readingMode.value === 'mushaf'
  await store.fetchVersesByChapter(chapterId.value, store.pagination.next_page, forceWords)
  loadingMore.value = false
}

function handleScroll(e) {
  const el = e.target
  if (el.scrollHeight - el.scrollTop - el.clientHeight < 400) {
    loadMore()
  }
}

let scrollEl = null

watch(chapterId, (newId) => { if (newId) loadSurah(newId) }, { immediate: true })

onMounted(() => {
  scrollEl = document.querySelector('.app-main')
  if (scrollEl) scrollEl.addEventListener('scroll', handleScroll)
})

onUnmounted(() => {
  if (scrollEl) scrollEl.removeEventListener('scroll', handleScroll)
})
</script>

<template>
  <div class="surah-view">
    <!-- Surah Header -->
    <div v-if="currentChapter" class="surah-header">
      <div class="surah-header-bg"></div>
      <div class="surah-header-content">
        <div class="surah-badge">
          <svg width="64" height="64" viewBox="0 0 72 72">
            <polygon points="36,4 66,20 66,52 36,68 6,52 6,20" fill="none" stroke="var(--color-gold)" stroke-width="1.5"/>
            <polygon points="36,10 60,23 60,49 36,62 12,49 12,23" fill="none" stroke="var(--color-gold)" stroke-width="0.8" opacity="0.4"/>
            <text x="36" y="40" text-anchor="middle" font-size="18" font-weight="700" fill="var(--color-gold)">{{ currentChapter.id }}</text>
          </svg>
        </div>
        <h1 class="surah-title-arabic" translate="no">{{ currentChapter.name_arabic }}</h1>
        <h2 class="surah-title-latin">{{ currentChapter.name_simple }}</h2>
        <p class="surah-meaning">{{ currentChapter.translated_name?.name }}</p>
        <div class="surah-info-pills">
          <span class="pill">{{ currentChapter.revelation_place === 'makkah' || currentChapter.revelation_place === 'makka' ? 'Makkiyyah' : 'Madaniyyah' }}</span>
          <span class="pill">{{ currentChapter.verses_count }} Ayat</span>
          <span class="pill">Hal. {{ currentChapter.pages?.[0] }} - {{ currentChapter.pages?.[1] }}</span>
        </div>
      </div>
    </div>

    <!-- Reading Mode Toggle Bar -->
    <div class="reading-mode-bar">
      <div class="mode-toggle">
        <button
          :class="['mode-btn', { active: readingMode === 'normal' }]"
          @click="setReadingMode('normal')"
        >
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round">
            <line x1="3" y1="6" x2="21" y2="6"/>
            <line x1="3" y1="12" x2="21" y2="12"/>
            <line x1="3" y1="18" x2="21" y2="18"/>
          </svg>
          <span>Per Ayat</span>
        </button>
        <button
          :class="['mode-btn', { active: readingMode === 'mushaf' }]"
          @click="setReadingMode('mushaf')"
        >
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round">
            <path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z"/>
            <path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"/>
          </svg>
          <span>Mushaf</span>
        </button>
      </div>
    </div>

    <!-- Bismillah (only in normal mode, mushaf handles its own) -->
    <div v-if="readingMode === 'normal' && showBismillah" class="bismillah" translate="no">
      بِسْمِ ٱللَّهِ ٱلرَّحْمَـٰنِ ٱلرَّحِيمِ
    </div>

    <!-- Loading -->
    <div v-if="store.loading && store.currentVerses.length === 0" class="loading-center">
      <div class="loading-spinner"></div>
      <p class="loading-text">Memuat surah...</p>
    </div>

    <!-- MUSHAF MODE -->
    <template v-else-if="readingMode === 'mushaf'">
      <MushafView
        :verses="store.currentVerses"
        :surah-name="surahName"
        :chapter-id="chapterId"
        :show-bismillah="showBismillah"
      />

      <div v-if="store.pagination?.next_page" class="load-more">
        <button v-if="!loadingMore" class="btn-load-more" @click="loadMore">
          Muat lebih banyak ayat
        </button>
        <div v-else class="loading-spinner" style="width:24px;height:24px;border-width:2px"></div>
      </div>
    </template>

    <!-- NORMAL MODE -->
    <template v-else>
      <div class="verses-list">
        <VerseCard
          v-for="verse in store.currentVerses"
          :key="verse.id"
          :verse="verse"
          :surah-name="surahName"
        />

        <div v-if="store.pagination?.next_page" class="load-more">
          <button v-if="!loadingMore" class="btn-load-more" @click="loadMore">
            Muat lebih banyak ayat
          </button>
          <div v-else class="loading-spinner" style="width:24px;height:24px;border-width:2px"></div>
        </div>
      </div>
    </template>
  </div>
</template>

<style scoped>
.surah-view { min-height: 100%; }

.surah-header {
  position: relative;
  text-align: center;
  padding: var(--space-2xl) var(--space-xl);
  background: linear-gradient(160deg, var(--color-primary-dark), var(--color-primary));
  color: white;
  overflow: hidden;
}

.surah-header-bg {
  position: absolute;
  inset: 0;
  opacity: 0.05;
  background-image: url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' stroke='%23fff' stroke-width='0.5'%3E%3Ccircle cx='30' cy='30' r='20'/%3E%3Ccircle cx='30' cy='30' r='10'/%3E%3C/g%3E%3C/svg%3E");
}

.surah-header-content { position: relative; z-index: 1; animation: fadeIn .6s ease; }
.surah-title-arabic { font-family: var(--font-arabic-quran); font-size: 2.5rem; font-weight: 400; margin: var(--space-md) 0 var(--space-xs); direction: rtl; }
.surah-title-latin { font-size: 1.3rem; font-weight: 600; margin-bottom: var(--space-xs); }
.surah-meaning { font-size: 0.9rem; opacity: 0.8; }

.surah-info-pills { display: flex; gap: var(--space-sm); justify-content: center; margin-top: var(--space-md); flex-wrap: wrap; }
.pill {
  padding: 4px 14px;
  background: rgba(255,255,255,0.15);
  border-radius: 99px;
  font-size: 0.75rem;
  font-weight: 500;
}

/* =============================================
   Reading Mode Toggle Bar
   ============================================= */
.reading-mode-bar {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: var(--space-sm) var(--space-lg);
  background: var(--color-bg-card);
  border-bottom: 1px solid var(--color-border-light);
  position: sticky;
  top: 0;
  z-index: 10;
}

.mode-toggle {
  display: flex;
  background: var(--color-parchment);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  overflow: hidden;
  padding: 3px;
  gap: 3px;
}

.mode-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 16px;
  border: none;
  background: none;
  font-family: var(--font-body);
  font-size: 0.8rem;
  font-weight: 500;
  color: var(--color-text-muted);
  cursor: pointer;
  border-radius: var(--radius-md);
  transition: all var(--transition-fast);
  white-space: nowrap;
}

.mode-btn:hover {
  color: var(--color-text);
}

.mode-btn.active {
  background: var(--color-bg-card);
  color: var(--color-primary);
  box-shadow: var(--shadow-sm);
  font-weight: 600;
}

/* =============================================
   Bismillah & Others
   ============================================= */
.bismillah {
  text-align: center;
  font-family: var(--font-arabic-quran);
  font-size: 2rem;
  color: var(--color-text-arabic);
  padding: var(--space-xl) var(--space-lg);
  direction: rtl;
  border-bottom: 1px solid var(--color-border-light);
  background: linear-gradient(to bottom, color-mix(in srgb, var(--color-gold) 4%, transparent), transparent);
}

.loading-center {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--space-md);
  padding: var(--space-3xl);
}

.loading-text { color: var(--color-text-muted); font-size: 0.9rem; }

.load-more {
  display: flex;
  justify-content: center;
  padding: var(--space-xl);
}

.btn-load-more {
  padding: var(--space-sm) var(--space-xl);
  background: var(--color-bg-card);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  font-family: var(--font-body);
  font-size: 0.85rem;
  font-weight: 500;
  color: var(--color-primary);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.btn-load-more:hover { border-color: var(--color-primary); box-shadow: var(--shadow-sm); }

@media (max-width: 768px) {
  .surah-header { padding: var(--space-xl) var(--space-md); }
  .surah-title-arabic { font-size: 1.8rem; }
  .bismillah { font-size: 1.5rem; }
  .mode-btn { padding: 5px 12px; font-size: 0.75rem; }
}
</style>
