
async def api_generate_custom_reels(request):
    try:
        from services.ai_agent import generate_b2b_custom_reels
        body = await request.json()
        angulo = body.get('angulo', 'Dolor Operativo')
        tono = body.get('tono', 'Controversial')
        instruccion = body.get('instruccion', '')
        reels = generate_b2b_custom_reels(angulo, tono, instruccion)
        return JSONResponse({'success': True, 'scripts': reels})
    except Exception as e:
        return JSONResponse({'success': False, 'error': str(e)}, status_code=500)

﻿import os
import sys
import json
import requests
import uvicorn
import math

# Ensure UTF-8 output on Windows terminal
sys.stdout.reconfigure(encoding='utf-8')

from starlette.applications import Starlette
from starlette.responses import JSONResponse, HTMLResponse
from starlette.routing import Route
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware
from services.meta_service import (
    get_channel_profile,
    get_channel_posts,
    generate_personal_plan,
    generate_nodo_plan
)
from services.tiktok_service import (
    get_tiktok_auth_url,
    get_female_audience_matrix,
    get_tiktok_live_profile,
    get_tiktok_api_user,
    get_tiktok_api_videos,
    get_valid_tiktok_token,
    save_tiktok_account_token
)

from services.token_manager import (
    extend_meta_user_token,
    get_permanent_page_token,
    exchange_tiktok_code,
    refresh_tiktok_token
)
from services.ai_agent import (
    generate_reels_with_ai,
    generate_hook_variations,
    save_gemini_api_key,
    get_gemini_api_key
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(BASE_DIR, "data", "config.json")
TEMPLATE_PATH = os.path.join(BASE_DIR, "templates", "index.html")

def load_config():
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def save_config(cfg):
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2)

async def homepage(request):
    with open(TEMPLATE_PATH, "r", encoding="utf-8") as f:
        html_content = f.read()
    return HTMLResponse(html_content)

async def api_status(request):
    config = load_config()
    
    personal_valid = False
    personal_error = None
    try:
        r = requests.get(f"https://graph.facebook.com/v21.0/{config['personal']['instagram_account_id']}?fields=username&access_token={config['personal']['access_token']}", timeout=10).json()
        if "error" not in r:
            personal_valid = True
        else:
            personal_error = r["error"].get("message")
    except Exception as e:
        personal_error = str(e)

    nodo_valid = False
    nodo_error = None
    try:
        r = requests.get(f"https://graph.facebook.com/v21.0/{config['nodo']['instagram_account_id']}?fields=username&access_token={config['nodo']['access_token']}", timeout=10).json()
        if "error" not in r:
            nodo_valid = True
        else:
            nodo_error = r["error"].get("message")
    except Exception as e:
        nodo_error = str(e)
        
    tiktok_tokens_file = os.path.join(BASE_DIR, "data", "tiktok_tokens.json")
    has_tiktok_tokens = os.path.exists(tiktok_tokens_file)
    connected_accounts = []
    if has_tiktok_tokens:
        try:
            with open(tiktok_tokens_file, "r", encoding="utf-8") as f:
                tt_data = json.load(f)
            for acc in config["tiktok"]["accounts"]:
                if acc in tt_data or (acc == "santiagoquevedo71" and "access_token" in tt_data):
                    connected_accounts.append(acc)
        except Exception:
            pass

    return JSONResponse({
        "status": "online",
        "personal": {
            "account": config["personal"]["username"],
            "page_id": config["personal"]["page_id"],
            "valid": personal_valid,
            "error": personal_error
        },
        "nodo": {
            "account": config["nodo"]["username"],
            "page_id": config["nodo"]["page_id"],
            "valid": nodo_valid,
            "error": nodo_error
        },
        "tiktok": {
            "app_name": config["tiktok"]["app_name"],
            "client_key": config["tiktok"]["client_key"],
            "redirect_uri": config["tiktok"]["redirect_uri"],
            "accounts": config["tiktok"]["accounts"],
            "connected_accounts": connected_accounts,
            "has_tokens": len(connected_accounts) > 0
        }
    })

