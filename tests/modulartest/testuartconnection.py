from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from uart_emulator.simulation.Timing import Clock
from uart_emulator.simulation.VirtualChannel import VirtualChannel
from uart_emulator.uart.UARTConnection import UARTConnection


def reset_singletons():
    Clock._instance = None
    if hasattr(Clock, "_initialized"):
        del Clock._initialized
    VirtualChannel._instance = None
    if hasattr(VirtualChannel, "_initialized"):
        del VirtualChannel._initialized


class TestUARTConnection(unittest.TestCase):
    def setUp(self):
        reset_singletons()

    def test_creates_duplex_hosts(self):
        connection = UARTConnection()

        self.assertIsNotNone(connection.hostA.tx)
        self.assertIsNotNone(connection.hostA.rx)
        self.assertIsNotNone(connection.hostB.tx)
        self.assertIsNotNone(connection.hostB.rx)
        self.assertIs(connection.hostA.clk, connection.hostB.clk)

        connection.hostA.logger.close()
        connection.hostB.logger.close()

    def test_can_run_one_tick(self):
        connection = UARTConnection()
        connection.run(max_ticks=1)

        self.assertEqual(connection.clk.curr_tick(), 1)
        connection.hostA.logger.close()
        connection.hostB.logger.close()


if __name__ == "__main__":
    unittest.main()
