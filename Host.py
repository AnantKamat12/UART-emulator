from Receiver import Rx
from Transmitter import Tx
from Reassembler import Reassembler as RA
from Timing import Clock as CLK


class Host:

    def __init__(
        self,
        host_type,
        baud_rate=9600,
        data_type=1,
        host_transmit_lane=0
    ):
        self.baud_rate = baud_rate
        self.host_type = host_type
        self.data_type = data_type

        # Host A transmits on line 0 and receives on line 1
        # Host B transmits on line 1 and receives on line 0
        self.host_transmit_lane = host_transmit_lane
        self.host_receive_lane = 1 - host_transmit_lane

        self.rck_reassembler = RA(data_type)
        self.send_reassembler = RA(data_type)

        # Host owns/accesses the simulation clock
        self.clk = CLK(self.baud_rate)

        self.tx = None
        self.rx = None

    def setuphost(self):
        if self.host_type not in [0, 1, 2]:
            raise ValueError(
                "Invalid host_type. "
                "Use 0 for Tx, 1 for Rx, or 2 for Tx + Rx."
            )

        if self.host_type in [0, 2]:
            self.tx = Tx(self.baud_rate)

        if self.host_type in [1, 2]:
            self.rx = Rx(self.baud_rate)

    def start_send(self, frame, start_tick):
        """
        Start a transmission.

        This only tells TX what to transmit.
        It does NOT advance the clock.
        """
        if self.tx is None:
            raise RuntimeError("TX is not initialized.")

        self.tx.start_transmission(
            frame=frame,
            start_tick=start_tick,
            line=self.host_transmit_lane
        )

    def step(self):
        """
        Execute one simulation step.

        TX and RX both operate at the SAME current tick.
        This method does NOT advance the clock.
        """

        current_tick = self.clk.curr_tick()

        # TX gets to act at this tick
        if self.tx is not None:
            self.tx.step(current_tick)

        # RX gets to act at this tick
        if self.rx is not None:
            frame = self.rx.step(
                current_tick,
                self.host_receive_lane
            )

            if frame is not None:
                print(
                    f"Host received complete frame "
                    f"at tick {current_tick}: {frame:016b}"
                )

                # Later we can pass this into your reassembler
                # self.rck_reassembler.decode(frame)