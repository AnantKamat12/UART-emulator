from Receiver import Rx
from Transceiver import Tx
class Host():
    def __init__(self,host_type,baud_rate:int=9600):
        self.baud_rate=baud_rate
        self.host_type=host_type
    def setuphost(self):
        if self.host_type not in [0,1,2]:
            raise ValueError("Invalid host_type. Use 0 for Tx, 1 for Rx, or 2 for Tx + Rx.")
        if self.host_type==0:
            self.tx=Tx(self.baud_rate)
        elif self.host_type==1:
            self.rx=Rx(self.baud_rate)
        elif self.host_type==2:
            self.tx=Tx(self.baud_rate)
            self.rx=Rx(self.baud_rate)
        

