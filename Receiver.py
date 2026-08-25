from VirtualChannel import VirtualChannel as VC


class Rx:
    def __init__(self, baud_rate=9600):
        self.baud_rate = baud_rate
        self.vc = VC()

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

        print(f"tick={current_tick}: RX bit={bit}")

        if not self.receiving:
            self.receiving = True
            self.frame = 0
            self.bit_index = 0

        self.frame |= (bit << self.bit_index)
        self.bit_index += 1

        if self.bit_index == 16:
            received_frame = self.frame
            print(f"tick={current_tick}: RX complete frame={received_frame:016b}")
            self.reset_receiver()
            return received_frame

        return None