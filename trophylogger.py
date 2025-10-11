import requests, os, dotenv
from time import sleep
dotenv.load_dotenv()

AUTH = None
USERNAME = os.environ.get('USERNAME')
PASSWORD = os.environ.get('PASSWORD')
WEBHOOK_URL = os.environ.get('WEBHOOK')

login_url = "https://us-central1-pocketrun-33bdc.cloudfunctions.net/v0280_login/login"

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

def send_discord_message(content: str):
    try:
        requests.post(WEBHOOK_URL, json={"content": content}, timeout=10)
    except Exception as e:
        print(f"[1] Error while sending Discord message: {e}")

savedtrophies = -1
while True:
    AUTH = requests.post(
        f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key=AIzaSyDyBOKTSOCMvzJJsaf14eU9SezR0B12uPs",
        json={
            "clientType": "CLIENT_TYPE_WEB",
            "email": f"{USERNAME}@rumblerush.invalid",
            "password": PASSWORD,
            "returnSecureToken": True
        }).json()["idToken"]
    headers["Authorization"] = f"Bearer {AUTH}"

    r = requests.post(login_url, headers=headers, timeout=60)
    if r.status_code == 200:
        trophies = r.json()["Rank"]["Xp"]
        if trophies != savedtrophies:
            diff = trophies - savedtrophies if savedtrophies != -1 else 0
            msg = f"🏆 **Trophies updated!** Now at `{trophies}` (+{diff})."
            print(msg, flush=True)
            send_discord_message(msg)
            savedtrophies = trophies
    else:
        print(f"[1] Failed to fetch trophies!\nStatus: {r.status_code}\nText: {r.text}", flush=True)
        
    sleep(10)