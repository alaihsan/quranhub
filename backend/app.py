"""
Quran Hub - Flask Backend
Proxy server for Quran Foundation API with caching
"""
import os
import time
import threading
import requests
from flask import Flask, jsonify, request
from flask_cors import CORS
from functools import lru_cache
import json
import hashlib

app = Flask(__name__)
CORS(app, origins=["http://localhost:5173", "http://localhost:3000", "http://127.0.0.1:5173"])

# =============================================================================
# Configuration
# =============================================================================
QF_CLIENT_ID = os.getenv("QF_CLIENT_ID", "")
QF_CLIENT_SECRET = os.getenv("QF_CLIENT_SECRET", "")
QF_ENV = os.getenv("QF_ENV", "production")

ENV_CONFIG = {
    "prelive": {
        "auth_base_url": "https://prelive-oauth2.quran.foundation",
        "api_base_url": "https://apis-prelive.quran.foundation",
    },
    "production": {
        "auth_base_url": "https://oauth2.quran.foundation",
        "api_base_url": "https://apis.quran.foundation",
    },
}

# Fallback to legacy API if no credentials
LEGACY_API_BASE = "https://api.quran.com"
USE_LEGACY = not (QF_CLIENT_ID and QF_CLIENT_SECRET)

# =============================================================================
# Token Management (OAuth2 Client Credentials)
# =============================================================================
_token_cache = {"token": None, "expires_at": 0}
_token_lock = threading.Lock()
BUFFER_SECONDS = 30


def get_access_token():
    if USE_LEGACY:
        return None

    if _token_cache["token"] and time.time() < _token_cache["expires_at"] - BUFFER_SECONDS:
        return _token_cache["token"]

    with _token_lock:
        if _token_cache["token"] and time.time() < _token_cache["expires_at"] - BUFFER_SECONDS:
            return _token_cache["token"]

        config = ENV_CONFIG[QF_ENV]
        response = requests.post(
            f"{config['auth_base_url']}/oauth2/token",
            auth=(QF_CLIENT_ID, QF_CLIENT_SECRET),
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            data="grant_type=client_credentials&scope=content",
            timeout=10,
        )
        response.raise_for_status()
        data = response.json()

        _token_cache["token"] = data["access_token"]
        _token_cache["expires_at"] = time.time() + data["expires_in"]
        return _token_cache["token"]


# =============================================================================
# API Client
# =============================================================================
# Simple in-memory cache
_api_cache = {}
_cache_lock = threading.Lock()
CACHE_TTL = 3600  # 1 hour


def call_quran_api(endpoint, params=None):
    """Call Quran API with caching"""
    cache_key = hashlib.md5(f"{endpoint}:{json.dumps(params or {}, sort_keys=True)}".encode()).hexdigest()

    with _cache_lock:
        if cache_key in _api_cache:
            cached = _api_cache[cache_key]
            if time.time() < cached["expires_at"]:
                return cached["data"]

    if USE_LEGACY:
        url = f"{LEGACY_API_BASE}{endpoint}"
        headers = {}
    else:
        config = ENV_CONFIG[QF_ENV]
        url = f"{config['api_base_url']}/content{endpoint}"
        token = get_access_token()
        headers = {
            "x-auth-token": token,
            "x-client-id": QF_CLIENT_ID,
        }

    response = requests.get(url, headers=headers, params=params, timeout=15)

    # Retry on 401
    if response.status_code == 401 and not USE_LEGACY:
        _token_cache["token"] = None
        token = get_access_token()
        headers["x-auth-token"] = token
        response = requests.get(url, headers=headers, params=params, timeout=15)

    response.raise_for_status()
    data = response.json()

    with _cache_lock:
        _api_cache[cache_key] = {"data": data, "expires_at": time.time() + CACHE_TTL}

    return data


# =============================================================================
# API Routes
# =============================================================================

@app.route("/api/chapters", methods=["GET"])
def get_chapters():
    """Get all 114 surahs"""
    language = request.args.get("language", "id")
    data = call_quran_api("/api/v4/chapters", {"language": language})
    return jsonify(data)


@app.route("/api/chapters/<int:chapter_id>", methods=["GET"])
def get_chapter(chapter_id):
    """Get single chapter info"""
    language = request.args.get("language", "id")
    data = call_quran_api(f"/api/v4/chapters/{chapter_id}", {"language": language})
    return jsonify(data)


