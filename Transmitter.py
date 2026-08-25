from VirtualChannel import VirtualChannel as VC


class Tx:
    def __init__(self, baud_rate=9600):
        self.baud_rate = baud_rate
        self.vc = VC()

        # Keep the simulation convention explicit.
        self.ticks_per_bit = 100

        self.frame = None
        self.start_tick = None
        self.bit_index = 0
        self.line = 0
        self.active = False

    def start_transmission(self, frame, start_tick, line=0):
        """Prepare a frame for transmission without advancing the clock."""
        self.frame = frame
        self.start_tick = start_tick
        self.bit_index = 0
        self.line = line
        self.active = True

    def step(self, current_tick):
        """Transmit exactly one bit when the current tick is on a bit boundary."""
        if not self.active:
            return

        if current_tick < self.start_tick:
            return

        if current_tick % self.ticks_per_bit != 0:
            return

        if self.bit_index >= 16:
            self.active = False
            return

        bit = (self.frame >> self.bit_index) & 1

        self.vc.push(
            tick=current_tick,
            bit=bit,
            line=self.line
        )

        print(f"tick={current_tick}: TX bit={bit}")
        self.bit_index += 1

        if self.bit_index >= 16:
            self.active = False