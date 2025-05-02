"""Конфигурационные параметры и константы."""

API_TOKEN = "7709742294:AAGEpeRanwIEufAP-fUHmapwaaEz_eo02eM"

from utils.misc import load_config

_config = load_config()

ADMIN_SOURCE = _config.get("admin_source", "api")
ADMIN_API_URL = _config.get("admin_api", {}).get("url")
ADMIN_API_HMAC_SECRET = _config.get("admin_api", {}).get("hmac_secret")
ADMIN_JSON_PATH = _config.get("admin_json_path", "admins.json")
ADMIN_API_KEY = _config.get("admin_api", {}).get("api_key")
ADMIN_API_SECRET = _config.get("admin_api", {}).get("api_secret")
