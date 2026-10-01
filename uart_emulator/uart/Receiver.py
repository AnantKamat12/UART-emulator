from uart_emulator.simulation.VirtualChannel import VirtualChannel as VC
from uart_emulator.simulation.Timing import ticks_per_bit_for_baud


class Rx:
    def __init__(
        self,
        baud_rate=9600,
        event_logger=None,
        hostname="HOST",
        data_size=1,
    ):
        if data_size not in (1, 2, 3):
            raise ValueError("data_size must be 1, 2, or 3 bytes")
        self.baud_rate = baud_rate
        self.vc = VC()
        self.logger = event_logger
        self.hostname = hostname
        self.frame_bits = data_size * 8 + 8

        self.ticks_per_bit = ticks_per_bit_for_baud(baud_rate)

        self.frame = 0
        self.bit_index = 0
        self.receiving = False

    def reset_receiver(self):
        """Reset the receive state for the next frame."""
        self.frame = 0
        self.bit_index = 0
        self.receiving = False

    def step(self, current_tick, line=0):
        """Read one bit from the virtual channel when it becomes available."""
        bit = self.vc.read(
            tick=current_tick,
            line=line
        )

        if bit is None:
            return None

        message = f"[{self.hostname}] RX bit={bit}"
        if self.logger is not None:
            self.logger.write(message, current_tick)
        if self.logger is not None:
            self.logger.logprint(message, current_tick)

        if not self.receiving:
            self.receiving = True
            self.frame = 0
            self.bit_index = 0

        self.frame |= (bit << self.bit_index)
        self.bit_index += 1

        if self.bit_index == self.frame_bits:
            received_frame = self.frame
            message = (
                f"[{self.hostname}] RX complete frame="
                f"{received_frame:0{self.frame_bits}b}"
            )
            if self.logger is not None:
                self.logger.write(message, current_tick)
            if self.logger is not None:
                self.logger.logprint(message, current_tick)
            self.reset_receiver()
            return received_frame

        return None