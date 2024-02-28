from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse
from fastapi import Request, WebSocketDisconnect
from fastapi.templating import Jinja2Templates

app = FastAPI()

# Store connected clients
connected_clients = set()

# Templates for rendering HTML page
templates = Jinja2Templates(directory="templates")


@app.get("/")
async def get():
    return HTMLResponse(content="This is a WebSocket chat server. Open the WebSocket in your browser.")


@app.get("/ws/{client_id}")
async def get_ws(request: Request, client_id: int):
    return templates.TemplateResponse("ws.html", {"request": request, "client_id": client_id})


@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: int):
    await websocket.accept()

    # Add the client to the set of connected clients
    connected_clients.add(websocket)

    try:
        while True:
            data = await websocket.receive_text()
            message = f"Message from {client_id}: {data}"

            # Broadcast the message to all connected clients
            for client in connected_clients:
                await client.send_text(message)
    except WebSocketDisconnect:
        print(f"WebSocket connection for {client_id} closed.")
    finally:
        # Remove the client from the set upon disconnect
        connected_clients.remove(websocket)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
