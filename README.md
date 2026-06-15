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

## Runsheet reference schema

When a circuit exists in the legacy Runsheet workbook, `metadata.json` also
contains a `runsheet_reference` object:

```json
{
  "source": "Runsheet.xlsm/database",
  "circuitName": "Silverstone Old GP",
  "circuitLengthKm": 5.8,
  "fuelConsumptionKgPerLap": 1.16,
  "timingOffsetSeconds": 120,
  "referenceSectorsSeconds": [36.976, 62.232, 22.15],
  "referenceLapTimeSeconds": 47.4,
  "performanceReference": 0.0035,
  "sectorCount": 3,
  "circuitCode": "SilverstoneOldGP"
}
```

Run `tools/migrate_runsheet_database.py` to repeat the migration from the
legacy workbook without overwriting maps, POIs, names, or notes.

## Next steps

1. Review each `metadata.json` and replace placeholder names where needed
2. Populate each `poi.csv`
3. Add optional overlay config files later if needed
