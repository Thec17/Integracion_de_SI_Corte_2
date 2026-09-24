import json
import socket
import threading
from pathlib import Path

from hsf_telemetry.acquisition import TelemetryReceiver
from hsf_telemetry.simulator import TelemetryDevice


def test_valid_and_anomalous_frames_are_persisted(tmp_path: Path) -> None:
    receiver = TelemetryReceiver(output_dir=tmp_path)
    server = receiver.listen()
    sender = socket.create_connection(("127.0.0.1", receiver.bound_port))
    device = TelemetryDevice(seed=1)
    for sequence in range(3):
        sender.sendall(device.frame(sequence, anomaly=sequence == 2))
    sender.close()
    summary = receiver.receive(expected_messages=3)
    assert summary["valid_messages"] == 3
    assert summary["anomalous_messages"] == 1
    assert (tmp_path / "telemetry.csv").exists()
    assert (tmp_path / "summary.json").exists()


def test_corrupt_and_out_of_range_frames_do_not_stop_receiver(tmp_path: Path) -> None:
    receiver = TelemetryReceiver(output_dir=tmp_path)
    receiver.listen()

    def send_frames() -> None:
        with socket.create_connection(("127.0.0.1", receiver.bound_port)) as sender:
            sender.sendall(b"{bad-json}\n")
            sender.sendall(json.dumps({"device_id": "SIM-001", "sequence": 1, "sent_at": "2026-01-01T00:00:00+00:00", "temperature_c": 999, "vibration_g": 0.2, "voltage_v": 5}).encode() + b"\n")
            sender.sendall(TelemetryDevice().frame(2))

    thread = threading.Thread(target=send_frames)
    thread.start()
    summary = receiver.receive(expected_messages=3)
    thread.join()
    assert summary["valid_messages"] == 1
    assert summary["errors"] == 2


def test_unavailable_device_is_reported(tmp_path: Path) -> None:
    receiver = TelemetryReceiver(port=0, output_dir=tmp_path)
    summary = receiver.receive(expected_messages=1, timeout=0.05)
    assert "device_unavailable" in receiver.errors
    assert summary["errors"] == 1
