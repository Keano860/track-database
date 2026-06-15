"""Migrate circuit reference values from Runsheet.xlsm into metadata.json."""

from __future__ import annotations

import argparse
import json
import re
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

MAIN_NS = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"


def normalize(value: str) -> str:
    return re.sub(r"[^a-z0-9]", "", value.lower())


def workbook_rows(workbook: Path) -> dict[str, dict[str, object]]:
    with zipfile.ZipFile(workbook) as archive:
        shared_strings: list[str] = []
        if "xl/sharedStrings.xml" in archive.namelist():
            root = ET.fromstring(archive.read("xl/sharedStrings.xml"))
            for item in root:
                shared_strings.append(
                    "".join(node.text or "" for node in item.iter(f"{{{MAIN_NS}}}t"))
                )

        root = ET.fromstring(archive.read("xl/worksheets/sheet14.xml"))
        result: dict[str, dict[str, object]] = {}
        for row in root.iter(f"{{{MAIN_NS}}}row"):
            values: dict[str, str] = {}
            for cell in row.findall(f"{{{MAIN_NS}}}c"):
                column = re.match(r"[A-Z]+", cell.attrib["r"])
                value = cell.find(f"{{{MAIN_NS}}}v")
                if column is None or value is None:
                    continue
                text = value.text or ""
                if cell.attrib.get("t") == "s" and text.isdigit():
                    text = shared_strings[int(text)]
                values[column.group()] = text

            name = values.get("B", "").strip()
            if not name:
                continue
            sectors = [
                number(values.get(column))
                for column in ("F", "G", "H", "I")
                if positive(number(values.get(column)))
            ]
            result[normalize(name)] = {
                "source": "Runsheet.xlsm/database",
                "circuitName": name,
                "circuitLengthKm": positive(number(values.get("C"))),
                "fuelConsumptionKgPerLap": positive(number(values.get("D"))),
                "timingOffsetSeconds": number(values.get("E")),
                "referenceSectorsSeconds": sectors,
                "referenceLapTimeSeconds": positive(number(values.get("J"))),
                "performanceReference": positive(number(values.get("P"))),
                "sectorCount": integer(values.get("Q")),
                "circuitCode": values.get("Y", "").strip() or None,
            }
        return result


def number(value: str | None) -> float | None:
    if value is None or value.strip() == "":
        return None
    try:
        return float(value)
    except ValueError:
        return None


def integer(value: str | None) -> int | None:
    parsed = number(value)
    return None if parsed is None else round(parsed)


def positive(value: float | None) -> float | None:
    return value if value is not None and value > 0 else None


def clean(value: object) -> object:
    if isinstance(value, dict):
        return {
            key: clean(item)
            for key, item in value.items()
            if item is not None and item != []
        }
    return value


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--workbook",
        type=Path,
        default=Path(r"C:\Rodin\Toolbox\Runsheet.xlsm"),
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).resolve().parents[1],
    )
    args = parser.parse_args()

    references = workbook_rows(args.workbook)
    updated: list[str] = []
    unmatched: list[str] = []
    for metadata_path in sorted((args.root / "tracks").glob("*/metadata.json")):
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        candidates = {
            normalize(str(metadata.get("track_name", ""))),
            normalize(str(metadata.get("slug", ""))),
            normalize(metadata_path.parent.name),
        }
        reference = next(
            (references[candidate] for candidate in candidates if candidate in references),
            None,
        )
        if reference is None:
            unmatched.append(metadata_path.parent.name)
            continue
        metadata["runsheet_reference"] = clean(reference)
        metadata_path.write_text(
            json.dumps(metadata, indent=2, ensure_ascii=True) + "\n",
            encoding="utf-8",
        )
        updated.append(metadata_path.parent.name)

    print(f"Updated {len(updated)} track metadata files.")
    print("Updated:", ", ".join(updated))
    print(f"No workbook match for {len(unmatched)} tracks.")


if __name__ == "__main__":
    main()
