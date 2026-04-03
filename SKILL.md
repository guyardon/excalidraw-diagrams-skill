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

| Rule | Topic |
|---|---|
| 1 | Aspect ratio controls perceived size — scaling coordinates changes nothing |
| 2 | Calculate ALL positions from constants — never eyeball |
| 3 | Text centering: set height from line count, calculate y offset manually |
| 4 | Box sizing: must accommodate text width + 20px padding each side |
| 5 | Arrow binding: use `startBinding`/`endBinding` to hit box edges |
| 6 | Arrow final segment must be perpendicular to target face |
| 7 | Encapsulating containers: shrink-wrap inner boxes with PADDING offset |
| 8 | Grid row heights: dynamic from content, never fixed |
| 9 | Use `#1e1e1e` for text — white inverts to black in dark mode |
| 10 | Pre-wrap long text with `\n`; pad free-floating text 15px from edges |
| 11 | Center titles and groups relative to diagram width |
| 12 | Paired/related elements must share identical dimensions |
| 13 | Title + subtitle: one rect, two text elements (bound title + free subtitle) |
| 14 | Subtitle color = box stroke color, never gray |
| 15 | Font size minimums: 28 title / 22 box titles / 20 body / 17 pills / 15 subtitles |
| 16 | Prefer vertical flows for multi-step processes |
| 17 | Arrow gap: minimum 50px between connected elements |
| 18 | Title-to-content gap: 25-30px |
| 19 | Sub-concepts get their own separate diagram |
| 20 | Secondary elements go below main content, not beside it |
| 21 | Layout type must reflect content semantics |
| 22 | No split left/right boxes for label/description pairs |
| 23 | To control size: widen canvas AND stretch content to fill it |
| 24 | Box widths derived from canvas width, never hardcoded |
| 25 | Text height from `text.count('\n') + 1` — wrong count crops lines |

### Rule 1: Aspect ratio controls perceived size, not internal scale

SVG renders at `width: 100%` of its container. Scaling all coordinates proportionally changes nothing visually. To make elements appear larger, make the diagram taller relative to its width (vertical layout) or use a narrower canvas.

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

Excalidraw does NOT auto-center text by matching container dimensions. Calculate manually:

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

**Always set `containerId` on text and add the text to the parent's `boundElements` array.** For dual-text hierarchy (title + subtitle) within one box, see Rule 13 — it extends this pattern. For height calculation in free-floating text, see Rule 25.

### Rule 4: Boxes must have padding for text

Box dimensions must accommodate text width + padding. For Virgil font (fontFamily 1), characters are ~60-70% of fontSize in width:

```
box_width >= max_line_chars * fontSize * 0.65 + 40   (20px padding each side)
box_height >= num_lines * fontSize * lineHeight + 30  (15px padding top/bottom)
```

For text like "Transformation\nQueries & Modeling" at fontSize 17:
- Longest line ~20 chars → width >= 20 * 17 * 0.65 + 40 = 261 → use 280
- 2 lines → height >= 2 * 17 * 1.25 + 30 = 72.5 → use 85

### Rule 5: Arrows must end at box borders, not inside

Use binding to attach arrows to box edges:

```python
arrow['startBinding'] = {"elementId": "source-box", "focus": 0, "gap": 4}
arrow['endBinding'] = {"elementId": "target-box", "focus": 0, "gap": 4}
```

**Bind to the actual target box, not an encapsulating container.**

### Rule 6: Arrow's final segment must be perpendicular to the target face

The arrowhead direction is determined by the **last segment** of `points`. Entering a left/right edge → final segment must be horizontal; entering top/bottom edge → final segment must be vertical:

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

Use `PADDING = 20` (tight) to `30` (comfortable). The `PAD = 30` constant from Rule 2 works well:

```python
container_x = inner_box_x - PADDING
container_y = inner_box_y - PADDING
container_w = inner_box_w + PADDING * 2
container_h = (last_inner_bottom + label_space + PADDING) - container_y
```

Place the container's label text **inside** the zone, below the last inner box.

### Rule 8: Grid layouts must use dynamic row/column heights

Never use a fixed row height. Calculate each row's height from its tallest element:

