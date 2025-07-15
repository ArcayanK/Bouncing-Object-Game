# GameManager.py
import asyncio
import json
import websockets
from database.db_manager import record_attempt

class GameManager:
    def __init__(self, websocket_uri="ws://localhost:8765"):
        self.websocket_uri = websocket_uri

    async def trigger_game(self, username: str):
        # Print the username for your logs
        print(f"🎮 Game triggered by: {username}")

        # ✅ Always record an attempt here
        record_attempt(username)

        # Prepare event message
        event = {
            "type": "start",
            "user": username
        }

        # Send event to overlay
        try:
            async with websockets.connect(self.websocket_uri) as ws:
                await ws.send(json.dumps(event))
                print(f"✅ Sent start event to overlay for {username}")
        except Exception as e:
            print(f"❌ Failed to send event: {e}")