@app.route("/api/verses/by_chapter/<int:chapter_id>", methods=["GET"])
def get_verses_by_chapter(chapter_id):
    """Get verses by chapter with translations, words, tafsir"""
    params = {
        "language": request.args.get("language", "id"),
        "words": request.args.get("words", "true"),
        "translations": request.args.get("translations", "33"),  # 33 = Indonesian translation
        "fields": request.args.get("fields", "text_uthmani,text_uthmani_tajweed,text_indopak"),
        "word_fields": request.args.get("word_fields", "text_uthmani,text_indopak,code_v1,code_v2,v1_page,v2_page,line_number"),
        "per_page": request.args.get("per_page", "50"),
        "page": request.args.get("page", "1"),
    }
    tafsirs = request.args.get("tafsirs", "")
    if tafsirs:
        params["tafsirs"] = tafsirs
    data = call_quran_api(f"/api/v4/verses/by_chapter/{chapter_id}", params)
    return jsonify(data)


@app.route("/api/verses/by_page/<int:page_number>", methods=["GET"])
def get_verses_by_page(page_number):
    """Get verses by mushaf page number (1-604)"""
    params = {
        "language": request.args.get("language", "id"),
        "words": request.args.get("words", "true"),
        "translations": request.args.get("translations", "33"),
        "fields": request.args.get("fields", "text_uthmani,text_uthmani_tajweed,text_indopak"),
        "word_fields": request.args.get("word_fields", "text_uthmani,text_indopak,code_v1,code_v2,v1_page,v2_page,line_number"),
        "per_page": "50",
    }
    tafsirs = request.args.get("tafsirs", "")
    if tafsirs:
        params["tafsirs"] = tafsirs
    data = call_quran_api(f"/api/v4/verses/by_page/{page_number}", params)
    return jsonify(data)


@app.route("/api/verses/by_juz/<int:juz_number>", methods=["GET"])
def get_verses_by_juz(juz_number):
    """Get verses by juz number"""
    params = {
        "language": request.args.get("language", "id"),
        "words": request.args.get("words", "true"),
        "translations": request.args.get("translations", "33"),
        "fields": request.args.get("fields", "text_uthmani,text_uthmani_tajweed"),
        "per_page": request.args.get("per_page", "50"),
        "page": request.args.get("page", "1"),
    }
    data = call_quran_api(f"/api/v4/verses/by_juz/{juz_number}", params)
    return jsonify(data)


@app.route("/api/quran/verses/uthmani_tajweed", methods=["GET"])
def get_uthmani_tajweed():
    """Get Uthmani tajweed text"""
    params = {
        "chapter_number": request.args.get("chapter_number", "1"),
    }
    data = call_quran_api("/api/v4/quran/verses/uthmani_tajweed", params)
    return jsonify(data)


@app.route("/api/tafsirs/<int:tafsir_id>/by_ayah/<path:verse_key>", methods=["GET"])
def get_tafsir(tafsir_id, verse_key):
    """Get tafsir for a specific verse"""
    data = call_quran_api(f"/api/v4/tafsirs/{tafsir_id}/by_ayah/{verse_key}")
    return jsonify(data)


@app.route("/api/resources/translations", methods=["GET"])
def get_translations():
    """Get available translations"""
    language = request.args.get("language", "id")
    data = call_quran_api("/api/v4/resources/translations", {"language": language})
    return jsonify(data)


@app.route("/api/resources/tafsirs", methods=["GET"])
def get_tafsirs():
    """Get available tafsirs"""
    language = request.args.get("language", "id")
    data = call_quran_api("/api/v4/resources/tafsirs", {"language": language})
    return jsonify(data)


@app.route("/api/resources/languages", methods=["GET"])
def get_languages():
    """Get available languages"""
    data = call_quran_api("/api/v4/resources/languages")
    return jsonify(data)


@app.route("/api/juzs", methods=["GET"])
def get_juzs():
    """Get all juzs"""
    data = call_quran_api("/api/v4/juzs")
    return jsonify(data)


@app.route("/api/search", methods=["GET"])
def search():
    """Search the Quran"""
    params = {
        "q": request.args.get("q", ""),
        "size": request.args.get("size", "20"),
        "page": request.args.get("page", "0"),
        "language": request.args.get("language", "id"),
    }
    data = call_quran_api("/api/v4/search", params)
    return jsonify(data)


@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({
        "status": "ok",
        "mode": "legacy" if USE_LEGACY else "oauth2",
        "env": QF_ENV,
    })


# =============================================================================
# Run
# =============================================================================
if __name__ == "__main__":
    print(f"🕌 Quran Hub Backend Starting...")
    print(f"   Mode: {'Legacy API' if USE_LEGACY else 'OAuth2'}")
    print(f"   Env: {QF_ENV}")
    app.run(debug=True, port=5000)
