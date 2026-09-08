from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from uart_emulator.simulation.VirtualChannel import VirtualChannel


class TestNoisyChannel(unittest.TestCase):
	def setUp(self):
		VirtualChannel._instance = None
		if hasattr(VirtualChannel, "_initialized"):
			del VirtualChannel._initialized

	def test_ideal_channel_preserves_bit(self):
		vc1 = VirtualChannel(is_ideal=True)
		vc1.push(tick=0, bit=1)
		self.assertEqual(vc1.read(tick=0), 1)

	def test_noisy_channel_flips_bit(self):
		vc2 = VirtualChannel(is_ideal=False, bit_flip_rate=1.0)
		vc2.push(tick=0, bit=1)
		self.assertEqual(vc2.read(tick=0), 0)

	def test_channel_can_flip_zero_and_one(self):
		vc3 = VirtualChannel(is_ideal=False, bit_flip_rate=1.0)
		vc3.push(tick=0, bit=0)
		vc3.push(tick=1, bit=1)
		self.assertEqual(vc3.read(tick=0), 1)
		self.assertEqual(vc3.read(tick=1), 0)


if __name__ == "__main__":
	unittest.main()
