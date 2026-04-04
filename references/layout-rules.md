# Layout Rules — Detailed Reference

Read this file when you need the specific formulas and code examples behind the layout rules summarized in SKILL.md.

---

## Rule 1: Aspect ratio controls perceived size, not internal scale

SVG renders at `width: 100%` of its container. Scaling all coordinates proportionally changes nothing visually. To make elements appear larger, make the diagram taller relative to its width (vertical layout) or use a narrower canvas.

## Rule 2: Calculate ALL positions from constants

Define constants and derive everything:

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

## Rule 3: Text centering requires correct height calculation

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

**Always set `containerId` on text and add the text to the parent's `boundElements` array.** For dual-text hierarchy (title + subtitle) within one box, see Rule 13. For height calculation in free-floating text, see Rule 25.

## Rule 4: Boxes must have padding for text

Box dimensions must accommodate text width + padding. For Virgil font (fontFamily 1), characters are ~60-70% of fontSize in width:

```
box_width >= max_line_chars * fontSize * 0.65 + 40   (20px padding each side)
box_height >= num_lines * fontSize * lineHeight + 30  (15px padding top/bottom)
```

For text like "Transformation\nQueries & Modeling" at fontSize 17:
- Longest line ~20 chars -> width >= 20 * 17 * 0.65 + 40 = 261 -> use 280
- 2 lines -> height >= 2 * 17 * 1.25 + 30 = 72.5 -> use 85

## Rule 5: Arrows must end at box borders, not inside

Use binding to attach arrows to box edges:

```python
arrow['startBinding'] = {"elementId": "source-box", "focus": 0, "gap": 4}
arrow['endBinding'] = {"elementId": "target-box", "focus": 0, "gap": 4}
```

**Bind to the actual target box, not an encapsulating container.**

## Rule 6: Arrow's final segment must be perpendicular to the target face

The arrowhead direction is determined by the **last segment** of `points`. Entering a left/right edge -> final segment must be horizontal; entering top/bottom edge -> final segment must be vertical:

```python
# Arrow arriving at bottom of a box (pointing UP):
points = [
    [0, 0],                    # start
    [dx, 0],                   # go horizontal
    [dx, dy - 40],             # go most of the way up
    [target_cx - start_x, dy - 40],  # go horizontal to align with target center
    [target_cx - start_x, dy]  # final vertical segment -> perpendicular to bottom edge
]
```

## Rule 7: Encapsulating containers need internal padding

Use `PADDING = 20` (tight) to `30` (comfortable):

```python
container_x = inner_box_x - PADDING
container_y = inner_box_y - PADDING
container_w = inner_box_w + PADDING * 2
container_h = (last_inner_bottom + label_space + PADDING) - container_y
```

Place the container's label text **inside** the zone, below the last inner box.

## Rule 8: Grid layouts must use dynamic row/column heights

Calculate each row's height from its tallest element:

```python
# BAD: fixed row height creates gaps when content varies
row2_y = START_Y + 350 + GAP

# GOOD: calculate from actual content
row1_heights = [calc_group_height(g) for g in row1_groups]
row1_max_h = max(row1_heights)
row2_y = START_Y + row1_max_h + GAP
```

## Rule 9: Use `#1e1e1e` for text readable in both themes

Excalidraw's dark mode inverts colors. `#ffffff` inverts to `#000000`, making text on colored backgrounds unreadable. `#1e1e1e` appears dark in light mode and inverts to near-white in dark mode:

```python
# BAD: white text disappears in dark mode (inverts to black)
title_color = "#ffffff"

# GOOD: near-black inverts to near-white
title_color = "#1e1e1e"
```

## Rule 10: Line-wrap long text and pad from box edges

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

## Rule 11: Center titles and element groups relative to diagram width

```python
# Center a title across the diagram
diagram_w = max_x - min_x
title_x = (diagram_w - title_width) // 2
title['textAlign'] = 'center'

# Center a row of pills within a container
pills_total = len(items) * PILL_W + (len(items) - 1) * PILL_GAP
pills_start_x = container_x + (container_w - pills_total) // 2
```

## Rule 12: Keep paired/related elements visually consistent

Related elements must have identical box dimensions, font size, and vertical alignment:

```python
# BAD: different sizes for parallel elements
devops_w, devops_h, devops_font = 180, 55, 20
dataops_w, dataops_h, dataops_font = 200, 65, 24

# GOOD: identical dimensions
BOX_W, BOX_H, FONT_SZ = 190, 60, 22
# use for both devops and dataops
```

## Rule 13: Title/subtitle hierarchy requires two text elements per box

When a box needs a title and subtitle, use **one rectangle with two text elements**. Never stack two rectangles or use a single `\n`-separated text at the same size.

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

Box height for 1-line title (fontSize 24-26) + 1-line subtitle (fontSize 17-19): recommended 95-110px. At 80px, content looks cramped after CSS max-height scaling.

## Rule 14: Subtitle color must be the box's stroke color, not gray

Gray (`#868e96`) is too dark in light mode and washes out in dark mode. The box's stroke color (e.g. `#1971c2` blue) harmonizes with the fill in light mode and inverts to a readable lighter variant in dark mode:

