# trigger_overlay.py
import asyncio
import websockets
import json

async def trigger():
    uri = "ws://localhost:8765"
    async with websockets.connect(uri) as websocket:
        print("✅ Connected to WebSocket")
        await websocket.send("start")
        print("🚀 Sent 'start' message")

        event = {
            "type": "start",
            "user": "CoolViewer123"
        }
        await websocket.send(json.dumps(event))
        print("Sent trigger with username")

asyncio.run(trigger())

