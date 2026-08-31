from uart_emulator.simulation.Timing import Clock

# Waveframe simulation — generates square wave based on baud rate
class Waveframe(Clock):
    def __init__(self):
        # Clock singleton must be already initialized,just use it
        self.half_time = self.no_of_ticks_per_bit // 2
    
    def wave(self):
        """Generate square wave: 1 for high half, -1 for low half"""
        if self.curr_tick() % self.no_of_ticks_per_bit >= self.half_time:
            return 1
        else:
            return -1