async def api_personal_stats(request):
    config = load_config()
    try:
        profile = get_channel_profile(config["personal"]["access_token"], config["personal"]["instagram_account_id"])
        posts = get_channel_posts(config["personal"]["access_token"], config["personal"]["instagram_account_id"], limit=8)
        return JSONResponse({"success": True, "profile": profile, "posts": posts})
    except Exception as e:
        return JSONResponse({"success": False, "error": str(e)}, status_code=500)

async def api_personal_plan(request):
    data = generate_personal_plan()
    if isinstance(data, dict):
        return JSONResponse({"success": True, "diagnostic_24h": data.get("diagnostic_24h"), "plan": data.get("plan", [])})
    return JSONResponse({"success": True, "plan": data})

async def api_nodo_stats(request):
    config = load_config()
    try:
        profile = get_channel_profile(config["nodo"]["access_token"], config["nodo"]["instagram_account_id"])
        posts = get_channel_posts(config["nodo"]["access_token"], config["nodo"]["instagram_account_id"], limit=8)
        return JSONResponse({"success": True, "profile": profile, "posts": posts})
    except Exception as e:
        return JSONResponse({"success": False, "error": str(e)}, status_code=500)

async def api_nodo_plan(request):
    data = generate_nodo_plan()
    if isinstance(data, dict):
        return JSONResponse({"success": True, "diagnostic_24h": data.get("diagnostic_24h"), "plan": data.get("plan", [])})
    return JSONResponse({"success": True, "plan": data})

async def api_tiktok_data(request):
    config = load_config()
    matrix = get_female_audience_matrix()
    auth_url = get_tiktok_auth_url(config["tiktok"]["client_key"], config["tiktok"]["redirect_uri"])
    
    # Scrape both accounts live
    profiles = []
    for acc in config["tiktok"]["accounts"]:
        prof = get_tiktok_live_profile(acc)
        if prof:
            profiles.append(prof)
        else:
            # Fallback stats
            if acc == "santiagoquevedo71":
                profiles.append({"username": acc, "nickname": "Santiago", "bio": "La vida desde mi perspectiva. Quizá algo de ella también sea tuyo.", "followers": 1211, "likes": 5603, "videos": 234})
            else:
                profiles.append({"username": acc, "nickname": "nodotechgrowth", "bio": "NODO. Automatización comercial B2B + IA.", "followers": 71, "likes": 875, "videos": 169})
                
    return JSONResponse({
        "success": True,
        "auth_url": auth_url,
        "client_key": config["tiktok"]["client_key"],
        "redirect_uri": config["tiktok"]["redirect_uri"],
        "profiles": profiles,
        "matrix": matrix
    })

async def api_tiktok_studio(request):
    studio_path = os.path.join(BASE_DIR, "data", "tiktok_studio.json")
    if os.path.exists(studio_path):
        with open(studio_path, "r", encoding="utf-8") as f:
            return JSONResponse({"success": True, "studio": json.load(f)})
    return JSONResponse({"success": False, "error": "No studio data found"}, status_code=404)

async def api_extend_meta(request):
    try:
        body = await request.json()
        short_token = body.get("short_token")
        app_id = body.get("app_id")
        app_secret = body.get("app_secret")
        account = body.get("account", "personal")
        page_id = body.get("page_id")
        
        if not short_token or not app_id or not app_secret:
            return JSONResponse({"success": False, "error": "Faltan short_token, app_id o app_secret"}, status_code=400)
            
        long_user_token = extend_meta_user_token(short_token, app_id, app_secret)
        
        permanent_token = None
        if page_id:
            try:
                permanent_token = get_permanent_page_token(long_user_token, page_id)
            except Exception as pe:
                print(f"Page token notice: {pe}")
                
        final_token = permanent_token or long_user_token
        is_permanent = permanent_token is not None
        
        cfg = load_config()
        if account in cfg:
            cfg[account]["access_token"] = final_token
            save_config(cfg)
            
        return JSONResponse({
            "success": True, 
            "is_permanent": is_permanent,
            "token_type": "Page Access Token (Permanente)" if is_permanent else "User Token (60 Días)",
            "account": account
        })
    except Exception as e:
        return JSONResponse({"success": False, "error": str(e)}, status_code=500)

