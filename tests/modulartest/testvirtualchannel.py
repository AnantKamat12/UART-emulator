from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from uart_emulator.simulation.VirtualChannel import VirtualChannel


def reset_channel():
    VirtualChannel._instance = None
    if hasattr(VirtualChannel, "_initialized"):
        del VirtualChannel._initialized


class TestVirtualChannel(unittest.TestCase):
    def setUp(self):
        reset_channel()

    def test_waits_until_tick(self):
        channel = VirtualChannel(is_ideal=True)
        channel.push(tick=10, bit=1, line=0)

        self.assertIsNone(channel.read(tick=9, line=0))
        self.assertEqual(channel.read(tick=10, line=0), 1)

    def test_ideal_channel_preserves_bit(self):
        channel = VirtualChannel(is_ideal=True)
        channel.push(tick=0, bit=1, line=1)

        self.assertEqual(channel.read(tick=0, line=1), 1)

    def test_noisy_channel_flips_every_bit_at_rate_one(self):
        channel = VirtualChannel(is_ideal=False, bit_flip_rate=1.0)
        channel.push(tick=0, bit=1)

        self.assertEqual(channel.read(tick=0), 0)


if __name__ == "__main__":
    unittest.main()
