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

    async def event_ready(self):
        user_info = await self.fetch_users(logins=[os.getenv("BOT_NICK")])
        print(f"✅ Logged in as | {user_info[0].display_name}")


if __name__ == "__main__":
    bot = Bot()
    bot.run()
