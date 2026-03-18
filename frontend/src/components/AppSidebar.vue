<script setup>
import { ref, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useQuranStore } from '@/stores/quran'

const router = useRouter()
const route = useRoute()
const store = useQuranStore()
const searchFilter = ref('')
const activeTab = ref('surah')

const filteredChapters = computed(() => {
  if (!searchFilter.value) return store.chapters
  const q = searchFilter.value.toLowerCase()
  return store.chapters.filter(ch =>
    ch.name_simple.toLowerCase().includes(q) ||
    ch.name_arabic.includes(q) ||
    ch.translated_name?.name?.toLowerCase().includes(q) ||
    String(ch.id).includes(q)
  )
})

const juzList = computed(() => Array.from({ length: 30 }, (_, i) => i + 1))

function navigateToSurah(id) { router.push(`/surah/${id}`); closeMobileSidebar() }
function navigateToPage(num) { router.push(`/page/${num}`); closeMobileSidebar() }
function navigateToJuz(num) { router.push(`/juz/${num}`); closeMobileSidebar() }
function closeMobileSidebar() { document.body.classList.remove('sidebar-open') }
function getRevelationIcon(place) { return place === 'makkah' || place === 'makka' ? '🕋' : '🕌' }
</script>

<template>
  <aside class="sidebar">
    <div class="sidebar-inner">
      <div v-if="store.lastRead" class="last-read" @click="navigateToSurah(store.lastRead.chapterId)">
        <div class="last-read-label">Terakhir dibaca</div>
        <div class="last-read-info">
          <span class="last-read-surah">{{ store.lastRead.surahName }}</span>
          <span class="last-read-ayah">Ayat {{ store.lastRead.verseNumber }}</span>
        </div>
      </div>

      <div class="sidebar-tabs">
        <button v-for="tab in [{id:'surah',label:'Surah'},{id:'juz',label:'Juz'},{id:'page',label:'Halaman'},{id:'bookmark',label:'♡'}]" :key="tab.id" :class="['tab-btn',{active:activeTab===tab.id}]" @click="activeTab=tab.id">{{ tab.label }}</button>
      </div>

      <div v-if="activeTab==='surah'" class="sidebar-search">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
        <input v-model="searchFilter" type="text" placeholder="Cari surah..." />
      </div>

      <div v-if="activeTab==='surah'" class="sidebar-list">
        <div v-for="ch in filteredChapters" :key="ch.id" :class="['surah-item',{active:route.params.id==ch.id}]" @click="navigateToSurah(ch.id)">
          <div class="surah-number">
            <svg width="36" height="36" viewBox="0 0 40 40"><polygon points="20,2 37,11 37,29 20,38 3,29 3,11" fill="none" stroke="var(--color-gold)" stroke-width="1.2" opacity="0.6"/><text x="20" y="22" text-anchor="middle" font-size="12" font-weight="600" fill="var(--color-text)">{{ ch.id }}</text></svg>
          </div>
          <div class="surah-info">
            <div class="surah-name-row">
              <span class="surah-name-latin">{{ ch.name_simple }}</span>
              <span class="surah-name-arabic">{{ ch.name_arabic }}</span>
            </div>
            <div class="surah-meta">
              <span>{{ getRevelationIcon(ch.revelation_place) }}</span>
              <span>{{ ch.translated_name?.name }}</span>
              <span class="dot">·</span>
              <span>{{ ch.verses_count }} Ayat</span>
            </div>
          </div>
        </div>
        <div v-if="filteredChapters.length===0" class="empty-state">Surah tidak ditemukan</div>
      </div>

      <div v-if="activeTab==='juz'" class="sidebar-list">
        <div v-for="j in juzList" :key="j" :class="['juz-item',{active:route.params.number==j&&route.name==='Juz'}]" @click="navigateToJuz(j)">
          <div class="juz-num">{{ j }}</div>
          <div class="juz-label">Juz {{ j }}</div>
        </div>
      </div>

      <div v-if="activeTab==='page'" class="sidebar-list">
        <div class="page-grid">
          <button v-for="p in 604" :key="p" :class="['page-btn',{active:route.params.number==p&&route.name==='Page'}]" @click="navigateToPage(p)">{{ p }}</button>
        </div>
      </div>

      <div v-if="activeTab==='bookmark'" class="sidebar-list">
        <div v-if="store.bookmarks.length===0" class="empty-state">
          <p>Belum ada penanda</p>
          <p class="empty-hint">Ketuk ikon ♡ pada ayat untuk menambahkan</p>
        </div>
        <div v-for="bm in store.bookmarks" :key="bm.verseKey" class="bookmark-item" @click="navigateToSurah(bm.verseKey.split(':')[0])">
          <div class="bookmark-info">
            <span class="bookmark-surah">{{ bm.surahName }}</span>
            <span class="bookmark-ayah">Ayat {{ bm.verseKey.split(':')[1] }}</span>
          </div>
          <button class="bookmark-remove" @click.stop="store.removeBookmark(bm.verseKey)">✕</button>
        </div>
      </div>
    </div>
  </aside>
  <div class="sidebar-overlay" @click="closeMobileSidebar"></div>
</template>

