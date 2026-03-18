<script setup>
import { reactive, watch } from 'vue'
import { useQuranStore } from '@/stores/quran'

const store = useQuranStore()
const form = reactive({ ...store.settings })

watch(form, (newVal) => {
  store.updateSettings({ ...newVal })
}, { deep: true })

const fontSizes = [
  { value: 'small', label: 'Kecil', preview: '1.5rem' },
  { value: 'medium', label: 'Sedang', preview: '1.75rem' },
  { value: 'large', label: 'Besar', preview: '2.25rem' },
  { value: 'xlarge', label: 'Sangat Besar', preview: '2.75rem' },
]

const translations = [
  { id: '33', name: 'Kemenag RI' },
  { id: '134', name: 'King Fahad Quran Complex (Indonesia)' },
  { id: '20', name: 'Sahih International (English)' },
  { id: '131', name: 'Dr. Mustafa Khattab (English)' },
]

const tafsirs = [
  { id: '816', name: 'Tafsir Ringkas Kemenag' },
  { id: '169', name: 'Tafsir Al-Muyassar (Arabic)' },
  { id: '164', name: 'Tafsir Ibn Kathir (English)' },
]
</script>

<template>
  <div class="settings-view">
    <div class="settings-container">
      <h1 class="settings-title">Pengaturan</h1>

      <!-- Display -->
      <section class="settings-section">
        <h2 class="section-title">Tampilan</h2>

        <div class="setting-row">
          <div class="setting-info">
            <span class="setting-label">Tema</span>
            <span class="setting-desc">Sesuaikan tampilan terang atau gelap</span>
          </div>
          <div class="toggle-group">
            <button :class="['toggle-btn', { active: form.theme === 'light' }]" @click="form.theme = 'light'">☀ Terang</button>
            <button :class="['toggle-btn', { active: form.theme === 'dark' }]" @click="form.theme = 'dark'">🌙 Gelap</button>
          </div>
        </div>

        <div class="setting-row">
          <div class="setting-info">
            <span class="setting-label">Ukuran Font Arab</span>
            <span class="setting-desc">Atur ukuran teks Al-Quran</span>
          </div>
          <div class="font-size-options">
            <button
              v-for="fs in fontSizes" :key="fs.value"
              :class="['font-btn', { active: form.fontSize === fs.value }]"
              @click="form.fontSize = fs.value"
            >
              {{ fs.label }}
            </button>
          </div>
        </div>

        <div class="setting-row preview-row">
          <p class="preview-label">Preview:</p>
          <p class="preview-text" :style="{ fontSize: store.arabicFontSize }" translate="no">
            بِسْمِ ٱللَّهِ ٱلرَّحْمَـٰنِ ٱلرَّحِيمِ
          </p>
        </div>
      </section>

      <!-- Content -->
      <section class="settings-section">
        <h2 class="section-title">Konten</h2>

        <div class="setting-row">
          <div class="setting-info">
            <span class="setting-label">Tajwid Berwarna</span>
            <span class="setting-desc">Tampilkan warna tajwid pada teks Arab</span>
          </div>
          <label class="switch">
            <input type="checkbox" v-model="form.showTajweed" />
            <span class="slider"></span>
          </label>
        </div>

        <div class="setting-row">
          <div class="setting-info">
            <span class="setting-label">Terjemahan</span>
            <span class="setting-desc">Tampilkan terjemahan per ayat</span>
          </div>
          <label class="switch">
            <input type="checkbox" v-model="form.showTranslation" />
            <span class="slider"></span>
          </label>
        </div>

        <div v-if="form.showTranslation" class="setting-row sub">
          <div class="setting-info">
            <span class="setting-label">Sumber Terjemahan</span>
          </div>
          <select v-model="form.translationId" class="setting-select">
            <option v-for="t in translations" :key="t.id" :value="t.id">{{ t.name }}</option>
          </select>
        </div>

        <div class="setting-row">
          <div class="setting-info">
            <span class="setting-label">Per Kata (Word by Word)</span>
            <span class="setting-desc">Tampilkan terjemahan dan transliterasi per kata</span>
          </div>
          <label class="switch">
            <input type="checkbox" v-model="form.showWordByWord" />
            <span class="slider"></span>
          </label>
        </div>

        <div class="setting-row">
          <div class="setting-info">
            <span class="setting-label">Tafsir</span>
            <span class="setting-desc">Muat tafsir bersama ayat</span>
          </div>
          <label class="switch">
            <input type="checkbox" v-model="form.showTafsir" />
            <span class="slider"></span>
          </label>
        </div>

        <div v-if="form.showTafsir" class="setting-row sub">
          <div class="setting-info">
            <span class="setting-label">Sumber Tafsir</span>
          </div>
          <select v-model="form.tafsirId" class="setting-select">
            <option v-for="t in tafsirs" :key="t.id" :value="t.id">{{ t.name }}</option>
          </select>
        </div>
      </section>

      <!-- Tajweed Legend -->
      <section class="settings-section">
        <h2 class="section-title">Legenda Tajwid</h2>
        <div class="tajweed-legend">
          <div class="legend-item"><span class="legend-color" style="background:var(--tajweed-ghunnah)"></span> Ghunnah</div>
          <div class="legend-item"><span class="legend-color" style="background:var(--tajweed-ikhfa)"></span> Ikhfa</div>
          <div class="legend-item"><span class="legend-color" style="background:var(--tajweed-idgham)"></span> Idgham</div>
          <div class="legend-item"><span class="legend-color" style="background:var(--tajweed-iqlab)"></span> Iqlab</div>
          <div class="legend-item"><span class="legend-color" style="background:var(--tajweed-qalqala)"></span> Qalqalah</div>
          <div class="legend-item"><span class="legend-color" style="background:var(--tajweed-madd-normal)"></span> Madd Normal</div>
          <div class="legend-item"><span class="legend-color" style="background:var(--tajweed-madd-permissible)"></span> Madd Ja'iz</div>
          <div class="legend-item"><span class="legend-color" style="background:var(--tajweed-madd-obligatory)"></span> Madd Lazim</div>
          <div class="legend-item"><span class="legend-color" style="background:var(--tajweed-laam-shamsiyah)"></span> Laam Shamsiyah</div>
          <div class="legend-item"><span class="legend-color" style="background:var(--tajweed-ham-wasl)"></span> Hamzah Wasl</div>
        </div>
      </section>

      <!-- About -->
      <section class="settings-section">
        <h2 class="section-title">Tentang</h2>
        <div class="about-info">
          <p><strong>Quran Hub</strong> v1.0.0</p>
          <p>Aplikasi Al-Quran digital dengan tajwid berwarna, terjemah Indonesia, tafsir, dan tampilan per kata.</p>
          <p class="about-credit">Data Al-Quran disediakan oleh <a href="https://quran.com" target="_blank" rel="noopener">Quran.com</a> (Quran Foundation API)</p>
        </div>
      </section>
    </div>
  </div>