async def api_tiktok_callback(request):
    code = request.query_params.get("code")
    if not code:
        return HTMLResponse("<h3>Error: No se recibió el código de autorización de TikTok.</h3>", status_code=400)
    
    cfg = load_config()
    try:
        tok_data = exchange_tiktok_code(
            code=code,
            client_key=cfg["tiktok"]["client_key"],
            client_secret=cfg["tiktok"]["client_secret"],
            redirect_uri=cfg["tiktok"]["redirect_uri"]
        )
        tokens_path = os.path.join(BASE_DIR, "data", "tiktok_tokens.json")
        with open(tokens_path, "w", encoding="utf-8") as f:
            json.dump(tok_data, f, indent=2)
            
        return HTMLResponse("""
            <div style="font-family: sans-serif; max-width: 600px; margin: 40px auto; padding: 30px; background: #0c0e12; color: white; border-radius: 16px; border: 1px solid #1e222b; text-align: center;">
                <h2 style="color: #10b981;">âœ… ¡Autorización de TikTok Exitosa!</h2>
                <p style="color: #94a3b8;">Los tokens de acceso (24h) y de refresco (365 días) han sido guardados correctamente en Nodo Content Hub.</p>
                <a href="/" style="display: inline-block; margin-top: 20px; padding: 10px 20px; background: white; color: black; font-weight: bold; border-radius: 8px; text-decoration: none;">Volver al Dashboard</a>
            </div>
        """)
    except Exception as e:
        return HTMLResponse(f"<h3>Error al intercambiar código de TikTok: {e}</h3>", status_code=500)

async def api_tiktok_live(request):
    account = request.query_params.get("account")
    
    if account:
        token = get_valid_tiktok_token(account)
        if not token:
            return JSONResponse({"success": False, "error": f"No TikTok token for {account}"}, status_code=404)
        user_info = get_tiktok_api_user(token) or {}
        live_prof = get_tiktok_live_profile(account) or {}
        if live_prof.get("bio"):
            user_info["bio"] = live_prof["bio"]
        if live_prof.get("avatar") and not user_info.get("avatar_url"):
            user_info["avatar_url"] = live_prof["avatar"]
        videos = get_tiktok_api_videos(token, max_count=12)
        return JSONResponse({"success": True, "account": account, "user": user_info, "videos": videos})
        
    results = {}
    for acc in ["santiagoquevedo71", "nodotechgrowth"]:
        tok = get_valid_tiktok_token(acc)
        if tok:
            u = get_tiktok_api_user(tok) or {}
            live_prof = get_tiktok_live_profile(acc) or {}
            if live_prof.get("bio"):
                u["bio"] = live_prof["bio"]
            if live_prof.get("avatar") and not u.get("avatar_url"):
                u["avatar_url"] = live_prof["avatar"]
            if not u.get("follower_count") and live_prof.get("followers"):
                u["follower_count"] = live_prof["followers"]
            v = get_tiktok_api_videos(tok, max_count=12)
            results[acc] = {"connected": True, "user": u, "videos": v}
        else:
            live_prof = get_tiktok_live_profile(acc) or {}
            results[acc] = {"connected": False, "user": live_prof, "videos": []}
            
    return JSONResponse({
        "success": True,
        "accounts": results
    })

from services.analytics_engine import (
    run_full_sync,
    load_latest_dashboard,
    load_latest_demographics,
    load_latest_insights,
    load_history,
    load_latest_strategy
)

