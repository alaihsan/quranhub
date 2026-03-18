<script setup>
import { ref, computed } from 'vue'
import { useQuranStore } from '@/stores/quran'

const props = defineProps({
  verse: { type: Object, required: true },
  surahName: { type: String, default: '' }
})

const store = useQuranStore()
const showTafsirPanel = ref(false)
const tafsirContent = ref(null)
const tafsirLoading = ref(false)

const verseNumber = computed(() => props.verse.verse_key?.split(':')[1])
const isBookmarked = computed(() => store.isBookmarked(props.verse.verse_key))

const arabicText = computed(() => {
  if (store.settings.showTajweed && props.verse.text_uthmani_tajweed) return props.verse.text_uthmani_tajweed
  return props.verse.text_uthmani || ''
})
const hasTajweed = computed(() => store.settings.showTajweed && props.verse.text_uthmani_tajweed)

const translationText = computed(() => {
  const t = props.verse.translations?.[0]
  if (!t) return null
  return t.text?.replace(/<sup[^>]*>.*?<\/sup>/g, '').replace(/<[^>]*>/g, '') || ''
})

const inlineTafsir = computed(() => props.verse.tafsirs?.[0]?.text || null)

function toggleBookmark() {
  if (isBookmarked.value) store.removeBookmark(props.verse.verse_key)
  else store.addBookmark(props.verse.verse_key, props.surahName)
}

async function toggleTafsir() {
  showTafsirPanel.value = !showTafsirPanel.value
  if (showTafsirPanel.value && !tafsirContent.value && !inlineTafsir.value) {
    tafsirLoading.value = true
    const data = await store.fetchTafsir(store.settings.tafsirId, props.verse.verse_key)
    if (data?.tafsir) tafsirContent.value = data.tafsir.text
    tafsirLoading.value = false
  }
}

function saveAsLastRead() {
  store.setLastRead({
    chapterId: props.verse.verse_key?.split(':')[0],
    verseNumber: verseNumber.value,
    surahName: props.surahName,
    verseKey: props.verse.verse_key
  })
}
</script>

<template>
  <div class="verse-card" :id="`verse-${verse.verse_key}`" @click="saveAsLastRead">
    <div class="verse-header">
      <div class="verse-badge">
        <svg width="38" height="38" viewBox="0 0 40 40">
          <circle cx="20" cy="20" r="17" fill="none" stroke="var(--color-gold)" stroke-width="1.2"/>
          <circle cx="20" cy="20" r="14" fill="none" stroke="var(--color-gold)" stroke-width="0.5" opacity="0.4"/>
          <text x="20" y="23" text-anchor="middle" font-size="12" font-weight="600" fill="var(--color-gold)" font-family="var(--font-body)">{{ verseNumber }}</text>
        </svg>
      </div>
      <div class="verse-actions">
        <button class="action-btn" @click.stop="toggleBookmark" :title="isBookmarked ? 'Hapus penanda' : 'Tandai ayat'">
          <svg width="18" height="18" viewBox="0 0 24 24" :fill="isBookmarked ? 'var(--color-gold)' : 'none'" :stroke="isBookmarked ? 'var(--color-gold)' : 'currentColor'" stroke-width="2"><path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"/></svg>
        </button>
        <button class="action-btn" @click.stop="toggleTafsir" :class="{active:showTafsirPanel}" title="Tafsir">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z"/><path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"/></svg>
        </button>
      </div>
    </div>

    <div class="verse-arabic" :class="{'tajweed-text':hasTajweed}" :style="{fontSize:store.arabicFontSize}" v-html="arabicText" translate="no"></div>

    <div v-if="store.settings.showWordByWord && verse.words" class="word-by-word">
      <div v-for="word in verse.words" :key="word.id" class="word-item">
        <span class="word-arabic" translate="no">{{ word.text_uthmani || word.text_indopak }}</span>
        <span v-if="word.transliteration?.text" class="word-translit">{{ word.transliteration.text }}</span>
        <span v-if="word.translation?.text" class="word-trans">{{ word.translation.text }}</span>
      </div>
    </div>

    <div v-if="store.settings.showTranslation && translationText" class="verse-translation">
      <span class="tr-num">{{ verse.verse_key }}</span> {{ translationText }}
    </div>

    <transition name="slide">
      <div v-if="showTafsirPanel" class="tafsir-panel">
        <div class="tafsir-head"><span class="tafsir-label">Tafsir</span><button class="tafsir-close" @click.stop="showTafsirPanel=false">✕</button></div>
        <div v-if="tafsirLoading" class="tafsir-loading"><div class="loading-spinner" style="width:20px;height:20px;border-width:2px"></div> Memuat...</div>
        <div v-else-if="inlineTafsir" class="tafsir-body" v-html="inlineTafsir"></div>
        <div v-else-if="tafsirContent" class="tafsir-body" v-html="tafsirContent"></div>
        <div v-else class="tafsir-empty">Tafsir tidak tersedia</div>
      </div>
    </transition>
  </div>
