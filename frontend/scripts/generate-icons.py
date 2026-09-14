"""Render the supplied polygon SVG into app icons, using only the standard library.

The source uses M/L/Z paths and even-odd fills. Reject other commands instead
of silently producing incorrect icons if the artwork changes.
"""
from pathlib import Path
import math
import re
import struct
import xml.etree.ElementTree as ET
import zlib

PUBLIC = Path(__file__).resolve().parents[1] / "public"
SVG = ET.parse(PUBLIC / "memento.svg").getroot()
_, _, WIDTH, HEIGHT = map(float, SVG.attrib["viewBox"].split())
PATHS = []
for path in SVG.iter("{http://www.w3.org/2000/svg}path"):
    tokens = re.findall(r"[A-Za-z]|-?\d+(?:\.\d+)?", path.attrib["d"])
    polygons, points = [], []
    i = 0
    while i < len(tokens):
        command = tokens[i]
        i += 1
        if command in ("M", "L"):
            points.append((float(tokens[i]), float(tokens[i + 1])))
            i += 2
        elif command == "Z":
            polygons.append(points)
            points = []
        else:
            raise ValueError(f"Unsupported SVG command: {command}")
    color = bytes.fromhex(path.attrib["fill"].removeprefix("#"))
    PATHS.append((polygons, color))


def chunk(kind, data):
    return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data))


def render(size, inset=0):
    # Supersampling keeps the traced edges smooth at small icon sizes.
    scale = 2
    side = size * scale
    pixels = bytearray(b"\xff\xff\xff" * side * side)
    factor = side * (1 - 2 * inset) / max(WIDTH, HEIGHT)
    ox, oy = (side - WIDTH * factor) / 2, (side - HEIGHT * factor) / 2
    for polygons, color in PATHS:
        edges = []
        for polygon in polygons:
            transformed = [(x * factor + ox, y * factor + oy) for x, y in polygon]
            edges.extend(zip(transformed, transformed[1:] + transformed[:1]))
        for y in range(side):
            scan = y + .5
            crossings = sorted(ax + (scan - ay) * (bx - ax) / (by - ay)
                               for (ax, ay), (bx, by) in edges
                               if (ay <= scan < by) or (by <= scan < ay))
            for left, right in zip(crossings[::2], crossings[1::2]):
                start = max(0, math.ceil(left - .5))
                end = min(side, math.ceil(right - .5))
                if end > start:
                    pixels[(y * side + start) * 3:(y * side + end) * 3] = color * (end - start)
    rows = bytearray()
    for y in range(size):
        rows.append(0)
        for x in range(size):
            for c in range(3):
                rows.append(sum(pixels[((y * scale + dy) * side + x * scale + dx) * 3 + c]
                                for dy in range(scale) for dx in range(scale)) // (scale * scale))
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", size, size, 8, 2, 0, 0, 0))
            + chunk(b"IDAT", zlib.compress(rows)) + chunk(b"IEND", b""))


OUTPUT = PUBLIC / "icons"
OUTPUT.mkdir(exist_ok=True)
for size, name, inset in [(192, "icon-192.png", 0), (512, "icon-512.png", 0),
                           (180, "apple-touch-icon.png", 0), (512, "icon-maskable-512.png", .15)]:
    (OUTPUT / name).write_bytes(render(size, inset))
# Keep legacy asset URLs consistent for bookmarks and cached pages.
(PUBLIC / "memento.png").write_bytes((OUTPUT / "icon-512.png").read_bytes())
favicon = render(32)
(PUBLIC / "favicon.ico").write_bytes(struct.pack("<HHH", 0, 1, 1)
    + struct.pack("<BBBBHHII", 32, 32, 0, 0, 1, 32, len(favicon), 22) + favicon)
