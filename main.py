import os
from aiohttp import web, WSCloseCode

connected_clients = set()

async def websocket_handler(request):
    if request.path != "/ws":
        return web.Response(status=404, text="Not Found")

    ws = web.WebSocketResponse()
    await ws.prepare(request)

    connected_clients.add(ws)
    print("New client connected")

    try:
        async for msg in ws:
            if msg.type == web.WSMsgType.TEXT:
                # Broadcast the message to other clients
                for client in connected_clients:
                    if client != ws:
                        await client.send_str(msg.data)
            elif msg.type == web.WSMsgType.ERROR:
                print(f"WebSocket connection closed with exception {ws.exception()}")
    finally:
        connected_clients.remove(ws)
        print("Client disconnected")

    return ws

async def health_check_handler(request):
    return web.Response(text="OK")

async def create_app():
    app = web.Application()

    # Route health check on "/"
    app.router.add_get("/", health_check_handler)
    app.router.add_head("/", health_check_handler)  # support HEAD too

    # Route WebSocket on "/ws"
    app.router.add_get("/ws", websocket_handler)

    return app

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app = create_app()
    web.run_app(app, host="0.0.0.0", port=port)
