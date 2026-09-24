import argparse
import json
import threading
from pathlib import Path

from .acquisition import TelemetryReceiver
from .simulator import serve


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="HSF telemetry integration prototype")
    subparsers = parser.add_subparsers(dest="command", required=True)
    for command in ("demo", "app", "simulator"):
        subparser = subparsers.add_parser(command)
        subparser.add_argument("--host", default="127.0.0.1")
        subparser.add_argument("--port", type=int, default=9100)
        subparser.add_argument("--messages", type=int, default=12)
        subparser.add_argument("--interval", type=float, default=0.15)
        subparser.add_argument("--output", type=Path, default=Path("output"))
        subparser.add_argument("--corrupt", action="store_true")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    if args.command == "simulator":
        serve(args.host, args.port, args.messages, args.interval, args.corrupt)
        return
    receiver = TelemetryReceiver(args.host, args.port if args.command == "app" else 0, args.output)
    if args.command == "demo":
        receiver.listen()
        sender = threading.Thread(target=serve, args=(args.host, receiver.bound_port, args.messages, args.interval, args.corrupt))
        sender.start()
        summary = receiver.receive(expected_messages=args.messages)
        sender.join(timeout=5)
    else:
        summary = receiver.receive(expected_messages=args.messages)
    print(json.dumps(summary, indent=2, ensure_ascii=True))


if __name__ == "__main__":
    main()
