# Track Database

Structured track map database for report generation, overlays and POI-based analysis.

## Structure

```text
tracks/
  <track_slug>/
    map.<ext>
    metadata.json
    poi.csv
```

## Conventions

- Folder names use lowercase snake_case
- `map.<ext>` is the base track map image
- `metadata.json` stores track-level metadata
- `poi.csv` stores corner and section point-of-interest definitions

## Next steps

1. Review each `metadata.json` and replace placeholder names where needed
2. Populate each `poi.csv`
3. Add optional overlay config files later if needed
