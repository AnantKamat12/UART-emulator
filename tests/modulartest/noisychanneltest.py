from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import numpy as np
from uart_emulator.simulation.VirtualChannel import VirtualChannel


def test_ideal_channel_preserves_bit():
	VirtualChannel._instance = None
	vc1 = VirtualChannel(is_ideal=True)

	vc1.push(tick=0, bit=1)

	assert vc1.read(tick=0) == 1


def test_noisy_channel_flips_bit():
	VirtualChannel._instance = None
	vc2 = VirtualChannel(is_ideal=False, bit_flip_rate=1.0)  # Set bit_flip_rate to 1.0 to ensure bit flipping

	vc2.push(tick=0, bit=1)

	assert vc2.read(tick=0) == 0
def test_bit_flip_at_half():

	VirtualChannel._instance = None
	vc3 = VirtualChannel(is_ideal=False, bit_flip_rate=0.5)
	# Set bit_flip_rate to 0.5 for a 50% chance of flipping

	# Push multiple bits to test the flipping behavior
	bits_to_test = np.random.randint(0, 2, size=100)
	flipped_bits = np.zeros_like(bits_to_test)
	num_flipped = 0

	for i, bit in enumerate(bits_to_test):
		vc3.push(tick=i, bit=bit)
		flipped_bit = vc3.read(tick=i)
		flipped_bits[i] = int(flipped_bit)

		if flipped_bit != bits_to_test[i]:
			num_flipped += 1

	print("Original bits:", bits_to_test)
	print("Flipped bits:", flipped_bits)
	print("Number of flipped bits:", num_flipped)
	print("Percentage of flipped bits:", (num_flipped / len(bits_to_test)) * 100, "%")


if __name__ == "__main__":
	test_ideal_channel_preserves_bit()
	test_noisy_channel_flips_bit()
	test_bit_flip_at_half()
	print("Noisy channel tests passed")
