"""
Excalidraw diagram generator template.

Copy this file and modify the "BUILD YOUR DIAGRAM" section.
Helper functions (rect, txt, arr) handle all the boilerplate.

Usage:
    python generator.py              # writes diagram.excalidraw
    python generator.py my-flow      # writes my-flow.excalidraw
"""

import json
import math
import sys

# === FILE STRUCTURE ===

data = {
    "type": "excalidraw",
    "version": 2,
    "source": "https://excalidraw.com",
    "elements": [],
    "appState": {"viewBackgroundColor": "#ffffff", "gridSize": None},
    "files": {},
}
els = data["elements"]
seed = 1000


def ns():
    global seed
    seed += 1
    return seed


# === COLOR PALETTE ===

BLUE = ("#1971c2", "#a5d8ff")
GREEN = ("#2f9e44", "#b2f2bb")
YELLOW = ("#e67700", "#ffec99")
PURPLE = ("#6741d9", "#d0bfff")
RED = ("#c92a2a", "#ffc9c9")
CYAN = ("#0c8599", "#99e9f2")
GRAY = ("#868e96", "#dee2e6")


# === HELPER FUNCTIONS ===


def rect(id, x, y, w, h, stroke, bg, fill="hachure", opacity=100, dashed=False, bnd=None):
    """Create a rectangle element."""
    els.append({
        "type": "rectangle", "id": id, "x": x, "y": y, "width": w, "height": h,
        "angle": 0, "strokeColor": stroke, "backgroundColor": bg,
        "fillStyle": fill, "strokeWidth": 2,
        "strokeStyle": "dashed" if dashed else "solid", "roughness": 1,
        "opacity": opacity, "roundness": {"type": 3},
        "seed": ns(), "version": 1, "versionNonce": ns(),
        "isDeleted": False, "groupIds": [], "boundElements": bnd or [],
        "frameId": None, "link": None, "locked": False, "updated": 1710000000000,
    })


def txt(id, x, y, w, h, t, sz, color="#1e1e1e", cid=None, op=100):
    """Create a text element. If cid (containerId) is set, auto-centers vertically."""
    if cid:
        num_lines = t.count("\n") + 1
        actual_h = math.ceil(num_lines * sz * 1.25)
        y = y + (h - actual_h) // 2
        h = actual_h
    els.append({
        "type": "text", "id": id, "x": x, "y": y, "width": w, "height": h,
        "angle": 0, "text": t, "originalText": t, "fontSize": sz, "fontFamily": 1,
        "textAlign": "center", "verticalAlign": "middle", "lineHeight": 1.25,
        "autoResize": True, "containerId": cid,
        "strokeColor": color, "backgroundColor": "transparent",
        "fillStyle": "solid", "strokeWidth": 2, "strokeStyle": "solid",
        "roughness": 1, "opacity": op,
        "seed": ns(), "version": 1, "versionNonce": ns(),
        "isDeleted": False, "groupIds": [], "boundElements": [],
        "frameId": None, "link": None, "locked": False, "updated": 1710000000000,
    })


def arr(id, x, y, pts, stroke, dash=False, op=100, sb=None, eb=None):
    """Create an arrow element. pts are relative to (x, y). Always starts with [0,0]."""
    els.append({
        "type": "arrow", "id": id, "x": x, "y": y,
        "width": pts[-1][0] - pts[0][0], "height": pts[-1][1] - pts[0][1],
        "angle": 0, "points": pts,
        "startArrowhead": None, "endArrowhead": "arrow",
        "startBinding": sb, "endBinding": eb, "elbowed": False,
        "strokeColor": stroke, "backgroundColor": "transparent",
        "fillStyle": "solid", "strokeWidth": 2,
        "strokeStyle": "dashed" if dash else "solid",
        "roughness": 1, "opacity": op,
        "seed": ns(), "version": 1, "versionNonce": ns(),
        "isDeleted": False, "groupIds": [], "boundElements": [],
        "frameId": None, "link": None, "locked": False, "updated": 1710000000000,
    })


# === LAYOUT CONSTANTS ===

BW, BH = 240, 85       # box width, height
GAP = 40                # space between stacked boxes
PAD = 30                # padding inside container zones


# === BUILD YOUR DIAGRAM ===
# Calculate all positions from constants (Rule 2).
# Example:
#
#   BOX1_Y = 90
#   BOX2_Y = BOX1_Y + BH + GAP
#   BOX3_Y = BOX2_Y + BH + GAP
#
#   rect("box1", 40, BOX1_Y, BW, BH, *BLUE,
#        bnd=[{"id": "t1", "type": "text"}])
#   txt("t1", 40, BOX1_Y, BW, BH, "Step 1", 22, cid="box1")
#
#   rect("box2", 40, BOX2_Y, BW, BH, *GREEN,
#        bnd=[{"id": "t2", "type": "text"}])
#   txt("t2", 40, BOX2_Y, BW, BH, "Step 2", 22, cid="box2")
#
#   arr("a1", 40 + BW // 2, BOX1_Y + BH, [[0, 0], [0, GAP]],
#       BLUE[0],
#       sb={"elementId": "box1", "focus": 0, "gap": 4},
#       eb={"elementId": "box2", "focus": 0, "gap": 4})


# === VERIFY NO OVERLAPS ===
# Print all y-ranges and check before exporting.


# === WRITE FILE ===

name = sys.argv[1] if len(sys.argv) > 1 else "diagram"
outfile = f"{name}.excalidraw"
with open(outfile, "w") as f:
    json.dump(data, f, indent=2)
print(f"Wrote {outfile}")
