from fastapi import WebSocket
from typing import Dict, Optional
import asyncio
import json
from app.models.game import GameState


class ConnectionManager:
    """Manages WebSocket connections for the Pong game"""

    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.game_state: Optional[GameState] = None
        self.game_loop_task: Optional[asyncio.Task] = None

    async def connect(self, websocket: WebSocket, player_id: str):
        """Accept a new WebSocket connection"""
        await websocket.accept()
        self.active_connections[player_id] = websocket

        # Initialize game state if this is the first connection
        if self.game_state is None:
            self.game_state = GameState.create_initial_state()

        # Update player connection status
        if player_id == "player1":
            self.game_state.player1_connected = True
        elif player_id == "player2":
            self.game_state.player2_connected = True

        # Start game if both players are connected
        if self.game_state.player1_connected and self.game_state.player2_connected:
            self.game_state.game_active = True
            # Start game loop if not already running
            if self.game_loop_task is None or self.game_loop_task.done():
                self.game_loop_task = asyncio.create_task(self.game_loop())

    def disconnect(self, player_id: str):
        """Remove a WebSocket connection"""
        if player_id in self.active_connections:
            del self.active_connections[player_id]

        # Update player connection status
        if self.game_state:
            if player_id == "player1":
                self.game_state.player1_connected = False
            elif player_id == "player2":
                self.game_state.player2_connected = False

            # Pause game if a player disconnects
            if not (self.game_state.player1_connected and self.game_state.player2_connected):
                self.game_state.game_active = False

    async def broadcast(self, message: dict):
        """Send message to all connected clients"""
        disconnected = []
        for player_id, connection in self.active_connections.items():
            try:
                await connection.send_json(message)
            except Exception as e:
                print(f"Error sending to {player_id}: {e}")
                disconnected.append(player_id)

        # Clean up disconnected clients
        for player_id in disconnected:
            self.disconnect(player_id)

    async def send_personal_message(self, message: dict, player_id: str):
        """Send message to a specific client"""
        if player_id in self.active_connections:
            try:
                await self.active_connections[player_id].send_json(message)
            except Exception as e:
                print(f"Error sending to {player_id}: {e}")
                self.disconnect(player_id)

    def handle_player_input(self, player_id: str, action: str):
        """Process player input (4-directional movement)"""
        if not self.game_state:
            return

        if player_id == "player1":
            if action == "UP":
                self.game_state.paddle1.move_up(self.game_state.canvas_height)
            elif action == "DOWN":
                self.game_state.paddle1.move_down(self.game_state.canvas_height)
            elif action == "LEFT":
                self.game_state.paddle1.move_left(self.game_state.canvas_width)
            elif action == "RIGHT":
                self.game_state.paddle1.move_right(self.game_state.canvas_width)
        elif player_id == "player2":
            if action == "UP":
                self.game_state.paddle2.move_up(self.game_state.canvas_height)
            elif action == "DOWN":
                self.game_state.paddle2.move_down(self.game_state.canvas_height)
            elif action == "LEFT":
                self.game_state.paddle2.move_left(self.game_state.canvas_width)
            elif action == "RIGHT":
                self.game_state.paddle2.move_right(self.game_state.canvas_width)

    def update_ball_physics(self):
        """Update ball position and handle collisions"""
        if not self.game_state or not self.game_state.game_active:
            return

        ball = self.game_state.ball
        paddle1 = self.game_state.paddle1
        paddle2 = self.game_state.paddle2

        # Update ball position
        ball.update_position()

        # Check top and bottom boundaries
        if ball.y - ball.radius <= 0 or ball.y + ball.radius >= self.game_state.canvas_height:
            ball.reverse_y()

        # Check collision with paddle 1 (left)
        if (ball.x - ball.radius <= paddle1.x + paddle1.width and
            ball.y >= paddle1.y and
            ball.y <= paddle1.y + paddle1.height and
            ball.velocity_x < 0):
            ball.reverse_x()

        # Check collision with paddle 2 (right)
        if (ball.x + ball.radius >= paddle2.x and
            ball.y >= paddle2.y and
            ball.y <= paddle2.y + paddle2.height and
            ball.velocity_x > 0):
            ball.reverse_x()

        # Check if ball goes out of bounds (scoring)
        if ball.x - ball.radius <= 0:
            # Player 2 scores
            self.game_state.score2 += 1
            ball.reset(self.game_state.canvas_width, self.game_state.canvas_height)
        elif ball.x + ball.radius >= self.game_state.canvas_width:
            # Player 1 scores
            self.game_state.score1 += 1
            ball.reset(self.game_state.canvas_width, self.game_state.canvas_height)

    async def game_loop(self):
        """Main game loop - runs at ~60 FPS"""
        while True:
            if self.game_state and self.game_state.game_active:
                # Update game physics
                self.update_ball_physics()

                # Broadcast game state to all clients
                await self.broadcast({
                    "type": "game_state",
                    "data": self.game_state.to_dict()
                })

            # Run at approximately 60 FPS
            await asyncio.sleep(1 / 60)

    def reset_game(self):
        """Reset game to initial state"""
        if self.game_state:
            self.game_state = GameState.create_initial_state()
            self.game_state.player1_connected = "player1" in self.active_connections
            self.game_state.player2_connected = "player2" in self.active_connections
            self.game_state.game_active = (
                self.game_state.player1_connected and
                self.game_state.player2_connected
            )


# Global connection manager instance
manager = ConnectionManager()