async def api_overview(request):
    try:
        config = load_config()

        # 1. Instagram Personal (@s_thiago7)
        ig_p_fol = 1951
        ig_p_media = 280
        ig_p_prof = {}
        try:
            ig_p_prof = get_channel_profile(config["personal"]["access_token"], config["personal"]["instagram_account_id"])
            ig_p_fol = ig_p_prof.get("followers_count", 1951)
            ig_p_media = ig_p_prof.get("media_count", 280)
        except Exception as e:
            print("Overview IG Personal fetch notice:", e)

        # 2. Instagram Nodo B2B (@nodo_tg)
        ig_n_fol = 38
        ig_n_media = 151
        ig_n_prof = {}
        try:
            ig_n_prof = get_channel_profile(config["nodo"]["access_token"], config["nodo"]["instagram_account_id"])
            ig_n_fol = ig_n_prof.get("followers_count", 38)
            ig_n_media = ig_n_prof.get("media_count", 151)
        except Exception as e:
            print("Overview IG Nodo fetch notice:", e)

        # 3. TikTok Personal (@santiagoquevedo71)
        tt_p_fol = 1211
        tt_p_videos = 253
        tt_p_likes = 6037
        try:
            tok = get_valid_tiktok_token("santiagoquevedo71")
            if tok:
                u = get_tiktok_api_user(tok) or {}
                tt_p_fol = u.get("follower_count", 1211)
                tt_p_videos = u.get("video_count", 253)
                tt_p_likes = u.get("likes_count", 6037)
        except Exception as e:
            print("Overview TT Personal fetch notice:", e)

        # 4. TikTok Nodo B2B (@nodotechgrowth)
        tt_n_fol = 74
        tt_n_videos = 175
        tt_n_likes = 934
        try:
            tok = get_valid_tiktok_token("nodotechgrowth")
            if tok:
                u = get_tiktok_api_user(tok) or {}
                tt_n_fol = u.get("follower_count", 74)
                tt_n_videos = u.get("video_count", 175)
                tt_n_likes = u.get("likes_count", 934)
        except Exception as e:
            print("Overview TT Nodo fetch notice:", e)

        total_followers = ig_p_fol + ig_n_fol + tt_p_fol + tt_n_fol
        personal_combined = ig_p_fol + tt_p_fol
        nodo_combined = ig_n_fol + tt_n_fol

        strat = {}
        try:
            strat = load_latest_strategy()
        except Exception:
            pass

        p_strat = strat.get("personal", {})
        n_strat = strat.get("nodo", {})

        return JSONResponse({
            "success": True,
            "ecosystem": {
                "total_followers": total_followers,
                "personal_combined": personal_combined,
                "nodo_combined": nodo_combined,
                "global_target": 10000,
                "global_progress_pct": round((total_followers / 10000) * 100, 1),
                "total_posts_created": ig_p_media + ig_n_media + tt_p_videos + tt_n_videos,
                "last_updated": "En vivo desde Meta Graph & TikTok API"
            },
            "accounts": {
                "ig_personal": {
                    "username": "@s_thiago7",
                    "channel": "Instagram Personal",
                    "current": ig_p_fol,
                    "target": 10000,
                    "remaining": max(0, 10000 - ig_p_fol),
                    "progress_pct": round((ig_p_fol / 10000) * 100, 1),
                    "daily_rate": 87,
                    "days_remaining": math.ceil(max(0, 10000 - ig_p_fol) / 87),
                    "media_count": ig_p_media,
                    "avatar": ig_p_prof.get("profile_picture_url")
                },
                "tt_personal": {
                    "username": "@santiagoquevedo71",
                    "channel": "TikTok Personal",
                    "current": tt_p_fol,
                    "target": 10000,
                    "remaining": max(0, 10000 - tt_p_fol),
                    "progress_pct": round((tt_p_fol / 10000) * 100, 1),
                    "daily_rate": 30,
                    "days_remaining": math.ceil(max(0, 10000 - tt_p_fol) / 30),
                    "media_count": tt_p_videos,
                    "likes": tt_p_likes
                },
                "ig_nodo": {
                    "username": "@nodo_tg",
                    "channel": "Instagram Nodo B2B",
                    "current": ig_n_fol,
                    "target": 10000,
                    "remaining": max(0, 10000 - ig_n_fol),
                    "progress_pct": round((ig_n_fol / 10000) * 100, 1),
                    "daily_rate": 10,
                    "days_remaining": math.ceil(max(0, 10000 - ig_n_fol) / 10),
                    "media_count": ig_n_media,
                    "avatar": ig_n_prof.get("profile_picture_url")
                },
                "tt_nodo": {
                    "username": "@nodotechgrowth",
                    "channel": "TikTok Nodo B2B",
                    "current": tt_n_fol,
                    "target": 10000,
                    "remaining": max(0, 10000 - tt_n_fol),
                    "progress_pct": round((tt_n_fol / 10000) * 100, 1),
                    "daily_rate": 12,
                    "days_remaining": math.ceil(max(0, 10000 - tt_n_fol) / 12),
                    "media_count": tt_n_videos,
                    "likes": tt_n_likes
                }
            },
            "diagnostics": {
                "personal": {
                    "winner_title": p_strat.get("winner_title", "Y uno siempre resulta ser el malo"),
                    "winner_stats": p_strat.get("winner_stats", "4,347 vistas · 19 guardados · 29.7% skip"),
                    "why_winner": p_strat.get("why_winner", "Gancho de conflicto directo en el segundo 1."),
                    "loser_title": p_strat.get("loser_title", "Empiezo yo ðŸ‘‡"),
                    "loser_stats": p_strat.get("loser_stats", "183 alcance · 77.7% skip"),
                    "why_loser": p_strat.get("why_loser", "Pregunta pasiva sin gancho genera abandono masivo."),
                    "renewed_focus": p_strat.get("renewed_focus", "Estándares innegociables en los 20s, loops visuales de 8 segundos.")
                },
                "nodo": {
                    "winner_title": n_strat.get("winner_title", "No se descarga en la App Store"),
                    "winner_stats": n_strat.get("winner_stats", "621 views · 38.8% skip"),
                    "why_winner": n_strat.get("why_winner", "Ataca el dolor de procesos manuales en empresas."),
                    "loser_title": n_strat.get("loser_title", "El link en el primer comentario"),
                    "loser_stats": n_strat.get("loser_stats", "80 views · 87.5% skip"),
                    "why_loser": n_strat.get("why_loser", "Pedir clics directos al segundo 1 provoca skip masivo."),
                    "renewed_focus": n_strat.get("renewed_focus", "Storytelling B2B de casos reales con Kommo CRM + IA.")
                }
            }
        })
    except Exception as e:
        return JSONResponse({"success": False, "error": str(e)}, status_code=500)

