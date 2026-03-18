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
import json
import hashlib

app = Flask(__name__)
CORS(app, origins=["http://localhost:5173", "http://localhost:3000", "http://127.0.0.1:5173"])

# =============================================================================
# Configuration
# =============================================================================
QF_CLIENT_ID = os.getenv("QF_CLIENT_ID", "9c369946-fb66-4e26-8fbb-586e6eea7843")
QF_CLIENT_SECRET = os.getenv("QF_CLIENT_SECRET", "zMcGHOyuCX8NAakDv1RE9obTQV")
QF_ENV = os.getenv("QF_ENV", "prelive")

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
        print(f"   🔑 Requesting token from {config['auth_base_url']}...")
        response = requests.post(
            f"{config['auth_base_url']}/oauth2/token",
            auth=(QF_CLIENT_ID, QF_CLIENT_SECRET),
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            data="grant_type=client_credentials&scope=content",
            timeout=15,
        )
        response.raise_for_status()
        data = response.json()

        _token_cache["token"] = data["access_token"]
        _token_cache["expires_at"] = time.time() + data.get("expires_in", 3600)
        print(f"   ✅ Token obtained (expires in {data.get('expires_in', 3600)}s)")
        return _token_cache["token"]


# =============================================================================
# API Client
# =============================================================================
_api_cache = {}
_cache_lock = threading.Lock()
CACHE_TTL = 1800  # 30 minutes


def call_quran_api(endpoint, params=None):
    """Call Quran API with caching and 401 retry"""
    cache_key = hashlib.md5(
        f"{endpoint}:{json.dumps(params or {}, sort_keys=True)}".encode()
    ).hexdigest()

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

    response = requests.get(url, headers=headers, params=params, timeout=20)

    # Retry on 401
    if response.status_code == 401 and not USE_LEGACY:
        print("   ⚠️  401 — re-requesting token...")
        _token_cache["token"] = None
        token = get_access_token()
        headers["x-auth-token"] = token
        response = requests.get(url, headers=headers, params=params, timeout=20)

    response.raise_for_status()
    data = response.json()

    with _cache_lock:
        _api_cache[cache_key] = {"data": data, "expires_at": time.time() + CACHE_TTL}

    return data


# =============================================================================
# Shared verse params builder
# =============================================================================
def _verse_params():
    p = {
        "language": request.args.get("language", "id"),
        "words": request.args.get("words", "true"),
        "translations": request.args.get("translations", "33"),
        "fields": request.args.get("fields", "text_uthmani,text_uthmani_tajweed,text_indopak"),
        "word_fields": request.args.get(
            "word_fields",
            "text_uthmani,text_indopak,code_v1,code_v2,v1_page,v2_page,line_number",
        ),
        "translation_fields": request.args.get("translation_fields", "resource_name"),
        "per_page": request.args.get("per_page", "50"),
        "page": request.args.get("page", "1"),
    }
    tafsirs = request.args.get("tafsirs", "")
    if tafsirs:
        p["tafsirs"] = tafsirs
    return p


# =============================================================================
# Error Handler
# =============================================================================
@app.errorhandler(Exception)
def handle_error(e):
    code = getattr(e, "code", 500) if hasattr(e, "code") else 500
    return jsonify({"error": str(e), "status": code}), code if isinstance(code, int) else 500


# =============================================================================
# API Routes
# =============================================================================

@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({
        "status": "ok",
        "mode": "legacy" if USE_LEGACY else "oauth2",
        "env": QF_ENV,
    })


@app.route("/api/chapters", methods=["GET"])
def get_chapters():
    language = request.args.get("language", "id")
    return jsonify(call_quran_api("/api/v4/chapters", {"language": language}))


@app.route("/api/chapters/<int:chapter_id>", methods=["GET"])
def get_chapter(chapter_id):
    language = request.args.get("language", "id")
    return jsonify(call_quran_api(f"/api/v4/chapters/{chapter_id}", {"language": language}))


@app.route("/api/chapters/<int:chapter_id>/info", methods=["GET"])
def get_chapter_info(chapter_id):
    language = request.args.get("language", "id")
    return jsonify(call_quran_api(f"/api/v4/chapters/{chapter_id}/info", {"language": language}))


@app.route("/api/verses/by_chapter/<int:chapter_id>", methods=["GET"])
def get_verses_by_chapter(chapter_id):
    return jsonify(call_quran_api(f"/api/v4/verses/by_chapter/{chapter_id}", _verse_params()))


@app.route("/api/verses/by_page/<int:page_number>", methods=["GET"])
def get_verses_by_page(page_number):
    return jsonify(call_quran_api(f"/api/v4/verses/by_page/{page_number}", _verse_params()))


@app.route("/api/verses/by_juz/<int:juz_number>", methods=["GET"])
def get_verses_by_juz(juz_number):
    return jsonify(call_quran_api(f"/api/v4/verses/by_juz/{juz_number}", _verse_params()))


@app.route("/api/verses/by_key/<path:verse_key>", methods=["GET"])
def get_verse_by_key(verse_key):
    return jsonify(call_quran_api(f"/api/v4/verses/by_key/{verse_key}", _verse_params()))


@app.route("/api/quran/verses/uthmani_tajweed", methods=["GET"])
def get_uthmani_tajweed():
    params = {"chapter_number": request.args.get("chapter_number", "1")}
    return jsonify(call_quran_api("/api/v4/quran/verses/uthmani_tajweed", params))


@app.route("/api/tafsirs/<int:tafsir_id>/by_ayah/<path:verse_key>", methods=["GET"])
def get_tafsir(tafsir_id, verse_key):
    return jsonify(call_quran_api(f"/api/v4/tafsirs/{tafsir_id}/by_ayah/{verse_key}"))


@app.route("/api/resources/translations", methods=["GET"])
def get_translations():
    language = request.args.get("language", "id")
    return jsonify(call_quran_api("/api/v4/resources/translations", {"language": language}))


@app.route("/api/resources/tafsirs", methods=["GET"])
def get_tafsirs():
    language = request.args.get("language", "id")
    return jsonify(call_quran_api("/api/v4/resources/tafsirs", {"language": language}))


@app.route("/api/resources/languages", methods=["GET"])
def get_languages():
    return jsonify(call_quran_api("/api/v4/resources/languages"))


@app.route("/api/juzs", methods=["GET"])
def get_juzs():
    return jsonify(call_quran_api("/api/v4/juzs"))


@app.route("/api/search", methods=["GET"])
def search():
    params = {
        "q": request.args.get("q", ""),
        "size": request.args.get("size", "20"),
        "page": request.args.get("page", "0"),
        "language": request.args.get("language", "id"),
    }
    return jsonify(call_quran_api("/api/v4/search", params))


# =============================================================================
# Run
# =============================================================================
if __name__ == "__main__":
    print()
    print("  ┌──────────────────────────────────────────────┐")
    print("  │  🕌  Quran Hub Backend                        │")
    print(f"  │  Mode : {'Legacy API' if USE_LEGACY else 'OAuth2 (' + QF_ENV + ')':35s} │")
    if not USE_LEGACY:
        print(f"  │  API  : {ENV_CONFIG[QF_ENV]['api_base_url']:35s} │")
    print("  │  Port : 5000                                  │")
    print("  └──────────────────────────────────────────────┘")
    print()
    app.run(debug=True, host="0.0.0.0", port=5000)
