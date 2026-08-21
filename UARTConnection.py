from Host import Host


class UARTConnection:

    def __init__(self, baud_rate=9600, data_type=1):
        # Host A: TX on line 0, RX on line 1
        self.hostA = Host(
            host_type=2,
            baud_rate=baud_rate,
            data_type=data_type,
            host_transmit_lane=0
        )

        # Host B: TX on line 1, RX on line 0
        self.hostB = Host(
            host_type=2,
            baud_rate=baud_rate,
            data_type=data_type,
            host_transmit_lane=1
        )

        self.hostA.setuphost()
        self.hostB.setuphost()

        # Both hosts use the same simulation clock.
        self.clk = self.hostA.clk

    def run(self, max_ticks=5000):
        """
        Run the complete simulation.

        One iteration = one simulation tick.

        At each tick:
            1. Host A acts
            2. Host B acts
            3. Simulation clock advances
        """

        while self.clk.curr_tick() < max_ticks:

            current_tick = self.clk.curr_tick()

            print(f"\n--- TICK {current_tick} ---")

            # Both hosts operate at the SAME simulated tick.
            self.hostA.step()
            self.hostB.step()

            # Only the simulation advances time.
            self.clk.tick()