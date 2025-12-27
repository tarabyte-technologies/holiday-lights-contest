"""
Brick Breaker Game on the Christmas Tree!
- Platform at the bottom moves left/right
- Ball bounces and breaks bricks
- Bricks are horizontal bars of lights
"""
from lib.base_animation import BaseAnimation
from typing import Optional
from utils.geometry import POINTS_3D
import numpy as np

class BrickBreaker(BaseAnimation):
    """
    Classic Brick Breaker game displayed on the tree.
    Uses YZ plane (front view) for game coordinates.
    """
    
    def __init__(self, frameBuf: np.ndarray, *, 
                 fps: Optional[int] = 30,
                 ball_speed: float = 0.015,
                 paddle_speed: float = 0.02,
                 paddle_width: float = 0.15,
                 num_brick_rows: int = 4):
        super().__init__(frameBuf, fps=fps)
        
        self.ball_speed = ball_speed
        self.paddle_speed = paddle_speed
        self.paddle_width = paddle_width
        self.num_brick_rows = num_brick_rows
        
        # Center the points
        self.center = np.mean(POINTS_3D, axis=0)
        self.centered = POINTS_3D - self.center
        
        # Game coordinates: Y = horizontal, Z = vertical
        self.y = self.centered[:, 1]  # horizontal (-0.4 to 0.4)
        self.z = self.centered[:, 2]  # vertical (-0.45 to 0.62)
        
        # Normalize to game coordinates
        self.y_min, self.y_max = self.y.min(), self.y.max()
        self.z_min, self.z_max = self.z.min(), self.z.max()
        
        # Game boundaries
        self.left_wall = self.y_min + 0.05
        self.right_wall = self.y_max - 0.05
        self.top_wall = self.z_max - 0.05
        self.bottom = self.z_min + 0.05
        
        # Paddle
        self.paddle_y = 0.0  # Horizontal position (center)
        self.paddle_z = self.z_min + 0.12  # Just above bottom
        self.paddle_height = 0.06  # Taller paddle
        self.paddle_direction = 1  # 1 = right, -1 = left
        
        # Ball
        self.ball_y = 0.0
        self.ball_z = self.paddle_z + 0.15
        self.ball_vy = ball_speed * 0.7  # Horizontal velocity
        self.ball_vz = ball_speed  # Vertical velocity
        self.ball_radius = 0.05  # Larger ball for visibility
        
        # Bricks: rows of lights at different heights
        self.brick_z_positions = np.linspace(
            self.z_max - 0.1,  # Top
            self.z_max - 0.35,  # Lower
            num_brick_rows
        )
        self.brick_height = 0.06  # Thicker bricks
        self.bricks_active = [True] * num_brick_rows  # Track which rows are still active
        
        # Colors
        self.bg_color = np.array([5, 5, 20])  # Dark blue background
        self.paddle_color = np.array([255, 255, 255])  # White paddle
        self.ball_color = np.array([255, 255, 0])  # Yellow ball
        self.brick_colors = [
            np.array([255, 0, 0]),    # Red
            np.array([255, 127, 0]),  # Orange
            np.array([255, 255, 0]),  # Yellow
            np.array([0, 255, 0]),    # Green
            np.array([0, 255, 255]),  # Cyan
            np.array([0, 127, 255]),  # Blue
        ]
        
        self.game_over = False
        self.won = False
        self.win_animation_frames = 0  # Track win animation duration
        self.frame_count = 0
        
        print(f"Brick Breaker initialized!")
        print(f"Game area: Y=[{self.left_wall:.2f}, {self.right_wall:.2f}], Z=[{self.bottom:.2f}, {self.top_wall:.2f}]")
        print(f"Brick rows: {num_brick_rows}")
    
    def _move_paddle(self):
        """Move paddle automatically (follows ball with some lag)."""
        # Simple AI: move toward ball
        if self.ball_y > self.paddle_y + 0.02:
            self.paddle_y += self.paddle_speed
        elif self.ball_y < self.paddle_y - 0.02:
            self.paddle_y -= self.paddle_speed
        
        # Clamp to boundaries
        half_width = self.paddle_width / 2
        self.paddle_y = np.clip(self.paddle_y, self.left_wall + half_width, self.right_wall - half_width)
    
    def _move_ball(self):
        """Move ball and handle collisions."""
        # Move ball
        self.ball_y += self.ball_vy
        self.ball_z += self.ball_vz
        
        # Wall collisions
        if self.ball_y <= self.left_wall or self.ball_y >= self.right_wall:
            self.ball_vy = -self.ball_vy
            self.ball_y = np.clip(self.ball_y, self.left_wall, self.right_wall)
        
        if self.ball_z >= self.top_wall:
            self.ball_vz = -self.ball_vz
            self.ball_z = self.top_wall
        
        # Paddle collision
        if (self.ball_z <= self.paddle_z + self.paddle_height and 
            self.ball_z >= self.paddle_z - self.ball_radius and
            abs(self.ball_y - self.paddle_y) < self.paddle_width / 2):
            self.ball_vz = abs(self.ball_vz)  # Bounce up
            # Add some angle based on where ball hits paddle
            hit_pos = (self.ball_y - self.paddle_y) / (self.paddle_width / 2)
            self.ball_vy = hit_pos * self.ball_speed
        
        # Brick collisions
        for i, brick_z in enumerate(self.brick_z_positions):
            if not self.bricks_active[i]:
                continue
            
            # Check if ball hits this brick row
            if (self.ball_z >= brick_z - self.brick_height / 2 and 
                self.ball_z <= brick_z + self.brick_height / 2):
                self.bricks_active[i] = False
                self.ball_vz = -self.ball_vz
                break
        
        # Ball falls below paddle - reset
        if self.ball_z < self.bottom - 0.1:
            self._reset_ball()
        
        # Check win condition
        if not any(self.bricks_active) and not self.won:
            self.won = True
            self.win_animation_frames = 0  # Start win animation
    
    def _reset_ball(self):
        """Reset ball to starting position."""
        self.ball_y = self.paddle_y
        self.ball_z = self.paddle_z + 0.1
        self.ball_vz = abs(self.ball_vz)  # Go up
    
    def _reset_game(self):
        """Reset the entire game."""
        self.bricks_active = [True] * self.num_brick_rows
        self._reset_ball()
        self.won = False
        self.win_animation_frames = 0
    
    def renderNextFrame(self) -> None:
        """Render one frame of the game."""
        self.frame_count += 1
        
        # Handle win animation
        if self.won:
            self.win_animation_frames += 1
            win_duration = 90  # 3 seconds at 30fps
            
            if self.win_animation_frames >= win_duration:
                # Animation complete, reset game
                self._reset_game()
            else:
                # Show win celebration effect
                self._render_win_celebration()
                return
        
        # Update game state
        self._move_paddle()
        self._move_ball()
        
        # Clear to background
        self.frameBuf[:] = self.bg_color
        
        # Draw bricks (horizontal bars)
        for i, brick_z in enumerate(self.brick_z_positions):
            if not self.bricks_active[i]:
                continue
            
            # Find all points in this brick row
            in_brick = (np.abs(self.z - brick_z) < self.brick_height / 2)
            color = self.brick_colors[i % len(self.brick_colors)]
            self.frameBuf[in_brick] = color
        
        # Draw paddle
        in_paddle = (
            (np.abs(self.y - self.paddle_y) < self.paddle_width / 2) &
            (np.abs(self.z - self.paddle_z) < self.paddle_height / 2)
        )
        self.frameBuf[in_paddle] = self.paddle_color
        
        # Draw ball
        ball_dist = np.sqrt((self.y - self.ball_y)**2 + (self.z - self.ball_z)**2)
        in_ball = ball_dist < self.ball_radius
        self.frameBuf[in_ball] = self.ball_color
    
    def _render_win_celebration(self):
        """Render a celebration effect when the game is won."""
        from utils.colors import hsv_to_rgb_numpy
        
        # Create a smooth rainbow effect with slow transitions
        center_y = 0.0
        center_z = (self.z_min + self.z_max) / 2
        
        # Calculate distance from center for each point (vectorized)
        distances = np.sqrt((self.y - center_y)**2 + (self.z - center_z)**2)
        max_dist = np.max(distances)
        
        # Calculate angles for rainbow effect (vectorized)
        angles = np.arctan2(self.z - center_z, self.y - center_y)
        
        # Slow hue rotation - much slower transition
        hue_rotation_speed = 0.005  # Very slow rotation
        hue_base = (angles / (2 * np.pi) + self.win_animation_frames * hue_rotation_speed) % 1.0
        
        # Create slow expanding waves
        wave_speed = 0.003  # Much slower wave expansion
        wave_offset = self.win_animation_frames * wave_speed
        wave_period = max_dist * 2.0  # Longer period for smoother transitions
        
        # Three expanding waves offset from each other
        wave1_dist = (wave_offset) % wave_period
        wave2_dist = (wave_offset + max_dist * 0.4) % wave_period
        wave3_dist = (wave_offset + max_dist * 0.8) % wave_period
        
        # Distance from each wave (vectorized)
        wave1_diff = np.abs(distances - wave1_dist)
        wave2_diff = np.abs(distances - wave2_dist)
        wave3_diff = np.abs(distances - wave3_dist)
        
        # Wider, smoother waves with gradual falloff
        wave_width = 0.25  # Wider waves for smoother transitions
        brightness1 = np.maximum(0, 1.0 - (wave1_diff / wave_width))
        brightness2 = np.maximum(0, 1.0 - (wave2_diff / wave_width))
        brightness3 = np.maximum(0, 1.0 - (wave3_diff / wave_width))
        
        # Combine waves smoothly
        brightness = np.maximum(np.maximum(brightness1, brightness2), brightness3)
        
        # Very gentle pulsing - much slower and subtler
        pulse_speed = 0.03  # Very slow pulse
        pulse = 0.7 + 0.3 * np.sin(self.win_animation_frames * pulse_speed)
        final_brightness = brightness * pulse
        
        # Ensure minimum brightness so it's always visible
        final_brightness = np.maximum(final_brightness, 0.3)
        
        # Create HSV array
        saturation = np.ones_like(hue_base) * 0.9  # Slightly less saturated for smoother look
        hsv = np.column_stack([hue_base, saturation, final_brightness])
        
        # Convert to RGB (vectorized)
        rgb = hsv_to_rgb_numpy(hsv)
        self.frameBuf[:] = (rgb * 255).astype(np.uint8)
