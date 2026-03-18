<script setup>
import { computed } from 'vue'
import { useQuranStore } from '@/stores/quran'

const props = defineProps({
  verses: { type: Array, required: true },
  surahName: { type: String, default: '' },
  chapterId: { type: Number, default: 0 },
  showBismillah: { type: Boolean, default: true }
})

const store = useQuranStore()

/**
 * Group by actual page/line data from API (mushaf positioning)
 */
const mushafPageLines = computed(() => {
  const pageMap = new Map()

  for (const verse of props.verses) {
    if (!verse.words) continue
    for (const word of verse.words) {
      const page = word.v1_page || word.v2_page || 1
      const line = word.line_number || 1
      const key = `${page}-${line}`

      if (!pageMap.has(key)) {
        pageMap.set(key, { page, line, words: [] })
      }

      pageMap.get(key).words.push({
        id: word.id,
        text: word.text_uthmani || word.text_indopak || '',
        charType: word.char_type_name,
        verseKey: verse.verse_key,
        verseNumber: verse.verse_key?.split(':')[1],
        isEnd: word.char_type_name === 'end',
      })
    }
  }

  return Array.from(pageMap.values())
})

/**
 * Fallback: build lines from character width estimation
 */
const mushafFallbackLines = computed(() => {
  const lines = []
  let currentLine = []
  let currentLineWidth = 0
  const MAX = 55

  for (const verse of props.verses) {
    if (!verse.words) continue
    for (const word of verse.words) {
      const wordText = word.text_uthmani || word.text_indopak || ''
      const wordLen = wordText.length + 1

      if (currentLine.length > 0 && currentLineWidth + wordLen > MAX) {
        lines.push({ page: 0, line: lines.length + 1, words: [...currentLine] })
        currentLine = []
        currentLineWidth = 0
      }

      currentLine.push({
        id: word.id,
        text: wordText,
        charType: word.char_type_name,
        verseKey: verse.verse_key,
        verseNumber: verse.verse_key?.split(':')[1],
        isEnd: word.char_type_name === 'end',
      })
      currentLineWidth += wordLen
    }
  }
  if (currentLine.length > 0) {
    lines.push({ page: 0, line: lines.length + 1, words: currentLine })
  }
  return lines
})

const displayLines = computed(() => {
  const hasLineData = props.verses.some(v =>
    v.words?.some(w => w.line_number != null)
  )
  return hasLineData ? mushafPageLines.value : mushafFallbackLines.value
})

// Group lines by page
const pages = computed(() => {
  const groups = new Map()
  for (const lineData of displayLines.value) {
    const p = lineData.page || 0
    if (!groups.has(p)) groups.set(p, [])
    groups.get(p).push(lineData)
  }
  return Array.from(groups.entries()).map(([num, lines]) => ({ number: num, lines }))
})

function saveAsLastRead(verseKey) {
  if (!verseKey) return
  const [chId, vNum] = verseKey.split(':')
  const ch = store.chapters.find(c => c.id === Number(chId))
  store.setLastRead({
    chapterId: chId,
    verseNumber: vNum,
    surahName: ch?.name_simple || props.surahName,
    verseKey
  })
}
</script>

<template>
  <div class="mushaf-container">
    <!-- Bismillah -->
    <div v-if="showBismillah" class="mushaf-bismillah" translate="no">
      بِسْمِ ٱللَّهِ ٱلرَّحْمَـٰنِ ٱلرَّحِيمِ
    </div>

    <!-- Mushaf Pages -->
    <div v-for="(page, pageIdx) in pages" :key="pageIdx" class="mushaf-page">
      <div v-if="page.number > 0" class="mushaf-page-number">
        صفحة {{ page.number }}
      </div>

      <div class="mushaf-page-content">
        <div
          v-for="(lineData, lineIdx) in page.lines"
          :key="`${pageIdx}-${lineIdx}`"
          class="mushaf-line"
          :class="{
            'mushaf-line-last': lineIdx === page.lines.length - 1
          }"
        >
          <!-- Render all words as continuous flowing Arabic text -->
          <template v-for="word in lineData.words" :key="word.id">
            <span
              v-if="word.isEnd"
              class="verse-end-marker"
              :title="`Ayat ${word.verseNumber}`"
              @click="saveAsLastRead(word.verseKey)"
            >{{ word.text }}</span>
            <span
              v-else
              class="mushaf-word"
              :data-verse="word.verseKey"
              @click="saveAsLastRead(word.verseKey)"
            >{{ word.text }}</span>
          </template>
        </div>
      </div>
    </div>

    <!-- Empty state -->
    <div v-if="verses.length === 0 || displayLines.length === 0" class="mushaf-empty">
      <p>Memuat tampilan mushaf...</p>
      <p class="mushaf-empty-hint">Mode mushaf memerlukan data per-kata (word by word).</p>
    </div>
  </div>
