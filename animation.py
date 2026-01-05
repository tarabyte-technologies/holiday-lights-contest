# animation.py
from __future__ import annotations

import time
from typing import Optional, Tuple

import numpy as np

from lib.base_animation import BaseAnimation
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
    """

    def __init__(
        self,
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
