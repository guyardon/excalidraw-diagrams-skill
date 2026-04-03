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

### Rule 8: Grid layouts must use dynamic row/column heights

When placing elements in a grid (e.g. 2x2), **never use a fixed row height**. Calculate each row's height from its tallest element, then position the next row relative to that:

```python
# BAD: fixed row height creates gaps when content varies
row2_y = START_Y + 350 + GAP  # 350 is a guess

# GOOD: calculate from actual content
row1_heights = [calc_group_height(g) for g in row1_groups]
row1_max_h = max(row1_heights)
row2_y = START_Y + row1_max_h + GAP
```

This applies to any layout with variable-size elements — timelines, grids, stacked sections. Always derive the next position from the actual computed height of the previous element.

### Rule 9: Use `#1e1e1e` for text that must be readable in both themes

Excalidraw's dark mode inverts colors. `#ffffff` (white) becomes `#000000` (black), making text on colored backgrounds unreadable in dark mode. Use `#1e1e1e` instead — it appears dark in light mode and gets inverted to near-white in dark mode. Stroke colors like `#1971c2` also invert to lighter variants automatically.

```python
# BAD: white text disappears in dark mode (inverts to black)
title_color = "#ffffff"

# GOOD: near-black inverts to near-white
title_color = "#1e1e1e"
```

### Rule 13: Title/subtitle hierarchy requires two text elements per box

When a box needs a title and a subtitle (e.g. a name and description), they must be visually distinct — different font size AND different color. Excalidraw bound text only supports one `fontSize` and one `strokeColor`, so you cannot achieve hierarchy with a single text element. Putting both lines in one bound text at the same size makes them visually indistinguishable.

The correct approach is **one rectangle with two text elements inside**:

1. **Bound title text** — larger fontSize (22-24), color `#1e1e1e`, with `containerId` set to the parent box. This is the primary label that Excalidraw associates with the container.
2. **Free subtitle text** — smaller fontSize (15-16), color = the box's **stroke color** (see Rule 14), with `containerId: None`. This is positioned manually inside the box boundaries but is not formally bound to it.

The box's `boundElements` array references only the title text. The subtitle floats visually inside the box.

**Positioning math:**

```python
# Calculate actual rendered heights
title_h = math.ceil(title_lines * title_fontSize * 1.25)
sub_h = math.ceil(sub_lines * sub_fontSize * 1.25)
gap = 6  # breathing room between title and subtitle

# Center the combined block vertically within the box
combined = title_h + gap + sub_h
top_pad = (BOX_H - combined) // 2

title_y = box_y + top_pad
sub_y = title_y + title_h + gap

# Create the box — only the title is in boundElements
rect(box_id, box_x, box_y, BOX_W, BOX_H, stroke, bg,
     bnd=[{"id": title_id, "type": "text"}])

# Title — bound to container (containerId = box_id)
txt(title_id, box_x, title_y, BOX_W, title_h,
    title_text, 24, color="#1e1e1e", cid=box_id)

# Subtitle — NOT bound (containerId = None), uses stroke color
txt(sub_id, box_x, sub_y, BOX_W, sub_h,
    sub_text, 16, color=stroke)
```

**Box height must accommodate both text elements.** For a single-line title (fontSize 24) + single-line subtitle (fontSize 16): minimum box height = 30 + 6 + 20 + padding = ~80px. For multi-line content, increase to 90-100px.

**Common wrong approaches that look bad:**

- **Stacking two rectangles** (title rect on top, subtitle rect below, 0px gap) — looks like two broken boxes, not one card. Never do this.
- **Single bound text with `\n` between title and subtitle** — both lines render at the same size and color. No visual hierarchy.
- **Using `fontFamily: 2` (Helvetica) for subtitle** — Excalidraw's dark mode color inversion doesn't distinguish between font families. The visual difference is too subtle.

### Rule 14: Subtitle color must be the box's stroke color, not gray

