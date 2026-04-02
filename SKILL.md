---
name: excalidraw-diagrams
description: Use when creating hand-drawn style diagrams for documentation, markdown pages, or static sites. Use when user asks for Excalidraw diagrams, block diagrams, flow diagrams, architecture diagrams, or visual explanations with a sketch aesthetic.
---

# Excalidraw Diagrams — Programmatic Generation & Embedding

## Overview

Generate `.excalidraw` JSON files programmatically, export to SVG via headless browser, and embed in static sites with light/dark theme support. No manual steps required.

## Pipeline

```
Generate .excalidraw JSON → Export via excalidraw-brute-export-cli → Embed SVG in markdown/HTML
```

### 1. Install export tool (once)

```bash
npm install -g excalidraw-brute-export-cli
npx playwright install  # needs browser for rendering
```

### 2. Generate `.excalidraw` JSON

Use a Python script to calculate positions systematically (see Layout Rules below). Never hand-place elements — calculate everything from constants.

### 3. Export both themes

```bash
# Light mode
npx excalidraw-brute-export-cli -i diagram.excalidraw \
  --format svg --background 1 --dark-mode 0 --scale 2 \
  -o public/images/diagrams/diagram.svg

# Dark mode
npx excalidraw-brute-export-cli -i diagram.excalidraw \
  --format svg --background 1 --dark-mode 1 --scale 2 \
  -o public/images/diagrams/diagram-dark.svg
```

### 4. Embed with theme switching

In markdown:
```html
<img src="/images/diagrams/diagram-dark.svg" alt="..." class="diagram diagram-dark" />
<img src="/images/diagrams/diagram.svg" alt="..." class="diagram diagram-light" />
```

CSS (adapt selectors for your theme toggle mechanism):
```css
.diagram { width: 100%; border-radius: 12px; margin: 1rem 0; }
.diagram-light { display: none; }
.diagram-dark { display: block; }
[data-theme="light"] .diagram-light { display: block; }
[data-theme="light"] .diagram-dark { display: none; }
```

---

## Layout Rules (Critical — Prevents Iteration)

### Rule 1: Aspect ratio controls perceived size, not internal scale

SVG renders at `width: 100%` of its container. Scaling all coordinates proportionally changes nothing visually. To make elements appear larger:
- Make the diagram **taller relative to its width** (vertical layout)
- Use a narrower canvas so elements fill more of the width

### Rule 2: Calculate ALL positions from constants

Never eyeball coordinates. Define constants and derive everything:

```python
BW, BH = 240, 85       # box width, height
GAP = 40                # space between stacked boxes
PAD = 30                # padding inside container zones

BOX1_Y = 90
BOX2_Y = BOX1_Y + BH + GAP       # 215
BOX3_Y = BOX2_Y + BH + GAP       # 340
LABEL_Y = BOX3_Y + BH + 15       # 440 (below last box)
NEXT_SECTION_Y = LABEL_Y + 50    # 490
```

Print all positions and verify no overlaps before exporting.

### Rule 3: Text centering requires correct height calculation

Excalidraw does NOT auto-center text by matching container dimensions. You must:

```python
import math

num_lines = text.count('\n') + 1
actual_text_height = math.ceil(num_lines * fontSize * lineHeight)

text_element['height'] = actual_text_height
text_element['y'] = parent['y'] + (parent['height'] - actual_text_height) // 2
text_element['x'] = parent['x']
text_element['width'] = parent['width']
text_element['textAlign'] = 'center'
text_element['verticalAlign'] = 'middle'
```

**Always set `containerId` on text and add the text to the parent's `boundElements` array.**

### Rule 4: Boxes must have padding for text

Box dimensions must accommodate text width + padding. For Virgil font (fontFamily 1), characters are ~60-70% of fontSize in width. Rule of thumb:

```
box_width >= max_line_chars * fontSize * 0.65 + 40   (20px padding each side)
box_height >= num_lines * fontSize * lineHeight + 30  (15px padding top/bottom)
```

For text like "Transformation\nQueries & Modeling" at fontSize 17:
- Longest line ~20 chars → width >= 20 * 17 * 0.65 + 40 = 261 → use 280
- 2 lines → height >= 2 * 17 * 1.25 + 30 = 72.5 → use 85

### Rule 5: Arrows must end at box borders, not inside

Arrow endpoints must be at the edge of the target element. Use binding:

```python
arrow['startBinding'] = {"elementId": "source-box", "focus": 0, "gap": 4}
arrow['endBinding'] = {"elementId": "target-box", "focus": 0, "gap": 4}
```

