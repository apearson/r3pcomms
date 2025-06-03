import sys
import argparse
import time

from collections.abc import Sequence

import r3pcomms

from r3pcomms import R3PComms


def run(port: str, actions: Sequence[dict]):
    inter_comms_delay_s = 1

    with R3PComms(port) as d:
        for i, action in enumerate(actions):
            if i != 0:
                time.sleep(inter_comms_delay_s)
            result = getattr(d, action["fun"])(*action["args"], **action["kwargs"])

            if action["fun"] in ("get_serial", "get_metrics"):
                print(result)


def main_parser() -> argparse.ArgumentParser:
    """
    Construct the main parser.
    """

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
        "--serial",
        "-s",
        action="store_true",
        help="get unit serial number",
    )
    parser.add_argument(
        "--metrics",
        "-m",
        action="store_true",
        help="get all metrics",
    )

    return parser


def main(cli_args: Sequence[str], prog: str | None = None) -> None:
    """
    Parse the CLI arguments then do comms actions.

    :param cli_args: CLI arguments
    :param prog: Program name to show in help text
    """

    parser = main_parser()
    if prog:
        parser.prog = prog
    args = parser.parse_args(cli_args)

    run_actions = []
    if args.serial:
        run_actions.append(({"fun": "get_serial", "args": (), "kwargs": {}}))
    if args.metrics:
        run_actions.append(({"fun": "get_metrics", "args": (), "kwargs": {}}))
        run_actions.append(({"fun": "get_metrics", "args": (), "kwargs": {}}))
        run_actions.append(({"fun": "get_metrics", "args": (), "kwargs": {}}))
        run_actions.append(({"fun": "get_metrics", "args": (), "kwargs": {}}))
        run_actions.append(({"fun": "get_metrics", "args": (), "kwargs": {}}))
        run_actions.append(({"fun": "get_metrics", "args": (), "kwargs": {}}))
        run_actions.append(({"fun": "get_metrics", "args": (), "kwargs": {}}))
        run_actions.append(({"fun": "get_metrics", "args": (), "kwargs": {}}))
        run_actions.append(({"fun": "get_metrics", "args": (), "kwargs": {}}))
        run_actions.append(({"fun": "get_metrics", "args": (), "kwargs": {}}))
        run_actions.append(({"fun": "get_metrics", "args": (), "kwargs": {}}))
        run_actions.append(({"fun": "get_metrics", "args": (), "kwargs": {}}))
        run_actions.append(({"fun": "get_metrics", "args": (), "kwargs": {}}))
        run_actions.append(({"fun": "get_metrics", "args": (), "kwargs": {}}))
        run_actions.append(({"fun": "get_metrics", "args": (), "kwargs": {}}))
        run_actions.append(({"fun": "get_metrics", "args": (), "kwargs": {}}))
        run_actions.append(({"fun": "get_metrics", "args": (), "kwargs": {}}))
        run_actions.append(({"fun": "get_metrics", "args": (), "kwargs": {}}))
        run_actions.append(({"fun": "get_metrics", "args": (), "kwargs": {}}))
        run_actions.append(({"fun": "get_metrics", "args": (), "kwargs": {}}))
        run_actions.append(({"fun": "get_metrics", "args": (), "kwargs": {}}))
        run_actions.append(({"fun": "get_metrics", "args": (), "kwargs": {}}))
        run_actions.append(({"fun": "get_metrics", "args": (), "kwargs": {}}))
        run_actions.append(({"fun": "get_metrics", "args": (), "kwargs": {}}))

    run(args.port, run_actions)


def entrypoint() -> None:
    main(sys.argv[1:])


if __name__ == "__main__":
    main(sys.argv[1:], "python -m r3pcomms")


__all__ = [
    "main",
    "main_parser",
]
