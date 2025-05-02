"""Работа с API администраторов."""

import requests
import hmac
import hashlib
import base64
import json
from config.config import ADMIN_SOURCE, ADMIN_API_URL, ADMIN_API_KEY, ADMIN_API_SECRET, ADMIN_JSON_PATH
from pathlib import Path

def get_secret_bytes(api_secret):
    missing_padding = len(api_secret) % 4
    if missing_padding:
        api_secret += '=' * (4 - missing_padding)
    return base64.urlsafe_b64decode(api_secret)

class AdminAPI:
    @staticmethod
    async def get_admins():
        if ADMIN_SOURCE == "api":
            return AdminAPI._get_admins_api()
        return AdminAPI._get_admins_json()

    @staticmethod
    def _get_admins_api():
        message = "all".encode("utf-8")
        secret = ADMIN_API_SECRET.encode("utf-8")
        signature = hmac.new(secret, message, hashlib.sha256).hexdigest()
        headers = {
            "x-api-key": ADMIN_API_KEY,
            "x-api-signature": signature,
            "accept": "application/json",
            "User-Agent": "curl/7.79.1"
        }
        try:
            resp = requests.get(ADMIN_API_URL, headers=headers)
            if resp.status_code == 200:
                return resp.json()
        except Exception:
            pass
        raise Exception("Не удалось получить список админов с правильной сигнатурой")

    @staticmethod
    def _get_admins_json():
        path = Path(ADMIN_JSON_PATH)
        if not path.exists():
            return []
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
