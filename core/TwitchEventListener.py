import os
import requests
import json
import asyncio
from aiohttp import web
import aiohttp
from dotenv import load_dotenv

load_dotenv()

CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
CALLBACK_URL = os.getenv("CALLBACK_URL")
BROADCASTER_LOGIN = os.getenv("BOT_LOGIN")
TWITCH_WEBHOOK_SECRET = os.getenv("TWITCH_WEBHOOK_SECRET", "supersecret123")

EVENTSUB_URL = "https://api.twitch.tv/helix/eventsub/subscriptions"

class TwitchEventListener:
    def __init__(self, on_cheer_callback=None):
        self.on_cheer_callback = on_cheer_callback
        self.app = web.Application()
        self.app.router.add_post('/a', self.handle_event)

    async def handle_event(self, request):
        body = await request.json()
        print("📥 Received from Twitch:", json.dumps(body, indent=2))

        # Verification challenge
        if body.get("challenge"):
            print("🎯 Responding to Twitch verification challenge")
            return web.Response(text=body["challenge"])

        # Event handling
        event_type = body.get("subscription", {}).get("type")
        event = body.get("event", {})

        if event_type == "channel.channel_points_custom_reward_redemption.add":
            user = event.get("user_name")
            reward_title = event.get("reward", {}).get("title", "")
            print(f"🎁 Redemption by: {user} | Reward: {reward_title}")

            if reward_title == "Corner Wars: Challenge":
                print("✅ Correct reward redeemed! Triggering game...")
                if self.on_cheer_callback:
                    await self.on_cheer_callback(user, None)
            else:
                print(f"⚠️ Redemption ignored (not Corner Wars): {reward_title}")

        return web.Response(status=200)

    def get_app_access_token(self):
        response = requests.post(
            "https://id.twitch.tv/oauth2/token",
            params={
                "client_id": CLIENT_ID,
                "client_secret": CLIENT_SECRET,
                "grant_type": "client_credentials"
            }
        )
        data = response.json()
        return data.get("access_token")

    def get_broadcaster_user_id(self, app_token, login):
        headers = {
            "Client-ID": CLIENT_ID,
            "Authorization": f"Bearer {app_token}"
        }
        resp = requests.get(
            "https://api.twitch.tv/helix/users",
            headers=headers,
            params={"login": login}
        )
        data = resp.json()
        return data["data"][0]["id"] if "data" in data and data["data"] else None

    async def ensure_subscription(self, session, headers, payload):
        # 1. List existing subscriptions
        async with session.get(EVENTSUB_URL, headers=headers) as resp:
            data = await resp.json()
            existing = data.get("data", [])

            # 2. Check if a matching subscription exists (type + broadcaster + callback)
            for sub in existing:
                if (
                    sub.get("type") == payload["type"]
                    and sub.get("condition", {}).get("broadcaster_user_id") == payload["condition"]["broadcaster_user_id"]
                    and sub.get("transport", {}).get("callback") == payload["transport"]["callback"]
                ):
                    print(f"✅ Subscription for {payload['type']} already exists, skipping.")
                    return

        # 3. If not found, create it
        async with session.post(EVENTSUB_URL, headers=headers, json=payload) as resp:
            rdata = await resp.json()
            if resp.status == 202:
                print(f"✅ Created subscription for {payload['type']}")
            else:
                print(f"❌ Failed to create subscription: {resp.status} {rdata}")

    async def start_server(self):
        app_token = self.get_app_access_token()
        user_id = self.get_broadcaster_user_id(app_token, BROADCASTER_LOGIN)
        if not user_id:
            print("❌ Could not get broadcaster ID.")
            return
        print(f"✅ Broadcaster user ID: {user_id}")

        headers = {
            "Client-ID": CLIENT_ID,
            "Authorization": f"Bearer {app_token}",
            "Content-Type": "application/json"
        }

        async with aiohttp.ClientSession() as session:
            # Channel points redemption subscription
            redemption_payload = {
                "type": "channel.channel_points_custom_reward_redemption.add",
                "version": "1",
                "condition": {"broadcaster_user_id": user_id},
                "transport": {
                    "method": "webhook",
                    "callback": CALLBACK_URL,
                    "secret": TWITCH_WEBHOOK_SECRET
                }
            }
            await self.ensure_subscription(session, headers, redemption_payload)

            # Cheer subscription
            cheer_payload = {
                "type": "channel.cheer",
                "version": "1",
                "condition": {"broadcaster_user_id": user_id},
                "transport": {
                    "method": "webhook",
                    "callback": CALLBACK_URL,
                    "secret": TWITCH_WEBHOOK_SECRET
                }
            }
            await self.ensure_subscription(session, headers, cheer_payload)

        print("✅ TwitchEventListener running at http://0.0.0.0:5000")
        runner = web.AppRunner(self.app)
        await runner.setup()
        site = web.TCPSite(runner, "0.0.0.0", 5000)
        await site.start()

        while True:
            await asyncio.sleep(3600)
