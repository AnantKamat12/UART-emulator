from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from uart_emulator.infrastructure.All_APIs_for_custom_tests import (
    build_frame,
    decode_frame,
    reset_simulation,
)
from uart_emulator.simulation.VirtualChannel import VirtualChannel


class TestNoisyChannel(unittest.TestCase):
    def setUp(self):
        reset_simulation()

    def test_bit_flip_rate_one_flips_bits(self):
        channel = VirtualChannel(is_ideal=False, bit_flip_rate=1.0)
        channel.push(tick=0, bit=1)
        channel.push(tick=1, bit=0)

        self.assertEqual(channel.read(tick=0), 0)
        self.assertEqual(channel.read(tick=1), 1)

    def test_noisy_frame_is_not_decoded_as_valid(self):
        channel = VirtualChannel(is_ideal=False, bit_flip_rate=1.0)
        frame = build_frame("A")
        frame_value = int.from_bytes(frame, byteorder="big")

        for bit_index in range(16):
            channel.push(
                tick=bit_index,
                bit=(frame_value >> bit_index) & 1,
                line=0,
            )

        received_value = 0
        for bit_index in range(16):
            received_value |= channel.read(tick=bit_index, line=0) << bit_index

        result = decode_frame(
            received_value.to_bytes(2, byteorder="big"),
            data_type=1,
            data_size=1,
            non_ideal=True,
        )

        self.assertTrue(result.startswith("Corrupted Frame due to "))


if __name__ == "__main__":
    unittest.main()