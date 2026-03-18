<script setup>
import { computed, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useQuranStore } from '@/stores/quran'
import VerseCard from '@/components/VerseCard.vue'

const route = useRoute()
const router = useRouter()
const store = useQuranStore()
const pageNumber = computed(() => Number(route.params.number))

function prevPage() { if (pageNumber.value > 1) router.push(`/page/${pageNumber.value - 1}`) }
function nextPage() { if (pageNumber.value < 604) router.push(`/page/${pageNumber.value + 1}`) }

watch(pageNumber, (n) => { if (n) store.fetchVersesByPage(n) }, { immediate: true })
</script>

<template>
  <div class="page-view">
    <div class="page-nav">
      <button class="nav-btn" @click="prevPage" :disabled="pageNumber<=1">◀</button>
      <div class="page-info"><span class="page-label">Halaman</span><span class="page-num">{{ pageNumber }}</span><span class="page-total">/ 604</span></div>
      <button class="nav-btn" @click="nextPage" :disabled="pageNumber>=604">▶</button>
    </div>
    <div v-if="store.loading" class="loading-center"><div class="loading-spinner"></div></div>
    <div v-else class="verses-list">
      <VerseCard v-for="v in store.currentVerses" :key="v.id" :verse="v" :surah-name="`Hal. ${pageNumber}`"/>
    </div>
    <div class="page-nav bottom">
      <button class="nav-btn-text" @click="prevPage" :disabled="pageNumber<=1">← Sebelumnya</button>
      <button class="nav-btn-text" @click="nextPage" :disabled="pageNumber>=604">Selanjutnya →</button>
    </div>
  </div>
</template>

<style scoped>
.page-nav{display:flex;align-items:center;justify-content:center;gap:var(--space-lg);padding:var(--space-md);background:var(--color-bg-card);border-bottom:1px solid var(--color-border);position:sticky;top:0;z-index:10}
.page-nav.bottom{border-top:1px solid var(--color-border);border-bottom:none;position:static;justify-content:space-between;padding:var(--space-lg)}
.nav-btn{width:40px;height:40px;border:1px solid var(--color-border);background:var(--color-bg-card);border-radius:var(--radius-sm);cursor:pointer;color:var(--color-text);font-size:.9rem;transition:all var(--transition-fast)}
.nav-btn:hover:not(:disabled){border-color:var(--color-primary);color:var(--color-primary)}.nav-btn:disabled{opacity:.3;cursor:default}
.page-info{display:flex;align-items:baseline;gap:var(--space-xs)}.page-label{font-size:.8rem;color:var(--color-text-muted)}.page-num{font-size:1.5rem;font-weight:700;color:var(--color-primary)}.page-total{font-size:.8rem;color:var(--color-text-muted)}
.loading-center{display:flex;justify-content:center;padding:var(--space-3xl)}
.nav-btn-text{padding:var(--space-sm) var(--space-lg);background:none;border:1px solid var(--color-border);border-radius:var(--radius-md);font-family:var(--font-body);font-size:.85rem;cursor:pointer;color:var(--color-text);transition:all var(--transition-fast)}
.nav-btn-text:hover:not(:disabled){border-color:var(--color-primary);color:var(--color-primary)}.nav-btn-text:disabled{opacity:.3;cursor:default}
</style>
