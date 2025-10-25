from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.services.game_manager import manager
import json

router = APIRouter()


@router.websocket("/ws/{player_id}")
async def websocket_endpoint(websocket: WebSocket, player_id: str):
    """
    WebSocket endpoint for game connections
    player_id should be either 'player1' or 'player2'
    """
    # Validate player_id
    if player_id not in ["player1", "player2"]:
        await websocket.close(code=1008, reason="Invalid player_id. Must be 'player1' or 'player2'")
        return

    # Check if player slot is already taken
    if player_id in manager.active_connections:
        await websocket.close(code=1008, reason=f"{player_id} is already connected")
        return

    # Connect the player
    await manager.connect(websocket, player_id)

    # Send initial connection confirmation
    await manager.send_personal_message({
        "type": "connected",
        "player_id": player_id,
        "message": f"Connected as {player_id}"
    }, player_id)

    # Send initial game state
    if manager.game_state:
        await manager.send_personal_message({
            "type": "game_state",
            "data": manager.game_state.to_dict()
        }, player_id)

    try:
        while True:
            # Receive messages from client
            data = await websocket.receive_text()
            message = json.loads(data)

            # Handle different message types
            if message["type"] == "input":
                # Player input (UP or DOWN)
                action = message.get("action")
                manager.handle_player_input(player_id, action)

            elif message["type"] == "reset":
                # Reset game
                manager.reset_game()
                await manager.broadcast({
                    "type": "game_state",
                    "data": manager.game_state.to_dict()
                })

    except WebSocketDisconnect:
        manager.disconnect(player_id)
        await manager.broadcast({
            "type": "player_disconnected",
            "player_id": player_id,
            "message": f"{player_id} disconnected"
        })
    except Exception as e:
        print(f"Error in websocket for {player_id}: {e}")
        manager.disconnect(player_id)


@router.get("/status")
async def game_status():
    """Get current game status"""
    if manager.game_state:
        return {
            "game_active": manager.game_state.game_active,
            "player1_connected": manager.game_state.player1_connected,
            "player2_connected": manager.game_state.player2_connected,
            "score1": manager.game_state.score1,
            "score2": manager.game_state.score2
        }
    return {
        "game_active": False,
        "player1_connected": False,
        "player2_connected": False,
        "score1": 0,
        "score2": 0
    }
