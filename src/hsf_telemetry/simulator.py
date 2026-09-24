import json
import random
import socket
import time
from datetime import datetime, timezone
from typing import Iterable


class TelemetryDevice:
    """Firmware emulator: creates deterministic, newline-delimited JSON frames."""

    def __init__(self, device_id: str = "SIM-001", seed: int = 7) -> None:
        self.device_id = device_id
        self.random = random.Random(seed)

    def frame(self, sequence: int, anomaly: bool = False) -> bytes:
        temperature = 24.0 + self.random.uniform(-2.0, 2.0)
        vibration = 0.4 + self.random.uniform(0.0, 0.4)
        voltage = 5.0 + self.random.uniform(-0.1, 0.1)
        if anomaly:
            temperature = 95.0
        payload = {
            "device_id": self.device_id,
            "sequence": sequence,
            "sent_at": datetime.now(timezone.utc).isoformat(),
            "temperature_c": round(temperature, 3),
            "vibration_g": round(vibration, 3),
            "voltage_v": round(voltage, 3),
        }
        return (json.dumps(payload) + "\n").encode("utf-8")

    def frames(self, count: int) -> Iterable[bytes]:
        for sequence in range(count):
            yield self.frame(sequence, anomaly=sequence == count // 2)


def serve(host: str, port: int, count: int, interval: float, corrupt: bool = False) -> None:
    device = TelemetryDevice()
    with socket.create_connection((host, port), timeout=5) as connection:
        for index, frame in enumerate(device.frames(count)):
            if corrupt and index == 1:
                frame = b"{not-valid-json}\n"
            connection.sendall(frame)
            time.sleep(interval)
