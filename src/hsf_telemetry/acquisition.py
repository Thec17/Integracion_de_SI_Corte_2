import json
import logging
import socket
import time
from pathlib import Path
from typing import Any

from .models import Telemetry, utc_now
from .persistence import configure_logging, write_outputs
from .processing import classify, summarize
from .system_info import collect_system_info


class TelemetryReceiver:
    def __init__(self, host: str = "127.0.0.1", port: int = 0, output_dir: Path = Path("output")) -> None:
        self.host = host
        self.port = port
        self.output_dir = output_dir
        self.records: list[dict[str, Any]] = []
        self.errors: list[str] = []
        self.system_info = collect_system_info()
        self.bound_port: int | None = None
        self._server: socket.socket | None = None

    def listen(self) -> socket.socket:
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((self.host, self.port))
        server.listen(1)
        server.settimeout(8)
        self.bound_port = server.getsockname()[1]
        self._server = server
        return server

    def receive(self, expected_messages: int | None = None, timeout: float = 3.0) -> dict[str, Any]:
        configure_logging(self.output_dir)
        server = self._server or self.listen()
        logging.info("integration_started port=%s", self.bound_port)
        try:
            connection, address = server.accept()
            connection.settimeout(timeout)
            logging.info("device_connected address=%s", address)
            with connection:
                buffer = b""
                while expected_messages is None or len(self.records) + len(self.errors) < expected_messages:
                    try:
                        chunk = connection.recv(4096)
                    except socket.timeout:
                        self.errors.append("communication_timeout")
                        logging.error("communication_timeout")
                        break
                    if not chunk:
                        logging.warning("communication_lost")
                        break
                    buffer += chunk
                    while b"\n" in buffer:
                        raw, buffer = buffer.split(b"\n", 1)
                        self._handle_frame(raw)
                        if expected_messages is not None and len(self.records) + len(self.errors) >= expected_messages:
                            break
        except socket.timeout:
            self.errors.append("device_unavailable")
            logging.error("device_unavailable")
        finally:
            server.close()
            self._server = None
            summary = summarize(self.records, self.system_info, self.errors)
            try:
                write_outputs(self.output_dir, self.records, summary)
            except OSError as error:
                self.errors.append(f"persistence_error:{error.__class__.__name__}")
                logging.exception("persistence_error")
                summary = summarize(self.records, self.system_info, self.errors)
            logging.info("integration_finished valid=%s errors=%s", len(self.records), len(self.errors))
            return summary

    def _handle_frame(self, raw: bytes) -> None:
        started = time.perf_counter()
        try:
            payload = json.loads(raw.decode("utf-8"))
            if not isinstance(payload, dict):
                raise ValueError("payload must be an object")
            telemetry = Telemetry.from_payload(payload)
            status = classify(telemetry.temperature_c, telemetry.vibration_g, telemetry.voltage_v)
            elapsed_ms = (time.perf_counter() - started) * 1000
            self.records.append(telemetry.as_record(utc_now(), status, elapsed_ms))
            logging.info("telemetry_accepted device=%s sequence=%s status=%s", telemetry.device_id, telemetry.sequence, status)
        except (UnicodeDecodeError, json.JSONDecodeError) as error:
            self.errors.append("invalid_json")
            logging.error("invalid_payload error=%s", error)
        except (TypeError, ValueError) as error:
            self.errors.append("invalid_telemetry")
            logging.error("invalid_telemetry error=%s", error)
