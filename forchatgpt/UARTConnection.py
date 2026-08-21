from Host import Host
class UARTConnection():
    def __init__(self,host_type,baud_rate:int=9600,data_type:int=1):
        self.hostA=Host(host_type,baud_rate,data_type)
        self.hostB=Host(host_type,baud_rate,data_type)
        self.hostA.setuphost()  
        self.hostB.setuphost()
        self.hostA.clk.reset()#clk is singleton..
        self.hostA.clk.startclock()#start clock for hostA
        #but if i startt cock cpu will be blocked
        