When using dual text elements (Rule 13), the subtitle color must be the parent box's **stroke color** — not a neutral gray.

Gray (`#868e96`) appears too dark and muddy in light mode, and when Excalidraw inverts it for dark mode, it becomes a washed-out light gray that lacks contrast against the dark background. It looks wrong in both themes.

The box's stroke color (e.g. `#1971c2` for blue, `#2f9e44` for green) works because:
- In **light mode**, it's a medium-saturated color that clearly differs from the `#1e1e1e` title while harmonizing with the box's fill
- In **dark mode**, Excalidraw inverts it to a lighter variant that remains readable against the dark background
- It creates a **color-coded relationship** between the subtitle and its parent box, reinforcing the visual grouping

```python
# BAD — gray subtitle: poor contrast in both themes
txt(sub_id, x, y, w, h, sub_text, 16, color="#868e96")

# BAD — black subtitle: same color as title, no hierarchy
txt(sub_id, x, y, w, h, sub_text, 16, color="#1e1e1e")

# GOOD — stroke color: harmonizes with box, inverts naturally
txt(sub_id, x, y, w, h, sub_text, 16, color=stroke)
```

This applies to any secondary/descriptive text within a colored box. If the box has stroke `#c92a2a` (red), the subtitle should be `#c92a2a`. If `#0c8599` (cyan), the subtitle should be `#0c8599`.

### Rule 15: Minimum font sizes

SVGs render at `width: 100%` of their container. On a typical content column (~700px), small font sizes become illegible. These are hard minimums — never go below them:

| Element | Min fontSize | Typical fontSize |
|---|---|---|
| Diagram title | 28 | 28 |
| Section subtitles / labels | 22 | 22-24 |
| Box text / body labels | 20 | 20-22 |
| Small pills / badges / tags | 17 | 17-18 |
| Subtitles / descriptions (Rule 13) | 15 | 15-16 |

**When font size feels too large for the layout, the layout is wrong** — don't shrink the font. Instead, rethink the layout: switch from horizontal to vertical (Rule 16), break into separate diagrams (Rule 19), or reduce the number of elements.

### Rule 16: Prefer vertical flows over horizontal for multi-step processes

When a process has 4+ sequential steps, a horizontal layout forces every box to be narrow and every label to use a small font to fit within the diagram width. A vertical layout (top to bottom) allows boxes to be wider with comfortable font sizes.

**Horizontal flow problems:**
- Box width shrinks proportionally with the number of steps (6 steps at 130px each = 780px + arrows = too wide or too small)
- Forces fontSize to 16-17px to fit labels — below the minimum (Rule 15)
- Arrows become short horizontal stubs that are hard to follow
- No room for branching or annotations

**Vertical flow advantages:**
- Box width is independent of step count — use 160-200px regardless
- Font can stay at 20px+ comfortably
- Downward arrows clearly show progression
- Side branches (e.g. a Data Mart branching off a Warehouse) have horizontal space

**For parallel processes** (e.g. ETL vs ELT vs Streaming), place each as a vertical column side by side with ~80px column gap. Label each column at the top. This creates a clear visual comparison.

```python
# Layout for 3 parallel vertical flows:
COL_GAP = 80
BOX_W = 160
BOX_H = 55
VERT_GAP = 50  # between boxes in a column (room for arrows)

COL1_X = 40
COL2_X = COL1_X + BOX_W + COL_GAP   # 280
COL3_X = COL2_X + BOX_W + COL_GAP   # 520

# Each column flows top-to-bottom with VERT_GAP between boxes
```

### Rule 17: Arrow spacing — minimum 50px gap between connected elements

The gap between a source box's bottom edge and a target box's top edge must be at least **50px** for vertical arrows (or 50px between right edge and left edge for horizontal arrows). This space is where the arrow shaft and arrowhead render.

Below 50px, arrows appear as tiny stubs that are hard to see and make the diagram feel cramped. This is especially important for **fan-out patterns** (one source → multiple targets) where arrows need room to diverge.

