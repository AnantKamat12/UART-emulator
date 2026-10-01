"""Interactive entry point for the UART emulator and modular test suite."""

import argparse
import subprocess
import sys
from pathlib import Path

from uart_emulator.infrastructure.All_APIs_for_custom_tests import (
    Create_duplex_hosts,
    close_hosts,
    get_segmented_data,
)
from uart_emulator.infrastructure.CLI_logger import CLI_logger
from uart_emulator.protocol.Frames import Frame

PROJECT_ROOT = Path(__file__).resolve().parent
MODULAR_TEST_RUNNER = PROJECT_ROOT / "tests" / "modulartest" / "runallunittest.py"


def prompt_value(label, default=None):
    """Read a value interactively, using default when the input is empty."""
    suffix = f" [{default}]" if default is not None else ""
    value = input(f"{label}{suffix}: ").strip()
    return default if value == "" and default is not None else value


def prompt_until_valid(label, parser, default=None):
    """Repeat one prompt until its parser accepts the value."""
    while True:
        value = prompt_value(label, default)
        try:
            return parser(value)
        except (TypeError, ValueError) as error:
            print(f"Invalid input: {error}")
            default = None


def validate_host(value):
    host = value.upper()
    if host not in {"A", "B"}:
        raise ValueError("enter A or B (for example, B)")
    return host


def validate_data_type(value):
    data_type = value.lower()
    if data_type not in {"string", "integer", "bytes"}:
        raise ValueError("enter string, integer, or bytes")
    return data_type


def validate_data_size(value):
    try:
        data_size = int(value)
    except (TypeError, ValueError) as error:
        raise ValueError("enter a frame width of 1, 2, or 3 bytes") from error
    if data_size not in {1, 2, 3}:
        raise ValueError("frame width must be 1, 2, or 3 bytes")
    return data_size


def validate_baud_rate(value):
    try:
        baud_rate = int(value)
    except (TypeError, ValueError) as error:
        raise ValueError("enter a positive baud rate, e.g. 9600") from error
    if baud_rate <= 0:
        raise ValueError("baud rate must be greater than zero")
    return baud_rate


def parse_data(data_type, value, data_size=1):
    """Convert CLI text into the selected application data type."""
    if data_type == "integer":
        try:
            data = int(value, 10)
        except (TypeError, ValueError) as error:
            raise ValueError("enter an integer in decimal (for example, 97)") from error
        max_value = (1 << (data_size * 8)) - 1
        if not 0 <= data <= max_value:
            raise ValueError(
                f"integer data must fit in {data_size} byte(s) "
                f"(0 through {max_value})"
            )
        return data

    if data_type == "bytes":
        try:
            data = bytes.fromhex(value)
        except (TypeError, ValueError) as error:
            raise ValueError(
                "enter hexadecimal byte pairs, such as 61 or 41 42 (no 0x prefix)"
            ) from error
        if not data:
            raise ValueError("enter at least one hex byte, such as 41")
        return data

    if not value:
        raise ValueError("enter non-empty text, such as hello")
    try:
        value.encode("ascii")
    except UnicodeEncodeError as error:
        raise ValueError("string data must contain ASCII characters") from error
    return value


def get_configuration(args, prompt_baud_rate=False):
    """Collect CLI options from arguments or interactive prompts."""
    host = (
        validate_host(args.host)
        if args.host
        else prompt_until_valid("Transmitting host (A/B)", validate_host, "A")
    )
    data_type = (
        validate_data_type(args.data_type)
        if args.data_type
        else prompt_until_valid(
            "Data type (string/integer/bytes)",
            validate_data_type,
            "string",
        )
    )
    data_size = (
        validate_data_size(args.data_size)
        if args.data_size is not None
        else prompt_until_valid(
            "Frame data size in bytes (1/2/3)",
            validate_data_size,
            "1",
        )
    )
    baud_rate = (
        validate_baud_rate(args.baud_rate)
        if args.baud_rate is not None
        else (
            prompt_until_valid(
                "Baud rate in bits per second",
                validate_baud_rate,
                "9600",
            )
            if prompt_baud_rate
            else 9600
        )
    )

    examples = {
        "string": "plain text; enter hello to send the word hello",
        "integer": (
            f"decimal integer 0-{(1 << (data_size * 8)) - 1}; "
            "for example, enter 97"
        ),
        "bytes": (
            "hexadecimal: 41 42 sends ASCII AB; AB alone is one byte 0xAB "
            "(no 0x prefix)"
        ),
    }
    data_parser = lambda value: parse_data(data_type, value, data_size)
    data = (
        data_parser(args.data)
        if args.data is not None
        else prompt_until_valid(f"Data ({examples[data_type]})", data_parser)
    )
    return host, data_type, data_size, baud_rate, data


