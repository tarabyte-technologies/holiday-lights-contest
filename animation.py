# animation.py
<<<<<<< Updated upstream
from __future__ import annotations

import time
from typing import Optional, Tuple
=======

from dataclasses import dataclass
from typing import Optional, Dict, List, Tuple
>>>>>>> Stashed changes

import numpy as np

from lib.base_animation import BaseAnimation
<<<<<<< Updated upstream
from utils.geometry import POINTS_3D


def _clamp01(x: np.ndarray) -> np.ndarray:
    return np.clip(x, 0.0, 1.0)


def _smoothstep(edge0: float, edge1: float, x: np.ndarray) -> np.ndarray:
    t = _clamp01((x - edge0) / (edge1 - edge0 + 1e-9))
    return t * t * (3.0 - 2.0 * t)


def _ease_in_out(x: float) -> float:
    x = float(np.clip(x, 0.0, 1.0))
    return 0.5 - 0.5 * np.cos(np.pi * x)


def _wrap01(d: np.ndarray) -> np.ndarray:
    d = np.abs(d)
    return np.minimum(d, 1.0 - d)


def _hsv_to_rgb(h: np.ndarray, s: np.ndarray, v: np.ndarray) -> np.ndarray:
    h = (h % 1.0) * 6.0
    i = np.floor(h).astype(int)
    f = h - i
    p = v * (1.0 - s)
    q = v * (1.0 - s * f)
    t = v * (1.0 - s * (1.0 - f))

    r = np.zeros_like(v)
    g = np.zeros_like(v)
    b = np.zeros_like(v)

    m0 = (i == 0)
    r[m0], g[m0], b[m0] = v[m0], t[m0], p[m0]

    m1 = (i == 1)
    r[m1], g[m1], b[m1] = q[m1], v[m1], p[m1]

    m2 = (i == 2)
    r[m2], g[m2], b[m2] = p[m2], v[m2], t[m2]

    m3 = (i == 3)
    r[m3], g[m3], b[m3] = p[m3], q[m3], v[m3]

    m4 = (i == 4)
    r[m4], g[m4], b[m4] = t[m4], p[m4], v[m4]

    m5 = (i >= 5)
    r[m5], g[m5], b[m5] = v[m5], p[m5], q[m5]

    return np.stack([r, g, b], axis=1)


class Animation(BaseAnimation):
    """
    Beat-synced (BPM-driven) progression with no startup pause.

    Visual concept:
    1) White spiral: top -> down
    2) Green spiral: bottom -> up
    3) Gold orb: top -> down (flicker)
    4) Multicolor: bottom -> up (blink) + pinned gold at the top when complete

    Notes:
    - The runner has no audio input. "Sync" means: start the song and start this together.
    - Stage timing is now BPM-based from t=0, so it will not feel slow.
    - tempo_start_seconds only offsets beat accents, not stage motion.
=======
from lib.constants import NUM_PIXELS
from utils.geometry import POINTS_3D


def _wrap_angle(d: np.ndarray) -> np.ndarray:
    """Wrap angular difference into [-pi, pi]."""
    return (d + np.pi) % (2.0 * np.pi) - np.pi


def _mix(a: np.ndarray, b: np.ndarray, t: float) -> np.ndarray:
    return a * (1.0 - t) + b * t


def _as_rgb(color: Tuple[int, int, int]) -> np.ndarray:
    return np.array(color, dtype=np.float32)


def _gamma_boost(rgb: np.ndarray, gamma: float) -> np.ndarray:
    """
    Simple gamma-like boost for perceived brightness.
    gamma < 1 brightens; gamma > 1 darkens.
    Works on 0..255 float RGB.
    """
    g = float(max(0.05, gamma))
    x = np.clip(rgb / 255.0, 0.0, 1.0)
    x = np.power(x, g)
    return x * 255.0


@dataclass
class _Particle:
    y: float
    theta: float
    r_target: float      # 0..1 (where in the tree depth the flake lives)
    speed: float
    color_idx: int
    sparkle: bool


class ConfettiSnowfallColorZones(BaseAnimation):
    """
    Confetti Snowfall with Color Zones (real-tree friendly, high-visibility)

    - Bright confetti flakes drift downward.
    - Tree divided into soft horizontal color zones.
    - Rare gold sparkles.
    - Finale: full-tree multicolor blink celebration.
