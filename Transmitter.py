from VirtualChannel import VirtualChannel as VC


class Tx:
    def __init__(self, baud_rate=9600):
        self.baud_rate = baud_rate
        self.vc = VC()

        # Your simulation convention:
        # 100 simulation ticks = 1 bit at 9600 baud
        self.ticks_per_bit = 100

        self.frame = None
        self.start_tick = None
        self.bit_index = 0
        self.line = 0
        self.active = False

    def start_transmission(self, frame, start_tick, line=0):
        """
        Prepare a frame for transmission.
        This does NOT advance the clock.
        """
        self.frame = frame
        self.start_tick = start_tick
        self.bit_index = 0
        self.line = line
        self.active = True

    def step(self, current_tick):
        """
        Perform whatever TX should do at the current simulation tick.

        The simulation/Host calls this once per tick.
        TX never advances the clock itself.
        """

        if not self.active:
            return

        if current_tick < self.start_tick:
            return

        # Only transmit at bit boundaries.
        if current_tick % self.ticks_per_bit != 0:
            return

        # Frame completely transmitted
        if self.bit_index >= 16:
            self.active = False
            return

        # Extract next bit, LSB first
        bit = (self.frame >> self.bit_index) & 1

        # Put the bit onto the virtual channel
        self.vc.push(
            tick=current_tick,
            bit=bit,
            line=self.line
        )

        print(f"tick={current_tick}: TX bit={bit}")

        self.bit_index += 1

        if self.bit_index >= 16:
            self.active = False