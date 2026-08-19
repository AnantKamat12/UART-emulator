class VirtualChannel():
    def __init__(self,is_ideal:int =0,baud_rate:int =9600):
        self.is_ideal=is_ideal
        self.baud_rate=baud_rate
        self.line0=[]#analogous to register in hardware, this is the lane where transmitter will push the bits to be transmitted
        self.line1=[]#analogous to register in hardware, this is the lane where receiver will pull the bits from