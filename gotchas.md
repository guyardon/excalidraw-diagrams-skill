# Gotchas — Things That Look Right in Code but Render Wrong

Scan this before exporting any diagram. These are the non-obvious failures that waste iteration cycles.

| Symptom | Fix | Rule |
|---|---|---|
| Diagram looks same size after coordinate scaling | SVG is `width: 100%` — only canvas width and aspect ratio affect apparent size | 1, 23 |
| Text top-aligned despite `verticalAlign: "middle"` | Text height must equal actual rendered height (`ceil(lines * size * 1.25)`), not box height | 3 |
| Arrow ends inside box or misses target | `endBinding.elementId` must point to the actual box, not an encapsulating container | 5 |
| Arrowhead points sideways into target face | Last segment of `points` must be perpendicular to the target edge | 6 |
| Container label overlaps inner boxes | Place label below all inner boxes; verify y-ranges don't overlap | 7 |
| Text unreadable in dark mode | Use `#1e1e1e` for text — `#ffffff` inverts to `#000000` | 9 |
| Text overflows box in rendering | Pre-wrap with `\n`; Virgil font is ~30% wider than standard fonts | 10 |
| Hachure pattern makes text hard to read | Use `fillStyle: "solid"` for any box that contains text | 10 |
| Title and subtitle look identical | Use dual text elements: bound title larger + free subtitle at stroke color | 13 |
| Subtitle muddy/washed out in both themes | Use box stroke color, not gray `#868e96` | 14 |
| Proportional scaling made no visual difference | Widen canvas AND stretch content to fill it | 23 |
| Content floats centered with side whitespace | Content must fill canvas width — no centered narrow blocks in wide canvas | 23, 24 |
| Bottom lines of multi-line text cropped | Height calculated for wrong line count — use `text.count('\n') + 1` | 25 |
| `autoResize` overrides calculated text height | Set `"autoResize": false` for free-floating text with manually calculated height | 25 |
