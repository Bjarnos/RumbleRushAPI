# test with uvicorn app:app --reload
from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
import requests, asyncio, time, os, dotenv
dotenv.load_dotenv()

CACHE_TTL = 60

USERNAME = os.environ.get('USERNAME')
PASSWORD = os.environ.get('PASSWORD')
WEBHOOK_URL = os.environ.get('WEBHOOK')
VERSION = os.environ.get('API_VERSION')

LEADERBOARD_URL = f"https://us-central1-pocketrun-33bdc.cloudfunctions.net/{VERSION}_maps/getTimeTrialLeaderboards"

headers = {
    "Accept": "*/*",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Accept-Language": "en-US,en;q=0.5",
    "Connection": "keep-alive",
    "Content-Type": "application/json",
    "Host": "us-central1-pocketrun-33bdc.cloudfunctions.net",
    "Origin": "https://rumblerush.io",
    "Referer": "https://rumblerush.io/",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "cross-site",
    "TE": "trailers",
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:143.0) Gecko/20100101 Firefox/143.0",
}

def set_auth():
    auth = requests.post(
        f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key=AIzaSyDyBOKTSOCMvzJJsaf14eU9SezR0B12uPs",
        json={
            "clientType": "CLIENT_TYPE_WEB",
            "email": f"{USERNAME}@rumblerush.invalid",
            "password": PASSWORD,
            "returnSecureToken": True
        }).json()["idToken"]
    headers["Authorization"] = f"Bearer {auth}"
    
set_auth()

app = FastAPI()

cache = {}
def cache_get(item, ttl):
    now = time.time()
    if cache[item] and cache[item]["data"] and now - cache[item]["timestamp"] < ttl:
        return cache[item]["data"]
    else:
        return False
    
def cache_set(item, data):
    cache[item]["data"] = data
    cache[item]["timestamp"] = time.time()

@app.get("/")
async def root():
    return "Hi!"

async def fetch_leaderboard():
    response = requests.post(LEADERBOARD_URL, headers=headers)
    response.raise_for_status()
    return response.json()

@app.get("/leaderboards")
async def get_leaderboards(bypass: str = Query(None, description="Use 'bypass' to ignore cache")):
    try:
        cached = cache_get("leaderboards", bypass == "bypass" and 1 or CACHE_TTL)
        if cached:
            return JSONResponse(content=cached)
        
        data = await fetch_leaderboard()
        cache_set("leaderboards", data)
        return JSONResponse(content=data)
    except requests.RequestException as e:
        print(f"Failed to fetch leaderboards: {e}", flush=True)
        return JSONResponse(content={"error": "Failed to fetch leaderboards"}, status_code=500)