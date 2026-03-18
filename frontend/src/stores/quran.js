import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import axios from 'axios'

const api = axios.create({ baseURL: '/api' })

export const useQuranStore = defineStore('quran', () => {
  // State
  const chapters = ref([])
  const currentVerses = ref([])
  const currentPage = ref(1)
  const pagination = ref(null)
  const loading = ref(false)
  const error = ref(null)

  // Settings
  const settings = ref({
    translationId: '33', // Indonesian - Kemenag
    tafsirId: '816',     // Tafsir Ringkas Kemenag (Indonesian)
    showTranslation: true,
    showTafsir: false,
    showWordByWord: false,
    showTajweed: true,
    fontSize: 'medium',    // small, medium, large, xlarge
    theme: 'light',        // light, dark
    displayMode: 'surah',  // surah, page, juz
  })

  // Load settings from localStorage
  const savedSettings = localStorage.getItem('quran-hub-settings')
  if (savedSettings) {
    try {
      Object.assign(settings.value, JSON.parse(savedSettings))
    } catch (e) { /* ignore */ }
  }

  // Watch and save settings
  function updateSettings(newSettings) {
    Object.assign(settings.value, newSettings)
    localStorage.setItem('quran-hub-settings', JSON.stringify(settings.value))
    // Apply theme
    document.documentElement.setAttribute('data-theme', settings.value.theme)
  }

  // Font size mapping
  const fontSizeMap = computed(() => ({
    small: '1.5rem',
    medium: '1.75rem',
    large: '2.25rem',
    xlarge: '2.75rem'
  }))

  const arabicFontSize = computed(() => fontSizeMap.value[settings.value.fontSize] || '1.75rem')

  // Actions
  async function fetchChapters() {
    if (chapters.value.length > 0) return
    loading.value = true
    error.value = null
    try {
      const { data } = await api.get('/chapters', { params: { language: 'id' } })
      chapters.value = data.chapters
    } catch (e) {
      error.value = 'Gagal memuat daftar surah'
      console.error(e)
    } finally {
      loading.value = false
    }
  }

  async function fetchVersesByChapter(chapterId, page = 1) {
    loading.value = true
    error.value = null
    try {
      const params = {
        language: 'id',
        words: settings.value.showWordByWord ? 'true' : 'false',
        translations: settings.value.translationId,
        fields: settings.value.showTajweed
          ? 'text_uthmani,text_uthmani_tajweed'
          : 'text_uthmani',
        per_page: 50,
        page
      }
      if (settings.value.showTafsir && settings.value.tafsirId) {
        params.tafsirs = settings.value.tafsirId
      }
      const { data } = await api.get(`/verses/by_chapter/${chapterId}`, { params })
      if (page === 1) {
        currentVerses.value = data.verses
      } else {
        currentVerses.value = [...currentVerses.value, ...data.verses]
      }
      pagination.value = data.pagination
    } catch (e) {
      error.value = 'Gagal memuat ayat'
      console.error(e)
    } finally {
      loading.value = false
    }
  }

  async function fetchVersesByPage(pageNumber) {
    loading.value = true
    error.value = null
    try {
      const params = {
        language: 'id',
        words: 'true',
        translations: settings.value.translationId,
        fields: settings.value.showTajweed
          ? 'text_uthmani,text_uthmani_tajweed'
          : 'text_uthmani',
        per_page: 50
      }
      if (settings.value.showTafsir && settings.value.tafsirId) {
        params.tafsirs = settings.value.tafsirId
      }
      const { data } = await api.get(`/verses/by_page/${pageNumber}`, { params })
      currentVerses.value = data.verses
      pagination.value = data.pagination
      currentPage.value = pageNumber
    } catch (e) {
      error.value = 'Gagal memuat halaman'
      console.error(e)
    } finally {
      loading.value = false
    }
  }

  async function fetchTafsir(tafsirId, verseKey) {
    try {
      const { data } = await api.get(`/tafsirs/${tafsirId}/by_ayah/${verseKey}`)
      return data
    } catch (e) {
      console.error(e)
      return null
    }
  }

  // Bookmarks
  const bookmarks = ref(JSON.parse(localStorage.getItem('quran-hub-bookmarks') || '[]'))

  function addBookmark(verseKey, surahName) {
    const bm = { verseKey, surahName, timestamp: Date.now() }
    bookmarks.value.push(bm)
    localStorage.setItem('quran-hub-bookmarks', JSON.stringify(bookmarks.value))
  }

  function removeBookmark(verseKey) {
    bookmarks.value = bookmarks.value.filter(b => b.verseKey !== verseKey)
    localStorage.setItem('quran-hub-bookmarks', JSON.stringify(bookmarks.value))
  }

  function isBookmarked(verseKey) {
    return bookmarks.value.some(b => b.verseKey === verseKey)
  }

  // Last read
  const lastRead = ref(JSON.parse(localStorage.getItem('quran-hub-lastread') || 'null'))

  function setLastRead(data) {
    lastRead.value = { ...data, timestamp: Date.now() }
    localStorage.setItem('quran-hub-lastread', JSON.stringify(lastRead.value))
  }

  return {
    chapters, currentVerses, currentPage, pagination,
    loading, error, settings, arabicFontSize,
    bookmarks, lastRead,
    fetchChapters, fetchVersesByChapter, fetchVersesByPage, fetchTafsir,
    updateSettings, addBookmark, removeBookmark, isBookmarked, setLastRead
  }
})
