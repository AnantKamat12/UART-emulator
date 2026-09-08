from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from uart_emulator.simulation.Timing import Clock


def reset_clock():
    Clock._instance = None
    if hasattr(Clock, "_initialized"):
        del Clock._initialized


class TestClock(unittest.TestCase):
    def setUp(self):
        reset_clock()

    def test_starts_at_requested_tick(self):
        clock = Clock(baud_rate=9600, current_tick=10)

        self.assertEqual(clock.curr_tick(), 10)
        self.assertEqual(clock.no_of_ticks_per_bit, 100)

    def test_is_singleton_and_advances(self):
        first = Clock()
        second = Clock(baud_rate=19200, current_tick=50)

        self.assertIs(first, second)
        self.assertEqual(second.curr_tick(), 0)
        self.assertEqual(first.tick(), 1)
        self.assertEqual(second.curr_tick(), 1)


if __name__ == "__main__":
    unittest.main()
