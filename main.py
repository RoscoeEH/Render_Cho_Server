import asyncio
import os
import websockets
from websockets import WebSocketServerProtocol
from http import HTTPStatus
from urllib.parse import urlparse

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
        # Reject WebSocket upgrade on other paths
        await ws.close()

async def health_check(reader, writer):
    data = await reader.read(1024)
    request_line = data.splitlines()[0].decode()
    method, path, _ = request_line.split()

    if method in ("GET", "HEAD") and path == "/":
        response = (
            "HTTP/1.1 200 OK\r\n"
            "Content-Type: text/plain\r\n"
            "Content-Length: 2\r\n"
            "Connection: close\r\n"
            "\r\n"
            "OK"
        )
        writer.write(response.encode())
        await writer.drain()

    writer.close()
    await writer.wait_closed()

async def main():
    port = int(os.environ.get("PORT", 8080))

    # Start a raw TCP listener to check for HTTP requests (Render sends HEAD/GET to /)
    http_server = await asyncio.start_server(health_check, host="0.0.0.0", port=port)

    # Start WebSocket server separately using same port and a different path
    ws_server = await websockets.serve(
        handler, sock=http_server.sockets[0]
    )

    print(f"Server running on port {port}")
    await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())