```python
# BAD: fixed row height creates gaps when content varies
row2_y = START_Y + 350 + GAP

# GOOD: calculate from actual content
row1_heights = [calc_group_height(g) for g in row1_groups]
row1_max_h = max(row1_heights)
row2_y = START_Y + row1_max_h + GAP
```

Always derive the next position from the actual computed height of the previous element.

### Rule 9: Use `#1e1e1e` for text readable in both themes

Excalidraw's dark mode inverts colors. `#ffffff` (white) inverts to `#000000` (black), making text on colored backgrounds unreadable. Use `#1e1e1e` — it appears dark in light mode and inverts to near-white in dark mode:

```python
# BAD: white text disappears in dark mode (inverts to black)
title_color = "#ffffff"

# GOOD: near-black inverts to near-white
title_color = "#1e1e1e"
```

### Rule 10: Line-wrap long text and pad from box edges

Virgil font is significantly wider than standard fonts. Pre-wrap long titles with `\n` to prevent overflow. For **free-floating text** (no `containerId`), offset 15px inward from box edges:

```python
# For free-floating text positioned manually inside a box:
text_x = box_x + 15
text_width = box_width - 30  # 15px padding each side
text_y = box_y + 12  # top padding

# Pre-wrap long titles
title = "3. Architect for\nScalability"
```

For **bound text** (using `containerId`), set text width = box width and make the box large enough per Rule 4's formula instead.

**Tip:** Use `fillStyle: "solid"` instead of `"hachure"` for blocks with overlaid text — diagonal lines reduce readability.

### Rule 11: Center titles and element groups relative to diagram width

Titles and grouped elements must be centered relative to the total diagram width, not left-aligned:

```python
# Center a title across the diagram
diagram_w = max_x - min_x
title_x = (diagram_w - title_width) // 2
title['textAlign'] = 'center'

# Center a row of pills within a container
pills_total = len(items) * PILL_W + (len(items) - 1) * PILL_GAP
pills_start_x = container_x + (container_w - pills_total) // 2
```

### Rule 12: Keep paired/related elements visually consistent

Related elements must have identical box dimensions, font size, and vertical alignment — inconsistent sizing implies unequal importance:

```python
# BAD: different sizes for parallel elements
devops_w, devops_h, devops_font = 180, 55, 20
dataops_w, dataops_h, dataops_font = 200, 65, 24

# GOOD: identical dimensions
BOX_W, BOX_H, FONT_SZ = 190, 60, 22
# use for both devops and dataops
```

### Rule 13: Title/subtitle hierarchy requires two text elements per box

When a box needs a title and subtitle, use **one rectangle with two text elements** — a single bound text can't support two font sizes or colors. Never stack two rectangles or use a single `\n`-separated text at the same size.

1. **Bound title text** — larger fontSize (22-24), color `#1e1e1e`, with `containerId` set to the parent box.
2. **Free subtitle text** — smaller fontSize (15-16), color = box's stroke color (Rule 14), `containerId: None`, positioned manually.

The box's `boundElements` array references only the title text.

**Positioning math:**

```python
title_h = math.ceil(title_lines * title_fontSize * 1.25)
sub_h = math.ceil(sub_lines * sub_fontSize * 1.25)
gap = 6

combined = title_h + gap + sub_h
top_pad = (BOX_H - combined) // 2

title_y = box_y + top_pad
sub_y = title_y + title_h + gap

rect(box_id, box_x, box_y, BOX_W, BOX_H, stroke, bg,
     bnd=[{"id": title_id, "type": "text"}])

txt(title_id, box_x, title_y, BOX_W, title_h,
    title_text, 24, color="#1e1e1e", cid=box_id)

txt(sub_id, box_x, sub_y, BOX_W, sub_h,
    sub_text, 16, color=stroke)
```

Box height for 1-line title (fontSize 24) + 1-line subtitle (fontSize 16): minimum ~80px.

### Rule 14: Subtitle color must be the box's stroke color, not gray

Gray (`#868e96`) is too dark in light mode and washes out in dark mode. The box's stroke color (e.g. `#1971c2` blue, `#2f9e44` green) harmonizes with the box fill in light mode and inverts to a readable lighter variant in dark mode:

```python
# BAD — gray subtitle: poor contrast in both themes
txt(sub_id, x, y, w, h, sub_text, 16, color="#868e96")

# GOOD — stroke color: harmonizes with box, inverts naturally
txt(sub_id, x, y, w, h, sub_text, 16, color=stroke)
```

