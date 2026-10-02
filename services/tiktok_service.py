import urllib.parse
import requests
import json
import re
import os

TIKTOK_TOKENS_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'tiktok_tokens.json')

def get_valid_tiktok_token(account="santiagoquevedo71"):
    if not os.path.exists(TIKTOK_TOKENS_PATH):
        return None
    try:
        with open(TIKTOK_TOKENS_PATH, 'r', encoding='utf-8') as f:
            tok_data = json.load(f)
        if account in tok_data:
            return tok_data[account].get('access_token')
        elif "access_token" in tok_data and account == "santiagoquevedo71":
            return tok_data.get('access_token')
    except Exception as e:
        print(f"Error loading TikTok token for {account}: {e}")
    return None

def save_tiktok_account_token(account, token_dict):
    data = {}
    if os.path.exists(TIKTOK_TOKENS_PATH):
        try:
            with open(TIKTOK_TOKENS_PATH, 'r', encoding='utf-8') as f:
                data = json.load(f)
            if "access_token" in data and "santiagoquevedo71" not in data:
                data = {"santiagoquevedo71": data}
        except Exception:
            data = {}
    data[account] = token_dict
    with open(TIKTOK_TOKENS_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)

def get_tiktok_api_user(access_token):
    url = "https://open.tiktokapis.com/v2/user/info/"
    headers = {"Authorization": f"Bearer {access_token}"}
    params = {"fields": "open_id,avatar_url,display_name,follower_count,following_count,likes_count,video_count"}
    try:
        res = requests.get(url, headers=headers, params=params, timeout=10).json()
        if res.get("error", {}).get("code") == "ok":
            return res.get("data", {}).get("user")
    except Exception as e:
        print(f"Error fetching TikTok user info: {e}")
    return None

def get_tiktok_api_videos(access_token, max_count=10):
    url = "https://open.tiktokapis.com/v2/video/list/?fields=id,title,video_description,duration,create_time,share_url,view_count,like_count,comment_count,share_count"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    data = {"max_count": max_count}
    try:
        res = requests.post(url, headers=headers, json=data, timeout=10).json()
        if res.get("error", {}).get("code") == "ok":
            return res.get("data", {}).get("videos", [])
    except Exception as e:
        print(f"Error fetching TikTok videos: {e}")
    return []

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "es-ES,es;q=0.9,en;q=0.8"
}

def get_tiktok_live_profile(username):
    """Scrapes live TikTok profile data (followers, likes, video count, bio)."""
    url = f"https://www.tiktok.com/@{username}"
    try:
        r = requests.get(url, headers=HEADERS, timeout=8)
        if r.status_code == 200:
            m = re.search(r'<script id="__UNIVERSAL_DATA_FOR_REHYDRATION__" type="application/json">([^<]+)</script>', r.text)
            if m:
                data = json.loads(m.group(1))
                scope = data.get("__DEFAULT_SCOPE__", {})
                user_detail = scope.get("webapp.user-detail", {})
                user_info = user_detail.get("userInfo", {})
                user = user_info.get("user", {})
                stats = user_info.get("stats", {})
                return {
                    "username": username,
                    "nickname": user.get("nickname", username),
                    "bio": user.get("signature", ""),
                    "followers": stats.get("followerCount", 0),
                    "likes": stats.get("heartCount", 0),
                    "videos": stats.get("videoCount", 0),
                    "avatar": user.get("avatarThumb", "")
                }
    except Exception as e:
        print(f"Error fetching TikTok profile @{username}: {e}")
    return None

def get_tiktok_auth_url(client_key, redirect_uri):
    """Generates the official TikTok OAuth2 authorization URL for Sandbox/Testing."""
    base_url = "https://www.tiktok.com/v2/auth/authorize/"
    params = {
        "client_key": client_key,
        "scope": "user.info.basic,user.info.stats,video.list",
        "response_type": "code",
        "redirect_uri": redirect_uri,
        "state": "content_hub_auth"
    }
    return f"{base_url}?{urllib.parse.urlencode(params)}"

def get_female_audience_matrix():
    """Returns the proven hook matrix and formulas tailored for the 90% female audience on TikTok."""
    return [
        {
            "category": "Green Flags & Estándares Altos",
            "why_it_works": "Detona comentarios de validación y compartidos masivos entre amigas ('dónde consigo uno así').",
            "hooks": [
                {
                    "setup": "Un hombre con metas claras no te revisa el celular ni te prohíbe salidas...",
                    "punchline": "...simplemente observa tus valores. Si no hay lealtad ni respeto, se va en silencio y nunca más regresa.",
                    "copy": "Cuidar la paz no se negocia. ¿De acuerdo? 👇"
                },
                {
                    "setup": "Normalicen a los hombres de 20 y tantos que no nos interesa tener 'ganado'...",
                    "punchline": "...preferimos esperar a una sola mujer con la que construir todo desde cero.",
                    "copy": "Pocos pero con intenciones reales 🔥."
                },
                {
                    "setup": "La diferencia entre un niño y un hombre en sus 20s:",
                    "punchline": "El niño presume con cuántas habla. El hombre presume a la única que tiene a su lado mientras construye su futuro.",
                    "copy": "Prioridades que separan etapas. Te leo abajo 👇"
                }
            ]
        },
        {
            "category": "Ambición & Estilo de Vida Silencioso",
            "why_it_works": "Atrae admiración por ética de trabajo, disciplina y sobriedad.",
            "hooks": [
                {
                    "setup": "Qué atractivo es cuando un hombre no necesita aparentar en redes...",
                    "punchline": "...está demasiado ocupado aprendiendo, entrenando y construyendo lo suyo en silencio.",
                    "copy": "Menos postureo, más resultados reales."
                },
                {
                    "setup": "Mi viernes por la noche trabajando en mi empresa vs lo que la gente cree que hago:",
                    "punchline": "Cero fiesta, café frío a las 11 PM y una obsesión sana por darle una vida tranquila a los míos.",
                    "copy": "El sacrificio de hoy es la tranquilidad de mañana."
                }
            ]
        },
        {
            "category": "Vulnerabilidad Masculina Sana",
            "why_it_works": "Genera empatía y ternura; rompe con la frialdad falsa de internet.",
            "hooks": [
                {
                    "setup": "A los hombres que también nos da miedo fracasar pero nos levantamos igual...",
                    "punchline": "...aquí un recordatorio de que no estás solo y que tu esfuerzo silencioso sí vale la pena.",
                    "copy": "Para todos los que están empujando hoy. Abrazo fuerte 🫂"
                },
                {
                    "setup": "Confesión honesta de un emprendedor a sus 20s:",
                    "punchline": "Lo más difícil no es la falta de dinero o clientes, es la soledad de no tener con quién compartir el proceso.",
                    "copy": "Empiezo yo... ¿a quién más le pasa? 👇"
                }
            ]
        }
    ]
