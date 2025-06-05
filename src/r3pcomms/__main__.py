import sys
import argparse
import time

from collections.abc import Sequence

import r3pcomms

from r3pcomms import R3PComms


def run(port: str, actions: list[dict], debug: bool, hide_sn: bool):
    inter_comms_delay_s = 1

    with R3PComms(port) as d:
        d.debug_prints = debug
        d.redact_sn = hide_sn
        for i, action in enumerate(actions):
            if i != 0:
                time.sleep(inter_comms_delay_s)
            result = getattr(d, action["fun"])(*action["args"], **action["kwargs"])

            if action["fun"] in ("get_serial", "get_metrics"):
                print(result)


def main_parser() -> argparse.ArgumentParser:
    description = "Local communication with River 3 Plus"
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument(
        "--version",
        "-V",
        action="version",
        version=f'r3pcomms {r3pcomms.__version__} ({",".join(r3pcomms.__path__)})',
    )
    parser.add_argument(
        "--port",
        "-p",
        required=True,
        help='comms port to use, like "COM3" or "/dev/ttyACM0" or '
        '"/dev/serial/by-id/usb-EcoFlow_EF-UPS-RIVER_3_Plus_${SERIALNUMBER}-if01"',
    )
    parser.add_argument(
        "--debug",
        "-d",
        action="store_true",
        help="print raw comms messages",
    )
    parser.add_argument(
        "--serial",
        "-s",
        action="store_true",
        help="get unit serial number",
    )
    parser.add_argument(
        "--redact-serial",
        "-r",
        action="store_true",
        help="redact serial number from all prints",
    )
    parser.add_argument(
        "--metrics",
        "-m",
        default="0",
        type=int,
        help="number of times to get all metrics",
    )

    return parser


def main(cli_args: Sequence[str], prog: str | None = None) -> None:
    parser = main_parser()
    if prog:
        parser.prog = prog
    args = parser.parse_args(cli_args)

    run_actions = []
    if args.serial:
        run_actions.append(({"fun": "get_serial", "args": (), "kwargs": {}}))
    for i in range(args.metrics):
        run_actions.append(({"fun": "get_metrics", "args": (), "kwargs": {}}))

    run_args = {
        "port": args.port,
        "actions": run_actions,
        "debug": args.debug,
        "hide_sn": args.redact_serial,
    }
    run(**run_args)


def entrypoint() -> None:
    main(sys.argv[1:])


if __name__ == "__main__":
    main(sys.argv[1:], "python -m r3pcomms")


__all__ = [
    "main",
    "main_parser",
]
