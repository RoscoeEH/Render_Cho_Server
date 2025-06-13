import asyncio
import os
import websockets
from websockets import WebSocketServerProtocol
from http import HTTPStatus

connected_clients = set()

async def handle_client(websocket: WebSocketServerProtocol):
    connected_clients.add(websocket)
    print("New client connected")
    try:
        async for message in websocket:
            for client in connected_clients:
                if client != websocket:
                    await client.send(message)
    finally:
        connected_clients.remove(websocket)
        print("Client disconnected")

async def handler(ws: WebSocketServerProtocol, path: str):
    if path == "/ws":
        await handle_client(ws)
    else:
        # Handle health check
        if ws.request_headers.get("Upgrade", "").lower() != "websocket":
            # Raw HTTP GET or HEAD to `/`
            await ws.send_http_response(
                HTTPStatus.OK,
                headers=[
                    ("Content-Type", "text/plain"),
                    ("Content-Length", "2"),
                    ("Connection", "close"),
                ],
                body=b"OK"
            )
        await ws.close()

async def main():
    port = int(os.environ.get("PORT", 8080))
    async with websockets.serve(handler, "0.0.0.0", port):
        print(f"Server running on port {port}")
        await asyncio.Future()  # Keep running

if __name__ == "__main__":
    asyncio.run(main())
