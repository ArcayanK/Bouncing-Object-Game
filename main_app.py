import asyncio
from aiohttp import web
from core.GameManager import GameManager
from core.TwitchEventListener import TwitchEventListener

class MainApp:
    def __init__(self):
        self.game_manager = GameManager()
        self.twitch_listener = TwitchEventListener(on_cheer_callback=self.on_cheer)

    async def on_cheer(self, username: str, bits: int = None):
        """Called whenever TwitchEventListener detects a cheer or reward redemption."""
        print(f"🎉 Acknowledging {username}'s event! (bits: {bits})")
        # Activate the bouncing object game
        await self.game_manager.trigger_game(username)

    async def start(self):
        """Start Twitch listener (and any other systems if needed)."""
        print("🚀 MainApp starting...")
        await self.twitch_listener.start_server()


if __name__ == "__main__":
    app = MainApp()
    asyncio.run(app.start())