### Rule 15: Minimum font sizes

SVGs render at `width: 100%`. On a typical content column (~700px), small fonts become illegible. Hard minimums:

| Element | Min fontSize | Typical fontSize |
|---|---|---|
| Diagram title | 28 | 28 |
| Section headers / box titles (Rule 13) | 22 | 22-24 |
| Box text / body labels (simple single-text boxes) | 20 | 20-22 |
| Small pills / badges / tags | 17 | 17-18 |
| Subtitles / descriptions (Rule 13) | 15 | 15-16 |

**When font size feels too large, the layout is wrong** — rethink the layout (switch to vertical per Rule 16, break into separate diagrams per Rule 19) rather than shrinking the font.

### Rule 16: Prefer vertical flows over horizontal for multi-step processes

Horizontal flows force narrow boxes and small fonts as step count increases. Vertical flows decouple box width from step count, keeping fonts at 20px+. For parallel processes (e.g. ETL vs ELT vs Streaming), use side-by-side vertical columns with ~80px gap:

```python
COL_GAP = 80
BOX_W = 160
BOX_H = 55
VERT_GAP = 50  # min per Rule 17 — enough room for arrow shaft

COL1_X = 40
COL2_X = COL1_X + BOX_W + COL_GAP   # 280
COL3_X = COL2_X + BOX_W + COL_GAP   # 520
```

### Rule 17: Arrow spacing — minimum 50px gap between connected elements

The gap between source bottom and target top (or right/left for horizontal arrows) must be at least **50px**. Below 50px, arrows appear as tiny stubs. For fan-out patterns (one → many), use 60-70px to give diverging arrows room:

```python
# BAD: 16px gap — arrow is barely visible
PILL_GAP_Y = 16

# GOOD: 50px gap — arrow has room to render clearly
PILL_GAP_Y = 50
```

### Rule 18: Title-to-content spacing — 25-30px

The gap between the diagram title and first content element should be **25-30px**. Less than 15px causes visual merging; more than 40px looks like missing content:

```python
TITLE_Y = 20
TITLE_H = math.ceil(2 * 28 * 1.25)  # 2-line title at fontSize 28
CONTENT_START_Y = TITLE_Y + TITLE_H + 25
```

### Rule 19: Separate diagrams for sub-concepts

Create a separate focused diagram (rather than forcing it into the main one) when a branch is cramped, adding it requires shrinking boxes/fonts, or the sub-concept has enough internal structure to stand alone. Each diagram should have **one clear focus** — flow, decomposition, or comparison.

### Rule 20: Secondary elements go below the main content, not beside it

Side placement forces a wide aspect ratio that makes the primary content smaller. Place callouts, legends, and supplementary elements **below**, centered across the diagram width:

```python
# content_bottom = y + height of the last primary content element
content_bottom = last_element_y + last_element_h
SECONDARY_TOP = content_bottom + 40
label_x = (CONTENT_W - label_w) // 2  # centered

pair_total_w = BOX_W * 2 + GAP
pair_start_x = (CONTENT_W - pair_total_w) // 2
```

Add a section label (fontSize 22) above secondary elements to visually separate them from main content.

### Rule 21: Choose layout type based on content semantics

| Content type | Layout | Why |
|---|---|---|
| Sequential process | **Vertical flow** with arrows | Shows progression/order |
| Parallel alternatives | **Side-by-side vertical columns** | Enables visual comparison |
| Hierarchical layers | **Stacked horizontal bands** | Conveys layering/strata |
| Categories of equal weight | **Grid (2x2, 3x2)** | No implied hierarchy |
| Decomposition | **Fan-out from top** | Shows breaking apart |
| Properties/principles | **Stacked cards** | Scannable ordered list |

Don't default to grids — use a layout that conveys the content's actual meaning.

### Rule 22: Don't use split left-right boxes for label/description pairs

Side-by-side name/description box pairs are cramped and spreadsheet-like. Use single wide boxes with the dual text element approach (Rule 13) instead.

### Rule 23: Controlling perceived diagram size through canvas width

Three approaches that **don't work**: proportional coordinate scaling (SVG stretches back to 100% width), CSS max-width wrappers (awkward whitespace), centering small content in a wide canvas (dead space with same apparent element size).

