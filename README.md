# excalidraw-diagrams-skill

A [Claude Code](https://claude.ai/claude-code) skill for programmatically generating hand-drawn Excalidraw diagrams and embedding them in static sites.

## What it does

Teaches Claude how to:

- Generate `.excalidraw` JSON files with correctly positioned elements
- Export to SVG via headless browser (pixel-perfect Excalidraw rendering)
- Embed diagrams with automatic light/dark theme switching
- Avoid common layout pitfalls (text overflow, arrow alignment, overlapping elements)

## Install

Copy the skill into your Claude Code skills directory:

```bash
# Global (all projects)
mkdir -p ~/.claude/skills/excalidraw-diagrams
cp SKILL.md ~/.claude/skills/excalidraw-diagrams/

# Or project-specific
mkdir -p .claude/skills/excalidraw-diagrams
cp SKILL.md .claude/skills/excalidraw-diagrams/
```

## Prerequisites

The skill instructs Claude to use these tools (installed automatically when needed):

```bash
npm install -g excalidraw-brute-export-cli
npx playwright install
```

## What's in the skill

- **Full pipeline**: Generate JSON -> Export SVG -> Embed with theme switching
- **7 layout rules** that prevent the most common iteration cycles:
  1. Aspect ratio controls perceived size (not internal scale)
  2. Calculate all positions from constants (never eyeball)
  3. Text centering requires manual height calculation
  4. Boxes must have padding for text
  5. Arrows must end at box borders
  6. Arrow's final segment must be perpendicular to target face
  7. Encapsulating containers need internal padding
- **Excalidraw JSON reference**: Element types, properties, color palette
- **Common mistakes table**: Problem -> Fix mappings
- **Python generator template**: Ready-to-use functions with centering logic baked in

## Example

Ask Claude:

> "Create an Excalidraw diagram showing the data flow from API to database to dashboard"

With this skill installed, Claude will generate a properly laid out `.excalidraw` file, export both light and dark SVGs, and embed them — without the usual back-and-forth iterations on text alignment, arrow directions, and sizing.

## How it was made

This skill was distilled from a real conversation where every layout rule was discovered through iteration. The goal: capture all those lessons so future diagrams work on the first try.

## License

MIT
