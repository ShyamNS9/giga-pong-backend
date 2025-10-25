from pydantic import BaseModel
from typing import Optional
import random


class Paddle(BaseModel):
    """Represents a player's paddle"""
    x: float
    y: float
    width: float = 10
    height: float = 100
    speed: float = 5
    player_side: str = "left"  # "left" for player1, "right" for player2

    def move_up(self, canvas_height: float):
        """Move paddle up with boundary check"""
        self.y = max(0, self.y - self.speed)

    def move_down(self, canvas_height: float):
        """Move paddle down with boundary check"""
        self.y = min(canvas_height - self.height, self.y + self.speed)

    def move_left(self, canvas_width: float):
        """Move paddle left with boundary check
        Player 1 (left side): Can move from x=0 to middle
        Player 2 (right side): Can move from middle to their starting position
        """
        if self.player_side == "left":
            # Player 1: stay on left half, minimum x = 0
            self.x = max(0, self.x - self.speed)
        else:
            # Player 2: stay on right half, minimum x = middle
            middle = canvas_width / 2
            self.x = max(middle, self.x - self.speed)

    def move_right(self, canvas_width: float):
        """Move paddle right with boundary check
        Player 1 (left side): Can move from x=0 to middle
        Player 2 (right side): Can move from middle to edge
        """
        if self.player_side == "left":
            # Player 1: stay on left half, maximum x = middle - paddle width
            middle = canvas_width / 2
            self.x = min(middle - self.width, self.x + self.speed)
        else:
            # Player 2: stay on right half, maximum x = canvas edge - paddle width
            self.x = min(canvas_width - self.width, self.x + self.speed)


class Ball(BaseModel):
    """Represents the game ball"""
    x: float
    y: float
    radius: float = 8
    velocity_x: float = 3
    velocity_y: float = 3
    speed: float = 3

    def reset(self, canvas_width: float, canvas_height: float):
        """Reset ball to center with random direction at varied angles

        Uses angle-based randomization for more interesting ball trajectories:
        - Horizontal direction: randomly left or right
        - Vertical angle: random between -60° and +60° from horizontal
        - This creates varied but fair starting angles
        """
        import math

        self.x = canvas_width / 2
        self.y = canvas_height / 2

        # Random horizontal direction (left or right)
        direction = random.choice([-1, 1])

        # Random angle between -60 and +60 degrees (in radians)
        # This prevents the ball from going too vertically (which would be boring)
        angle = random.uniform(-math.pi/3, math.pi/3)  # -60° to +60°

        # Calculate velocity components based on angle
        # speed is the magnitude, angle determines the direction
        self.velocity_x = self.speed * direction * math.cos(angle)
        self.velocity_y = self.speed * math.sin(angle)

    def update_position(self):
        """Update ball position based on velocity"""
        self.x += self.velocity_x
        self.y += self.velocity_y

    def reverse_x(self):
        """Reverse horizontal direction"""
        self.velocity_x *= -1

    def reverse_y(self):
        """Reverse vertical direction"""
        self.velocity_y *= -1


class GameState(BaseModel):
    """Represents the complete game state"""
    canvas_width: float = 800
    canvas_height: float = 600
    paddle1: Paddle
    paddle2: Paddle
    ball: Ball
    score1: int = 0
    score2: int = 0
    game_active: bool = False
    player1_connected: bool = False
    player2_connected: bool = False

    class Config:
        arbitrary_types_allowed = True

    @classmethod
    def create_initial_state(cls) -> "GameState":
        """Create initial game state with default positions"""
        canvas_width = 800
        canvas_height = 600

        # Player 1 paddle (left side)
        paddle1 = Paddle(
            x=20,
            y=canvas_height / 2 - 50,
            player_side="left"
        )

        # Player 2 paddle (right side)
        paddle2 = Paddle(
            x=canvas_width - 30,
            y=canvas_height / 2 - 50,
            player_side="right"
        )

        # Ball at center with randomized initial direction
        ball = Ball(
            x=canvas_width / 2,
            y=canvas_height / 2
        )
        # Randomize initial ball direction
        ball.reset(canvas_width, canvas_height)

        return cls(
            canvas_width=canvas_width,
            canvas_height=canvas_height,
            paddle1=paddle1,
            paddle2=paddle2,
            ball=ball
        )

    def to_dict(self):
        """Convert game state to dictionary for JSON serialization"""
        return {
            "canvas_width": self.canvas_width,
            "canvas_height": self.canvas_height,
            "paddle1": {
                "x": self.paddle1.x,
                "y": self.paddle1.y,
                "width": self.paddle1.width,
                "height": self.paddle1.height
            },
            "paddle2": {
                "x": self.paddle2.x,
                "y": self.paddle2.y,
                "width": self.paddle2.width,
                "height": self.paddle2.height
            },
            "ball": {
                "x": self.ball.x,
                "y": self.ball.y,
                "radius": self.ball.radius
            },
            "score1": self.score1,
            "score2": self.score2,
            "game_active": self.game_active,
            "player1_connected": self.player1_connected,
            "player2_connected": self.player2_connected
        }
