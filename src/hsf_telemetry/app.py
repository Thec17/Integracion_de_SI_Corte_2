from pathlib import Path

from .acquisition import TelemetryReceiver


def run_capture(output_dir: Path, expected_messages: int, host: str = "127.0.0.1", port: int = 0) -> dict:
    receiver = TelemetryReceiver(host=host, port=port, output_dir=output_dir)
    return receiver.receive(expected_messages=expected_messages)
