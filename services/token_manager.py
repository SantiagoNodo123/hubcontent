import requests
import json
import os

CONFIG_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'config.json')

def load_config():
    with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_config(cfg):
    with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
        json.dump(cfg, f, indent=2)

def extend_meta_user_token(short_token, app_id, app_secret):
    """
    Exchanges a short-lived Meta user access token (1-2 hours) 
    for a long-lived user access token (valid for 60 days).
    """
    url = "https://graph.facebook.com/v21.0/oauth/access_token"
    params = {
        "grant_type": "fb_exchange_token",
        "client_id": app_id,
        "client_secret": app_secret,
        "fb_exchange_token": short_token
    }
    res = requests.get(url, params=params).json()
    if "error" in res:
        raise Exception(res["error"].get("message", "Error extending token"))
    return res.get("access_token")

def get_permanent_page_token(long_user_token, page_id):
    """
    Using a 60-day user token, queries the Facebook Page to get
    a Page Access Token that NEVER EXPIRES.
    """
    url = f"https://graph.facebook.com/v21.0/{page_id}"
    params = {
        "fields": "access_token,name,id,instagram_business_account",
        "access_token": long_user_token
    }
    res = requests.get(url, params=params).json()
    if "error" in res:
        raise Exception(res["error"].get("message", "Error getting page token"))
    return res.get("access_token")

def exchange_tiktok_code(code, client_key, client_secret, redirect_uri):
    """
    Exchanges TikTok OAuth authorization code for an access token (24h)
    and a refresh token (365 days).
    """
    url = "https://open.tiktokapis.com/v2/oauth/token/"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    data = {
        "client_key": client_key,
        "client_secret": client_secret,
        "code": code,
        "grant_type": "authorization_code",
        "redirect_uri": redirect_uri
    }
    res = requests.post(url, headers=headers, data=data).json()
    if "error" in res or res.get("message") != "OK":
        err = res.get("error_description") or res.get("message") or "Error exchanging TikTok code"
        raise Exception(err)
    return res.get("data")

def refresh_tiktok_token(refresh_token, client_key, client_secret):
    """
    Refreshes TikTok access token using the 365-day refresh token.
    """
    url = "https://open.tiktokapis.com/v2/oauth/token/"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    data = {
        "client_key": client_key,
        "client_secret": client_secret,
        "grant_type": "refresh_token",
        "refresh_token": refresh_token
    }
    res = requests.post(url, headers=headers, data=data).json()
    if "error" in res or res.get("message") != "OK":
        err = res.get("error_description") or res.get("message") or "Error refreshing TikTok token"
        raise Exception(err)
    return res.get("data")