</template>

<style scoped>
.settings-view{padding:var(--space-xl);min-height:100%}
.settings-container{max-width:680px;margin:0 auto}
.settings-title{font-size:1.5rem;font-weight:700;margin-bottom:var(--space-xl);color:var(--color-text)}
.settings-section{margin-bottom:var(--space-2xl);background:var(--color-bg-card);border:1px solid var(--color-border-light);border-radius:var(--radius-lg);padding:var(--space-lg);box-shadow:var(--shadow-sm)}
.section-title{font-size:1rem;font-weight:700;color:var(--color-primary);margin-bottom:var(--space-lg);padding-bottom:var(--space-sm);border-bottom:1px solid var(--color-border-light)}

.setting-row{display:flex;align-items:center;justify-content:space-between;padding:var(--space-sm) 0;gap:var(--space-md)}
.setting-row.sub{padding-left:var(--space-lg);opacity:.9}
.setting-row + .setting-row{border-top:1px solid var(--color-border-light)}
.setting-info{flex:1}.setting-label{font-weight:600;font-size:.9rem;color:var(--color-text);display:block}
.setting-desc{font-size:.8rem;color:var(--color-text-muted)}

/* Toggle group */
.toggle-group{display:flex;border:1px solid var(--color-border);border-radius:var(--radius-md);overflow:hidden}
.toggle-btn{padding:var(--space-xs) var(--space-md);border:none;background:none;font-family:var(--font-body);font-size:.8rem;cursor:pointer;color:var(--color-text-muted);transition:all var(--transition-fast)}
.toggle-btn.active{background:var(--color-primary);color:white}

/* Font size */
.font-size-options{display:flex;gap:var(--space-xs);flex-wrap:wrap}
.font-btn{padding:var(--space-xs) var(--space-sm);border:1px solid var(--color-border);background:var(--color-bg-card);border-radius:var(--radius-sm);font-family:var(--font-body);font-size:.8rem;cursor:pointer;color:var(--color-text);transition:all var(--transition-fast)}
.font-btn.active{background:var(--color-primary);color:white;border-color:var(--color-primary)}
.font-btn:hover:not(.active){border-color:var(--color-primary)}

/* Preview */
.preview-row{flex-direction:column;align-items:stretch}
.preview-label{font-size:.8rem;color:var(--color-text-muted);margin-bottom:var(--space-xs)}
.preview-text{font-family:var(--font-arabic-quran);direction:rtl;text-align:center;color:var(--color-text-arabic);line-height:2.2;padding:var(--space-md);background:var(--color-parchment);border-radius:var(--radius-md)}

/* Switch */
.switch{position:relative;display:inline-block;width:48px;height:26px;flex-shrink:0}
.switch input{opacity:0;width:0;height:0}
.slider{position:absolute;cursor:pointer;inset:0;background:var(--color-border);transition:.3s;border-radius:26px}
.slider::before{content:'';position:absolute;height:20px;width:20px;left:3px;bottom:3px;background:white;transition:.3s;border-radius:50%}
.switch input:checked + .slider{background:var(--color-primary)}
.switch input:checked + .slider::before{transform:translateX(22px)}

/* Select */
.setting-select{padding:var(--space-xs) var(--space-sm);border:1px solid var(--color-border);border-radius:var(--radius-sm);font-family:var(--font-body);font-size:.85rem;color:var(--color-text);background:var(--color-bg-card);outline:none;min-width:200px}

/* Tajweed legend */
.tajweed-legend{display:grid;grid-template-columns:repeat(auto-fill,minmax(180px,1fr));gap:var(--space-sm)}
.legend-item{display:flex;align-items:center;gap:var(--space-sm);font-size:.85rem;color:var(--color-text-secondary)}
.legend-color{width:16px;height:16px;border-radius:4px;flex-shrink:0}

/* About */
.about-info{font-size:.9rem;line-height:1.8;color:var(--color-text-secondary)}
.about-info p+p{margin-top:var(--space-xs)}
.about-credit{margin-top:var(--space-md);font-size:.8rem}
.about-credit a{color:var(--color-primary);text-decoration:none}
.about-credit a:hover{text-decoration:underline}

@media(max-width:768px){
  .settings-view{padding:var(--space-md)}
  .setting-row{flex-direction:column;align-items:flex-start}
  .font-size-options{margin-top:var(--space-sm)}
  .toggle-group{margin-top:var(--space-sm)}
  .setting-select{width:100%;margin-top:var(--space-sm)}
}
</style>
