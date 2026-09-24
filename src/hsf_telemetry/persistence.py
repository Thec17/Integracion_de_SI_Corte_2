import csv
import json
import logging
from pathlib import Path
from typing import Any

FIELDS = ["device_id", "sequence", "sent_at", "received_at", "temperature_c", "vibration_g", "voltage_v", "status", "processing_ms"]


def configure_logging(output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        filename=output_dir / "hsf.log",
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        force=True,
    )


def write_outputs(output_dir: Path, records: list[dict[str, Any]], summary: dict[str, Any]) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    with (output_dir / "telemetry.csv").open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(records)
    (output_dir / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=True), encoding="utf-8")
