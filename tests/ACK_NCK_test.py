"""End-to-end ACK/NACK and retransmission test for the UART emulator."""

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from uart_emulator.infrastructure.All_APIs_for_custom_tests import (
    Create_duplex_hosts,
    build_frame,
    close_hosts,
    get_segmented_data,
    get_last_reassembled_data,
    log_received_data,
)
from uart_emulator.infrastructure.Logger import logger
from uart_emulator.protocol.ACK import ACK
from uart_emulator.protocol.FSM import (
    Event,
    ReceiverFSM,
    ReceiverState,
    SenderFSM,
    SenderState,
)
from uart_emulator.protocol.Feedback import Feedback
from uart_emulator.protocol.Frames import Deserialise, Frame

SIMULATION_TIME = 10**7


class ACKNCKCommunication:
    """Send segmented data and retry until each segment is acknowledged."""

    def __init__(
        self,
        data_type=1,
        data_size=1,
        data="An-An-T",
        is_ideal=False,
        bit_flip_rate=0.03,
        simulation_time=SIMULATION_TIME,
    ):
        if data_size != 1:
            raise ValueError("The current UART receiver supports one-byte data frames.")

        self.data_type = data_type
        self.data_size = data_size
        self.data = data
        self.data_segments = get_segmented_data(
            data,
            max_segment_size=data_size * 8,
        )
        self.frames = [
            build_frame(segment, data_size=data_size)
            for segment in self.data_segments
        ]
        self.simulation_time = simulation_time
        (
            self.host_a,
            self.host_b,
            self.clk,
            self.vc,
        ) = Create_duplex_hosts(
            is_ideal=is_ideal,
            bit_flip_rate=bit_flip_rate,
            data_type=data_type,
        )
        self.sender_fsm = SenderFSM()
        self.receiver_fsm = ReceiverFSM()
        self.feedback = Feedback(self.host_a, self.host_b)
        self.attempts = [0 for _ in self.frames]
        self.accepted_segments = set()
        self.decoded_segments = []
        self.current_segment = 0
        self.data_tx_pending = False
        self.feedback_tx_pending = False
        self.retransmissions = 0

    @staticmethod
    def _next_bit_boundary(tick, ticks_per_bit):
        return ((tick + ticks_per_bit - 1) // ticks_per_bit) * ticks_per_bit

    def _log_event(self, host, message, tick):
        host.host_logger.write(message, tick)
        logger.logprint(message, tick)

    def _start_current_frame(self, tick):
        index = self.current_segment
        self.attempts[index] += 1
        frame_value = int.from_bytes(self.frames[index], byteorder="big")

        start_tick = self._next_bit_boundary(tick, self.host_a.tx.ticks_per_bit)
        self.host_a.start_send(
            frame=frame_value,
            start_tick=start_tick,
            line=self.host_a.host_transmit_lane,
        )
        self.data_tx_pending = True

    def _handle_data_frame(self, received_frame, tick):
        self.receiver_fsm.handle(Event.FRAME_RECEIVED)
        self.receiver_fsm.handle(Event.FRAME_COMPLETE)
        status, raw_data = Deserialise(data_size=self.data_size).decode_data(
            received_frame
        )

        # The frame parity check can miss an even number of flipped bits.
        # Reject non-ASCII payloads for string-mode transfers instead of
        # letting the reassembler raise while decoding them.
        if status == "OK" and self.data_type == 1:
            try:
                raw_data.to_bytes(self.data_size, byteorder="big").decode("ascii")
            except UnicodeDecodeError:
                status = "PE"

        if status == "OK":
            self.receiver_fsm.handle(Event.VALID_FRAME)
            self._log_event(
                self.host_b,
                f"[HOST_B] accepted segment {self.current_segment + 1} "
                f"on attempt {self.attempts[self.current_segment]}; sending ACK",
                tick,
            )
            if self.current_segment not in self.accepted_segments:
                frame_bytes = received_frame.to_bytes(
                    self.data_size + 1,
                    byteorder="big",
                )
                self.host_b.rck_reassembler.decode(
                    frame_bytes,
                    data_size=self.data_size,
                )
                last_decoded_data = get_last_reassembled_data(
                    self.host_b.rck_reassembler
                )
                self.accepted_segments.add(self.current_segment)
                self.decoded_segments.append(last_decoded_data)
                self._log_event(
                    self.host_b,
                    f"[HOST_B] last decoded frame for segment "
                    f"{self.current_segment + 1}: {last_decoded_data!r}",
                    tick,
                )
        else:
            self.receiver_fsm.handle(Event.INVALID_FRAME)
            self._log_event(
                self.host_b,
                f"[HOST_B] rejected received frame and sends NACK "
                f"for segment "
                f"{self.current_segment + 1} (attempt "
                f"{self.attempts[self.current_segment]}, status={status})",
                tick,
            )

        self.feedback.send_feedback(
            status=status,
            rxhost=self.host_b,
            curr_tick=tick,
            data_size=self.data_size,
        )
        self.feedback_tx_pending = True

    def _handle_feedback_frame(self, received_frame):
        status, feedback = Deserialise.decode_ack_nck_frame(received_frame)
        tick = self.clk.curr_tick()
        if status != "OK":
            self._log_event(
                self.host_a,
                f"[HOST_A] received corrupt ACK/NACK (status={status}); "
                f"retransmitting segment {self.current_segment + 1}",
                tick,
            )
            self.sender_fsm.handle(Event.FEEDBACK_CORRUPT)
            self.retransmissions += 1
            return

        if feedback == ACK.ACK.name:
            self._log_event(
                self.host_a,
                f"[HOST_A] received ACK for segment {self.current_segment + 1}",
                tick,
            )
            self.sender_fsm.handle(Event.ACK_RECEIVED)
            self.current_segment += 1
            if self.current_segment < len(self.frames):
                self.sender_fsm.handle(Event.NEXT_PACKET)
            else:
                self.sender_fsm.handle(Event.NO_MORE_DATA)
        elif feedback == ACK.NACK.name:
            self._log_event(
                self.host_a,
                f"[HOST_A] received NACK for segment "
                f"{self.current_segment + 1}; retransmitting",
                tick,
            )
            self.sender_fsm.handle(Event.NACK_RECEIVED)
            self.retransmissions += 1
        else:
            self._log_event(
                self.host_a,
                f"[HOST_A] received unknown feedback {feedback!r}; "
                f"retransmitting segment {self.current_segment + 1}",
                tick,
            )
            self.sender_fsm.handle(Event.NO_VALID_FEEDBACK)
            self.retransmissions += 1

    def start_communication(self):
        """Run both hosts until all frames are ACKed or simulation times out."""
        if not self.frames:
            result = self._result()
            log_received_data(
                self.host_a,
                self.host_a.get_rcvd_data(),
                self.host_a.get_joined_rcvd_data(),
                self.clk.curr_tick(),
            )
            log_received_data(
                self.host_b,
                result["decoded_segments"],
                result["received_data"],
                self.clk.curr_tick(),
            )
            return result

        self.sender_fsm.handle(Event.DATA_READY)
        try:
            while self.clk.curr_tick() < self.simulation_time:
                tick = self.clk.curr_tick()

                if (
                    not self.data_tx_pending
                    and not self.host_a.tx.active
                    and self.sender_fsm.get_state()
                    in (SenderState.SENDING, SenderState.RESEND)
                ):
                    self._start_current_frame(tick)

                self.host_a.tx.step(tick)
                self.host_b.tx.step(tick)
                received_by_a = self.host_a.rx.step(
                    tick,
                    self.host_a.host_receive_lane,
                )
                received_by_b = self.host_b.rx.step(
                    tick,
                    self.host_b.host_receive_lane,
                )

                if self.data_tx_pending and not self.host_a.tx.active:
                    self.data_tx_pending = False
                    self.sender_fsm.handle(Event.FRAME_SENT)

                if received_by_b is not None:
                    self._handle_data_frame(received_by_b, tick)

                if received_by_a is not None:
                    self._handle_feedback_frame(received_by_a)

                if self.feedback_tx_pending and not self.host_b.tx.active:
                    self.feedback_tx_pending = False
                    self.receiver_fsm.handle(Event.FEEDBACK_SENT)

                if self.sender_fsm.get_state() == SenderState.IDLE:
                    break

                self.clk.tick()

            return self._result()
        finally:
            close_hosts(self.host_a, self.host_b)

    def _result(self):
        received = self.host_b.get_joined_rcvd_data()
        expected = self.data
        if isinstance(expected, str) and isinstance(received, str):
            expected = expected.rstrip("$")
            received = received.rstrip("$")

        return {
            "success": (
                self.current_segment == len(self.frames)
                and self.sender_fsm.get_state() == SenderState.IDLE
            ),
            "sent_data": self.data,
            "received_data": received,
            "decoded_segments": list(self.decoded_segments),
            "payload_matches": received == expected,
            "attempts": list(self.attempts),
            "retransmissions": self.retransmissions,
            "sender_state": self.sender_fsm.get_state(),
            "receiver_state": self.receiver_fsm.get_state(),
            "end_tick": self.clk.curr_tick(),
        }


class TestACKNCK(unittest.TestCase):
    def test_noisy_channel_completes_fsm_transfer(self):
        communication = ACKNCKCommunication()
        result = communication.start_communication()

        self.assertTrue(result["success"], result)
        self.assertEqual(result["sender_state"], SenderState.IDLE)
        self.assertEqual(result["receiver_state"], ReceiverState.IDLE)


if __name__ == "__main__":
    unittest.main()



