# Quran Hub

Aplikasi Al-Quran berbasis web full-stack dengan tajwid berwarna, terjemah Indonesia, tafsir, dan tampilan per kata (word-by-word).

## Tech Stack
- Frontend: Vue 3 + Vite + Pinia + Vue Router
- Backend: Flask (Python) + Flask-CORS
- API: Quran Foundation API (quran.com)

## Quick Start

### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app.py
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

Buka http://localhost:5173

## API Credentials (Opsional)
Tanpa kredensial, aplikasi menggunakan legacy API. Untuk OAuth2:
1. Daftar di https://api-docs.quran.foundation/request-access
2. Copy backend/.env.example ke backend/.env
3. Isi QF_CLIENT_ID dan QF_CLIENT_SECRET
