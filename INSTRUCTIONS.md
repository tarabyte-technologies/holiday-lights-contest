# Holiday Lights Contest - Development Instructions

**Current Project:** Brick Breaker Game  
**Designed by:** Pat "seeknay" (from TikTok)  
**Created with:** Cursor AI Assistant  
**Purpose:** For fun and learning - NOT a contest entry

---

## Project Overview

This is a Python-based animation framework for creating 3D light animations for a programmable Christmas tree with 500 LEDs. The current implementation is a fully playable Brick Breaker game that showcases advanced 3D spatial programming, game physics, and AI-controlled gameplay.

This project was created as a learning experience exploring LED programming, spatial algorithms, and AI-assisted development. Feel free to use and learn from this code!

**Key Details:**
- **NUM_PIXELS**: 500 (hardcoded in `lib/constants.py`)
- **Python Version**: 3.10 or higher
- **Main Dependencies**: numpy, matplotlib, typeguard
- **Contest Deadline**: January 11, 2026 at 11:59 pm (not participating for prizes)

## Project Structure

```
.
├── animation.py              # Main animation file (current: Brick Breaker game)
├── run_animation.py          # Entry point script
├── samples/                  # Example animations
│   ├── down_the_line.py     # 1D animation with decay
│   ├── red_green_swap.py    # Simple alternating pattern
│   └── sweeping_planes.py   # 3D geometric animation
├── utils/                    # Utility functions
│   ├── colors.py            # Color conversion utilities
│   ├── geometry.py          # 3D point coordinates (POINTS_3D)
│   ├── validation.py        # Parameter validation helpers
│   └── points/
│       └── 3dpoints.npy     # 3D coordinate data (500, 3) array
├── lib/                      # Framework library (don't modify)
│   ├── base_animation.py    # BaseAnimation class
│   ├── base_controller.py   # BaseController class
│   ├── matplotlib_controller.py # Matplotlib visualization
│   └── constants.py         # NUM_PIXELS = 500
├── tree_points.json          # 3D points exported for web viewer
├── brickbreaker_viewer.html  # Web-based game viewer (Three.js)
├── requirements.txt
└── README.md
```

## Core Architecture

### BaseAnimation Class (`lib/base_animation.py`)

All animations must inherit from `BaseAnimation`. Key methods and properties:

**Required Methods:**
- `__init__(self, frameBuf: np.ndarray, *, fps: Optional[int] = None, ...)`
  - `frameBuf`: numpy array of shape `(500, 3)` for RGB values (0-255)
  - `fps`: Optional frames per second (None = run as fast as possible)
  - Additional parameters must be keyword-only (use `*` separator)
  
- `renderNextFrame(self) -> None`
  - Called every frame
  - Update `self.frameBuf` with RGB values (0-255)
  - Shape: `(NUM_PIXELS, 3)` where each row is `[R, G, B]`

**Optional Methods:**
- `shutdown(self)`: Cleanup when animation stops
- `validate_parameters(cls, parameters)`: Custom parameter validation

**Properties:**
- `self.frameBuf`: The pixel buffer (numpy array, shape `(500, 3)`)
- `self.fps`: Frames per second (None or int)
- `self.period`: Time per frame in seconds (1/fps if fps is set, else 0)

**Class Methods:**
- `get_default_parameters(cls)`: Returns dict of default parameter values
- `validate_parameters(cls, parameters)`: Validates parameters (can override)
- `serialize_parameters(cls, parameters)`: Serialize for storage
- `deserialize_parameters(cls, parameters)`: Deserialize from storage

### Animation Execution Flow

1. `run_animation.py` loads animation class from `animation.py` or sample
2. Creates `MatplotlibController` instance
3. Controller creates animation instance with `frameBuf` and parameters
4. Controller calls `renderNextFrame()` in a loop
5. Each frame is displayed in matplotlib 3D scatter plot
6. Frame rate is controlled by `fps` parameter

## Creating Animations

### Basic Animation Template

