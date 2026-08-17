from VirtualChannel import VirtualChannel as VC
class Tx():
    def __init__(self,baud_rate):
        self.baud_rate=baud_rate
    def send_data(data):
        VC.push_frame(data)