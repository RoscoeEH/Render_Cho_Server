import asyncio
import os
import websockets

# Store connected clients
connected_clients = set()

async def handle_client(websocket):
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

async def main():
    port = int(os.environ.get("PORT", 8080))  # Get PORT from Render
    async with websockets.serve(handle_client, "0.0.0.0", port):
        print(f"WebSocket server running on port {port}")
        await asyncio.Future()  # run forever

if __name__ == "__main__":
    asyncio.run(main())