```python
from lib.base_animation import BaseAnimation
from typing import Optional
import numpy as np

class MyAnimation(BaseAnimation):
    def __init__(self, frameBuf: np.ndarray, *, fps: Optional[int] = 30):
        super().__init__(frameBuf, fps=fps)
        self.t = 0  # Frame counter

    def renderNextFrame(self) -> None:
        # Update self.frameBuf with RGB values (0-255)
        for i in range(len(self.frameBuf)):
            self.frameBuf[i] = [255, 0, 0]  # Red
        self.t += 1
```

### Animation with Custom Parameters

```python
from lib.base_animation import BaseAnimation
from typing import Optional, Collection
from utils.validation import is_valid_rgb_color

class SolidColor(BaseAnimation):
    def __init__(self, frameBuf, *, fps: Optional[int] = None,
                 color: Collection[int] = (255, 255, 255)):
        super().__init__(frameBuf, fps=fps)
        self.color = color

    def renderNextFrame(self):
        self.frameBuf[:] = self.color

    @classmethod
    def validate_parameters(cls, parameters):
        super().validate_parameters(parameters)
        full_parameters = {**cls.get_default_parameters(), **parameters}
        color = full_parameters['color']
        if not is_valid_rgb_color(color):
            raise TypeError("color must be a valid rgb color tuple")
```

**Key Points:**
- All custom parameters must be keyword-only (after `*`)
- Use `validate_parameters()` for custom validation
- Access defaults with `cls.get_default_parameters()`
- Merge user parameters: `{**cls.get_default_parameters(), **parameters}`

## Available Utilities

### Color Utilities (`utils/colors.py`)

**HSV/RGB Conversion:**
- `hsv_to_rgb(h, s, v)` → `[R, G, B]` (0-255)
  - `h`: hue (0-1)
  - `s`: saturation (0-1)
  - `v`: value/brightness (0-1)
  
- `rgb_to_hsv(r, g, b)` → `(h, s, v)` (0-1)
  - Input: RGB values (0-255)

**Numpy Array Versions:**
- `rgb_to_hsv_numpy(rgb)` → HSV array (shape `(N, 3)`)
- `hsv_to_rgb_numpy(hsv)` → RGB array (shape `(N, 3)`)

**Helper Functions:**
- `randomColor()` → Random RGB tuple `[R, G, B]` (0-255)
- `rainbowFrame(t, NUM_PIXELS)` → List of RGB tuples for rainbow gradient
- `brightnessFrame(color, NUM_PIXELS)` → Brightness gradient from color
- `decayPixel(r, g, b, decayRate)` → Decayed color (HSV brightness decay)
- `desaturatePixel(r, g, b, desaturationRate)` → Desaturated color

### Geometry Utilities (`utils/geometry.py`)

- `POINTS_3D`: Numpy array of shape `(500, 3)` containing (x, y, z) coordinates for each pixel
  - Each row is `[x, y, z]` coordinate
  - Use for 3D spatial animations

**Common 3D Patterns:**
- **Centering points**: `CENTERED_POINTS_3D = POINTS_3D - np.mean(POINTS_3D, axis=0)`
- **Distance from origin**: `distances = np.linalg.norm(POINTS_3D, axis=1)`
- **Distance from point**: `distances = np.linalg.norm(POINTS_3D - point, axis=1)`
- **Plane distance**: `distances = np.abs(np.dot(POINTS_3D, plane_normal) + d)`
- **Sphere**: `distances = np.linalg.norm(POINTS_3D - center, axis=1) - radius`

### Validation Utilities (`utils/validation.py`)

- `is_valid_rgb_color(color)` → bool
  - Checks if color is tuple/list of 3 integers in range [0, 255]
  
- `is_valid_inclusive_range(r, m, M)` → bool
  - Validates range `r` is within bounds `[m, M]`

## Sample Animations Analysis

### 1. `red_green_swap.py` - Simple 1D Pattern

**Pattern**: Alternates red/green based on frame and pixel index
- Even frames: even indices = red, odd indices = green
- Odd frames: even indices = green, odd indices = red

**Key Techniques:**
- Simple boolean logic for pattern
- Frame counter (`self.t`)
- Direct RGB tuple assignment

### 2. `down_the_line.py` - 1D Animation with Decay

**Pattern**: Moving light that travels down the line with color decay

