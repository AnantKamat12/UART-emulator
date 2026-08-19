from VirtualChannel import VirtualChannel as VC #this VC will be initialized in UARTConfig.py
from Timing import Clock as CLK
class Tx():
    def __init__(self,baud_rate):
        self.baud_rate=baud_rate
        self.clk=CLK(self.baud_rate)
        self.clk.reset()
    def send_data(self, frame, tick,line=0):
        if self.clk.curr_tick() == tick:
            #send the bit to the virtual channel
            if line==0:
                for x in range(16):
                    VC.line0.append((frame >> x) & 0x1)
                    self.clk.tick()
            if line==1:
                for x in range(16):
                    VC.line1.append((frame >> x) & 0x1)
                    self.clk.tick()
        else:
            #send high signal to indicate no data transfer
            if line==0:
                VC.line0.append(1)      
            if line==1:
                VC.line1.append(1)
        
   