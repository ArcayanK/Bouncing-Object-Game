# twitch_trigger_bot.py
import asyncio
import json
import websockets
from twitchio.ext import commands
import os
from dotenv import load_dotenv

load_dotenv()

class Bot(commands.Bot):
    def __init__(self):
        super().__init__(
            token=os.getenv("TWITCH_TOKEN"),
            prefix='!',
            initial_channels=os.getenv("CHANNEL"),
            client_id=os.getenv("CLIENT_ID"),
            client_secret=os.getenv("CLIENT_SECRET"),
            bot_id=os.getenv("BOT_ID")
        )
        self.add_command(self.test_overlay)


    async def event_ready(self):
        user_info = await self.fetch_users(logins=[os.getenv("BOT_NICK")])
        print(f"✅ Logged in as | {user_info[0].display_name}")

    async def event_message(self, message):
        await self.handle_commands(message)

        if message.content.lower() == "!startgame":
            print(f"🚀 Triggered by {message.author.name}")
            await send_to_overlay(message.author.name)

    async def event_raw_usernotice(self, channel, tags):
        if tags.get("msg-id") == "reward-redeemed":
            user = tags.get("display-name")
            print(f"🎁 Channel point redemption by: {user}")
            await send_to_overlay(user)

        # Bits are handled in event_message via cheer messages
        elif tags.get("msg-id") == "cheer":
            user = tags.get("display-name")
            print(f"💎 Bits used by: {user}")
            await send_to_overlay(user)

    @commands.command(name="redeem")
    async def fake_redeem(self, ctx):
        await send_to_overlay(ctx.author.name)
        await ctx.send(f"{ctx.author.name} triggered the overlay manually for testing.")


            

async def send_to_overlay(username, retries=3, delay=2):
    event = {
        "type": "start",
        "user": username
    }

    for attempt in range(retries):
        try:
            async with websockets.connect("ws://localhost:8765") as ws:
                await ws.send(json.dumps(event))
                print(f"✅ Sent event to overlay: {username}")
                return
        except Exception as e:
            print(f"❌ Attempt {attempt + 1} failed: {e}")
            if attempt < retries - 1:
                await asyncio.sleep(delay)
            else:
                print(f"❌ Failed to send event after {retries} attempts.")

@commands.command(name="testoverlay")
async def test_overlay(self, ctx):
    await self.send_to_overlay(ctx.author.name)


if __name__ == "__main__":
    bot = Bot()
    bot.run()