<style scoped>
.sidebar{width:var(--sidebar-width);height:calc(100vh - var(--header-height));position:sticky;top:var(--header-height);background:var(--color-bg-sidebar);border-right:1px solid var(--color-border);overflow:hidden;flex-shrink:0}
.sidebar-inner{height:100%;display:flex;flex-direction:column;overflow:hidden}
.sidebar-overlay{display:none;position:fixed;inset:0;background:var(--color-bg-overlay);z-index:49}
.last-read{padding:var(--space-md) var(--space-lg);background:linear-gradient(135deg,var(--color-primary),var(--color-primary-dark));color:white;cursor:pointer;transition:opacity var(--transition-fast)}
.last-read:hover{opacity:.9}.last-read-label{font-size:.7rem;text-transform:uppercase;letter-spacing:.08em;opacity:.7}
.last-read-info{display:flex;justify-content:space-between;align-items:center;margin-top:2px}
.last-read-surah{font-weight:600;font-size:.95rem}.last-read-ayah{font-size:.8rem;opacity:.8}
.sidebar-tabs{display:flex;padding:var(--space-sm) var(--space-sm) 0;gap:2px;border-bottom:1px solid var(--color-border-light)}
.tab-btn{flex:1;padding:var(--space-sm) var(--space-xs);border:none;background:none;font-family:var(--font-body);font-size:.8rem;font-weight:500;color:var(--color-text-muted);cursor:pointer;border-radius:var(--radius-sm) var(--radius-sm) 0 0;transition:all var(--transition-fast)}
.tab-btn:hover{color:var(--color-text)}.tab-btn.active{color:var(--color-primary);background:var(--color-bg-card);border-bottom:2px solid var(--color-primary)}
.sidebar-search{display:flex;align-items:center;gap:var(--space-sm);padding:var(--space-sm) var(--space-md);margin:var(--space-sm) var(--space-sm) 0;background:var(--color-bg-card);border:1px solid var(--color-border-light);border-radius:var(--radius-md);color:var(--color-text-muted)}
.sidebar-search input{flex:1;border:none;background:none;font-family:var(--font-body);font-size:.85rem;color:var(--color-text);outline:none}
.sidebar-search input::placeholder{color:var(--color-text-muted)}
.sidebar-list{flex:1;overflow-y:auto;padding:var(--space-sm)}
.surah-item{display:flex;align-items:center;gap:var(--space-sm);padding:var(--space-sm);border-radius:var(--radius-md);cursor:pointer;transition:background var(--transition-fast)}
.surah-item:hover{background:var(--color-bg-card)}.surah-item.active{background:color-mix(in srgb,var(--color-primary) 10%,transparent)}
.surah-info{flex:1;min-width:0}.surah-name-row{display:flex;justify-content:space-between;align-items:center;gap:var(--space-sm)}
.surah-name-latin{font-weight:600;font-size:.9rem;color:var(--color-text)}.surah-name-arabic{font-family:var(--font-arabic);font-size:1.1rem;color:var(--color-text-arabic);direction:rtl}
.surah-meta{display:flex;align-items:center;gap:4px;font-size:.75rem;color:var(--color-text-muted)}.dot{opacity:.4}
.juz-item{display:flex;align-items:center;gap:var(--space-md);padding:var(--space-sm) var(--space-md);border-radius:var(--radius-md);cursor:pointer;transition:background var(--transition-fast)}
.juz-item:hover{background:var(--color-bg-card)}.juz-item.active{background:color-mix(in srgb,var(--color-primary) 10%,transparent)}
.juz-num{width:32px;height:32px;display:flex;align-items:center;justify-content:center;background:var(--color-primary);color:white;font-weight:700;font-size:.8rem;border-radius:var(--radius-sm)}
.juz-label{font-weight:500;font-size:.9rem}
.page-grid{display:grid;grid-template-columns:repeat(6,1fr);gap:4px}
.page-btn{padding:var(--space-xs);border:1px solid var(--color-border-light);background:var(--color-bg-card);border-radius:var(--radius-sm);font-size:.75rem;font-family:var(--font-body);cursor:pointer;transition:all var(--transition-fast);color:var(--color-text)}
.page-btn:hover{border-color:var(--color-primary);color:var(--color-primary)}.page-btn.active{background:var(--color-primary);color:white;border-color:var(--color-primary)}
.bookmark-item{display:flex;align-items:center;justify-content:space-between;padding:var(--space-sm) var(--space-md);border-radius:var(--radius-md);cursor:pointer;transition:background var(--transition-fast)}
.bookmark-item:hover{background:var(--color-bg-card)}.bookmark-info{display:flex;flex-direction:column}
.bookmark-surah{font-weight:600;font-size:.9rem}.bookmark-ayah{font-size:.75rem;color:var(--color-text-muted)}
.bookmark-remove{background:none;border:none;color:var(--color-text-muted);cursor:pointer;font-size:.9rem;padding:4px 8px;border-radius:var(--radius-sm)}
.bookmark-remove:hover{background:#fee;color:#c00}
.empty-state{text-align:center;padding:var(--space-2xl);color:var(--color-text-muted);font-size:.9rem}.empty-hint{font-size:.8rem;margin-top:var(--space-xs)}

@media(max-width:768px){
  .sidebar{position:fixed;left:0;top:var(--header-height);z-index:50;transform:translateX(-100%)}
  :global(body.sidebar-open) .sidebar{transform:translateX(0)}
  :global(body.sidebar-open) .sidebar-overlay{display:block}
}
</style>
