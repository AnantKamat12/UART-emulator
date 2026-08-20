from VirtualChannel import VirtualChannel as VC
from Timing import Clock as CLK
#for test purpose importing tx
from Transmitter import Tx as TX
class Rx(VC):
    def __init__(self,baud_rate):
        super().__init__(baud_rate=baud_rate)
        self.baud_rate=baud_rate
        self.clk=CLK(self.baud_rate)
        self.clk.reset()
        self.vc=VC()#singleton VC instance
    #receiver will wait for line to be pulled low, which indicates start of data transfer, then it will start receiving the data bits
    def receive_data(self, tick, line=0):
        if line==0:#here tick is used just to print in logs,reciving is asynchronous, so no need to check for tick
            if self.vc.line0.pop(0)==1:
                pass
            if self.vc.line0.pop(0)==0:
                #detected data tarnsfer start, so start receiving data
                frame=0
                for x in range(16):
                    bit=self.vc.line0.pop(0)
                    frame|=(bit<<x) 
                return frame
        if line==1: 
            if self.vc.line1.pop(0)==1:
                pass
            if self.vc.line1.pop(0)==0:
                #detected data tarnsfer start, so start receiving data
                frame=0
                for x in range(16):
                    bit=self.vc.line1.pop(0)
                    frame|=(bit<<x) 
                return frame

if __name__=="__main__":

    tx=TX(baud_rate=9600)
    rx=Rx(baud_rate=9600)
    tx.send_data(frame=0b1010101010101010,Start_tick=10,line=0)
    while True:
        frame=rx.receive_data(tick=tx.clk.curr_tick(),line=0)
        if frame is not None:
            print(f"Received frame: {frame:016b}")
            break