**Critical: bind to the actual target box, not an encapsulating container.** If an arrow should reach the Ingestion box, bind to `"ing-box"`, not to `"storage-zone"`.

### Rule 6: Arrow's final segment must be perpendicular to the target face

The arrowhead direction is determined by the **last segment** of the `points` array. To arrive perpendicular:

- Entering a box's **left/right edge**: final segment must be **horizontal** (constant y)
- Entering a box's **top/bottom edge**: final segment must be **vertical** (constant x)

```python
# Arrow arriving at bottom of a box (pointing UP):
points = [
    [0, 0],                    # start
    [dx, 0],                   # go horizontal
    [dx, dy - 40],             # go most of the way up
    [target_cx - start_x, dy - 40],  # go horizontal to align with target center
    [target_cx - start_x, dy]  # final vertical segment → perpendicular to bottom edge
]
```

### Rule 7: Encapsulating containers need internal padding

When a dashed container wraps other boxes (like a "Storage" zone):

```python
container_x = inner_box_x - PADDING
container_y = inner_box_y - PADDING
container_w = inner_box_w + PADDING * 2
container_h = (last_inner_bottom + label_space + PADDING) - container_y
```

Place the container's label text **inside** the zone, below the last inner box, with enough room that it doesn't overlap anything below.

---

## Excalidraw JSON Element Reference

### Universal properties (every element)

```json
{
  "type": "rectangle",
  "id": "unique-id",
  "x": 100, "y": 100, "width": 200, "height": 80,
  "angle": 0,
  "strokeColor": "#1971c2",
  "backgroundColor": "#a5d8ff",
  "fillStyle": "hachure",
  "strokeWidth": 2,
  "strokeStyle": "solid",
  "roughness": 1,
  "opacity": 100,
  "roundness": { "type": 3 },
  "seed": 42,
  "version": 1, "versionNonce": 1,
  "isDeleted": false,
  "groupIds": [],
  "boundElements": [],
  "frameId": null, "link": null, "locked": false,
  "updated": 1710000000000
}
```

### Key property values

| Property | Values |
|---|---|
| `fontFamily` | `1` = Virgil (hand-drawn), `2` = Helvetica, `3` = Cascadia (mono), `5` = Excalifont (new hand-drawn) |
| `roughness` | `0` = clean, `1` = sketchy, `2` = very rough |
| `fillStyle` | `"solid"`, `"hachure"`, `"cross-hatch"`, `"zigzag"`, `"dots"` |
| `strokeStyle` | `"solid"`, `"dashed"`, `"dotted"` |
| `roundness` | `null` = sharp corners, `{ "type": 3 }` = rounded |

### Text element (bound to container)

```json
{
  "type": "text",
  "id": "label-1",
  "containerId": "rect-1",
  "text": "Hello\nWorld",
  "originalText": "Hello\nWorld",
  "fontSize": 20,
  "fontFamily": 1,
  "textAlign": "center",
  "verticalAlign": "middle",
  "lineHeight": 1.25,
  "autoResize": true
}
```

**Bidirectional binding:** Text sets `containerId`, parent adds `{"id": "label-1", "type": "text"}` to `boundElements`.

### Arrow element

```json
{
  "type": "arrow",
  "points": [[0, 0], [150, 0]],
  "startArrowhead": null,
  "endArrowhead": "arrow",
  "startBinding": { "elementId": "box-1", "focus": 0, "gap": 4 },
  "endBinding": { "elementId": "box-2", "focus": 0, "gap": 4 }
}
```

Arrow `points` are **relative to the element's x,y**. Always start with `[0,0]`.

### Recommended color palette

| Purpose | Stroke | Background |
|---|---|---|
| Blue | `#1971c2` | `#a5d8ff` |
| Green | `#2f9e44` | `#b2f2bb` |
| Yellow/Orange | `#e67700` | `#ffec99` or `#fff3bf` |
| Purple | `#6741d9` | `#d0bfff` |
| Red/Pink | `#c92a2a` | `#ffc9c9` |
| Cyan | `#0c8599` | `#99e9f2` |
| Gray (muted) | `#868e96` | `#dee2e6` |

### File wrapper

```json
{
  "type": "excalidraw",
  "version": 2,
  "source": "https://excalidraw.com",
  "elements": [],
  "appState": { "viewBackgroundColor": "#ffffff", "gridSize": null },
  "files": {}
}
```

---

## Common Mistakes