```python
# BAD — gray subtitle
txt(sub_id, x, y, w, h, sub_text, 16, color="#868e96")

# GOOD — stroke color
txt(sub_id, x, y, w, h, sub_text, 16, color=stroke)
```

## Rule 15: Recommended font sizes

SVGs render at `width: 100%` and are typically capped by a CSS `max-height` (650px recommended). Diagrams need generous font sizes to remain legible after scaling.

| Element | Min fontSize | Recommended fontSize |
|---|---|---|
| Diagram title | 28 | 32-34 |
| Section headers / box titles (Rule 13) | 22 | 24-26 |
| Box text / body labels (simple single-text boxes) | 20 | 22 |
| Small pills / badges / tags | 17 | 20 |
| Subtitles / descriptions (Rule 13) | 15 | 17-19 |

Use the **recommended** sizes as your starting point, not the minimums. The minimums are hard floors — diagrams at minimum sizes look cramped after CSS scaling.

**When font size feels too large, the layout is wrong** — rethink the layout (switch to vertical per Rule 16, break into separate diagrams per Rule 19) rather than shrinking the font.

## Rule 16: Prefer vertical flows over horizontal for multi-step processes

Horizontal flows force narrow boxes and small fonts as step count increases. Vertical flows decouple box width from step count. For parallel processes, use side-by-side vertical columns:

```python
COL_GAP = 80
BOX_W = 160
BOX_H = 55
VERT_GAP = 50  # min per Rule 17

COL1_X = 40
COL2_X = COL1_X + BOX_W + COL_GAP   # 280
COL3_X = COL2_X + BOX_W + COL_GAP   # 520
```

## Rule 17: Arrow spacing — minimum 70px gap between connected elements

The gap between source bottom and target top should be at least **70px** for readable arrow spacing. Below 50px, arrows appear as tiny stubs. For fan-out patterns (one -> many), use 80-85px:

```python
# BAD: 16px gap — arrow is invisible stub
PILL_GAP_Y = 16

# MINIMUM: 50px — functional but tight
PILL_GAP_Y = 50

# RECOMMENDED: 70-85px — comfortable spacing after CSS scaling
PILL_GAP_Y = 70
```

## Rule 18: Title-to-content spacing — 25-30px

```python
TITLE_Y = 20
TITLE_H = math.ceil(2 * 28 * 1.25)  # 2-line title at fontSize 28
CONTENT_START_Y = TITLE_Y + TITLE_H + 25
```

## Rule 19: Separate diagrams for sub-concepts

Create a separate focused diagram when a branch is cramped, adding it requires shrinking boxes/fonts, or the sub-concept has enough internal structure to stand alone. Each diagram should have **one clear focus** — flow, decomposition, or comparison.

## Rule 20: Secondary elements go below the main content, not beside it

Side placement forces a wide aspect ratio that makes the primary content smaller:

```python
content_bottom = last_element_y + last_element_h
SECONDARY_TOP = content_bottom + 40
label_x = (CONTENT_W - label_w) // 2  # centered

pair_total_w = BOX_W * 2 + GAP
pair_start_x = (CONTENT_W - pair_total_w) // 2
```

Add a section label (fontSize 22) above secondary elements.

## Rule 21: Choose layout type based on content semantics

| Content type | Layout | Why |
|---|---|---|
| Sequential process | **Vertical flow** with arrows | Shows progression/order |
| Parallel alternatives | **Side-by-side vertical columns** | Enables visual comparison |
| Hierarchical layers | **Stacked horizontal bands** | Conveys layering/strata |
| Categories of equal weight | **Grid (2x2, 3x2)** | No implied hierarchy |
| Decomposition | **Fan-out from top** | Shows breaking apart |
| Properties/principles | **Stacked cards** | Scannable ordered list |

## Rule 22: Don't use split left-right boxes for label/description pairs

Side-by-side name/description box pairs are cramped and spreadsheet-like. Use single wide boxes with the dual text element approach (Rule 13) instead.

## Rule 23: Controlling perceived diagram size through canvas width

Three approaches that **don't work**: proportional coordinate scaling, CSS max-width wrappers, centering small content in a wide canvas.

**The correct approach:** Widen the canvas AND stretch all content blocks to fill it:

```python
# BAD: wide canvas, narrow content centered
CANVAS_W = 700
CONTENT_W = 380
OFFSET_X = (CANVAS_W - CONTENT_W) // 2

# GOOD: wide canvas, content stretches to fill
CANVAS_W = 700
PAD_X = 20
CONTENT_W = CANVAS_W - 2 * PAD_X  # 660
WIDE_W = CONTENT_W
PAIR_W = (CONTENT_W - PAIR_GAP) // 2
```

## Rule 24: Calculate box widths dynamically from canvas width

Never hardcode box widths:

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

## Rule 25: Always calculate text height from actual line count

Always derive height from `text.count('\n') + 1`:

```python
# BAD: hardcoded line count
sub_text = "Single codebase,\ntightly coupled"  # 2 lines!
sub_h = math.ceil(1 * 16 * 1.25)  # crops "tightly coupled"

# GOOD: derive from text
num_lines = sub_text.count('\n') + 1  # 2
sub_h = math.ceil(num_lines * 16 * 1.25)
```