</template>

<style scoped>
.mushaf-container {
  max-width: 780px;
  margin: 0 auto;
  padding: var(--space-lg) var(--space-md);
}

/* ── Bismillah ── */
.mushaf-bismillah {
  text-align: center;
  font-family: var(--font-arabic-quran);
  font-size: 2rem;
  color: var(--color-text-arabic);
  padding: var(--space-xl) var(--space-lg);
  direction: rtl;
  border-bottom: 2px solid var(--color-gold);
  margin-bottom: var(--space-xl);
  background: linear-gradient(to bottom, color-mix(in srgb, var(--color-gold) 4%, transparent), transparent);
  border-radius: var(--radius-md) var(--radius-md) 0 0;
}

/* ── Page Frame ── */
.mushaf-page {
  position: relative;
  margin-bottom: var(--space-xl);
  padding: var(--space-xl) var(--space-lg);
  background: var(--color-bg-card);
  border: 1px solid var(--color-border-light);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-card);
}

.mushaf-page::before {
  content: '';
  position: absolute;
  top: 8px; left: 8px; right: 8px; bottom: 8px;
  border: 1px solid var(--color-border-gold);
  border-radius: var(--radius-md);
  pointer-events: none;
}

.mushaf-page::after {
  content: '❊';
  position: absolute;
  top: -4px;
  left: 50%;
  transform: translateX(-50%);
  color: var(--color-gold);
  font-size: 0.9rem;
  background: var(--color-bg-card);
  padding: 0 var(--space-sm);
  opacity: 0.5;
}

.mushaf-page-number {
  text-align: center;
  font-size: 0.8rem;
  color: var(--color-gold-dark);
  margin-bottom: var(--space-md);
  font-family: var(--font-arabic);
  direction: rtl;
}

.mushaf-page-content {
  padding: var(--space-xs) var(--space-sm);
}

/* ── Line — the key: continuous text, no word gaps ── */
.mushaf-line {
  direction: rtl;
  text-align: justify;
  text-align-last: justify; /* force justify on every line */
  font-family: var(--font-arabic-quran);
  font-size: v-bind('store.arabicFontSize');
  color: var(--color-text-arabic);
  line-height: 2.6;
  min-height: 2em;
  padding: 2px 0;
  border-bottom: 1px solid color-mix(in srgb, var(--color-border-light) 40%, transparent);
  /* Continuous text — no flex, no gaps, just inline flow */
  word-spacing: 0;
  letter-spacing: 0;
}

/* Last line of a page: center, don't force justify */
.mushaf-line-last {
  text-align-last: center;
}

.mushaf-line:last-child {
  border-bottom: none;
}

/* ── Word — inline, no padding, no gaps ── */
.mushaf-word {
  cursor: pointer;
  border-radius: 3px;
  transition: background 0.15s ease;
  /* no padding, no margin — text flows naturally like real mushaf */
}

.mushaf-word:hover {
  background: color-mix(in srgb, var(--color-gold) 12%, transparent);
}

/* ── Verse End Marker ── */
.verse-end-marker {
  display: inline;
  font-size: 0.8em;
  color: var(--color-gold-dark);
  cursor: pointer;
  padding: 0 0.05em;
  vertical-align: baseline;
}

[data-theme="dark"] .verse-end-marker {
  color: var(--color-gold);
}

/* ── Empty ── */
.mushaf-empty {
  text-align: center;
  padding: var(--space-3xl);
  color: var(--color-text-muted);
}
.mushaf-empty-hint {
  font-size: 0.85rem;
  margin-top: var(--space-sm);
  opacity: 0.7;
}

/* ── Responsive ── */
@media (max-width: 768px) {
  .mushaf-container { padding: var(--space-sm); }
  .mushaf-page { padding: var(--space-md) var(--space-sm); border-radius: var(--radius-md); }
  .mushaf-page::before { top: 4px; left: 4px; right: 4px; bottom: 4px; }
  .mushaf-line { line-height: 2.3; }
  .mushaf-bismillah { font-size: 1.5rem; padding: var(--space-lg) var(--space-md); }
}

@media (max-width: 480px) {
  .mushaf-page-content { padding: 0 var(--space-xs); }
  .mushaf-line { line-height: 2.1; }
}
</style>
