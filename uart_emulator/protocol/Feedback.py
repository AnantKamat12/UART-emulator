
from uart_emulator.protocol.Frames import Frame


class Feedback():
    def __init__(self, hosta, hostb):
        self.hosta = hosta
        self.hostb = hostb

    def send_feedback(self, status, rxhost, curr_tick, data_size=1):
        """Schedule an ACK or NACK from the receiving host.
        """
        ack_nck = 0 if status == "OK" else 1
        feedback_frame = Frame.gen_ack_nack_frame(
            ack_nck=ack_nck,
            data_size=data_size
        )
        frame_value = int.from_bytes(
            feedback_frame.serialise(),
            byteorder="big"
        )

        ticks_per_bit = rxhost.tx.ticks_per_bit
        next_boundary = curr_tick + ticks_per_bit - (
            curr_tick % ticks_per_bit
        )
        if next_boundary == curr_tick:
            next_boundary += ticks_per_bit
        """just activates Receiver's transmission line not a single bit is sent,
        and Rxhost.tx =active , so that in next step() of simulation, the first bit of feedback frame is sent"""
        rxhost.start_send(
            frame=frame_value,
            start_tick=next_boundary,
            line=rxhost.host_transmit_lane
        )
        return feedback_frame
