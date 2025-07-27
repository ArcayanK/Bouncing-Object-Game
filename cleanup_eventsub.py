import os
import requests
from dotenv import load_dotenv

# ✅ Load credentials from .env
load_dotenv()
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")

# ✅ Step 1: Get an app access token
print("🔑 Getting app access token...")
resp = requests.post(
    "https://id.twitch.tv/oauth2/token",
    params={
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "grant_type": "client_credentials"
    }
)
resp.raise_for_status()
access_token = resp.json()["access_token"]
print(f"✅ Access token acquired.")

# ✅ Step 2: Get current subscriptions
headers = {
    "Client-ID": CLIENT_ID,
    "Authorization": f"Bearer {access_token}"
}

print("📋 Fetching current subscriptions...")
subs_resp = requests.get("https://api.twitch.tv/helix/eventsub/subscriptions", headers=headers)
subs_resp.raise_for_status()
data = subs_resp.json()

if not data.get("data"):
    print("✅ No existing subscriptions found.")
    exit()

# ✅ Step 3: List and delete subscriptions
for sub in data["data"]:
    sub_id = sub["id"]
    type_name = sub["type"]
    condition = sub["condition"]
    callback = sub.get("transport", {}).get("callback")
    print(f"🗑️ Deleting subscription: {sub_id} | {type_name} | {condition} | {callback}")

    delete_resp = requests.delete(
        f"https://api.twitch.tv/helix/eventsub/subscriptions?id={sub_id}",
        headers=headers
    )
    if delete_resp.status_code == 204:
        print(f"✅ Deleted {sub_id}")
    else:
        print(f"⚠️ Failed to delete {sub_id}: {delete_resp.status_code} {delete_resp.text}")

print("✨ Cleanup complete.")
