import asyncio
import websockets
import json

async def simulate_corner_hit(user, corner):
    async with websockets.connect("ws://localhost:8765") as ws:
        message = {
            "type": "corner_hit",
            "user": user,
            "corner": corner
        }
        await ws.send(json.dumps(message))
        print(f"✅ Sent corner_hit for {user} at {corner}")

asyncio.run(simulate_corner_hit("TestUser02", "SW"))
