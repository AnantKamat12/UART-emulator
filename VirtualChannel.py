class VirtualChannel():
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    def __init__(self,is_ideal:int =0,baud_rate:int =9600):
        if getattr(self, "_initialized", False):
            return
        self.is_ideal=is_ideal
        self.baud_rate=baud_rate
        self.line0=[]#analogous to register in hardware, this is the lane where transmitter will push the bits to be transmitted
        self.line1=[]#analogous to register in hardware, this is the lane where receiver will pull the bits from
        self._initialized = True
    def reset(self):
        self.line0.clear()
        self.line1.clear()