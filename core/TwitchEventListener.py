import os
import requests
import json
import asyncio
from aiohttp import web
from dotenv import load_dotenv

load_dotenv()

CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
CALLBACK_URL = os.getenv("CALLBACK_URL")
BROADCASTER_LOGIN = os.getenv("BOT_LOGIN")
TWITCH_WEBHOOK_SECRET = os.getenv("TWITCH_WEBHOOK_SECRET", "supersecret123")

class TwitchEventListener:
    def __init__(self, on_cheer_callback=None):
        self.on_cheer_callback = on_cheer_callback
        self.app = web.Application()
        self.app.router.add_post('/eventsub', self.handle_event)

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

            # ✅ Only trigger if reward title matches
            if reward_title == "Corner Wars: Challenge":
                print("✅ Correct reward redeemed! Triggering game...")
                if self.on_cheer_callback:
                    await self.on_cheer_callback(user, None)
            else:
                print(f"⚠️ Redemption ignored (not Corner Wars): {reward_title}")

        # # Handle ALL cheer events
        # if event_type == "channel.channel_points_custom_reward_redemption.add":
        #     user = event.get("user_name")
        #     print(f"🎁 Redemption by: {user}")
        #     if self.on_cheer_callback:
        #         await self.on_cheer_callback(user, None)

        # elif event_type == "channel.cheer":
        #     user = event.get("user_name")
        #     bits = event.get("bits")
        #     print(f"💎 Cheer by: {user} - {bits} bits")
        #     if self.on_cheer_callback:
        #         await self.on_cheer_callback(user, bits)

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

    def subscribe_to_eventsub(self, app_token, broadcaster_user_id):
        headers = {
            "Client-ID": CLIENT_ID,
            "Authorization": f"Bearer {app_token}",
            "Content-Type": "application/json"
        }

        def make_subscription(type_name, condition):
            return {
                "type": type_name,
                "version": "1",
                "condition": condition,
                "transport": {
                    "method": "webhook",
                    "callback": CALLBACK_URL,
                    "secret": TWITCH_WEBHOOK_SECRET
                }
            }

        subs = [
            make_subscription("channel.channel_points_custom_reward_redemption.add", {"broadcaster_user_id": broadcaster_user_id}),
            make_subscription("channel.cheer", {"broadcaster_user_id": broadcaster_user_id}),
        ]

        for sub in subs:
            r = requests.post("https://api.twitch.tv/helix/eventsub/subscriptions", headers=headers, json=sub)
            print("🔔 Subscription response:", r.status_code, r.text)

    async def start_server(self):
        app_token = self.get_app_access_token()
        user_id = self.get_broadcaster_user_id(app_token, BROADCASTER_LOGIN)
        if not user_id:
            print("❌ Could not get broadcaster ID.")
            return
        print(f"✅ Broadcaster user ID: {user_id}")
        self.subscribe_to_eventsub(app_token, user_id)
        print("✅ TwitchEventListener running at http://0.0.0.0:8080")
        runner = web.AppRunner(self.app)
        await runner.setup()
        site = web.TCPSite(runner, "0.0.0.0", 8080)
        await site.start()
        # keep running
        while True:
            await asyncio.sleep(3600)
