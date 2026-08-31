from uart_emulator.uart.Receiver import Rx
from uart_emulator.uart.Transmitter import Tx
from uart_emulator.protocol.Reassembler import Reassembler as RA
from uart_emulator.simulation.Timing import Clock as CLK
from uart_emulator.infrastructure.Logger import HostType, logger


class Host:

    def __init__(
        self,
        host_type,
        baud_rate=9600,
        data_type=1,
        host_transmit_lane=0,
        hostname=None
    ):
        self.baud_rate = baud_rate
        self.host_type = host_type
        self.data_type = data_type

        # Host A transmits on line 0 and receives on line 1.
        # Host B transmits on line 1 and receives on line 0.
        self.host_transmit_lane = host_transmit_lane
        self.host_receive_lane = 1 - host_transmit_lane
        self.hostname = hostname or (
            "HOST_A" if host_transmit_lane == 0 else "HOST_B"
        )

        host_type_names = {
            0: HostType.TxHost,
            1: HostType.RxHost,
            2: HostType.DuplexHost,
        }
        self.logger = logger(
            log_id=0,
            hostname=self.hostname,
            start_tick=0,
            host_type=host_type_names.get(host_type, HostType.DuplexHost)
        )

        self.rck_reassembler = RA(data_type)
        self.send_reassembler = RA(data_type)

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
            self.tx = Tx(self.baud_rate, self.logger, self.hostname)

        if self.host_type in [1, 2]:
            self.rx = Rx(self.baud_rate, self.logger, self.hostname)

    def start_send(self, frame, start_tick,line):
        """Queue a frame for transmission at the requested start tick."""
        if line is None:
            line=self.host_transmit_lane
        if self.tx is None:
            raise RuntimeError("TX is not initialized.")

        self.tx.start_transmission(
            frame=frame,
            start_tick=start_tick,
            line=line
        )
    #send logger for custom log printing in test cases
    @property
    def host_logger(self):
        return self.logger
    def current_rcvd_data(self):
        if self.rck_reassembler is not None:
            return self.rck_reassembler.rcvd_data_comb()

    def step(self):
        """Advance one simulation tick and let TX/RX operate at that tick."""
        current_tick = self.clk.curr_tick()

        if self.tx is not None:
            self.tx.step(current_tick)

        if self.rx is not None:
            frame = self.rx.step(
                current_tick,
                self.host_receive_lane
            )

            if frame is not None:
                message = (
                    f"[{self.hostname}] received complete frame: "
                    f"{frame:016b}"
                )
                self.logger.write(message, current_tick)
                logger.logprint(message, current_tick)

                # Later we can pass this into your reassembler
                self.rck_reassembler.decode(frame)
                #would be handled later by test cases
            