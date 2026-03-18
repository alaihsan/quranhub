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
 * Build mushaf lines from verses.
 * Each verse's words are laid out RTL, flowing line by line.
 * We group words into lines based on approximate character width.
 */
const mushafLines = computed(() => {
  const lines = []
  let currentLine = []
  let currentLineWidth = 0
  const MAX_LINE_CHARS = store.settings.mushafLineWidth || 55 // approximate chars per line

  for (const verse of props.verses) {
    if (!verse.words) continue

    for (const word of verse.words) {
      const wordText = word.text_uthmani || word.text_indopak || ''
      const wordLen = wordText.length + 1 // +1 for space

      // If adding this word exceeds line width, start new line
      if (currentLine.length > 0 && currentLineWidth + wordLen > MAX_LINE_CHARS) {
        lines.push([...currentLine])
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
        transliteration: word.transliteration?.text,
        translation: word.translation?.text,
        code_v1: word.code_v1,
        code_v2: word.code_v2,
        lineNumber: word.line_number,
        pageNumber: word.v1_page || word.v2_page,
      })
      currentLineWidth += wordLen
    }
  }

  // Push remaining words
  if (currentLine.length > 0) {
    lines.push(currentLine)
  }

  return lines
})

/**
 * Alternative: group by actual page/line data from API
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
        code_v1: word.code_v1,
        code_v2: word.code_v2,
      })
    }
  }

  return Array.from(pageMap.values())
})

// Use API line data if available, otherwise fallback to computed lines
const displayLines = computed(() => {
  const hasLineData = props.verses.some(v =>
    v.words?.some(w => w.line_number != null)
  )

  if (hasLineData && store.settings.mushafUseApiLines !== false) {
    return mushafPageLines.value
  }

  // Fallback: wrap computed lines into the same shape
  return mushafLines.value.map((words, idx) => ({
    page: 0,
    line: idx + 1,
    words
  }))
})

// Group lines by page number
const pages = computed(() => {
  const pageGroups = new Map()
  for (const lineData of displayLines.value) {
    const pageNum = lineData.page || 0
    if (!pageGroups.has(pageNum)) {
      pageGroups.set(pageNum, [])
    }
    pageGroups.get(pageNum).push(lineData)
  }
  return Array.from(pageGroups.entries()).map(([num, lines]) => ({ number: num, lines }))
})

function saveAsLastRead(verseKey) {
  if (!verseKey) return
  const [chId, vNum] = verseKey.split(':')
  store.setLastRead({
    chapterId: chId,
    verseNumber: vNum,
    surahName: props.surahName,
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
    <div
      v-for="(page, pageIdx) in pages"
      :key="pageIdx"
      class="mushaf-page"
    >
      <div v-if="page.number > 0" class="mushaf-page-number">
        {{ page.number }}
      </div>

      <div class="mushaf-page-content">
        <div
          v-for="(lineData, lineIdx) in page.lines"
          :key="`${pageIdx}-${lineIdx}`"
          class="mushaf-line"
          :class="{ 'mushaf-line-first': lineIdx === 0, 'mushaf-line-last': lineIdx === page.lines.length - 1 }"
        >
          <span
            v-for="word in lineData.words"
            :key="word.id"
            class="mushaf-word"
            :class="{
              'mushaf-word-end': word.isEnd,
              'mushaf-word-verse': word.charType === 'word'
            }"
            :data-verse="word.verseKey"
            :title="word.isEnd ? `Ayat ${word.verseNumber}` : ''"
            @click="saveAsLastRead(word.verseKey)"
          >
            <span v-if="word.isEnd" class="verse-end-marker">
              {{ word.text }}
            </span>
            <span v-else class="word-text">{{ word.text }}</span>
          </span>
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
  max-width: 800px;
  margin: 0 auto;
  padding: var(--space-lg) var(--space-md);
}

/* Bismillah */
.mushaf-bismillah {
  text-align: center;
  font-family: var(--font-arabic-quran);
  font-size: 2rem;
  color: var(--color-text-arabic);
  padding: var(--space-xl) var(--space-lg);
  direction: rtl;
  border-bottom: 2px solid var(--color-gold);
  margin-bottom: var(--space-xl);
  background: linear-gradient(
    to bottom,
    color-mix(in srgb, var(--color-gold) 4%, transparent),
    transparent
  );
  border-radius: var(--radius-md) var(--radius-md) 0 0;
}

/* Page */
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
  top: 8px;
  left: 8px;
  right: 8px;
  bottom: 8px;
  border: 1px solid var(--color-border-gold);
  border-radius: var(--radius-md);
  pointer-events: none;
}

.mushaf-page-number {
  text-align: center;
  font-size: 0.75rem;
  color: var(--color-text-muted);
  margin-bottom: var(--space-md);
  font-weight: 500;
  letter-spacing: 0.05em;
}

.mushaf-page-content {
  padding: var(--space-sm) var(--space-md);
}

/* Line */
.mushaf-line {
  display: flex;
  flex-wrap: nowrap;
  direction: rtl;
  justify-content: center;
  align-items: baseline;
  padding: var(--space-xs) 0;
  min-height: 3.2em;
  border-bottom: 1px solid transparent;
  transition: border-color var(--transition-fast);
  line-height: 2.8;
}

.mushaf-line:not(.mushaf-line-last) {
  border-bottom-color: color-mix(in srgb, var(--color-border-light) 50%, transparent);
}

/* Justify lines - stretch words to fill width like a real mushaf */
.mushaf-line {
  justify-content: space-between;
}

/* Last line may not be full, so center it */
.mushaf-line-last {
  justify-content: center;
  gap: 0.3em;
}

/* Word */
.mushaf-word {
  font-family: var(--font-arabic-quran);
  font-size: v-bind('store.arabicFontSize');
  color: var(--color-text-arabic);
  cursor: default;
  padding: 0 0.12em;
  border-radius: 4px;
  transition: background var(--transition-fast);
  white-space: nowrap;
  user-select: text;
}

.mushaf-word:hover {
  background: color-mix(in srgb, var(--color-gold) 10%, transparent);
}

.mushaf-word-verse {
  cursor: pointer;
}

/* Verse end marker */
.verse-end-marker {
  font-family: var(--font-arabic-quran);
  font-size: 0.85em;
  color: var(--color-gold-dark);
  padding: 0 0.15em;
  display: inline-block;
}

[data-theme="dark"] .verse-end-marker {
  color: var(--color-gold);
}

/* Empty state */
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

/* ==========================================
   Ornamental frame decorations
   ========================================== */
.mushaf-page {
  position: relative;
}

/* Corner ornaments */
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

/* ==========================================
   Responsive
   ========================================== */
@media (max-width: 768px) {
  .mushaf-container {
    padding: var(--space-sm);
  }

  .mushaf-page {
    padding: var(--space-md) var(--space-sm);
    border-radius: var(--radius-md);
  }

  .mushaf-page::before {
    top: 4px;
    left: 4px;
    right: 4px;
    bottom: 4px;
  }

  .mushaf-word {
    padding: 0 0.06em;
  }

  .mushaf-line {
    line-height: 2.4;
    min-height: 2.8em;
  }

  .mushaf-bismillah {
    font-size: 1.5rem;
    padding: var(--space-lg) var(--space-md);
  }
}

@media (max-width: 480px) {
  .mushaf-page-content {
    padding: var(--space-xs);
  }

  .mushaf-line {
    line-height: 2.2;
  }
}
</style>