| Mistake | Fix |
|---|---|
| Scaling coordinates proportionally expecting bigger rendering | Change aspect ratio instead — make layout taller/narrower |
| Text overflows box boundaries | Calculate required box size from text content + padding |
| Text appears top-aligned despite `verticalAlign: "middle"` | Set text height to actual rendered height, calculate y offset manually |
| Arrow ends mid-box or at wrong element | Verify `endBinding.elementId` points to the actual target box |
| Arrowhead points parallel to target face | Ensure last segment of `points` array is perpendicular to target edge |
| Storage label overlaps inner boxes | Place label below all inner boxes, verify y-ranges don't overlap |
| Elements overlap after adjustments | Use systematic position calculation, print & verify all y-ranges |
| Diagram looks same size despite scaling | SVG is `width: 100%` — only aspect ratio changes perceived size |

---

## Generator Script Template

Use this Python template as a starting point for new diagrams:

```python
import json, math

data = {
    "type": "excalidraw", "version": 2,
    "source": "https://excalidraw.com",
    "elements": [], "appState": {"viewBackgroundColor": "#ffffff", "gridSize": None}, "files": {}
}
els = data["elements"]
seed = 1000

def ns():
    global seed; seed += 1; return seed

def rect(id, x, y, w, h, stroke, bg, fill="hachure", opacity=100, dashed=False, bnd=None):
    els.append({"type":"rectangle","id":id,"x":x,"y":y,"width":w,"height":h,"angle":0,
        "strokeColor":stroke,"backgroundColor":bg,"fillStyle":fill,"strokeWidth":2,
        "strokeStyle":"dashed" if dashed else "solid","roughness":1,"opacity":opacity,
        "roundness":{"type":3},"seed":ns(),"version":1,"versionNonce":ns(),
        "isDeleted":False,"groupIds":[],"boundElements":bnd or [],
        "frameId":None,"link":None,"locked":False,"updated":1710000000000})

def txt(id, x, y, w, h, t, sz, color="#1e1e1e", cid=None, op=100):
    # If bound to container, calculate centered position
    if cid:
        num_lines = t.count('\n') + 1
        actual_h = math.ceil(num_lines * sz * 1.25)
        y = y + (h - actual_h) // 2
        h = actual_h
    els.append({"type":"text","id":id,"x":x,"y":y,"width":w,"height":h,"angle":0,
        "text":t,"originalText":t,"fontSize":sz,"fontFamily":1,
        "textAlign":"center","verticalAlign":"middle","lineHeight":1.25,"autoResize":True,
        "containerId":cid,"strokeColor":color,"backgroundColor":"transparent",
        "fillStyle":"solid","strokeWidth":2,"strokeStyle":"solid","roughness":1,"opacity":op,
        "seed":ns(),"version":1,"versionNonce":ns(),
        "isDeleted":False,"groupIds":[],"boundElements":[],
        "frameId":None,"link":None,"locked":False,"updated":1710000000000})

def arr(id, x, y, pts, stroke, dash=False, op=100, sb=None, eb=None):
    els.append({"type":"arrow","id":id,"x":x,"y":y,
        "width":pts[-1][0]-pts[0][0],"height":pts[-1][1]-pts[0][1],"angle":0,
        "points":pts,"startArrowhead":None,"endArrowhead":"arrow",
        "startBinding":sb,"endBinding":eb,"elbowed":False,
        "strokeColor":stroke,"backgroundColor":"transparent",
        "fillStyle":"solid","strokeWidth":2,"strokeStyle":"dashed" if dash else "solid",
        "roughness":1,"opacity":op,"seed":ns(),"version":1,"versionNonce":ns(),
        "isDeleted":False,"groupIds":[],"boundElements":[],
        "frameId":None,"link":None,"locked":False,"updated":1710000000000})

# === DEFINE LAYOUT CONSTANTS ===
BW, BH = 240, 85
GAP = 40
PAD = 30

# === CALCULATE ALL POSITIONS ===
# ... derive from constants ...

# === CREATE ELEMENTS ===
# ... use rect(), txt(), arr() ...

# === VERIFY NO OVERLAPS ===
# Print all y-ranges and check

# === WRITE FILE ===
with open('diagram.excalidraw', 'w') as f:
    json.dump(data, f, indent=2)
```

Then export:
```bash
npx excalidraw-brute-export-cli -i diagram.excalidraw --format svg --background 1 --dark-mode 0 --scale 2 -o output.svg
npx excalidraw-brute-export-cli -i diagram.excalidraw --format svg --background 1 --dark-mode 1 --scale 2 -o output-dark.svg
```