async def api_analytics_sync(request):
    try:
        summary = run_full_sync()
        return JSONResponse({"success": True, "summary": summary})
    except Exception as e:
        return JSONResponse({"success": False, "error": str(e)}, status_code=500)

async def api_analytics_dashboard(request):
    try:
        data = load_latest_dashboard()
        return JSONResponse({"success": True, **data})
    except Exception as e:
        return JSONResponse({"success": False, "error": str(e)}, status_code=500)

async def api_analytics_demographics(request):
    try:
        data = load_latest_demographics()
        return JSONResponse({"success": True, "personal": data.get("personal", {}), "nodo": data.get("nodo", {})})
    except Exception as e:
        return JSONResponse({"success": False, "error": str(e)}, status_code=500)

async def api_analytics_insights(request):
    try:
        data = load_latest_insights()
        return JSONResponse({"success": True, **data})
    except Exception as e:
        return JSONResponse({"success": False, "error": str(e)}, status_code=500)

async def api_analytics_history(request):
    try:
        data = load_history()
        return JSONResponse({"success": True, "history": data})
    except Exception as e:
        return JSONResponse({"success": False, "error": str(e)}, status_code=500)

async def api_ai_generate_reels(request):
    try:
        body = await request.json()
    except Exception:
        body = {}
        
    account = body.get("account", "personal")
    angle = body.get("angle", "record")
    tone = body.get("tone", "santiago")
    custom_prompt = body.get("custom_prompt", "")
    count = int(body.get("count", 8))
    model = body.get("model", "gemini-3.8-flash")
    api_key = body.get("api_key")
    
    result = generate_reels_with_ai(
        account=account,
        angle=angle,
        tone=tone,
        custom_prompt=custom_prompt,
        count=count,
        model=model,
        api_key=api_key
    )
    return JSONResponse(result)

