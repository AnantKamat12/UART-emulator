from VirtualChannel import VirtualChannel as VC


class Rx:
    def __init__(self, baud_rate=9600):
        self.baud_rate = baud_rate
        self.vc = VC()

        # Same simulation convention as TX
        self.ticks_per_bit = 100

        self.frame = 0
        self.bit_index = 0
        self.receiving = False

    def reset_receiver(self):
        """
        Reset receiver state so the next frame can be received.
        """
        self.frame = 0
        self.bit_index = 0
        self.receiving = False

    def step(self, current_tick, line=0):
        """
        Check whether a bit is available on the VC at current_tick.

        RX does NOT wait.
        RX does NOT advance the clock.
        RX simply checks the channel once per simulation tick.

        Returns:
            Complete frame when 16 bits have been received.
            None otherwise.
        """

        bit = self.vc.read(
            tick=current_tick,
            line=line
        )

        # Nothing available at this tick
        if bit is None:
            return None

        print(f"tick={current_tick}: RX bit={bit}")

        # First bit of a new frame
        if not self.receiving:
            self.receiving = True
            self.frame = 0
            self.bit_index = 0

        # Put received bit into the frame
        self.frame |= (bit << self.bit_index)

        self.bit_index += 1

        # Full 16-bit frame received
        if self.bit_index == 16:
            received_frame = self.frame

            print(
                f"tick={current_tick}: "
                f"RX complete frame={received_frame:016b}"
            )

            self.reset_receiver()

            return received_frame

        return None