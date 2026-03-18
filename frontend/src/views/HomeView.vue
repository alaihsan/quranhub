<script setup>
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useQuranStore } from '@/stores/quran'

const router = useRouter()
const store = useQuranStore()

onMounted(() => { store.fetchChapters() })

function goToSurah(id) { router.push(`/surah/${id}`) }
function goToLastRead() {
  if (store.lastRead) router.push(`/surah/${store.lastRead.chapterId}`)
}
function getRevelation(place) { return place === 'makkah' || place === 'makka' ? 'Makkiyyah' : 'Madaniyyah' }
</script>

<template>
  <div class="home">
    <!-- Hero -->
    <section class="hero">
      <div class="hero-pattern"></div>
      <div class="hero-content">
        <h1 class="hero-bismillah" translate="no">بِسْمِ ٱللَّهِ ٱلرَّحْمَـٰنِ ٱلرَّحِيمِ</h1>
        <h2 class="hero-title">Quran Hub</h2>
        <p class="hero-subtitle">Baca Al-Quran dengan tajwid berwarna, terjemah Indonesia, dan tafsir lengkap</p>
        <div class="hero-actions">
          <button v-if="store.lastRead" class="btn btn-primary" @click="goToLastRead">
            Lanjutkan Membaca — {{ store.lastRead.surahName }} : {{ store.lastRead.verseNumber }}
          </button>
          <button class="btn btn-secondary" @click="goToSurah(1)">
            Mulai dari Al-Fatihah
          </button>
        </div>
      </div>
    </section>

    <!-- Surah Grid -->
    <section class="surah-section">
      <div class="section-header">
        <h3>114 Surah</h3>
        <div class="ornament-divider"><span class="ornament">✦</span></div>
      </div>

      <div v-if="store.loading" class="loading-center">
        <div class="loading-spinner"></div>
      </div>

      <div v-else class="surah-grid">
        <div
          v-for="ch in store.chapters"
          :key="ch.id"
          class="surah-card"
          @click="goToSurah(ch.id)"
        >
          <div class="card-number">{{ ch.id }}</div>
          <div class="card-body">
            <div class="card-row">
              <span class="card-latin">{{ ch.name_simple }}</span>
              <span class="card-arabic" translate="no">{{ ch.name_arabic }}</span>
            </div>
            <div class="card-meta">
              {{ getRevelation(ch.revelation_place) }} · {{ ch.verses_count }} Ayat
            </div>
            <div class="card-meaning">{{ ch.translated_name?.name }}</div>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<style scoped>
.home { padding-bottom: var(--space-3xl); }

/* Hero */
.hero {
  position: relative;
  padding: var(--space-3xl) var(--space-xl);
  text-align: center;
  overflow: hidden;
  background: linear-gradient(160deg, var(--color-primary-dark) 0%, var(--color-primary) 50%, var(--color-primary-light) 100%);
  color: white;
}

.hero-pattern {
  position: absolute;
  inset: 0;
  opacity: 0.06;
  background-image: url("data:image/svg+xml,%3Csvg width='80' height='80' viewBox='0 0 80 80' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='%23ffffff' fill-opacity='1'%3E%3Cpath d='M40 0l40 40-40 40L0 40z' fill='none' stroke='%23fff' stroke-width='1'/%3E%3C/g%3E%3C/svg%3E");
}

.hero-content { position: relative; z-index: 1; max-width: 640px; margin: 0 auto; }
.hero-bismillah { font-family: var(--font-arabic-quran); font-size: 2.5rem; font-weight: 400; margin-bottom: var(--space-lg); opacity: 0.9; direction: rtl; animation: fadeIn .8s ease; }
.hero-title { font-size: 2rem; font-weight: 700; letter-spacing: -0.02em; margin-bottom: var(--space-sm); animation: fadeIn .8s ease .1s both; }
.hero-subtitle { font-size: 1rem; opacity: 0.8; margin-bottom: var(--space-xl); animation: fadeIn .8s ease .2s both; }

.hero-actions { display: flex; gap: var(--space-md); justify-content: center; flex-wrap: wrap; animation: fadeIn .8s ease .3s both; }

.btn {
  padding: var(--space-sm) var(--space-xl);
  border: none;
  border-radius: var(--radius-lg);
  font-family: var(--font-body);
  font-size: 0.9rem;
  font-weight: 600;
  cursor: pointer;
  transition: all var(--transition-fast);
}

.btn-primary { background: white; color: var(--color-primary-dark); }
.btn-primary:hover { transform: translateY(-1px); box-shadow: 0 4px 16px rgba(0,0,0,0.2); }
.btn-secondary { background: rgba(255,255,255,0.15); color: white; border: 1px solid rgba(255,255,255,0.3); }
.btn-secondary:hover { background: rgba(255,255,255,0.25); }

/* Section */
.surah-section { padding: var(--space-xl) var(--space-xl); max-width: 1100px; margin: 0 auto; }
.section-header h3 { font-size: 1.3rem; font-weight: 700; color: var(--color-text); text-align: center; }

.loading-center { display: flex; justify-content: center; padding: var(--space-3xl); }

/* Grid */
.surah-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: var(--space-md);
}

.surah-card {
  display: flex;
  gap: var(--space-md);
  padding: var(--space-md) var(--space-lg);
  background: var(--color-bg-card);
  border: 1px solid var(--color-border-light);
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.surah-card:hover {
  border-color: var(--color-gold);
  box-shadow: var(--shadow-md);
  transform: translateY(-1px);
}

.card-number {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: color-mix(in srgb, var(--color-primary) 8%, transparent);
  color: var(--color-primary);
  font-weight: 700;
  font-size: 0.85rem;
  border-radius: var(--radius-sm);
  flex-shrink: 0;
}

.card-body { flex: 1; min-width: 0; }
.card-row { display: flex; justify-content: space-between; align-items: center; gap: var(--space-sm); }
.card-latin { font-weight: 600; font-size: 0.95rem; color: var(--color-text); }
.card-arabic { font-family: var(--font-arabic); font-size: 1.2rem; color: var(--color-text-arabic); direction: rtl; }
.card-meta { font-size: 0.75rem; color: var(--color-text-muted); margin-top: 2px; }
.card-meaning { font-size: 0.8rem; color: var(--color-text-secondary); margin-top: 2px; }

@media (max-width: 768px) {
  .hero { padding: var(--space-xl) var(--space-md); }
  .hero-bismillah { font-size: 1.8rem; }
  .hero-title { font-size: 1.5rem; }
  .surah-section { padding: var(--space-lg) var(--space-md); }
  .surah-grid { grid-template-columns: 1fr; }
}
</style>
