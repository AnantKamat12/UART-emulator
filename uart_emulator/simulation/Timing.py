def ticks_per_bit_for_baud(baud_rate):
    """Convert a baud rate to integer simulation ticks per bit."""
    if baud_rate <= 0:
        raise ValueError("baud_rate must be a positive integer")
    return max(1, round(100 * 9600 / baud_rate))


class Clock:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, baud_rate=9600, current_tick=0):
        if getattr(self, "_initialized", False):
            return

        self.baud_rate = baud_rate
        self.current_tick = current_tick
        # 1 bit at 9600 baud is represented as 100 simulator ticks.
        self.no_of_ticks_per_bit = ticks_per_bit_for_baud(baud_rate)
        self._initialized = True

    def tick(self):
        self.current_tick += 1
        return self.current_tick

    def curr_tick(self):
        return self.current_tick

    def reset(self):
        self.current_tick = 0


if __name__ == "__main__":
    c = Clock(9600, 0)
    while c.curr_tick() < 1000:
        if c.curr_tick() % c.no_of_ticks_per_bit == 0:
            print(f"{c.curr_tick()}: This is where bit transmission or reception is happening")
        c.tick()
