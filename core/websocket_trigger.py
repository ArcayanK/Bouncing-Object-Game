# websocket_trigger.py
import asyncio
import websockets
import json
from database.db_manager import update_corner_lord, check_for_corner_king, update_corner_king
import sqlite3


connected = set()

async def handler(websocket):
    connected.add(websocket)

    # send current corner lords immediately
    conn = sqlite3.connect("game_stats.db")
    c = conn.cursor()
    c.execute("SELECT corner, username FROM GameHierarchy")
    data = { row[0]: row[1] for row in c.fetchall() }
    conn.close()
    await websocket.send(json.dumps({"type": "corner_lords_snapshot", "data": data}))

    try:
        async for message in websocket:
            print(f"🔁 Received message: {message}")
            data = json.loads(message)

            # 👇 NEW: handle corner hit events
            if data.get("type") == "corner_hit":
                user = data.get("user")
                corner = data.get("corner")
                print(f"🟢 Corner hit by {user} at {corner}")

                update_corner_lord(user, corner)
                king = check_for_corner_king()
                if king:
                    update_corner_king(king)

            # broadcast to other clients as before
            for conn in connected:
                if conn != websocket:
                    await conn.send(message)
    finally:
        connected.remove(websocket)

async def main():
    server = await websockets.serve(handler, "localhost", 8765)
    print("✅ WebSocket server running on ws://localhost:8765")

    while True:
        await asyncio.sleep(1)

asyncio.run(main())


