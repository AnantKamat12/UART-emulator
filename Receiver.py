from VirtualChannel import VirtualChannel as VC
from Timing import Clock as CLK
class Rx():
    def __init__(self,baud_rate):
        self.baud_rate=baud_rate
        self.clk=CLK(self.baud_rate)
        self.clk.reset()
    #receiver will wait for line to be pulled low, which indicates start of data transfer, then it will start receiving the data bits
    def receive_data(self, tick,line=0):
        if line==0:#here tick is used just to print in logs,reciving is asynchronous, so no need to check for tick
            if VC.line0.pop(0)==1:
                pass
            if VC.line0.pop(0)==0:
                #detected data tarnsfer start, so start receiving data
                frame=0
                for x in range(16):
                    bit=VC.line0.pop(0)
                    frame|=(bit<<x) 
                return frame
        if line==1: 
            if VC.line1.pop(0)==1:
                pass
            if VC.line1.pop(0)==0:
                #detected data tarnsfer start, so start receiving data
                frame=0
                for x in range(16):
                    bit=VC.line1.pop(0)
                    frame|=(bit<<x) 
                return frame

