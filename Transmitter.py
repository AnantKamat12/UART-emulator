from VirtualChannel import VirtualChannel as VC
from Timing import Clock as CLK


class Tx(VC):
    def __init__(self, baud_rate):
        super().__init__(baud_rate=baud_rate, is_ideal=0)
        self.baud_rate = baud_rate
        self.vc = VC()  # singleton VC instance
        self.clk = CLK(self.baud_rate)
        self.clk.reset()

    def _idle(self, line):
        if line == 0:
            self.vc.line0.append(1)
        else:
            self.vc.line1.append(1)

    def send_data(self, frame, Start_tick, line=0):
        # wait until start tick
        while self.clk.curr_tick() < Start_tick:
            self._idle(line)
            self.clk.tick()

        # send 16 bits
        if self.clk.curr_tick() == Start_tick:
            print(self.clk.curr_tick(), ": transmission start")
        for x in range(16):
        #this is the moment frame transmission starts, and at every self.clk.curr_tick()%self.clk.no_of_ticks_per_bit==0, a bit is transmitted
            bit = (frame >> x) & 0x1
            if line == 0:
                self.vc.line0.append(bit)
                print(self.clk.curr_tick(), ": transmission happening", bit)
            else:
                self.vc.line1.append(bit)
                print(self.clk.curr_tick(), ": transmission happening", bit)

            self.clk.tick()


if __name__ == "__main__":
    tx = Tx(baud_rate=9600)
    tx.send_data(frame=0b1010101010101010, Start_tick=1000000, line=0)