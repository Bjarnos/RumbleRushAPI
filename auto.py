import requests, json, os, dotenv
from datetime import datetime
from time import sleep
dotenv.load_dotenv()

AUTH = None
USERNAME = os.environ.get('USERNAME')
PASSWORD = os.environ.get('PASSWORD')

quest_url = "https://us-central1-pocketrun-33bdc.cloudfunctions.net/v0270_quests/progressQuests"
purchase_url = "https://us-central1-pocketrun-33bdc.cloudfunctions.net/v0270_purchases/purchase"
adchest_url = "https://us-central1-pocketrun-33bdc.cloudfunctions.net/v0270_ads/claimAdChest"

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

relnow = None
timedheaders = headers.copy()
timedheaders["variants"] = json.dumps({
    "General":"0_270_web",
    "Gameplay":"default",
    "Cosmetics":"default",
    "Ranks":"default",
    "LootBoxes":"default",
    "Currencies":"default",
    "Shop":"0_250_web",
    "WinProgression":"default",
    "Items":"0_240_web",
    "PendingRewardUpgrades":"default",
    "Ads":"default",
    "TrophyLeaderboard":"default",
    "NewPlayerGifts":"default",
    "FriendReferral":"default",
    "PassConfigs":"0_270_web",
    "DailyQuests":"default",
    "Events":"0_270_web"
})

def update_reltime():
    global relnow
    relnow += 30
    timedheaders["time"] = datetime.fromtimestamp(relnow).strftime("%m/%d/%Y %H:%M:%S")

watched = 0
def watch_ad(data):
    global watched
    update_reltime()
    r = requests.post(purchase_url, headers=timedheaders, json=data, timeout=60)
    watched += 1
    if watched == 3:
        watched = 0
        requests.post(adchest_url, headers=timedheaders, timeout=60)
    return r

#requests.post(quest_url, headers=timedheaders, json={"questsToProgress":{"DailyQuests":{"quests.daily.tuesday.3":1.0}}}) # for real quests

schunks = 0
echunks = 0
while True:
    try:
        relnow = datetime.now().timestamp()
        AUTH = requests.post(
            f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key=AIzaSyDyBOKTSOCMvzJJsaf14eU9SezR0B12uPs",
            json={
                "clientType": "CLIENT_TYPE_WEB",
                "email": f"{USERNAME}@rumblerush.invalid",
                "password": PASSWORD,
                "returnSecureToken": True
            }).json()["idToken"]
        timedheaders["Authorization"] = f"Bearer {AUTH}"

        watch_ad({"purchaseItemId":"uncommon_lootbox.rv","purchaseSource":"Shop"})
        watch_ad({"purchaseItemId":"pack.freegems.1","purchaseSource":"Shop"})
        watch_ad({"purchaseItemId":"pack.freecoins.1","purchaseSource":"Shop"})

        watch_ad({"purchaseItemId":"uncommon_lootbox.rv","purchaseSource":"Shop"})
        watch_ad({"purchaseItemId":"pack.freegems.1","purchaseSource":"Shop"})
        watch_ad({"purchaseItemId":"pack.freecoins.1","purchaseSource":"Shop"})

        watch_ad({"purchaseItemId":"items_upgrade_rv","purchaseSource":"RandomizedItemUpgrade"})
        r = watch_ad({"purchaseItemId":"items_upgrade_rv","purchaseSource":"RandomizedItemUpgrade"})
        print(f"[0] Done with status {r.status_code}: {r.text}", flush=True)
        if r.status_code == 200:
            schunks += 1
        else:
            echunks += 1
    except Exception as e:
        print(f"[0] Errored: {e}", flush=True)

    sleep(7200)