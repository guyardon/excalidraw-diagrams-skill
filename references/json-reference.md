# Excalidraw JSON Element Reference

Read this file when you need exact property names, valid values, or the file wrapper structure.

---

## Universal properties (every element)

Other shape types (`"ellipse"`, `"diamond"`) use the same properties — only `"type"` changes.

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

## Key property values

| Property | Values |
|---|---|
| `fontFamily` | `1` = Virgil (hand-drawn), `2` = Helvetica, `3` = Cascadia (mono), `5` = Excalifont (new hand-drawn) |
| `roughness` | `0` = clean, `1` = sketchy, `2` = very rough |
| `fillStyle` | `"solid"`, `"hachure"`, `"cross-hatch"`, `"zigzag"`, `"dots"` |
| `strokeStyle` | `"solid"`, `"dashed"`, `"dotted"` |
| `roundness` | `null` = sharp corners, `{ "type": 3 }` = rounded |

## Text element (bound to container)

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

**`autoResize` caveat:** When `true`, Excalidraw may override your calculated height. For free-floating text where exact height matters (Rule 13 subtitles, Rule 25), set `"autoResize": false`.

## Arrow element

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

## Color palette

| Purpose | Stroke | Background |
|---|---|---|
| Blue | `#1971c2` | `#a5d8ff` |
| Green | `#2f9e44` | `#b2f2bb` |
| Yellow/Orange | `#e67700` | `#ffec99` or `#fff3bf` |
| Purple | `#6741d9` | `#d0bfff` |
| Red/Pink | `#c92a2a` | `#ffc9c9` |
| Cyan | `#0c8599` | `#99e9f2` |
| Gray (muted) | `#868e96` | `#dee2e6` |

These are also available as tuples in `references/generator.py` (e.g. `BLUE = ("#1971c2", "#a5d8ff")`).

## File wrapper

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
