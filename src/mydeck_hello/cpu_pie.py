"""CPU usage pie chart app for mydeck.

Draws a live pie chart of CPU time breakdown (user / system / idle / iowait /
irq+softirq / nice / other) on a STREAM DECK key, with the active-CPU
percentage as the label.

Configure in YAML:

    apps:
      - app: mydeck_hello.cpu_pie.CpuPie
        option:
          page_key:
            '@HOME': 5
          interval: 2   # optional, seconds between samples (default 2)
"""
from __future__ import annotations

import logging
from typing import Optional

import psutil
from PIL import Image, ImageDraw

from mydeck import MyDeck, ThreadAppBase, ImageOrFile


# Per-category colors, chosen to be distinguishable on the 72-96px key.
# Order is also the drawing order (counter-clockwise from 12 o'clock).
_SLICES = [
    ("user",    (76, 175, 80)),    # green
    ("nice",    (129, 199, 132)),  # light green
    ("system",  (244, 67, 54)),    # red
    ("irq",     (255, 193, 7)),    # amber (irq + softirq combined)
    ("iowait",  (255, 152, 0)),    # orange
    ("other",   (156, 39, 176)),   # purple (steal + guest + guest_nice)
    ("idle",    (66, 66, 66)),     # dark gray
]

_IMG_SIZE = 100
_PIE_MARGIN = 6  # leave room for the label


class CpuPie(ThreadAppBase):
    """Draws a CPU-time pie chart on the configured key, updated every N seconds."""

    def __init__(self, mydeck: MyDeck, option: Optional[dict] = None):
        super().__init__(mydeck, option or {})
        interval = (option or {}).get("interval", 2)
        try:
            self.time_to_sleep = float(interval)
        except (TypeError, ValueError):
            self.time_to_sleep = 2.0
        # psutil's first call to cpu_times_percent returns zeros; prime it.
        psutil.cpu_times_percent(interval=None)

    def set_image_to_key(self, key: int, page: str) -> None:
        buckets = self._sample()
        busy_percent = 100.0 - buckets.get("idle", 0.0)
        image = self._render_pie(buckets)
        label = f"CPU {busy_percent:5.1f}%"
        try:
            rendered = self.mydeck.render_key_image(
                ImageOrFile(image), label=label, bg_color="black")
            self.update_key_image(key, rendered)
        except Exception as e:
            logging.debug("CpuPie render failed: %s", e)

    def _sample(self) -> dict:
        """Return a name→percent dict with the buckets we care about.

        psutil exposes different fields on Linux vs. macOS vs. Windows; we
        collapse the missing-on-this-OS fields to zero.
        """
        t = psutil.cpu_times_percent(interval=None)
        raw = {
            "user":   getattr(t, "user", 0.0),
            "nice":   getattr(t, "nice", 0.0),
            "system": getattr(t, "system", 0.0),
            "iowait": getattr(t, "iowait", 0.0),
            "irq":    getattr(t, "irq", 0.0) + getattr(t, "softirq", 0.0),
            "other": (getattr(t, "steal", 0.0)
                      + getattr(t, "guest", 0.0)
                      + getattr(t, "guest_nice", 0.0)),
            "idle":   getattr(t, "idle", 0.0),
        }
        # Normalise: psutil is usually already near-100 but clamp to avoid
        # drawing past 360°.
        total = sum(raw.values()) or 1.0
        return {k: (v / total) * 100.0 for k, v in raw.items()}

    def _render_pie(self, buckets: dict) -> Image.Image:
        img = Image.new("RGBA", (_IMG_SIZE, _IMG_SIZE), (0, 0, 0, 255))
        draw = ImageDraw.Draw(img)
        bbox = (
            _PIE_MARGIN, _PIE_MARGIN,
            _IMG_SIZE - _PIE_MARGIN, _IMG_SIZE - _PIE_MARGIN,
        )
        # Start at the top (12 o'clock); PIL's 0° is at 3 o'clock so shift -90.
        angle = -90.0
        for name, color in _SLICES:
            pct = buckets.get(name, 0.0)
            if pct <= 0.01:
                continue
            end = angle + (pct / 100.0) * 360.0
            draw.pieslice(bbox, start=angle, end=end, fill=color,
                          outline=(0, 0, 0, 255))
            angle = end
        return img