**Key Techniques:**
- Multiple pixels lit simultaneously (`rate` parameter)
- Color decay: `frameBuf[i] = tuple(int(c * decay) for c in frameBuf[i])`
- Random color generation: `randomColor()` from utils
- Parameter validation for `rate > 0` and `decay in [0, 1)`

**Parameters:**
- `rate: int = 10`: Number of pixels to light up
- `decay: float = 0.9`: Decay factor per frame (0-1)

### 3. `sweeping_planes.py` - 3D Geometric Animation

**Pattern**: Colored planes sweep through 3D space

**Key Techniques:**
- **3D coordinate usage**: `POINTS_3D` from `utils.geometry`
- **Centering points**: `CENTERED_POINTS_3D = POINTS_3D - mid_point`
- **Plane distance calculation**: `np.abs(np.dot(points, plane_normal) + d)`
- **Bandwidth filtering**: `within = distances < bandwidth`
- **Decay for non-lit pixels**: `frameBuf[~within] *= decay`
- **Plane movement**: `point += plane * speed`
- **Random plane generation**: Normalized random vector on sphere

**Parameters:**
- `speed: float = 0.01`: Plane movement speed
- `bandwidth: float = 0.2`: Thickness of lit band
- `decay: float = 0.85`: Decay for non-lit pixels

### 4. `animation.py` (Current) - Brick Breaker Game v2.1 (Grid-Based)

**Pattern**: Classic Brick Breaker game using TRUE 3D GRID system with cylindrical coordinate mapping

**Key Innovation - Grid-Based Face Mapping:**
This version represents a major improvement over previous implementations. Instead of using sequential LED indices (which don't match the tree's 3D structure), we now use a proper **3D grid system**:

- **Angular Sections**: Divide the tree into 8 angular sections (like pizza slices when viewed from above, 45° each)
- **Height Bands**: Divide each section into 8 height bands (horizontal layers)
- **Grid Cells**: Each brick = one cell in this grid (section × band)
- **Spatial Mapping**: LEDs are assigned to bricks based on their actual 3D position (angle, height), not their string order

**Why This Matters:**
- Previous versions used sequential LED indices, which meant bricks wrapped unpredictably around the tree
- This version uses cylindrical coordinates (angle, height), so bricks are properly organized spatially
- Collision detection works in 3D space - the ball bounces off bricks that are actually next to each other
- The "visible face" system shows only the front portion of the tree (±72°), making it feel like a traditional 2D game while showcasing the 3D structure

**Key Techniques:**
- **Cylindrical Coordinates**: Convert 3D (x,y,z) to cylindrical (r,θ,z) for proper angular calculations
- **Grid Assignment**: Each LED assigned to (section, band) based on its angle and height
- **Face-Aware Rendering**: Only sections within ±72° of viewing angle are fully visible
- **Angular Collision Detection**: Ball position tracked in (angle, z) space, collisions use angular distance
- **Checkerboard Pattern**: Bricks alternate red/green based on (section + band) % 2
- **Game state management**: Ball position/velocity in cylindrical space, paddle tracking, brick states
- **Auto-paddle AI**: Paddle follows ball with lag, stays within visible face
- **Win/Loss Animations**: Rainbow wave for wins, white wash for losses

**Current Configuration (v2.1):**
- **64 bricks** (8 sections × 8 bands) covering upper 2/3 of tree
- **Brick coverage**: From 33% height to 100% height (upper 2/3 of tree)
- **Colors**: Alternating RED and GREEN in checkerboard pattern
- **Paddle**: Width 0.8 radians (~45°), AI-controlled, at bottom 15% of tree
- **Ball**: Speed 0.02, bounces off walls/paddle/bricks in cylindrical space
- **Visible face**: ±72° (144° total visible) that slowly rotates around tree
- **Lives**: Ball can fall 3 times before game over
- **Auto-reset**: Game automatically restarts after win/loss animations, rotates to new face

**Parameters:**
- `fps: int = 30`: Frame rate (30 FPS for smooth gameplay)
- `ball_speed: float = 0.02`: Ball movement speed (radians per frame for angle, units for z)
- `paddle_speed: float = 0.025`: Paddle AI tracking speed (radians per frame)
- `paddle_width: float = 0.8`: Paddle width in radians (~45 degrees)
- `num_sections: int = 8`: Number of angular sections (8 = 45° each)
- `num_bands: int = 8`: Number of height bands (8 bands = more bricks)
- `rotation_speed: float = 0.002`: Speed of slow rotation around tree

