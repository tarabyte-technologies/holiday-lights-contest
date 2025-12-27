from typing import Dict
from lib.base_controller import BaseController
import numpy as np
from utils.geometry import POINTS_3D
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

class MatplotlibController(BaseController):

  def __init__(self, animation, animation_kwargs: Dict, n_pixels: int, validate_parameters=True, background_color: str = 'black'):
    super().__init__(animation, animation_kwargs, n_pixels, validate_parameters=validate_parameters)
    screencolor = background_color
    self.fig = plt.figure(figsize=(10, 10), facecolor=screencolor)
    self.ax = self.fig.add_subplot(111, projection='3d')
    self.ax.set_facecolor(screencolor)
    self.points = POINTS_3D
    self.sizes = 100 * np.ones(n_pixels)

    # Add static 3D Christmas tree
    self._add_christmas_tree()

    self.scatter = self.ax.scatter(self.points[:, 0], self.points[:, 1], self.points[:, 2], c=self.frameBuf / 255, s=self.sizes, marker='o', edgecolors=None, alpha=0.4)
    self.ax.set_aspect('equal')

  def _add_christmas_tree(self):
    """Add a static 3D Christmas tree (cone + trunk + star) to the plot."""
    # Get tree dimensions from the light positions
    z_min, z_max = self.points[:, 2].min(), self.points[:, 2].max()
    tree_height = z_max - z_min

    # Calculate max radius from light positions
    max_radius = 0
    for i in range(len(self.points)):
      r = np.sqrt(self.points[i, 0]**2 + self.points[i, 1]**2)
      if r > max_radius:
        max_radius = r

    cone_resolution = 60
    theta = np.linspace(0, 2 * np.pi, cone_resolution)

    # Create layered branch tiers (like a real Christmas tree)
    num_tiers = 6
    for tier in range(num_tiers):
      # Each tier starts wider and tapers up
      tier_base_z = z_min + tree_height * tier / num_tiers
      tier_top_z = z_min + tree_height * (tier + 0.7) / num_tiers

      # Top tier extends to a sharp point (taller to stick out over lights)
      if tier == num_tiers - 1:
        tier_top_z = z_max + tree_height * 0.12

      z_tier = np.linspace(tier_base_z, tier_top_z, 15)
      theta_grid, z_grid = np.meshgrid(theta, z_tier)

      # Base radius for this tier (smaller as we go up)
      tier_base_radius = max_radius * 0.95 * (1 - tier / num_tiers * 0.85)

      # Taper within tier - wide at bottom, narrow at top
      tier_progress = (z_grid - tier_base_z) / (tier_top_z - tier_base_z + 0.001)

      # Top tier tapers to a point
      if tier == num_tiers - 1:
        radius_grid = tier_base_radius * (1 - tier_progress)
      else:
        radius_grid = tier_base_radius * (1 - tier_progress * 0.5)

      # Add branch-like bumps around the edge
      bump = 0.04 * np.sin(theta_grid * 12) * tier_base_radius * (1 - tier_progress * 0.5)
      radius_grid = radius_grid + bump

      x_cone = radius_grid * np.cos(theta_grid)
      y_cone = radius_grid * np.sin(theta_grid)

      # Vary green color per tier
      green_val = 0.25 + 0.2 * (tier / num_tiers)
      tier_color = (0.05, green_val, 0.02)

      self.ax.plot_surface(x_cone, y_cone, z_grid, color=tier_color, alpha=1.0, shade=True, antialiased=True)

    # Add 3D branches sticking out
    num_branches = 20
    np.random.seed(42)  # Consistent branch placement
    for b in range(num_branches):
      branch_angle = 2 * np.pi * b / num_branches + np.random.uniform(-0.2, 0.2)
      branch_base_z = z_min + np.random.uniform(0.1, 0.85) * tree_height
      branch_length = max_radius * 0.3 * (1 - (branch_base_z - z_min) / tree_height)

      # Branch points outward and slightly down
      t = np.linspace(0, 1, 10)
      branch_r = max_radius * 0.9 * (1 - (branch_base_z - z_min) / tree_height) + t * branch_length
      branch_z = branch_base_z - t * branch_length * 0.3
      branch_x = branch_r * np.cos(branch_angle)
      branch_y = branch_r * np.sin(branch_angle)

      self.ax.plot(branch_x, branch_y, branch_z, color=(0.0, 0.35, 0.0), linewidth=2.5)

    # Tree trunk (brown cylinder at bottom)
    trunk_height = tree_height * 0.12
    trunk_radius = max_radius * 0.12
    z_trunk = np.linspace(z_min - trunk_height, z_min, 10)
    theta_trunk, z_trunk_grid = np.meshgrid(theta, z_trunk)
    x_trunk = trunk_radius * np.cos(theta_trunk)
    y_trunk = trunk_radius * np.sin(theta_trunk)

    self.ax.plot_surface(x_trunk, y_trunk, z_trunk_grid, color='saddlebrown', alpha=1.0, shade=True)

    # 3D Star at the top - vertical in XZ plane
    star_center_z = z_max + tree_height * 0.18
    star_size = max_radius * 0.18
    num_points = 5

    # Create a 3D star with actual triangular faces
    from mpl_toolkits.mplot3d.art3d import Poly3DCollection

    # Star points in XZ plane (vertical star)
    # outer points are the 5 tips, inner points are the valleys between tips
    outer_points = []
    inner_points = []
    for i in range(num_points):
      # Outer point (tips of star) - in XZ plane
      angle_out = 2 * np.pi * i / num_points + np.pi / 2  # Start at top (point up)
      outer_points.append([
        star_size * np.cos(angle_out),  # X
        0,                                # Y = 0 (flat in XZ plane)
        star_center_z + star_size * np.sin(angle_out)  # Z
      ])
      # Inner point (valleys between tips)
      angle_in = 2 * np.pi * (i + 0.5) / num_points + np.pi / 2
      inner_points.append([
        star_size * 0.4 * np.cos(angle_in),  # X
        0,                                    # Y = 0
        star_center_z + star_size * 0.4 * np.sin(angle_in)  # Z
      ])

    # Front and back center points for 3D depth (along Y axis)
    front_center = [0, star_size * 0.25, star_center_z]
    back_center = [0, -star_size * 0.25, star_center_z]

    # Create triangular faces
    faces = []
    for i in range(num_points):
      next_i = (i + 1) % num_points
      # Front faces
      faces.append([outer_points[i], inner_points[i], front_center])
      faces.append([inner_points[i], outer_points[next_i], front_center])
      # Back faces
      faces.append([outer_points[i], inner_points[i], back_center])
      faces.append([inner_points[i], outer_points[next_i], back_center])

    star_mesh = Poly3DCollection(faces, alpha=1.0, facecolor='gold', edgecolor='orange', linewidth=0.5)
    self.ax.add_collection3d(star_mesh)

  def run(self):
    interval = int(self.animation.period * 1000) if self.animation.period > 0 else 10
    self.ani = FuncAnimation(self.fig, self.update, interval=interval, frames=None, cache_frame_data=False)
    plt.grid(False)
    plt.axis('off')
    plt.show()

  def update(self, frame):
    self.animation.renderNextFrame()
    self.scatter.set_color(self.frameBuf / 255)

