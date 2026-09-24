from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any


@dataclass(frozen=True)
class Telemetry:
    device_id: str
    sequence: int
    sent_at: str
    temperature_c: float
    vibration_g: float
    voltage_v: float

    @classmethod
    def from_payload(cls, payload: dict[str, Any]) -> "Telemetry":
        required = {"device_id", "sequence", "sent_at", "temperature_c", "vibration_g", "voltage_v"}
        missing = required.difference(payload)
        if missing:
            raise ValueError(f"missing fields: {sorted(missing)}")
        device_id = payload["device_id"]
        if not isinstance(device_id, str) or not device_id.strip():
            raise ValueError("device_id must be a non-empty string")
        sequence = payload["sequence"]
        if not isinstance(sequence, int) or isinstance(sequence, bool) or sequence < 0:
            raise ValueError("sequence must be a non-negative integer")
        sent_at = payload["sent_at"]
        if not isinstance(sent_at, str):
            raise ValueError("sent_at must be an ISO string")
        datetime.fromisoformat(sent_at.replace("Z", "+00:00"))
        values = [payload["temperature_c"], payload["vibration_g"], payload["voltage_v"]]
        if not all(isinstance(value, (int, float)) and not isinstance(value, bool) for value in values):
            raise ValueError("measurements must be numeric")
        telemetry = cls(device_id, sequence, sent_at, float(values[0]), float(values[1]), float(values[2]))
        telemetry.validate_ranges()
        return telemetry

    def validate_ranges(self) -> None:
        ranges = {
            "temperature_c": (-40.0, 125.0, self.temperature_c),
            "vibration_g": (0.0, 10.0, self.vibration_g),
            "voltage_v": (0.0, 24.0, self.voltage_v),
        }
        for name, (lower, upper, value) in ranges.items():
            if not lower <= value <= upper:
                raise ValueError(f"{name} out of range: {value}")

    def as_record(self, received_at: str, status: str, processing_ms: float) -> dict[str, Any]:
        return {
            "device_id": self.device_id,
            "sequence": self.sequence,
            "sent_at": self.sent_at,
            "received_at": received_at,
            "temperature_c": self.temperature_c,
            "vibration_g": self.vibration_g,
            "voltage_v": self.voltage_v,
            "status": status,
            "processing_ms": round(processing_ms, 3),
        }


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()