```python
# BAD: 16px gap — arrow is barely visible
PILL_GAP_Y = 16
pill_y = card_bottom + PILL_GAP_Y

# GOOD: 50px gap — arrow has room to render clearly
PILL_GAP_Y = 50
pill_y = card_bottom + PILL_GAP_Y
```

For fan-out arrows (e.g. one box splitting into 5 targets), 50px is the minimum. 60-70px gives even better results because the arrows need horizontal space to diverge.

### Rule 18: Title-to-content spacing — 25-30px

The vertical gap between the diagram's main title and the first content element (box, card, etc.) should be **25-30px**.

- **Too little (< 15px):** The title visually merges with or overlaps the first element, especially in Virgil font which has tall ascenders/descenders.
- **Too much (> 40px):** Creates a visible blank band that looks like a rendering error or missing content. The diagram feels disconnected from its title.

```python
TITLE_Y = 20
TITLE_H = math.ceil(2 * 28 * 1.25)  # 2-line title at fontSize 28
CONTENT_START_Y = TITLE_Y + TITLE_H + 25  # 25px gap — not 10, not 50
```

This rule applies only to the **diagram title → first element** gap. Gaps between content sections within the diagram can vary based on context (e.g. 40px before a new section label, 12-16px between stacked cards of the same type).

### Rule 19: Separate diagrams for sub-concepts

If a concept requires visual explanation but doesn't integrate cleanly into the main diagram, **create a separate focused diagram** rather than forcing it in. Signs you need a separate diagram:

- A branch or callout is cramped and overlapping other elements
- Adding it requires shrinking the main diagram's boxes or fonts
- The sub-concept has enough internal structure to stand on its own (e.g. a warehouse breaking into 4 data marts)
- The sub-concept appears in a different paragraph of the source content

Each diagram should have **one clear focus**. A flow diagram shows a process. A breakdown diagram shows decomposition. A comparison diagram shows alternatives. Don't mix these in one diagram — create one per concept and embed each in the relevant content section.

### Rule 20: Secondary elements go below the main content, not beside it

Callout boxes, legend items, decision categories, notes, and other supplementary elements should be placed **below** the primary diagram content, centered across the diagram width.

**Why not beside:**
- Side placement forces the diagram into a wide aspect ratio that wastes vertical space and makes the primary content narrower
- SVGs render at `width: 100%` — a wide diagram makes everything smaller
- Side elements look disconnected from the main visual flow
- Readers scan top-to-bottom, not left-to-right

**Layout pattern:**
```python
# Primary content occupies full width
CONTENT_W = 500
# ... build main diagram ...

# Secondary elements centered below, with a section gap
SECONDARY_TOP = content_bottom + 40
label_x = (CONTENT_W - label_w) // 2  # centered

# Side-by-side callout boxes, centered as a group
pair_total_w = BOX_W * 2 + GAP
pair_start_x = (CONTENT_W - pair_total_w) // 2
```

Add a **section label** (fontSize 22) above secondary elements to introduce them (e.g. "Decision Categories" above a pair of decision-type boxes). This visually separates the secondary section from the main content.

### Rule 21: Choose layout type based on content semantics

The layout should reflect what the content **means**, not just organize it spatially:

| Content type | Layout | Why |
|---|---|---|
| Sequential process (ETL pipeline) | **Vertical flow** with arrows | Shows progression/order |
| Parallel alternatives (ETL vs ELT) | **Side-by-side vertical columns** | Enables visual comparison |
| Hierarchical layers (architecture domains) | **Stacked horizontal bands** | Conveys layering/strata |
| Categories of equal weight | **Grid (2x2, 3x2)** | No implied hierarchy |
| Decomposition (warehouse → marts) | **Fan-out from top** | Shows breaking apart |
| Properties/principles (list of 5) | **Stacked cards** | Scannable ordered list |

**Don't default to grids.** A 2x2 grid implies all four items are equal-weight categories. If the content has layers, hierarchy, or ordering, use a layout that conveys that meaning.

