from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from uart_emulator.simulation.Timing import Clock
from uart_emulator.simulation.VirtualChannel import VirtualChannel
from uart_emulator.uart.Host import Host


def reset_singletons():
    Clock._instance = None
    if hasattr(Clock, "_initialized"):
        del Clock._initialized
    VirtualChannel._instance = None
    if hasattr(VirtualChannel, "_initialized"):
        del VirtualChannel._initialized


class TestHost(unittest.TestCase):
    def setUp(self):
        reset_singletons()

    def test_duplex_host_setup(self):
        host = Host(host_type=2, host_transmit_lane=0, hostname="TEST_HOST")
        host.setuphost()

        self.assertIsNotNone(host.tx)
        self.assertIsNotNone(host.rx)
        self.assertEqual(host.host_transmit_lane, 0)
        self.assertEqual(host.host_receive_lane, 1)
        self.assertIs(host.host_logger, host.logger)

        host.logger.close()

    def test_invalid_host_type_is_rejected(self):
        host = Host(host_type=99, hostname="TEST_HOST")

        host.logger.close()
        with self.assertRaises(ValueError):
            host.setuphost()


if __name__ == "__main__":
    unittest.main()
