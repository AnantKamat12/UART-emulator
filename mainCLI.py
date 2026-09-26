"""Interactive command-line interface for one UART transmission."""

import argparse

from uart_emulator.infrastructure.All_APIs_for_custom_tests import (
    Create_duplex_hosts,
    close_hosts,
    get_segmented_data,
)
from uart_emulator.protocol.Frames import Frame


def prompt_value(label, default=None):
    """Read a value interactively, using default when the input is empty."""
    suffix = f" [{default}]" if default is not None else ""
    value = input(f"{label}{suffix}: ").strip()
    return default if value == "" and default is not None else value


def parse_data(data_type, value):
    """Convert CLI text into the selected application data type."""
    if data_type == "integer":
        return int(value)
    if data_type == "bytes":
        return bytes.fromhex(value)
    return value


def get_configuration(args):
    """Collect CLI options from arguments or interactive prompts."""
    host = args.host or prompt_value("Transmitting host (A/B)", "A").upper()
    data_type = args.data_type or prompt_value(
        "Data type (string/integer/bytes)",
        "string",
    ).lower()
    data_size = args.data_size or int(
        prompt_value("Data size in bytes (1/2/3)", "1")
    )
    data = args.data
    if data is None:
        data = prompt_value("Data to transmit")

    if host not in {"A", "B"}:
        raise ValueError("host must be A or B")
    if data_type not in {"string", "integer", "bytes"}:
        raise ValueError("data type must be string, integer, or bytes")
    if data_size not in {1, 2, 3}:
        raise ValueError("data size must be 1, 2, or 3 bytes")

    return host, data_type, data_size, parse_data(data_type, data)


def run_once(host_name, data_type, data_size, data, baud_rate=9600):
    """Transmit one message and return its simulation result."""
    if data_size != 1:
        raise ValueError(
            "The current live TX/RX path supports 1-byte CLI frames; "
            "multi-byte frame support remains a protocol task."
        )

    type_id = {"integer": 0, "string": 1, "bytes": 2}[data_type]
    host_a, host_b, clock, _ = Create_duplex_hosts(
        baud_rate=baud_rate,
        data_type=type_id,
        is_ideal=True,
    )
    sender = host_a if host_name == "A" else host_b
    receiver = host_b if host_name == "A" else host_a

    try:
        if data_type == "integer":
            segments = [data]
        else:
            segments = get_segmented_data(data, max_segment_size=data_size * 8)
        received = []
        frame_start = 100
        frame_ticks = 16 * 100

        for segment_index, segment in enumerate(segments):
            frame = Frame(data=segment, data_size=data_size)
            sender.start_send(
                frame=int.from_bytes(frame.serialise(), byteorder="big"),
                start_tick=frame_start + segment_index * frame_ticks,
                line=sender.host_transmit_lane,
            )

        end_tick = frame_start + len(segments) * frame_ticks + frame_ticks
        while clock.curr_tick() < end_tick:
            sender.step()
            received_frame = receiver.step()
            if received_frame is not None:
                received.append(received_frame)
            clock.tick()

        return {
            "sent_data": data,
            "received_frames": received,
            "success": bool(received),
            "end_tick": clock.curr_tick(),
        }
    finally:
        close_hosts(host_a, host_b)


def build_parser():
    parser = argparse.ArgumentParser(description="Interactive UART emulator")
    parser.add_argument("--host", choices=["A", "B"])
    parser.add_argument("--data")
    parser.add_argument("--data-type", choices=["string", "integer", "bytes"])
    parser.add_argument("--data-size", type=int, choices=[1, 2, 3])
    parser.add_argument("--baud-rate", type=int, default=9600)
    return parser


def main():
    args = build_parser().parse_args()
    try:
        host, data_type, data_size, data = get_configuration(args)
        result = run_once(host, data_type, data_size, data, args.baud_rate)
    except (TypeError, ValueError) as error:
        print(f"Input error: {error}")
        return 2

    print(f"Transmitting host : HOST_{host}")
    print(f"Data type         : {data_type}")
    print(f"Data size         : {data_size} byte(s)")
    print(f"Transmitted data  : {result['sent_data']!r}")
    print(f"Received frames   : {len(result['received_frames'])}")
    print(f"Simulation ticks  : {result['end_tick']}")
    print(f"Status            : {'SUCCESS' if result['success'] else 'FAILURE'}")
    return 0 if result["success"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
