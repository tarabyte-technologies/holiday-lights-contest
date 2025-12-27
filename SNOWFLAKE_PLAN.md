# Snowflake Animation - Projection Plan

## Tree Geometry Analysis

- **Shape**: 500 points in 3D space
- **X range**: [-0.42, 0.40] (centered around 0)
- **Y range**: [-0.41, 0.42] (centered around 0)
- **Z range**: [0.00, 1.07] (tree height, bottom to top)
- **Center**: Approximately (0, 0, 0.45)
- **Distance from center**: 0.26 to 0.64 (radial distribution)
- **Angles**: Full 360° in XY plane

## Snowflake Design Approach

### 1. **6-Fold Symmetry (Standard Snowflake)**
   - Snowflakes have 6 arms (60° apart)
   - Each arm at: 0°, 60°, 120°, 180°, 240°, 300°
   - Use XY plane angle to determine which arm a point belongs to

### 2. **Projection Strategy**

#### Option A: Top-Down View (XY Plane Projection)
- Project all points onto XY plane (ignore Z)
- Calculate angle from center: `angle = arctan2(y, x)`
- Normalize angle to 0-360° or 0-2π
- Determine which of 6 arms: `arm = int(angle / 60) % 6`
- Use distance from center for radial patterns

#### Option B: Side View (XZ or YZ Plane)
- Project onto XZ or YZ plane
- Good for vertical snowflake patterns
- Use height (Z) as one dimension

#### Option C: 3D Radial (Recommended)
- Use angle in XY plane for 6 arms
- Use distance from center for radial effects
- Use Z height for layering/brightness variation
- Most natural for tree structure

### 3. **Snowflake Pattern Elements**

#### Core Structure:
1. **Center**: Bright white/blue at tree center
2. **6 Main Arms**: Extend outward from center
3. **Branching**: Smaller branches off main arms
4. **Radial Rings**: Concentric circles at specific distances

#### Implementation Details:

```python
# 1. Center points at origin
centered_points = POINTS_3D - center

# 2. Calculate XY plane angle (0-360°)
angles = np.arctan2(centered_points[:, 1], centered_points[:, 0])
angles_deg = np.degrees(angles) % 360  # Normalize to 0-360

# 3. Determine which arm (0-5)
arm_index = (angles_deg / 60).astype(int) % 6

# 4. Calculate distance from center in XY plane
xy_distances = np.linalg.norm(centered_points[:, :2], axis=1)

# 5. Calculate distance from center in 3D
distances_3d = np.linalg.norm(centered_points, axis=1)

# 6. Angle within arm (0-60°)
angle_within_arm = angles_deg % 60
```

### 4. **Pattern Generation Logic**

#### Simple Snowflake Pattern:
- **Center**: All points within small radius (e.g., < 0.1) → white
- **Main Arms**: Points aligned with 6 directions (±5° tolerance) → white/blue
- **Branching**: Points at specific distances with angular offsets → white
- **Background**: All other points → dark/off

#### Detailed Pattern:
- **Center Core**: `distance < 0.1` → bright white
- **Main Arms**: 
  - `angle_within_arm < 2°` (aligned with arm) → white
  - At specific distances: `0.2, 0.3, 0.4, 0.5` → create branches
- **Branches**: 
  - At branch distances, points with `angle_within_arm` near 30° or 45° → white
- **Radial Rings**: Points at specific distances regardless of angle → dim white

### 5. **Color Scheme Options**

- **Classic**: White (255, 255, 255) for snowflake, black (0, 0, 0) for background
- **Cool**: Light blue/cyan for snowflake, dark blue for background
- **Warm**: White with slight blue tint, warm background
- **Gradient**: Brightness based on distance from center

### 6. **Implementation Steps**

1. **Load geometry**: `from utils.geometry import POINTS_3D`
2. **Center points**: Calculate center, subtract from all points
3. **Calculate angles**: `np.arctan2(y, x)` for XY plane
4. **Determine arms**: Divide 360° into 6 arms (60° each)
5. **Calculate distances**: From center in XY plane and 3D
6. **Pattern matching**: 
   - Check if point is in center
   - Check if point aligns with main arms
   - Check if point is at branch locations
   - Check if point is on radial rings
7. **Color assignment**: White/blue for pattern, dark for background
8. **Render**: Update `frameBuf` with colors

### 7. **Parameters to Consider**

- `center_radius`: Radius for center core (default: 0.1)
- `arm_width`: Angular tolerance for main arms (default: 2°)
- `branch_distances`: List of distances for branches (e.g., [0.2, 0.3, 0.4, 0.5])
- `branch_angles`: Angles for branches within each arm (e.g., [30, 45])
- `ring_distances`: Distances for radial rings
- `snowflake_color`: RGB tuple for snowflake (default: white)
- `background_color`: RGB tuple for background (default: black)

### 8. **Visualization Approach**

Since the tree is 3D, the snowflake will appear differently from different angles:
- **Top view**: Classic 6-armed snowflake pattern
- **Side view**: Vertical lines/patterns
- **3D view**: Snowflake pattern wrapped around tree

The pattern should be designed to look good from multiple viewing angles.

## Next Steps

1. Create basic 6-arm snowflake pattern
2. Test with simple center + main arms
3. Add branching patterns
4. Add radial rings
5. Fine-tune parameters based on visual results
6. Adjust colors and brightness