>>>>>>> Stashed changes
    """

    def __init__(
        self,
<<<<<<< Updated upstream
        frameBuf: np.ndarray,
        *,
        fps: Optional[int] = 30,

        # --- Music clock ---
        bpm: float = 150.0,
        # This shifts ONLY beat accents. Stage progression starts immediately.
        tempo_start_seconds: float = 0.0,

        # --- Stage lengths in bars (4/4) ---
        # 150 BPM => 1 bar = 1.6 seconds. Smaller bars = faster.
        stage_bars_white: int = 10,   # ~16s
        stage_bars_green: int = 10,   # ~16s
        stage_bars_gold: int = 8,     # ~12.8s
        stage_bars_multi: int = 12,   # ~19.2s
        # Total default loop ~64s (energetic; not sluggish)

        # Crossfade between stages (in bars)
        transition_bars: float = 1.0,

        # Global brightness multiplier
        brightness: float = 2.6,

        # Spiral look & motion
        spiral_turns: float = 3.0,
        spiral_rot_rate: float = 0.18,
        spiral_width: float = 0.13,
        spiral_softness: float = 0.10,

        # Spiral segment shaping
        spiral_head_len: float = 0.26,
        spiral_tail_len: float = 0.36,

        white_spiral_color: Tuple[int, int, int] = (255, 245, 235),
        green_spiral_color: Tuple[int, int, int] = (40, 255, 120),

        # Gold fall (cone-aware blob)
        orb_color: Tuple[int, int, int] = (255, 210, 70),
        orb_flicker_hz: float = 14.0,
        orb_z_width: float = 0.10,
        orb_r_min: float = 0.18,
        orb_r_extra: float = 0.55,
        orb_softness: float = 0.25,

        # Multicolor finale
        finale_blink_hz: float = 12.0,
        finale_saturation: float = 0.95,
        finale_value: float = 1.0,
        finale_speckle: float = 0.65,

        # Multicolor visibility/motion
        finale_front_width: float = 0.14,
        finale_front_boost: float = 1.35,
        finale_trailing_fill: float = 0.55,
        finale_min_fill: float = 0.08,

        # Beat accent tuning
        beat_pulse_strength: float = 0.26,
        backbeat_boost: float = 0.22,   # beats 2 and 4
        offbeat_sparkle: float = 0.12,
    ):
        super().__init__(frameBuf, fps=fps)

        pts = POINTS_3D.astype(np.float32)
        center = pts.mean(axis=0)
        P = pts - center
        self.P = P

        x = P[:, 0]
        y = P[:, 1]
        z = P[:, 2]

        zmin, zmax = z.min(), z.max()
        self.zn = (z - zmin) / (zmax - zmin + 1e-9)

        ang = np.arctan2(y, x)
        self.an = (ang + np.pi) / (2.0 * np.pi)

        r = np.sqrt(x * x + y * y)
        rmin, rmax = float(r.min()), float(r.max())
        self.rn = (r - rmin) / (rmax - rmin + 1e-9)

        # Music clock
        self.bpm = float(max(20.0, bpm))
        self.tempo_start_seconds = float(max(0.0, tempo_start_seconds))

        # Stage bars
        self.stage_bars_white = int(max(1, stage_bars_white))
        self.stage_bars_green = int(max(1, stage_bars_green))
        self.stage_bars_gold = int(max(1, stage_bars_gold))
        self.stage_bars_multi = int(max(1, stage_bars_multi))
        self.transition_bars = float(max(0.0, transition_bars))

        self.total_bars = (
            self.stage_bars_white
            + self.stage_bars_green
            + self.stage_bars_gold
            + self.stage_bars_multi
        )

        # Visual params
        self.brightness = float(brightness)

        self.spiral_turns = float(spiral_turns)
        self.spiral_rot_rate = float(spiral_rot_rate)
        self.spiral_width = float(spiral_width)
        self.spiral_softness = float(spiral_softness)
        self.spiral_head_len = float(np.clip(spiral_head_len, 0.05, 0.85))
        self.spiral_tail_len = float(np.clip(spiral_tail_len, 0.05, 0.95))

        self.white_spiral_color = np.array(white_spiral_color, dtype=np.float32)
        self.green_spiral_color = np.array(green_spiral_color, dtype=np.float32)

        self.orb_color = np.array(orb_color, dtype=np.float32)
        self.orb_flicker_hz = float(max(0.1, orb_flicker_hz))
        self.orb_z_width = float(max(0.02, orb_z_width))
        self.orb_r_min = float(np.clip(orb_r_min, 0.05, 0.95))
        self.orb_r_extra = float(np.clip(orb_r_extra, 0.0, 1.5))
        self.orb_softness = float(np.clip(orb_softness, 0.05, 1.0))

        self.finale_blink_hz = float(finale_blink_hz)
        self.finale_saturation = float(finale_saturation)
        self.finale_value = float(finale_value)
        self.finale_speckle = float(finale_speckle)

        self.finale_front_width = float(max(0.03, finale_front_width))
        self.finale_front_boost = float(max(1.0, finale_front_boost))
        self.finale_trailing_fill = float(np.clip(finale_trailing_fill, 0.0, 1.0))
        self.finale_min_fill = float(np.clip(finale_min_fill, 0.0, 0.35))

        self.beat_pulse_strength = float(np.clip(beat_pulse_strength, 0.0, 0.75))
        self.backbeat_boost = float(np.clip(backbeat_boost, 0.0, 0.75))
        self.offbeat_sparkle = float(np.clip(offbeat_sparkle, 0.0, 0.75))

        rng = np.random.default_rng(42)
        self._pix_rand = rng.random(len(self.zn)).astype(np.float32)

        self._t0 = time.perf_counter()

    # ---------- Music helpers ----------
    def _beats_from_time(self, t: float) -> float:
        # beats for stage progression: always running from t=0
        return t * (self.bpm / 60.0)

    def _beats_for_accents(self, t: float) -> float:
        # beat accents can be offset if you want
        tt = t - self.tempo_start_seconds
        if tt < 0.0:
            tt = 0.0
        return tt * (self.bpm / 60.0)

    def _pulse_envelope(self, beat_phase: float) -> float:
        x = float(np.clip(beat_phase, 0.0, 1.0))
        p = 1.0 - _ease_in_out(min(1.0, x / 0.16))  # slightly snappier than before
        return p

    def _beat_accents(self, beats: float) -> float:
        beat_in_bar = beats % 4.0
        beat_index = int(np.floor(beat_in_bar + 1e-9))  # 0,1,2,3
        beat_phase = beat_in_bar - float(beat_index)

        base_pulse = self._pulse_envelope(beat_phase)

        is_backbeat = 1.0 if beat_index in (1, 3) else 0.0
        backbeat = is_backbeat * base_pulse

        off = 1.0 - min(1.0, abs(beat_phase - 0.5) / 0.16)
        off = _ease_in_out(max(0.0, off))

        return 1.0 + self.beat_pulse_strength * base_pulse + self.backbeat_boost * backbeat + self.offbeat_sparkle * off

    # ---------- Visual stages ----------
    def _spiral_segment(self, t: float, z_head: float, color: np.ndarray, downward: bool) -> np.ndarray:
        n = len(self.zn)
        col = np.zeros((n, 3), dtype=np.float32)

        rot = (t * self.spiral_rot_rate) % 1.0
        helix = (self.an + self.spiral_turns * self.zn + rot) % 1.0

        stripe_phase = (self.spiral_turns * z_head + rot) % 1.0
        d = _wrap01(helix - stripe_phase)

        stripe = 1.0 - _smoothstep(self.spiral_width, self.spiral_width + self.spiral_softness, d)

        z = self.zn
        if downward:
            head = 1.0 - _smoothstep(0.0, self.spiral_head_len, np.abs(z - z_head))
            tail = 1.0 - _smoothstep(0.0, self.spiral_tail_len, np.maximum(0.0, z - z_head))
        else:
            head = 1.0 - _smoothstep(0.0, self.spiral_head_len, np.abs(z - z_head))
            tail = 1.0 - _smoothstep(0.0, self.spiral_tail_len, np.maximum(0.0, z_head - z))

        env = _clamp01(0.85 * head + 0.55 * tail)
        shimmer = 0.88 + 0.12 * np.sin(t * 3.2 + self.zn * 9.0 + self.an * 7.0)

        intensity = _clamp01(stripe * env * shimmer.astype(np.float32))
        col[:] = color[None, :] * intensity[:, None]
        return col

    def _stage_white_spiral_down(self, t: float, s: float) -> np.ndarray:
        z_head = 1.0 - s
        return self._spiral_segment(t, z_head=z_head, color=self.white_spiral_color, downward=True)

    def _stage_green_spiral_up(self, t: float, s: float) -> np.ndarray:
        z_head = s
        return self._spiral_segment(t, z_head=z_head, color=self.green_spiral_color, downward=False)

    def _gold_blob(self, t: float, z_head: float, extra_flicker: float = 1.0) -> np.ndarray:
        n = len(self.zn)
        col = np.zeros((n, 3), dtype=np.float32)

        dz = np.abs(self.zn - z_head)
        z_core = 1.0 - _smoothstep(self.orb_z_width, self.orb_z_width * 1.9, dz)

        r_reach = self.orb_r_min + self.orb_r_extra * (1.0 - z_head)
        dr = np.maximum(0.0, self.rn - r_reach)
        r_core = 1.0 - _smoothstep(0.0, self.orb_softness, dr)

        core = _clamp01(z_core * r_core).astype(np.float32)

        w = 2.0 * np.pi * self.orb_flicker_hz
        global_f = 0.55 + 0.45 * np.sin(w * t)
        pix_f = 0.55 + 0.45 * np.sin(w * (t + self._pix_rand * 0.12))
        flick = (0.55 * global_f + 0.45 * pix_f).astype(np.float32)

        intensity = _clamp01(core * flick * float(extra_flicker))
        col[:] = self.orb_color[None, :] * intensity[:, None]
        return col

    def _stage_gold_fall(self, t: float, s: float) -> np.ndarray:
        z_head = 1.0 - s
        return self._gold_blob(t, z_head=z_head, extra_flicker=1.0)

    def _stage_multicolor_rise(self, t: float, s: float) -> np.ndarray:
        n = len(self.zn)
        col = np.zeros((n, 3), dtype=np.float32)

        s = float(np.clip(s, 0.0, 1.0))
        fill = max(self.finale_min_fill, s)
        z_head = fill

        blink = 0.5 + 0.5 * np.sin(2.0 * np.pi * self.finale_blink_hz * t)
        blink_pix = 0.5 + 0.5 * np.sin(2.0 * np.pi * self.finale_blink_hz * (t + self._pix_rand * 0.18))
        b = ((1.0 - self.finale_speckle) * blink + self.finale_speckle * blink_pix).astype(np.float32)

        hue = (self._pix_rand * 0.97 + t * 0.33 + self.an * 0.12) % 1.0
        sat = np.full_like(hue, self.finale_saturation, dtype=np.float32)
        val = np.full_like(hue, self.finale_value, dtype=np.float32) * b
        rgb = _hsv_to_rgb(hue, sat, val) * 255.0

        behind = self.zn <= z_head
        if np.any(behind) and self.finale_trailing_fill > 0.0:
            col[behind] = rgb[behind] * self.finale_trailing_fill

        band_d = np.abs(self.zn - z_head)
        band = (1.0 - _smoothstep(self.finale_front_width, self.finale_front_width * 1.8, band_d)).astype(np.float32)

        if np.any(band > 0.0):
            band_rgb = rgb * (band[:, None] * self.finale_front_boost)
            col = np.maximum(col, band_rgb.astype(np.float32))

        if s >= 0.999:
            orb = self._gold_blob(t, z_head=1.0, extra_flicker=1.15)
            col = np.maximum(col, orb)

        return col

    def renderNextFrame(self) -> None:
        self.frameBuf[:] = 0.0

        t = time.perf_counter() - self._t0

        # Stage progression: always running
        beats_prog = self._beats_from_time(t)
        bars_prog = beats_prog / 4.0

        # Loop inside our stage plan
        total_bars = float(max(1, self.total_bars))
        bar_stage = bars_prog % total_bars

        b0 = float(self.stage_bars_white)
        b1 = b0 + float(self.stage_bars_green)
        b2 = b1 + float(self.stage_bars_gold)
        b3 = b2 + float(self.stage_bars_multi)

        if bar_stage < b0:
            idx = 0
            bar_in = bar_stage
            dur_bars = b0
        elif bar_stage < b1:
            idx = 1
            bar_in = bar_stage - b0
            dur_bars = (b1 - b0)
        elif bar_stage < b2:
            idx = 2
            bar_in = bar_stage - b1
            dur_bars = (b2 - b1)
        else:
            idx = 3
            bar_in = bar_stage - b2
            dur_bars = (b3 - b2)

        s = float(np.clip(bar_in / (dur_bars + 1e-9), 0.0, 1.0))

        def stage(i: int, s_local: float) -> np.ndarray:
            if i == 0:
                return self._stage_white_spiral_down(t, s_local)
            if i == 1:
                return self._stage_green_spiral_up(t, s_local)
            if i == 2:
                return self._stage_gold_fall(t, s_local)
            return self._stage_multicolor_rise(t, s_local)

        # Crossfade in bars
        trans = float(self.transition_bars)
        if trans > 0.0 and idx < 3 and bar_in >= (dur_bars - trans):
            a = (bar_in - (dur_bars - trans)) / (trans + 1e-9)
            a = _ease_in_out(a)
            col_a = stage(idx, s)
            col_b = stage(idx + 1, 0.0)
            col = (1.0 - a) * col_a + a * col_b
        else:
            col = stage(idx, s)

        # Beat accents (optionally offset)
        beats_acc = self._beats_for_accents(t)
        accent = self._beat_accents(beats_acc)

        # Push accents more as we progress to later stages (feels “song lifts”)
        if idx == 0:
            accent_mix = 1.0 + (accent - 1.0) * 0.60
        elif idx == 1:
            accent_mix = 1.0 + (accent - 1.0) * 0.80
        elif idx == 2:
            accent_mix = 1.0 + (accent - 1.0) * 0.95
        else:
            accent_mix = 1.0 + (accent - 1.0) * 1.15

        col *= float(self.brightness) * float(accent_mix)
        self.frameBuf[:] = np.clip(col, 0, 255)
=======
        frameBuf,
        *,
        fps: Optional[int] = 30,

        # Confetti density / look
        particles: int = 210,

        # Footprint (smaller = brighter flakes; larger = softer wash)
        y_band: float = 0.030,
        theta_band: float = 0.22,
        r_band: float = 0.26,   # widened a bit to help fill depth

        # Motion
        speed_min: float = 0.24,
        speed_max: float = 0.62,
        drift: float = 0.20,

        # Zone behavior
        soft_zone_edges: float = 0.05,

        # Sparkles
        sparkle_chance: float = 0.12,
        sparkle_boost: float = 1.75,

        # Global brightness / pop
        brightness: float = 1.80,
        gamma: float = 0.70,             # <1 = brighter/more vivid
        flake_peak: float = 1.60,        # boosts the core intensity of flakes
        ambient_zone_glow: float = 0.07, # subtle colored “atmosphere” per zone

        # Depth behavior (THIS FIXES THE HOLE)
        r_min: float = 0.22,             # allow flakes closer to trunk
        r_max: float = 0.98,             # and near outer surface
        r_outer_bias: float = 0.60,      # 0..1 higher = more flakes outward

        # Finale
        loop_seconds: float = 34.0,
        finale_seconds: float = 6.0,
        finale_blink_hz: float = 10.0,
        finale_brightness: float = 1.45,

        seed: int = 20251225,
    ):
        super().__init__(frameBuf, fps=fps)

        self.rng = np.random.default_rng(int(seed))
        self.t = 0.0

        self.particles_n = int(max(20, particles))
        self.y_band = float(max(0.006, y_band))
        self.theta_band = float(max(0.04, theta_band))
        self.r_band = float(max(0.02, r_band))

        self.speed_min = float(max(0.01, speed_min))
        self.speed_max = float(max(self.speed_min, speed_max))
        self.drift = float(drift)

        self.soft_zone_edges = float(max(0.0, soft_zone_edges))

        self.sparkle_chance = float(np.clip(sparkle_chance, 0.0, 0.7))
        self.sparkle_boost = float(max(1.0, sparkle_boost))

        self.brightness = float(max(0.1, brightness))
        self.gamma = float(max(0.05, gamma))
        self.flake_peak = float(max(1.0, flake_peak))
        self.ambient_zone_glow = float(max(0.0, ambient_zone_glow))

        self.r_min = float(np.clip(r_min, 0.0, 1.0))
        self.r_max = float(np.clip(r_max, 0.0, 1.0))
        if self.r_max <= self.r_min + 1e-6:
            self.r_max = min(1.0, self.r_min + 0.10)
        self.r_outer_bias = float(np.clip(r_outer_bias, 0.0, 1.0))

        self.loop_seconds = float(max(6.0, loop_seconds))
        self.finale_seconds = float(np.clip(finale_seconds, 1.0, self.loop_seconds - 1.0))
        self.finale_blink_hz = float(max(0.5, finale_blink_hz))
        self.finale_brightness = float(max(0.2, finale_brightness))

        # Geometry -> centered cylindrical
        pts = np.asarray(POINTS_3D, dtype=np.float32)
        if pts.shape[0] != NUM_PIXELS:
            pts = pts[:NUM_PIXELS]

        min_pt = pts.min(axis=0)
        max_pt = pts.max(axis=0)
        mid = (min_pt + max_pt) / 2.0
        cpts = pts - mid

        x = cpts[:, 0]
        y = cpts[:, 1]
        z = cpts[:, 2]

        self.theta = np.arctan2(z, x)
        r = np.sqrt(x * x + z * z)
        rmax = float(r.max()) if float(r.max()) > 1e-6 else 1.0
        self.rn = r / rmax

        ymin, ymax = float(y.min()), float(y.max())
        denom = (ymax - ymin) if (ymax - ymin) > 1e-6 else 1.0
        self.yn = (y - ymin) / denom  # 0..1 bottom->top

        # Stable per-pixel values for finale shimmer
        self.pixel_phase = self.rng.random(NUM_PIXELS).astype(np.float32)
        self.pixel_choice = self.rng.integers(0, 10_000_000, size=NUM_PIXELS, dtype=np.int32)

        # Higher-saturation palettes (camera friendly)
        self.zones = [
            # Top: Cool Sparkle
            (0.78, 1.01, [
                (255, 255, 255),
                ( 80, 220, 255),
                ( 90, 140, 255),
                (160, 120, 255),
            ]),
            # Upper-mid: Classic holiday
            (0.52, 0.78, [
                (255, 255, 255),
                (255,  25,  25),
                ( 35, 255, 120),
                (255, 120,  40),
            ]),
            # Lower-mid: Warm celebration
            (0.26, 0.52, [
                (255,  50,  60),
                (255,  40, 210),
                (190, 255,  60),
                ( 60, 255, 220),
            ]),
            # Bottom: Grounded glow
            (-0.01, 0.26, [
                (255, 255, 255),
                ( 40, 255, 120),
                (255, 190,  40),
                (255, 120,  20),
            ]),
        ]

        self.zone_edges = np.array([0.26, 0.52, 0.78], dtype=np.float32)

        self.particles: List[_Particle] = []
        for _ in range(self.particles_n):
            self.particles.append(self._spawn_particle(at_top=True))

    @classmethod
    def get_default_parameters(cls) -> Dict:
        return {
            "fps": 30,
            "particles": 210,
            "y_band": 0.030,
            "theta_band": 0.22,
            "r_band": 0.26,
            "speed_min": 0.24,
            "speed_max": 0.62,
            "drift": 0.20,
            "soft_zone_edges": 0.05,
            "sparkle_chance": 0.12,
            "sparkle_boost": 1.75,
            "brightness": 1.80,
            "gamma": 0.70,
            "flake_peak": 1.60,
            "ambient_zone_glow": 0.07,
            "r_min": 0.22,
            "r_max": 0.98,
            "r_outer_bias": 0.60,
            "loop_seconds": 34.0,
            "finale_seconds": 6.0,
            "finale_blink_hz": 10.0,
            "finale_brightness": 1.45,
            "seed": 20251225,
        }

    @classmethod
    def validate_parameters(cls, parameters):
        super().validate_parameters(parameters)
        p = {**cls.get_default_parameters(), **parameters}

        if not isinstance(p["particles"], int):
            raise TypeError("particles must be an int")

        numeric_fields = [
            "y_band", "theta_band", "r_band",
            "speed_min", "speed_max", "drift",
            "soft_zone_edges",
            "sparkle_chance", "sparkle_boost",
            "brightness", "gamma", "flake_peak", "ambient_zone_glow",
            "r_min", "r_max", "r_outer_bias",
            "loop_seconds", "finale_seconds", "finale_blink_hz", "finale_brightness",
        ]
        for k in numeric_fields:
            if not isinstance(p[k], (int, float)):
                raise TypeError(f"{k} must be a number")

        if p["particles"] < 20 or p["particles"] > 800:
            raise ValueError("particles should be between 20 and 800")

        if p["speed_min"] <= 0 or p["speed_max"] <= 0 or p["speed_max"] < p["speed_min"]:
            raise ValueError("speed_min/speed_max must be positive and speed_max >= speed_min")

        if p["loop_seconds"] < 6:
            raise ValueError("loop_seconds must be >= 6")
        if not (1.0 <= p["finale_seconds"] < p["loop_seconds"]):
            raise ValueError("finale_seconds must be >= 1 and < loop_seconds")

        if not (0.0 <= p["sparkle_chance"] <= 0.7):
            raise ValueError("sparkle_chance must be between 0 and 0.7")
        if p["sparkle_boost"] < 1.0:
            raise ValueError("sparkle_boost must be >= 1.0")

        if p["gamma"] <= 0:
            raise ValueError("gamma must be > 0")
        if p["flake_peak"] < 1.0:
            raise ValueError("flake_peak must be >= 1.0")
        if p["brightness"] <= 0:
            raise ValueError("brightness must be > 0")

        if not (0.0 <= p["r_min"] <= 1.0 and 0.0 <= p["r_max"] <= 1.0):
            raise ValueError("r_min and r_max must be in [0, 1]")
        if p["r_max"] <= p["r_min"]:
            raise ValueError("r_max must be > r_min")
        if not (0.0 <= p["r_outer_bias"] <= 1.0):
            raise ValueError("r_outer_bias must be in [0, 1]")

    def _biased_radius(self) -> float:
        """
        Choose a radius target for a particle.
        r_outer_bias > 0.5 biases toward outer radii (more visible),
        but still allows inner flakes to fill the core (fixes the hole).
        """
        u = float(self.rng.random())
        # Blend between linear (u) and outer-biased (sqrt) based on r_outer_bias
        outer = np.sqrt(u)             # biases toward 1.0
        inner = u                      # uniform
        b = self.r_outer_bias
        v = (1.0 - b) * inner + b * outer
        return float(self.r_min + (self.r_max - self.r_min) * v)

    def _spawn_particle(self, *, at_top: bool) -> _Particle:
        y = 1.0 + float(self.rng.random() * 0.12) if at_top else float(self.rng.random())
        theta = float(self.rng.uniform(-np.pi, np.pi))
        r_target = self._biased_radius()
        speed = float(self.rng.uniform(self.speed_min, self.speed_max))

        color_idx = int(self.rng.integers(0, 10))
        sparkle = bool(self.rng.random() < self.sparkle_chance)

        return _Particle(y=y, theta=theta, r_target=r_target, speed=speed, color_idx=color_idx, sparkle=sparkle)

    def _zone_color(self, y: float, idx: int) -> np.ndarray:
        for low, high, palette in self.zones:
            if low <= y < high:
                return _as_rgb(palette[idx % len(palette)])
        return _as_rgb((255, 255, 255))

    def _zone_blend_color(self, y: float, idx: int) -> np.ndarray:
        base = self._zone_color(y, idx)
        w = self.soft_zone_edges
        if w <= 1e-6:
            return base

        for edge in self.zone_edges:
            d = y - float(edge)
            if abs(d) < w:
                t = abs(d) / w
                mix_amt = 0.40 * (1.0 - t)

                if d > 0:
                    other = self._zone_color(y - 0.12, idx + 1)
                else:
                    other = self._zone_color(y + 0.12, idx + 1)

                return _mix(base, other, mix_amt)

        return base

    def _render_finale(self, local_t: float):
        palette = np.array(
            [
                (255,  30,  30),
                ( 30, 255, 120),
                ( 90, 140, 255),
                (255,  40, 210),
                ( 80, 220, 255),
                (255, 190,  40),
                (255, 255, 255),
                (190, 255,  60),
            ],
            dtype=np.float32,
        )

        blink = 0.5 + 0.5 * np.sin(2.0 * np.pi * self.finale_blink_hz * local_t)
        blink_gate = (blink > 0.10).astype(np.float32)

        tw = (self.pixel_phase + local_t * 1.10) % 1.0
        twinkle = (tw > 0.35).astype(np.float32)

        idx = (self.pixel_choice + int(local_t * 23.0)) % len(palette)
        colors = palette[idx]

        weight = 0.85 + 0.55 * (1.0 - self.yn)
        out = colors * (blink_gate * twinkle)[:, None] * weight[:, None] * self.finale_brightness
        out = _gamma_boost(out, self.gamma)

        self.frameBuf[:] = np.clip(out, 0.0, 255.0).astype(np.uint8)

    def renderNextFrame(self):
        dt = 1.0 / float(self.fps) if self.fps else 1.0 / 30.0
        self.t += dt

        loop_t = self.t % self.loop_seconds
        finale_start = self.loop_seconds - self.finale_seconds

        self.frameBuf[:] = 0

        if loop_t >= finale_start:
            self._render_finale(loop_t - finale_start)
            return

        accum = np.zeros((NUM_PIXELS, 3), dtype=np.float32)
        base_weight = 0.95 + 0.55 * (1.0 - self.yn)

        # Ambient zone glow (helps zones read even between flakes)
        if self.ambient_zone_glow > 1e-6:
            zone_glow = np.zeros((NUM_PIXELS, 3), dtype=np.float32)
            for i in range(NUM_PIXELS):
                zone_glow[i] = self._zone_color(float(self.yn[i]), int(self.pixel_choice[i] % 11))
            zone_glow *= (self.ambient_zone_glow * base_weight)[:, None]
            accum += zone_glow

        for p in self.particles:
            p.y -= p.speed * dt

            p.theta += self.drift * (0.35 + 0.65 * p.speed) * dt * float(
                np.sin((p.y * 6.0 + self.t * 0.85) * 2.0 * np.pi)
            )
            p.theta = float(_wrap_angle(np.array([p.theta], dtype=np.float32))[0])

            if p.y < -0.14:
                newp = self._spawn_particle(at_top=True)
                p.y, p.theta, p.r_target, p.speed, p.color_idx, p.sparkle = (
                    newp.y, newp.theta, newp.r_target, newp.speed, newp.color_idx, newp.sparkle
                )

            dy = np.abs(self.yn - p.y)
            dth = np.abs(_wrap_angle(self.theta - p.theta))
            dr = np.abs(self.rn - p.r_target)

            mask = (dy < self.y_band) & (dth < self.theta_band) & (dr < self.r_band)
            if not np.any(mask):
                continue

            fy = 1.0 - (dy[mask] / self.y_band)
            fth = 1.0 - (dth[mask] / self.theta_band)
            fr = 1.0 - (dr[mask] / self.r_band)

            core = (fy * fth * fr)
            strength = np.power(core, 0.75) * self.flake_peak

            yy = float(np.clip(p.y, 0.0, 1.0))
            c = self._zone_blend_color(yy, p.color_idx)

            if p.sparkle:
                sparkle_wave = 0.60 + 0.40 * np.sin(2.0 * np.pi * (6.5 * self.t + (p.theta + np.pi) * 0.25))
                c = c * (1.0 + (self.sparkle_boost - 1.0) * float(np.clip(sparkle_wave, 0.0, 1.0)))

            w = base_weight[mask]
            accum[mask] += (c[None, :] * strength[:, None] * w[:, None])

        accum *= self.brightness
        accum = _gamma_boost(accum, self.gamma)
        self.frameBuf[:] = np.clip(accum, 0.0, 255.0).astype(np.uint8)


class Animation(ConfettiSnowfallColorZones):
    pass
>>>>>>> Stashed changes
