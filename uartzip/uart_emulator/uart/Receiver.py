from uart_emulator.simulation.VirtualChannel import VirtualChannel as VC
from uart_emulator.infrastructure.Logger import logger


class Rx:
    def __init__(self, baud_rate=9600, event_logger=None, hostname="HOST"):
        self.baud_rate = baud_rate
        self.vc = VC()
        self.logger = event_logger
        self.hostname = hostname

        self.ticks_per_bit = 100

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
        logger.logprint(message, current_tick)

        if not self.receiving:
            self.receiving = True
            self.frame = 0
            self.bit_index = 0

        self.frame |= (bit << self.bit_index)
        self.bit_index += 1

        if self.bit_index == 16:
            received_frame = self.frame
            message = (
                f"[{self.hostname}] RX complete frame="
                f"{received_frame:016b}"
            )
            if self.logger is not None:
                self.logger.write(message, current_tick)
            logger.logprint(message, current_tick)
            self.reset_receiver()
            return received_frame

        return None