import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from uart_emulator.infrastructure.All_APIs_for_custom_tests import (
    build_frame,
    close_hosts,
    Create_duplex_hosts,
    decode_frame,
    get_ack_nack_from_frame,
)


def run_retransmission_test():
    """Simulate NACK feedback followed by a successful retransmission."""
    host_a, host_b, clock, _ = Create_duplex_hosts(
        is_ideal=True,
        bit_flip_rate=0.0,
        baud_rate=9600,
    )

    try:
        message = "R"
        frame_bytes = build_frame(message)
        frame_value = int.from_bytes(frame_bytes, byteorder="big")

        first_attempt = get_ack_nack_from_frame(
            ack_nck=1,
            data_size=1,
            status="PE",
        )
        assert first_attempt is not None
        assert decode_frame(
            first_attempt.serialise(),
            data_type=0,
            data_size=1,
        ) == 2

        host_a.start_send(
            frame=frame_value,
            start_tick=100,
            line=host_a.host_transmit_lane,
        )
        received_frame = None
        while received_frame is None and clock.curr_tick() <= 2000:
            host_a.step()
            received_frame = host_b.step()
            clock.tick()

        assert received_frame is not None
        decoded = decode_frame(
            received_frame.to_bytes(2, byteorder="big"),
            data_type=1,
            data_size=1,
        )
        ack = get_ack_nack_from_frame(
            ack_nck=0,
            data_size=1,
            status="ACK",
        )

        return {
            "message": message,
            "nack": first_attempt,
            "retransmitted_data": decoded,
            "ack": ack,
            "success": decoded == message and ack is not None,
        }
    finally:
        close_hosts(host_a, host_b)


if __name__ == "__main__":
    result = run_retransmission_test()
    print(result)
    if not result["success"]:
        raise SystemExit(1)