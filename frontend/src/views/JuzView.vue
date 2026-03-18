<script setup>
import { ref, computed, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useQuranStore } from '@/stores/quran'
import VerseCard from '@/components/VerseCard.vue'

const route = useRoute()
const router = useRouter()
const store = useQuranStore()
const loadingMore = ref(false)
const juzNumber = computed(() => Number(route.params.number))

async function loadJuz(n) {
  store.loading = true
  try {
    const params = {
      language: 'id', words: store.settings.showWordByWord ? 'true' : 'false',
      translations: store.settings.translationId,
      fields: store.settings.showTajweed ? 'text_uthmani,text_uthmani_tajweed' : 'text_uthmani',
      per_page: 50, page: 1
    }
    const res = await fetch(`/api/verses/by_juz/${n}?` + new URLSearchParams(params))
    const data = await res.json()
    store.currentVerses = data.verses || []
    store.pagination = data.pagination
  } catch (e) { store.error = 'Gagal memuat juz' }
  store.loading = false
}

function prevJuz() { if (juzNumber.value > 1) router.push(`/juz/${juzNumber.value - 1}`) }
function nextJuz() { if (juzNumber.value < 30) router.push(`/juz/${juzNumber.value + 1}`) }

watch(juzNumber, (n) => { if (n) loadJuz(n) }, { immediate: true })
</script>

<template>
  <div class="juz-view">
    <div class="juz-header">
      <button class="nav-btn" @click="prevJuz" :disabled="juzNumber<=1">◀</button>
      <div class="juz-info"><span class="juz-label">Juz</span><span class="juz-num">{{ juzNumber }}</span><span class="juz-total">/ 30</span></div>
      <button class="nav-btn" @click="nextJuz" :disabled="juzNumber>=30">▶</button>
    </div>
    <div v-if="store.loading" class="loading-center"><div class="loading-spinner"></div></div>
    <div v-else class="verses-list">
      <VerseCard v-for="v in store.currentVerses" :key="v.id" :verse="v" :surah-name="`Juz ${juzNumber}`"/>
    </div>
  </div>
</template>

<style scoped>
.juz-header{display:flex;align-items:center;justify-content:center;gap:var(--space-lg);padding:var(--space-md);background:var(--color-bg-card);border-bottom:1px solid var(--color-border);position:sticky;top:0;z-index:10}
.nav-btn{width:40px;height:40px;border:1px solid var(--color-border);background:var(--color-bg-card);border-radius:var(--radius-sm);cursor:pointer;color:var(--color-text);font-size:.9rem;transition:all var(--transition-fast)}
.nav-btn:hover:not(:disabled){border-color:var(--color-primary);color:var(--color-primary)}.nav-btn:disabled{opacity:.3;cursor:default}
.juz-info{display:flex;align-items:baseline;gap:var(--space-xs)}.juz-label{font-size:.8rem;color:var(--color-text-muted)}.juz-num{font-size:1.5rem;font-weight:700;color:var(--color-primary)}.juz-total{font-size:.8rem;color:var(--color-text-muted)}
.loading-center{display:flex;justify-content:center;padding:var(--space-3xl)}
</style>
