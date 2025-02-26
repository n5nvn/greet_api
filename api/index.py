from flask import Flask, request, jsonify
import requests
import time
import json

app = Flask(__name__)

# بيانات API الأصلي
API_URL = "https://100067.msdk.garena.com/api/msdk/info/rebates"
ACCESS_TOKEN = "46062e0bdd57ad315a8abc51e5730929e0077d3b27c9ee2ee6ea5d35b377b0bc"

# إعدادات التخزين المؤقت (Cache)
CACHE_FILE = "cache.json"
CACHE_EXPIRY = 300  # 5 دقائق

def get_cached_response():
    """استرجاع البيانات من التخزين المؤقت إذا لم تنتهِ مدة صلاحيتها"""
    try:
        with open(CACHE_FILE, "r") as file:
            data = json.load(file)
            if time.time() - data["timestamp"] < CACHE_EXPIRY:
                return data["response"]
    except (FileNotFoundError, json.JSONDecodeError):
        pass
    return None

def save_cache(response):
    """حفظ البيانات في التخزين المؤقت"""
    with open(CACHE_FILE, "w") as file:
        json.dump({"timestamp": time.time(), "response": response}, file)

@app.route("/proxy", methods=["GET"])
def proxy_request():
    """توجيه الطلبات إلى API Garena مع التخزين المؤقت"""
    cached_response = get_cached_response()
    if cached_response:
        return jsonify(cached_response)

    params = {
        "access_token": ACCESS_TOKEN,
        "app_server_id": request.args.get("app_server_id", 0),
        "open_id": request.args.get("open_id", "8f6a3c5891d92c1d7c6a03a882320b58"),
        "for_rebate_ids": "4620,90157,4621,90158,4619",
        "client_type": 2,
        "locale": "en_AE",
        "app_id": 100067,
        "app_role_id": 0,
        "platform": 4
    }

    response = requests.get(API_URL, params=params)
    if response.status_code == 200:
        save_cache(response.json())
    return jsonify(response.json())

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