**Game Elements:**
- **Paddle** (white): AI-controlled bar at bottom of tree, follows ball within visible face
- **Ball** (yellow): Bounces around in cylindrical space, breaks bricks on contact
- **Bricks** (red/green): Grid cells containing all LEDs within that (section, band) cell
- **Back-face bricks**: Dimmed red/green so you can see the tree structure
- **Win animation**: Rainbow wave effect rotating around tree (3 seconds)
- **Loss animation**: White wash cascading from top to bottom (4 seconds)

**Implementation Details:**
- **Grid Setup**: `_setup_grid()` assigns each LED to (section, band) based on angle and height
- **Cylindrical Conversion**: All coordinates converted to (r, θ, z) for proper angular math
- **Brick Storage**: Dictionary keyed by (section, band) containing LED indices and center coordinates
- **Collision Detection**: Uses angular distance between ball and brick centers, handles wraparound
- **Face Visibility**: Only sections within ±72° of viewing angle can be hit
- **Coordinate System**: 
  - Angle: [-π, π] radians (wraps around at ±180°)
  - Height: [0, 1] normalized (0 = bottom, 1 = top)
- **Bounce Logic**: Determines bounce direction based on which side of brick was hit
- **State Machine**: Handles playing, won, and lost states with animations

**Design Philosophy:**
This version was created after analyzing the tree's actual 3D structure using a visualization tool (`tree_unwrap_viz.py`). The visualization revealed that LEDs are strung in a continuous spiral pattern, which means sequential indices don't correspond to spatial neighbors. The grid-based approach solves this by organizing bricks by their actual 3D position, creating a proper 2D game grid mapped onto the 3D conical surface.

## Running Animations

### Basic Commands

```bash
# Run animation.py with defaults
python run_animation.py

# Run with custom parameters (JSON format)
python run_animation.py --args '{"fps": 60, "color": [255, 0, 0]}'

# Change background color
python run_animation.py --background white

# Skip parameter validation
python run_animation.py --no_validation

# List available samples
python run_animation.py --list-samples

# Run a sample directly
python run_animation.py --sample red_green_swap
python run_animation.py --sample down_the_line
python run_animation.py --sample sweeping_planes

# Run Brick Breaker game (current animation.py)
python run_animation.py

# Brick Breaker v2.1 with custom parameters
python run_animation.py --args '{"ball_speed": 0.025}'       # Faster ball
python run_animation.py --args '{"num_bands": 10}'          # More height bands (more bricks)
python run_animation.py --args '{"num_sections": 12}'       # More angular sections (finer grid)
python run_animation.py --args '{"paddle_width": 1.0}'      # Wider paddle (easier)
python run_animation.py --args '{"rotation_speed": 0.005}'   # Faster rotation around tree
```

### Command-Line Arguments

- `--args`: JSON string with animation parameters
- `--no_validation`: Skip parameter validation
- `--sample <name>`: Run sample animation by name
- `--list-samples`: List all available samples
- `--background <color>`: Background color (default: 'gray')

## Best Practices

### 1. Parameter Design
- Always use keyword-only arguments (after `*`)
- Provide sensible defaults
- Validate parameters in `validate_parameters()` method
- Use type hints for better IDE support

### 2. Performance
- Use numpy vectorized operations when possible
- Avoid Python loops for pixel updates when you can use array operations
- Example: `self.frameBuf[:] = color` (vectorized) vs loop

### 3. Color Management
- RGB values must be integers in range [0, 255]
- Use HSV for smooth color transitions
- Use `hsv_to_rgb()` for color generation
- Consider brightness/decay in HSV space

### 4. 3D Animations
- Center points around origin for easier calculations
- Use `np.linalg.norm()` for distances
- Use dot products for plane calculations
- Consider bandwidth/thickness for geometric effects

### 5. Frame Timing
- Use `self.t` or similar counter for time-based animations
- Consider `self.fps` for animation speed
- Use `self.period` if you need frame timing info

