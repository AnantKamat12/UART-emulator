from Receiver import Rx
from Transmitter import Tx
from Reassembler import Reassembler as RA
from Timing import Clock as CLK

# goal is to make this CLI based real time data transfer simulation, so that user can see how data is being transmitted and received in real time
class Host:
    def __init__(self, host_type, baud_rate: int = 9600, data_type: int = 1, host_transmit_lane: int = 0):
        self.baud_rate = baud_rate
        self.host_type = host_type
        self.data_type = data_type
        self.host_transmit_lane = host_transmit_lane
        self.host_receive_lane = 1 - host_transmit_lane
        self.rck_reassembler = RA(self.data_type)
        self.send_reassembler = RA(self.data_type)
        self.clk = CLK(self.baud_rate)
        self.clk.reset()
        self.tx = None
        self.rx = None

    def setuphost(self):
        if self.host_type not in [0, 1, 2]:
            raise ValueError("Invalid host_type. Use 0 for Tx, 1 for Rx, or 2 for Tx + Rx.")
        if self.host_type == 0:
            self.tx = Tx(self.baud_rate)
        elif self.host_type == 1:
            self.rx = Rx(self.baud_rate)
        elif self.host_type == 2:
            self.tx = Tx(self.baud_rate)
            self.rx = Rx(self.baud_rate)

    def hostsend(self, frame, start_tick):
        if self.tx is None:
            raise RuntimeError("Tx not initialized. Call setuphost() first.")

        # wait until start tick
        while self.clk.curr_tick() < start_tick:
            self.clk.tick()

        # send one bit at each bit-boundary tick
        for bit_index in range(16):
            while self.clk.curr_tick() % self.clk.no_of_ticks_per_bit != 0:
                self.clk.tick()

            bit = (frame >> bit_index) & 0x1

            if self.host_transmit_lane == 0:
                self.tx.vc.line0.append(bit)
            else:
                self.tx.vc.line1.append(bit)

            print(f"tick={self.clk.curr_tick()} : sent bit {bit}")
            self.clk.tick()

        # frame is complete
        self.send_reassembler.decode(frame)

    def hostreceive(self, tick):
        if self.rx is None:
            raise RuntimeError("Rx not initialized. Call setuphost() first.")

        frame = self.rx.receive_data(tick, self.host_receive_lane)
        if frame is not None:
            self.rck_reassembler.decode(frame)

    def get_current_received_data(self):
        return self.rck_reassembler.rcvd_data

    def get_current_transmitted_data(self):
        return self.send_reassembler.rcvd_data

    def __str__(self):
        return f"Host Type: {self.host_type}, Baud Rate: {self.baud_rate}, Data Type: {self.data_type}, Transmit Lane: {self.host_transmit_lane}, Receive Lane: {self.host_receive_lane}"