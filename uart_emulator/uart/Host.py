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
        hostname=None,
        logger_class=logger,
        data_size=1,
    ):
        if data_size not in (1, 2, 3):
            raise ValueError("data_size must be 1, 2, or 3 bytes")
        self.baud_rate = baud_rate
        self.host_type = host_type
        self.data_type = data_type
        self.data_size = data_size

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
        self.logger = logger_class(
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
            self.tx = Tx(
                self.baud_rate,
                self.logger,
                self.hostname,
                data_size=self.data_size,
            )

        if self.host_type in [1, 2]:
            self.rx = Rx(
                self.baud_rate,
                self.logger,
                self.hostname,
                data_size=self.data_size,
            )

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

    def transmit_step(self, current_tick=None):
        """Advance only this host's transmitter for the given simulation tick."""
        if current_tick is None:
            current_tick = self.clk.curr_tick()
        if self.tx is not None:
            self.tx.step(current_tick)

    def receive_step(self, current_tick=None):
        """Advance only this host's receiver and process any complete frame."""
        if current_tick is None:
            current_tick = self.clk.curr_tick()
        if self.rx is None:
            return None

        received_frame = self.rx.step(
            current_tick,
            self.host_receive_lane
        )
        if received_frame is not None:
            received_bytes = received_frame.to_bytes(
                self.data_size + 1,
                byteorder="big"
            )
            decoded_data = self.rck_reassembler.decode(
                received_bytes,
                data_size=self.data_size
            )
            message = (
                f"[{self.hostname}] Host Received complete frame: "
                f"{received_frame:0{self.rx.frame_bits}b}"
            )
            self.logger.write(message, current_tick)
            self.logger.logprint(message, current_tick)
            decoded_message = (
                f"[{self.hostname}] decoded data: {decoded_data!r}"
            )
            self.logger.write(decoded_message, current_tick)
            self.logger.logprint(decoded_message, current_tick)

        return received_frame

    def step(self):
        """Advance this host's TX then RX for one tick."""
        current_tick = self.clk.curr_tick()
        self.transmit_step(current_tick)
        return self.receive_step(current_tick)
    def get_joined_rcvd_data(self):
        """Return the complete received data from the reassembler."""
        if self.rck_reassembler is not None:
            return self.rck_reassembler.rcvd_data_comb()
        return None
    def get_rcvd_data(self):
        """Return the complete received data from the reassembler."""
        if self.rck_reassembler is not None:
            return self.rck_reassembler.rcvd_data
        return None
            