async def api_ai_mutate_hook(request):
    try:
        body = await request.json()
    except Exception:
        body = {}
        
    hook = body.get("hook", "")
    theme = body.get("theme", "")
    tone = body.get("tone", "santiago")
    model = body.get("model", "gemini-3.8-flash")
    api_key = body.get("api_key")
    
    result = generate_hook_variations(
        hook=hook,
        theme=theme,
        tone=tone,
        model=model,
        api_key=api_key
    )
    return JSONResponse(result)

async def api_config_gemini_key_get(request):
    key = get_gemini_api_key()
    return JSONResponse({
        "success": True,
        "has_key": bool(key),
        "model": "gemini-3.8-flash",
        "key_preview": f"{key[:4]}...{key[-4:]}" if key and len(key) > 8 else None
    })

async def api_config_gemini_key_post(request):
    try:
        body = await request.json()
        api_key = body.get("api_key", "").strip()
        if not api_key:
            return JSONResponse({"success": False, "error": "API Key vacía"}, status_code=400)
            
        save_gemini_api_key(api_key)
        return JSONResponse({
            "success": True, 
            "message": "API Key de Google AI Studio guardada correctamente. Modelo activado: gemini-3.8-flash"
        })
    except Exception as e:
        return JSONResponse({"success": False, "error": str(e)}, status_code=500)

routes = [
    Route('/api/ai/generate-scripts', api_generate_custom_reels, methods=['POST']),
    Route("/", homepage),
    Route("/api/overview", api_overview),
    Route("/api/status", api_status),
    Route("/api/personal/stats", api_personal_stats),
    Route("/api/personal/plan", api_personal_plan),
    Route("/api/nodo/stats", api_nodo_stats),
    Route("/api/nodo/plan", api_nodo_plan),
    Route("/api/tiktok/matrix", api_tiktok_data),
    Route("/api/tiktok/studio", api_tiktok_studio),
    Route("/api/tiktok/live", api_tiktok_live),
    Route("/api/tiktok/callback", api_tiktok_callback),
    Route("/api/meta/extend", api_extend_meta, methods=["POST"]),
    Route("/api/analytics/sync", api_analytics_sync, methods=["POST"]),
    Route("/api/analytics/dashboard", api_analytics_dashboard),
    Route("/api/analytics/demographics", api_analytics_demographics),
    Route("/api/analytics/insights", api_analytics_insights),
    Route("/api/analytics/history", api_analytics_history),
    Route("/api/ai/generate-reels", api_ai_generate_reels, methods=["POST"]),
    Route("/api/ai/mutate-hook", api_ai_mutate_hook, methods=["POST"]),
    Route("/api/config/gemini-key", api_config_gemini_key_get, methods=["GET"]),
    Route("/api/config/gemini-key", api_config_gemini_key_post, methods=["POST"]),
]


middleware = [
    Middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
        allow_credentials=True
    )
]

app = Starlette(debug=True, routes=routes, middleware=middleware)

if __name__ == "__main__":
    print("Content Hub running on http://localhost:8000")
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=False)