def run_once(host_name, data_type, data_size, data, baud_rate=9600):
    """Transmit one message and return its simulation result."""
    type_id = {"integer": 0, "string": 1, "bytes": 2}[data_type]
    CLI_logger.mark_simulation_log()
    host_a, host_b, clock, _ = Create_duplex_hosts(
        baud_rate=baud_rate,
        data_type=type_id,
        is_ideal=True,
        logger_class=CLI_logger,
        data_size=data_size,
    )
    sender = host_a if host_name == "A" else host_b
    receiver = host_b if host_name == "A" else host_a

    try:
        if data_type == "integer":
            segments = [data]
        elif data_type == "bytes":
            segments = [
                data[offset:offset + data_size].ljust(data_size, b"\x00")
                for offset in range(0, len(data), data_size)
            ]
        else:
            segments = get_segmented_data(data, max_segment_size=data_size * 8)
        received = []
        frame_start = sender.tx.ticks_per_bit
        frame_ticks = sender.tx.frame_bits * sender.tx.ticks_per_bit

        next_segment = 0
        end_tick = frame_start + len(segments) * frame_ticks
        while clock.curr_tick() < end_tick:
            current_tick = clock.curr_tick()
            if (
                next_segment < len(segments)
                and not sender.tx.active
                and current_tick >= frame_start + next_segment * frame_ticks
            ):
                frame = Frame(data=segments[next_segment], data_size=data_size)
                sender.start_send(
                    frame=int.from_bytes(frame.serialise(), byteorder="big"),
                    start_tick=current_tick,
                    line=sender.host_transmit_lane,
                )
                next_segment += 1

            sender.step()
            received_frame = receiver.step()
            if received_frame is not None:
                received.append(received_frame)
            clock.tick()

        received_data = receiver.get_joined_rcvd_data()
        if data_type == "bytes":
            received_data = received_data[:len(data)]

        return {
            "sent_data": data,
            "received_frames": received,
            "received_data": received_data,
            "success": len(received) == len(segments),
            "end_tick": clock.curr_tick(),
        }
    finally:
        close_hosts(host_a, host_b)


def build_parser():
    """Build the existing direct-CLI argument parser."""
    parser = argparse.ArgumentParser(description="Interactive UART emulator")
    parser.add_argument("--host", choices=["A", "B"])
    parser.add_argument("--data")
    parser.add_argument("--data-type", choices=["string", "integer", "bytes"])
    parser.add_argument("--data-size", type=int, choices=[1, 2, 3])
    parser.add_argument("--baud-rate", type=int)
    return parser


def run_modular_tests():
    """Run all unittest-discoverable tests under tests/modulartest."""
    completed = subprocess.run(
        [sys.executable, str(MODULAR_TEST_RUNNER)],
        cwd=PROJECT_ROOT,
        check=False,
    )
    return completed.returncode


def run_uart_cli(args, prompt_baud_rate=False):
    """Run the existing UART CLI flow (menu option 1)."""
    try:
        host, data_type, data_size, baud_rate, data = get_configuration(
            args,
            prompt_baud_rate=prompt_baud_rate,
        )
        result = run_once(host, data_type, data_size, data, baud_rate)
    except (TypeError, ValueError) as error:
        print(f"Input error: {error}")
        return 2

    print(f"Transmitting host : HOST_{host}")
    print(f"Data type         : {data_type}")
    print(f"Data size         : {data_size} byte(s)")
    print(f"Baud rate         : {baud_rate} bps")
    print(f"Transmitted data  : {result['sent_data']!r}")
    print(f"Received frames   : {len(result['received_frames'])}")
    print(f"Received data     : {result['received_data']!r}")
    print(f"Simulation ticks  : {result['end_tick']}")
    print(f"Status            : {'SUCCESS' if result['success'] else 'FAILURE'}")
    return 0 if result["success"] else 1


def main():
    args = build_parser().parse_args()

    # Keep existing command-line invocations working without showing the menu.
    if len(sys.argv) > 1:
        return run_uart_cli(args)

    print("UART Emulator")
    print("0. Run all modular unit tests")
    print("1. Run the UART CLI test")
    choice = input("Choose an option (0/1): ").strip()

    if choice == "0":
        return run_modular_tests()
    if choice == "1":
        return run_uart_cli(args, prompt_baud_rate=True)

    print("Invalid option. Choose 0 or 1.")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
