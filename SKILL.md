---
name: excalidraw-diagrams
description: >
  TRIGGER when user asks to create diagrams, flowcharts, architecture visuals,
  or block diagrams in hand-drawn/sketch style. TRIGGER when user mentions
  Excalidraw, .excalidraw files, or wants SVG diagrams with light/dark theme
  support. DO NOT trigger for Mermaid, PlantUML, or other diagram formats.
---

# Excalidraw Diagrams — Programmatic Generation & Embedding

Generate `.excalidraw` JSON files programmatically, export to SVG via headless browser, and embed in static sites with light/dark theme support.

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

Copy `references/generator.py` from this skill folder and modify the "BUILD YOUR DIAGRAM" section. The script provides `rect()`, `txt()`, and `arr()` helpers with centering logic baked in, plus a color palette as tuples (e.g. `BLUE = ("#1971c2", "#a5d8ff")`).

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
.diagram { width: 100%; max-height: 650px; object-fit: contain; border-radius: 12px; margin: 1rem 0; }
.diagram-light { display: none; }
.diagram-dark { display: block; }
[data-theme="light"] .diagram-light { display: block; }
[data-theme="light"] .diagram-dark { display: none; }
```

**Critical:** The `max-height` caps the rendered diagram height. If diagrams appear too small or changes to internal coordinates have no visible effect, this is likely the bottleneck — not the Excalidraw coordinates. 650px is a good balance; 500px clips most diagrams, 800px dominates the page.

**Tall vertical diagrams:** When a diagram has many vertically stacked elements (5+ boxes with arrows and section titles), the default 650px `max-height` will shrink it too much. Override per-diagram with an inline style:
```html
<img src="/images/diagrams/diagram-dark.svg" alt="..." class="diagram diagram-dark" style="max-height: 900px;" />
<img src="/images/diagrams/diagram.svg" alt="..." class="diagram diagram-light" style="max-height: 900px;" />
```
Rule of thumb: 650px for 3-4 vertical blocks, 900px for 5-6+ vertical blocks with arrows and titles.

---

## Layout Rules Summary

These 25 rules prevent the most common iteration cycles. The table below gives the gist — read `references/layout-rules.md` for formulas and code examples when you need them.

| # | Rule | Key point |
|---|---|---|
| 1 | Aspect ratio controls perceived size | Scaling coordinates changes nothing — only canvas width matters |
| 2 | Calculate ALL positions from constants | Define constants, derive everything, print and verify |
| 3 | Text centering needs correct height | `height = ceil(lines * fontSize * 1.25)`, then center in parent |
| 4 | Boxes must have text padding | `width >= chars * fontSize * 0.65 + 40`, `height >= lines * fontSize * 1.25 + 30` |
| 5 | Arrows bind to box edges | Use `startBinding`/`endBinding` to actual target box, not container |
| 6 | Arrow final segment perpendicular | Last point in `points` array determines arrowhead direction |
| 7 | Containers need internal padding | `PADDING = 20-30`, label below inner boxes |
| 8 | Dynamic row heights in grids | Calculate from tallest element, never fixed |
| 9 | Use `#1e1e1e` for text color | Inverts cleanly for dark mode; `#ffffff` becomes unreadable |
| 10 | Pre-wrap text, pad from edges | Virgil is ~30% wider than standard; use `fillStyle: "solid"` for text boxes |
| 11 | Center titles and groups | Relative to diagram width, not left-aligned |
| 12 | Identical dims for related elements | Inconsistent sizing implies unequal importance |
| 13 | Title + subtitle = two text elements | Bound title (large) + free subtitle (small, stroke-colored) in one rect |
| 14 | Subtitle color = stroke color | Not gray — stroke color harmonizes and inverts naturally |
| 15 | Recommended font sizes | 32 title / 24-26 headers / 22 body / 20 pills / 17-19 subtitles |
| 16 | Prefer vertical flows | Horizontal forces narrow boxes; vertical decouples width from step count |
| 17 | Min 70px arrow gap | Below 50px, arrows are tiny stubs; 70-85px recommended for readable spacing |
| 18 | Title-to-content: 25-30px | Less than 15px merges visually; more than 40px looks empty |
| 19 | Separate diagrams for sub-concepts | One clear focus per diagram — don't cram |
| 20 | Secondary elements go below | Side placement forces wide aspect ratio |
| 21 | Layout matches content semantics | Vertical flow for sequence, columns for comparison, grid for equal-weight |
| 22 | No split left/right label boxes | Use single wide box with dual text (Rule 13) |
| 23 | Canvas width controls size | Widen canvas AND stretch content to fill — no centered narrow blocks |
| 24 | Box widths from canvas width | `CONTENT_W = CANVAS_W - 2 * PAD_X`, derive all widths from that |
| 25 | Text height from line count | `text.count('\n') + 1` — wrong count crops bottom lines |

---

## Before Exporting

Check `gotchas.md` for the full list of things that look right in code but render wrong. The top traps:

- **Text not centered?** Height must be `ceil(lines * fontSize * 1.25)`, not the box height (Rule 3)
- **Dark mode broken?** Text must be `#1e1e1e`, never `#ffffff` (Rule 9)
- **Arrow invisible?** Gap between elements must be >= 50px (Rule 17)
- **Scaling did nothing?** Widen canvas AND stretch content to fill (Rule 23)
- **Bottom text cropped?** Height uses wrong line count — check `text.count('\n') + 1` (Rule 25)

---

## Reference Files

| File | Contains |
|---|---|
| `references/generator.py` | Runnable Python template with `rect()`, `txt()`, `arr()` helpers and color palette |
| `references/layout-rules.md` | All 25 layout rules with detailed formulas and code examples |
| `references/json-reference.md` | Excalidraw JSON element types, property values, color palette, file wrapper |
| `gotchas.md` | Pre-export checklist — symptoms and fixes for common rendering bugs |