### 6. Code Organization
- Import utilities from `utils/` modules
- Use constants from `lib.constants` (NUM_PIXELS)
- Follow sample animation patterns
- Add docstrings to animation classes

## Common Patterns

### Pattern 1: Solid Color
```python
def renderNextFrame(self):
    self.frameBuf[:] = self.color
```

### Pattern 2: Color Cycle
```python
def renderNextFrame(self):
    for i in range(len(self.frameBuf)):
        hue = (i + self.t) / len(self.frameBuf)
        self.frameBuf[i] = hsv_to_rgb(hue, 1.0, 1.0)
    self.t += 1
```

### Pattern 3: Moving Wave
```python
def renderNextFrame(self):
    for i in range(len(self.frameBuf)):
        phase = (i + self.t * self.speed) / len(self.frameBuf)
        brightness = 0.5 + 0.5 * np.sin(phase * 2 * np.pi)
        self.frameBuf[i] = [int(c * brightness) for c in self.color]
    self.t += 1
```

### Pattern 4: Distance-Based (3D)
```python
from utils.geometry import POINTS_3D
import numpy as np

def renderNextFrame(self):
    center = np.array([0, 0, 0])
    distances = np.linalg.norm(POINTS_3D - center, axis=1)
    within = distances < self.radius
    self.frameBuf[within] = self.color
    self.frameBuf[~within] = 0
```

### Pattern 5: Decay Effect
```python
def renderNextFrame(self):
    # Apply decay to all pixels
    self.frameBuf = (self.frameBuf * self.decay).astype(np.uint8)
    # Add new light
    self.frameBuf[self.current_pixel] = self.color
```

### Pattern 6: YZ Plane Projection (Front View)
```python
from utils.geometry import POINTS_3D
import numpy as np

def __init__(self, frameBuf, *, fps=30):
    super().__init__(frameBuf, fps=fps)
    # Center points and extract YZ coordinates
    self.center = np.mean(POINTS_3D, axis=0)
    self.centered = POINTS_3D - self.center
    self.y = self.centered[:, 1]  # Horizontal
    self.z = self.centered[:, 2]  # Vertical

def renderNextFrame(self):
    # Draw horizontal bar at height z=0.2
    bar_height = 0.2
    bar_thickness = 0.05
    in_bar = np.abs(self.z - bar_height) < bar_thickness
    self.frameBuf[:] = [0, 0, 0]  # Background
    self.frameBuf[in_bar] = [255, 0, 0]  # Red bar
```

### Pattern 7: Game Loop Structure
```python
def __init__(self, frameBuf, *, fps=30):
    super().__init__(frameBuf, fps=fps)
    self.game_state = "playing"  # playing, won, lost
    self.frame = 0

def _update_game_logic(self):
    """Separate game logic from rendering."""
    # Move objects, check collisions, update state
    pass

def _render_frame(self):
    """Render current game state to frameBuf."""
    self.frameBuf[:] = self.bg_color
    # Draw game objects based on state
    pass

def renderNextFrame(self):
    self.frame += 1
    self._update_game_logic()
    self._render_frame()
```

## Development Workflow

1. **Setup Environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Create Animation**
   - Edit `animation.py` with your animation class
   - Or copy a sample: `cp samples/sweeping_planes.py animation.py`

3. **Test Animation**
   ```bash
   python run_animation.py
   ```

4. **Iterate**
   - Modify `animation.py`
   - Re-run to see changes
   - Press Ctrl+C to stop

5. **Test with Parameters**
   ```bash
   python run_animation.py --args '{"fps": 60, "speed": 0.02}'
   ```

6. **Submission**
   - Submit via Google Form or Pull Request
   - Include screen recording if possible
   - Note any special configuration requirements

## Tree Visualization Tool

A diagnostic visualization tool (`tree_unwrap_viz.py`) was created to understand the tree's 3D structure:

**Purpose**: "Unwrap" the 3D tree into a 2D view to visualize LED distribution and verify spatial mapping.

**Features**:
- **2D Unwrapped View**: Shows angle (0-360°) vs height, effectively "unrolling" the tree like a cylinder
- **Section Coloring**: Divides tree into angular sections (default 16) with distinct colors
- **Nearest Neighbor Lines**: Shows connections between spatially adjacent LEDs
- **Statistics**: Analyzes sequential continuity (how well LED indices match spatial proximity)

