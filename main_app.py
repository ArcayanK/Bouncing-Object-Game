import asyncio
from core.GameManager import GameManager
from core.TwitchEventListener import TwitchEventListener
from core.websocket_trigger import WebSocketServer

class MainApp:
    def __init__(self):
        self.game_manager = GameManager()
        self.twitch_listener = TwitchEventListener(on_cheer_callback=self.on_cheer)
        self.websocket_server = WebSocketServer()  # 👈 create instance

    async def on_cheer(self, username: str, bits: int = None):
        print(f"🎉 Acknowledging {username}'s event! (bits: {bits})")
        await self.websocket_server.broadcast({
            "type": "start",
            "user": username
        })
        await self.game_manager.trigger_game(username)

    async def start(self):
        print("🚀 MainApp starting...")
        await asyncio.gather(
            self.twitch_listener.start_server(),
            self.websocket_server.start()  # 👈 run websocket concurrently
        )

if __name__ == "__main__":
    asyncio.run(MainApp().start())