</template>

<style scoped>
.verse-card{padding:var(--space-lg) var(--space-xl);border-bottom:1px solid var(--color-border-light);transition:background var(--transition-fast);animation:fadeIn .3s ease forwards}
.verse-card:hover{background:color-mix(in srgb,var(--color-parchment) 40%,transparent)}
.verse-header{display:flex;align-items:center;justify-content:space-between;margin-bottom:var(--space-sm)}
.verse-actions{display:flex;gap:var(--space-xs)}
.action-btn{display:flex;align-items:center;justify-content:center;width:36px;height:36px;border:none;background:none;color:var(--color-text-muted);cursor:pointer;border-radius:var(--radius-sm);transition:all var(--transition-fast)}
.action-btn:hover{background:var(--color-parchment);color:var(--color-primary)}
.action-btn.active{color:var(--color-primary);background:color-mix(in srgb,var(--color-primary) 8%,transparent)}
.verse-arabic{font-family:var(--font-arabic-quran);direction:rtl;text-align:right;line-height:2.4;color:var(--color-text-arabic);padding:var(--space-md) 0;word-spacing:4px}
.word-by-word{display:flex;flex-wrap:wrap-reverse;direction:rtl;gap:var(--space-sm);padding:var(--space-md) 0;border-top:1px dashed var(--color-border-light);border-bottom:1px dashed var(--color-border-light);margin:var(--space-sm) 0}
.word-item{display:flex;flex-direction:column;align-items:center;gap:2px;padding:var(--space-xs) var(--space-sm);border-radius:var(--radius-sm);min-width:60px;transition:background var(--transition-fast)}
.word-item:hover{background:var(--color-parchment)}
.word-arabic{font-family:var(--font-arabic-quran);font-size:1.3rem;color:var(--color-text-arabic);direction:rtl}
.word-translit{font-size:.7rem;color:var(--color-primary);font-style:italic}
.word-trans{font-size:.7rem;color:var(--color-text-muted);text-align:center;direction:ltr}
.verse-translation{font-size:.95rem;line-height:1.8;color:var(--color-text-secondary);padding-top:var(--space-sm)}
.tr-num{font-size:.75rem;font-weight:700;color:var(--color-primary);margin-right:var(--space-xs)}
.tafsir-panel{margin-top:var(--space-md);padding:var(--space-md) var(--space-lg);background:var(--color-parchment);border-radius:var(--radius-md);border:1px solid var(--color-border-light)}
.tafsir-head{display:flex;align-items:center;justify-content:space-between;margin-bottom:var(--space-sm)}
.tafsir-label{font-weight:700;font-size:.85rem;color:var(--color-primary);text-transform:uppercase;letter-spacing:.05em}
.tafsir-close{background:none;border:none;color:var(--color-text-muted);cursor:pointer;font-size:1rem;padding:2px 6px}
.tafsir-body{font-size:.9rem;line-height:1.9;color:var(--color-text-secondary)}
.tafsir-body :deep(h2){font-size:1rem;color:var(--color-text);margin:var(--space-md) 0 var(--space-sm)}
.tafsir-loading{display:flex;align-items:center;gap:var(--space-sm);color:var(--color-text-muted);font-size:.85rem}
.tafsir-empty{color:var(--color-text-muted);font-size:.85rem;font-style:italic}
.slide-enter-active,.slide-leave-active{transition:all .25s ease}
.slide-enter-from,.slide-leave-to{opacity:0;transform:translateY(-8px)}
@media(max-width:768px){.verse-card{padding:var(--space-md)}.verse-arabic{font-size:1.5rem!important;line-height:2.2}}
</style>
