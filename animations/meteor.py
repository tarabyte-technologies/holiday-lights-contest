from lib.base_animation import BaseAnimation
from typing import Optional
import numpy as np
from utils.colors import hsv_to_rgb
from utils.geometry import POINTS_3D

class Meteor(BaseAnimation):
  """A moving comet/meteor that follows a wrapped path around the tree.

  Path is defined by angle around center plus normalized height, producing
  a looped ordering around the structure. The meteor has a bright head and
  configurable tail shapes.
  """
  def __init__(self, frameBuf, *, fps: Optional[int] = 60, speed: float = 0.005, tail_length: float = 0.08, hue: float = 0.0, saturation: float = 1.0, falloff: float = 4.0, both_sides: bool = True, tail_shape: str = 'exponential'):
    super().__init__(frameBuf, fps=fps)
    self.t = 0
    self.speed = float(speed)
    self.tail_length = float(tail_length)
    self.hue = float(hue)
    self.saturation = float(saturation)
    self.falloff = float(falloff)
    self.both_sides = bool(both_sides)
    self.tail_shape = str(tail_shape)

    centered = POINTS_3D - POINTS_3D.mean(axis=0)
    # Position along a wrapped path: angle around + normalized height
    angles = (np.arctan2(centered[:, 1], centered[:, 0]) / (2 * np.pi)) % 1.0
    zmin, zmax = centered[:, 2].min(), centered[:, 2].max()
    height_norm = (centered[:, 2] - zmin) / (zmax - zmin + 1e-9)
    self.path_pos = (angles + height_norm) % 1.0

  def renderNextFrame(self):
    # Clear frame
    self.frameBuf[:] = 0

    head = (self.t * self.speed) % 1.0

    # optionally mirror at opposite side
    heads = [head]
    if self.both_sides:
      heads.append((head + 0.5) % 1.0)

    def _shape_brightness(nd: float) -> float:
      # nd is normalized distance along tail: 0=head, 1=tail end
      if self.tail_shape == 'exponential':
        return float(np.exp(-self.falloff * nd))
      if self.tail_shape == 'gaussian':
        return float(np.exp(- (nd * nd) * self.falloff))
      if self.tail_shape == 'linear':
        return float(max(0.0, 1.0 - self.falloff * nd))
      if self.tail_shape == 'triangular':
        return float(max(0.0, 1.0 - 2.0 * nd))
      # fallback
      return float(np.exp(-self.falloff * nd))

    # Draw meteor: head(s) + tail with selected shape
    for i, p in enumerate(self.path_pos):
      brightness = 0.0
      for h in heads:
        d = abs(p - h)
        d = min(d, 1.0 - d)  
        if d <= self.tail_length:
          nd = d / self.tail_length  
          brightness = max(brightness, _shape_brightness(nd))
      if brightness > 0.001:
        r, g, b = hsv_to_rgb(self.hue, self.saturation, brightness)
        self.frameBuf[i] = [r, g, b]

    self.t += 1
