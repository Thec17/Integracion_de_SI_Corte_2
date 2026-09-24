from typing import Any


def classify(temperature_c: float, vibration_g: float, voltage_v: float) -> str:
    if temperature_c > 80 or vibration_g > 5 or not 3.0 <= voltage_v <= 6.0:
        return "ANOMALO"
    return "NORMAL"


def summarize(records: list[dict[str, Any]], system_info: dict[str, Any], errors: list[str]) -> dict[str, Any]:
    accepted = [record for record in records if record["status"] in {"NORMAL", "ANOMALO"}]
    normal = sum(record["status"] == "NORMAL" for record in accepted)
    anomalous = sum(record["status"] == "ANOMALO" for record in accepted)
    return {
        "device_id": records[0]["device_id"] if records else None,
        "messages_received": len(records) + len(errors),
        "valid_messages": len(accepted),
        "normal_messages": normal,
        "anomalous_messages": anomalous,
        "errors": len(errors),
        "availability_percent": round((len(records) / max(len(records) + len(errors), 1)) * 100, 2),
        "validity_percent": round((len(accepted) / max(len(records) + len(errors), 1)) * 100, 2),
        "system": system_info,
    }