**Usage**:
```bash
# Generate visualization with 16 sections (default)
python tree_unwrap_viz.py

# Use 8 sections (matches game grid)
python tree_unwrap_viz.py --sections 8

# Skip neighbor lines for faster rendering
python tree_unwrap_viz.py --no-neighbors
```

**Output Files**:
- `tree_unwrap.png`: 2D unwrapped scatter plot showing LED distribution
- `tree_sections_3d.png`: 3D view with section coloring for verification

**Key Insights from Visualization**:
- Tree is wound in a continuous spiral pattern (~7-8 revolutions from bottom to top)
- Sequential LED indices have strong spatial continuity (ratio ~0.08)
- LEDs are evenly distributed across angular sections
- This data informed the grid-based brick system in v2.1

## Web-Based Debugging (Optional)

For faster iteration, you can use a web-based Three.js viewer instead of matplotlib:

### Setup Web Viewer

1. **Export tree coordinates to JSON** (one-time):
   ```python
   import json
   import numpy as np
   from utils.geometry import POINTS_3D
   
   points_list = POINTS_3D.tolist()
   with open('tree_points.json', 'w') as f:
       json.dump(points_list, f)
   ```

2. **Start local server**:
   ```bash
   python3 -m http.server 8000 &
   ```

3. **Create HTML viewer** (see `brickbreaker_viewer.html` for example)

4. **Open in browser**: `http://localhost:8000/your_viewer.html`

### Benefits
- **Faster iteration**: No matplotlib window startup time
- **Interactive controls**: Rotate, zoom, adjust parameters in real-time
- **Visual debugging**: Immediate feedback on pattern changes

### Tree Coordinate System
- **X**: Front-to-back (use for "front face" filtering)
- **Y**: Left-to-right (horizontal position)
- **Z**: Bottom-to-top (vertical height)
- **Center**: `np.mean(POINTS_3D, axis=0)`
- **Typical ranges**: Y: [-0.4, 0.4], Z: [-0.45, 0.6]

## Troubleshooting

### Common Issues

1. **"No animation class found"**
   - Ensure class inherits from `BaseAnimation`
   - Ensure class is not named `BaseAnimation`
   - Check file has exactly one animation class

2. **"Unknown parameter"**
   - Parameter not in `__init__` defaults
   - Check parameter name spelling
   - Use `--no_validation` to skip (not recommended)

3. **Colors not displaying**
   - Ensure RGB values are integers [0, 255]
   - Check `frameBuf` shape is `(500, 3)`
   - Verify values are not floats > 1.0

4. **Animation too fast/slow**
   - Set `fps` parameter
   - Use `--args '{"fps": 30}'` for 30 FPS

5. **3D coordinates not working**
   - Import: `from utils.geometry import POINTS_3D`
   - Shape is `(500, 3)`, not `(3, 500)`
   - Use `axis=1` for row-wise operations

6. **Pattern looks "wrapped" or distorted**
   - The tree is a 3D spiral, not a flat surface
   - Use YZ plane projection for "front view" patterns
   - Center points first: `centered = POINTS_3D - np.mean(POINTS_3D, axis=0)`
   - Use Y for horizontal, Z for vertical positioning

7. **Game elements not visible**
   - Increase element sizes (ball_radius, paddle_width, brick_height)
   - Check Z coordinate bounds match tree geometry
   - Print debug info: `print(f"Lit pixels: {(frameBuf.sum(axis=1) > 0).sum()}")`

## Submission Guidelines

- **Multiple submissions welcome**: Submit as many as you like
- **Screen recording**: Highly encouraged
- **Configuration notes**: Document any special parameters
- **Submission methods**:
  1. Google Form
  2. Pull Request (fork repo, edit `animation.py`, open PR)

## Notes

- Animation runs in matplotlib 3D scatter plot window
- Press Ctrl+C to stop animation
- `NUM_PIXELS` is hardcoded to 500 (matches physical tree)
- All animations must inherit from `BaseAnimation`
- Parameters are validated by default (use `--no_validation` to skip)
- Background color defaults to 'gray' but can be changed

