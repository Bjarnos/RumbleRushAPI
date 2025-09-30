# test with uvicorn app:app --reload
from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
import requests, asyncio, time, os, dotenv
dotenv.load_dotenv()

API_KEY = os.environ.get('API_KEY')
LEADERBOARD_URL = "https://us-central1-pocketrun-33bdc.cloudfunctions.net/v0270_maps/getTimeTrialLeaderboards"

headers = {
    "Accept": "*/*",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Accept-Language": "en-US,en;q=0.5",
    "Authorization": f"Bearer {API_KEY}",
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

app = FastAPI()

cache = {
    "data": None,
    "timestamp": 0
}
CACHE_TTL = 60

def fetch_leaderboard():
    response = requests.post(LEADERBOARD_URL, headers=headers)
    response.raise_for_status()
    return response.json()

@app.get("/")
async def root():
    return "Hi!"

@app.get("/leaderboards")
async def get_leaderboards(cache: str = Query(None, description="Use 'bypass' to ignore cache")):
    now = time.time()
    
    bypass_cache = cache == "bypass"
    
    if cache["data"] and not bypass_cache and now - cache["timestamp"] < CACHE_TTL:
        return JSONResponse(content=cache["data"])
    
    try:
        data = await asyncio.to_thread(fetch_leaderboard)
        cache["data"] = data
        cache["timestamp"] = now
        return JSONResponse(content=data)
    except requests.RequestException as e:
        if cache["data"]:
            return JSONResponse(content=cache["data"], status_code=503)
        print(f"Failed to fetch leaderboard: {e}", flush=True)
        return JSONResponse(content={"error": "Failed to fetch leaderboard"}, status_code=500)