**The correct approach:** Widen the canvas AND stretch all content blocks to fill it. The canvas width is the lever — content must always fill it:

```python
# BAD: wide canvas, narrow content centered → dead whitespace, same apparent size
CANVAS_W = 700
CONTENT_W = 380                         # content doesn't fill the canvas
OFFSET_X = (CANVAS_W - CONTENT_W) // 2  # floating in the middle

# GOOD: wide canvas, content stretches to fill → elements appear smaller
CANVAS_W = 700
PAD_X = 20
CONTENT_W = CANVAS_W - 2 * PAD_X  # 660 — fills the canvas
WIDE_W = CONTENT_W                 # headers span full width
PAIR_W = (CONTENT_W - PAIR_GAP) // 2  # pairs fill half each
```

### Rule 24: Calculate box widths dynamically from canvas width

Never hardcode box widths — derive from canvas/content width so they scale when canvas changes:

```python
CANVAS_W = 700
PAD_X = 20
CONTENT_W = CANVAS_W - 2 * PAD_X

WIDE_W = CONTENT_W                         # full-width headers
PAIR_W = (CONTENT_W - PAIR_GAP) // 2       # half-width pairs
COL_W = (CONTENT_W - 2 * COL_GAP) // 3    # third-width columns

LEFT_X = PAD_X
RIGHT_X = LEFT_X + PAIR_W + PAIR_GAP
WIDE_X = PAD_X
```

### Rule 25: Always calculate text height from actual line count

Always derive height from `text.count('\n') + 1`. A common bug: calculating for 1 line when text has `\n`, cropping the bottom lines. (Rule 3 uses the same formula for centering bound text — the two rules are complementary: Rule 3 sets the y-position, this rule ensures the height is correct first.)

```python
# BAD: hardcoded line count
sub_text = "Single codebase,\ntightly coupled"  # 2 lines!
sub_h = math.ceil(1 * 16 * 1.25)  # crops "tightly coupled"

# GOOD: derive from text
num_lines = sub_text.count('\n') + 1  # 2
sub_h = math.ceil(num_lines * 16 * 1.25)
```

---

## Excalidraw JSON Element Reference

Other shape types (`"ellipse"`, `"diamond"`) use the same universal properties below — only `"type"` changes.

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

**`autoResize` caveat:** When `true`, Excalidraw may override your calculated height. For free-floating text where exact height matters (Rule 13 subtitles, Rule 25), set `"autoResize": false` if text still renders incorrectly after calculating height manually.

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

## Pre-export Checklist

Scan this before exporting. These are the non-obvious gotchas — things that look right in code but render wrong.

| Symptom | Fix |
|---|---|
| Diagram looks same size after coordinate scaling | SVG is `width: 100%` — only canvas width and aspect ratio affect apparent size |
| Text top-aligned despite `verticalAlign: "middle"` | Text height must equal actual rendered height (`ceil(lines * size * 1.25)`), not box height |
| Arrow ends inside box or misses target | `endBinding.elementId` must point to the actual box, not an encapsulating container |
| Arrowhead points sideways into target face | Last segment of `points` must be perpendicular to the target edge (Rule 6) |
| Container label overlaps inner boxes | Place label below all inner boxes; verify y-ranges don't overlap |
| Text unreadable in dark mode | Use `#1e1e1e` for text — `#ffffff` inverts to `#000000` |
| Text overflows box in rendering | Pre-wrap with `\n`; Virgil font is ~30% wider than standard fonts |
| Hachure pattern makes text hard to read | Use `fillStyle: "solid"` for any box that contains text |
| Title and subtitle look identical | Use dual text elements (Rule 13): bound title larger + free subtitle at stroke color |
| Subtitle muddy/washed out in both themes | Use box stroke color, not gray `#868e96` |
| Proportional scaling made no visual difference | Widen canvas AND stretch content to fill it (Rule 23) |
| Content floats centered with side whitespace | Content must fill canvas width — no centered narrow blocks in wide canvas |
| Bottom lines of multi-line text cropped | Height calculated for wrong line count — use `text.count('\n') + 1` |
| `autoResize` overrides calculated text height | Set `"autoResize": false` for free-floating text with manually calculated height |

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