### Rule 22: Don't use split left-right boxes for label/description pairs

A common temptation is to show name/description pairs as two boxes side-by-side — a narrow colored box with the name on the left, and a wider lighter box with the description on the right. This looks cramped, wastes horizontal space on borders, and creates a spreadsheet aesthetic.

Instead, use **single wide boxes with the dual text element approach** (Rule 13): title text on the first line, subtitle text on the second line within the same rectangle. This is cleaner, gives text more room, and reads naturally top-to-bottom.

### Rule 10: Line-wrap long text and pad from box edges

Text that fits at a given font size in standard fonts may overflow in Excalidraw's Virgil font, which is significantly wider. Pre-wrap long titles with `\n` and pad text inward from box edges:

```python
# Pad text 15px from each box edge
text_x = box_x + 15
text_width = box_width - 30
text_y = box_y + 12  # top padding

# Pre-wrap long titles
title = "3. Architect for\nScalability"  # not "3. Architect for Scalability"
```

**Tip:** Use `fillStyle: "solid"` instead of `"hachure"` for blocks with text overlaid — diagonal hachure lines reduce text readability.

### Rule 11: Center titles and element groups relative to diagram width

Titles and grouped elements (like a row of tool pills) must be centered relative to the total diagram width, not left-aligned. Calculate the diagram's effective width from its widest row of elements, then center everything:

```python
# Center a title across the diagram
diagram_w = max_x - min_x  # or calculate from widest element row
title_x = (diagram_w - title_width) // 2
title['textAlign'] = 'center'

# Center a row of pills within a container
pills_total = len(items) * PILL_W + (len(items) - 1) * PILL_GAP
pills_start_x = container_x + (container_w - pills_total) // 2
```

### Rule 12: Keep paired/related elements visually consistent

When two elements are related (e.g. DevOps → DataOps), they must have the same box dimensions, font size, and vertical alignment. Inconsistent sizing makes one element appear more important than the other.

```python
# BAD: different sizes for parallel elements
devops_w, devops_h, devops_font = 180, 55, 20
dataops_w, dataops_h, dataops_font = 200, 65, 24

# GOOD: identical dimensions
BOX_W, BOX_H, FONT_SZ = 190, 60, 22
# use for both devops and dataops
```

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
| Large gap between grid rows/columns | Use dynamic row heights calculated from content, not fixed values |
| Text unreadable in dark mode | Use `#1e1e1e` instead of `#ffffff` — Excalidraw inverts colors in dark mode |
| Text overflows box in Excalidraw rendering | Pre-wrap with `\n`, pad 15px from edges — Virgil font is wider than standard |
| Hachure fill makes overlaid text hard to read | Use `fillStyle: "solid"` for blocks containing text |
| Title not centered over diagram | Calculate diagram width, set `title_x = (diagram_w - title_w) // 2` with `textAlign: "center"` |
| Paired elements have inconsistent sizing | Use same width, height, and fontSize for related/parallel elements |
| Title and subtitle at same font size/color | Use dual text elements: bound title (larger, #1e1e1e) + free subtitle (smaller, box stroke color) |
| Subtitle text in gray (#868e96) | Use box's stroke color instead — gray is unreadable in both themes |
| Two stacked rectangles for title/subtitle hierarchy | Never stack rects — use one rect with two text elements inside |
| Horizontal flow with tiny font for multi-step processes | Use vertical flows — allows wider boxes and 20px+ font |
| Font size below 20px for body text | Minimum: 28 title, 22 box titles, 20 body, 17 pills, 15 subtitles |
| Arrows cramped between boxes | Leave at least 50px gap between source and target boxes |
| Title too close or too far from content | Use 25-30px gap between diagram title and first element |
| Sub-concept crammed into main diagram | Create separate focused diagrams for sub-concepts |
| Callout boxes placed beside main content | Place secondary/callout elements below, not to the side |

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
