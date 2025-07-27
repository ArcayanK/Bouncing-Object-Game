import asyncio
import websockets
import json
import sqlite3
from database.db_manager import update_corner_lord, check_for_corner_king, update_corner_king

class WebSocketServer:
    def __init__(self, host: str = "localhost", port: int = 8765, db_path: str = "game_stats.db"):
        self.host = host
        self.port = port
        self.db_path = db_path
        self.connected = set()

    async def send_current_corner_lords(self, websocket):
        """Send the current state of corner lords to a newly connected client."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("SELECT corner, username FROM GameHierarchy")
        data = {row[0]: row[1] for row in c.fetchall()}
        conn.close()
        await websocket.send(json.dumps({"type": "corner_lords_snapshot", "data": data}))

    async def handler(self, websocket):
        self.connected.add(websocket)
        await self.send_current_corner_lords(websocket)  # send snapshot immediately

        try:
            async for message in websocket:
                print(f"🔁 Received message: {message}")
                data = json.loads(message)

                if data.get("type") == "corner_hit":
                    user = data.get("user")
                    corner = data.get("corner")
                    print(f"🟢 Corner hit by {user} at {corner}")

                    # Update DB
                    update_corner_lord(user, corner)
                    king = check_for_corner_king()
                    if king:
                        update_corner_king(king)

                    # 🔥 Build updated snapshot (lords + king)
                    conn = sqlite3.connect(self.db_path)
                    c = conn.cursor()
                    c.execute("SELECT corner, username FROM GameHierarchy")
                    lords_data = {row[0]: row[1] for row in c.fetchall()}
                    conn.close()

                    broadcast_payload = {
                        "type": "corner_update",
                        "corner_lords": lords_data,
                        "corner_king": king
                    }
                    # Broadcast to *all* clients
                    for conn_ws in list(self.connected):
                        try:
                            await conn_ws.send(json.dumps(broadcast_payload))
                        except Exception as e:
                            print(f"❌ Failed to send to a client: {e}")
        finally:
            self.connected.remove(websocket)

    async def broadcast(self, message: dict):
        """Broadcast a message to all connected clients."""
        if not self.connected:
            print("⚠️ No connected clients to broadcast to.")
            return

        payload = json.dumps(message)
        print(f"📡 Broadcasting to {len(self.connected)} clients: {payload}")

        # Send to each connected websocket
        for ws in list(self.connected):
            try:
                await ws.send(payload)
            except Exception as e:
                print(f"❌ Failed to send to a client: {e}")



    async def start(self):
        """Start the websocket server and keep it running."""
        server = await websockets.serve(self.handler, self.host, self.port)
        print(f"✅ WebSocket server running on ws://{self.host}:{self.port}")
        await asyncio.Future()  # run forever


# No asyncio.run() here — we’ll run WebSocketServer().start() from main_app.py
