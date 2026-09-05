"""Render the Vocab V mark to PNG with no third-party dependencies."""
from pathlib import Path
import struct
import zlib

OUTPUT = Path(__file__).resolve().parents[1] / "public" / "icons"
# A serif V, within the central safe area for maskable icons.
POLYGON = [(29, 30), (47, 30), (47, 34), (43, 34), (53, 59),
           (63, 34), (58, 34), (58, 30), (73, 30), (73, 34),
           (69, 34), (54, 71), (48, 71), (33, 34), (29, 34)]


def inside(x, y):
    result = False
    for i, (ax, ay) in enumerate(POLYGON):
        bx, by = POLYGON[i - 1]
        if (ay > y) != (by > y) and x < (bx - ax) * (y - ay) / (by - ay) + ax:
            result = not result
    return result


def chunk(kind, data):
    return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data))


OUTPUT.mkdir(parents=True, exist_ok=True)
for size, name in [(192, "icon-192.png"), (512, "icon-512.png"), (180, "apple-touch-icon.png")]:
    rows = bytearray()
    for y in range(size):
        rows.append(0)
        for x in range(size):
            coverage = sum(inside((x + dx) * 100 / size, (y + dy) * 100 / size)
                           for dx in (.25, .75) for dy in (.25, .75)) / 4
            rows.extend(round(bg + (fg - bg) * coverage)
                        for bg, fg in zip((239, 71, 111), (255, 209, 102)))
    png = b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", size, size, 8, 2, 0, 0, 0))
    png += chunk(b"IDAT", zlib.compress(rows)) + chunk(b"IEND", b"")
    (OUTPUT / name).write_bytes(png)
