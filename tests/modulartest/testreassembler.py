import sys
from pathlib import Path
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from uart_emulator.protocol.Frames import Frame
from uart_emulator.protocol.Reassembler import Reassembler


class TestReassembler(unittest.TestCase):
    def test_reassemble_integer_data(self):
        reassembler = Reassembler(data_type=0)
        frames = [
            Frame(data="A", data_size=1).serialise(),
            Frame(data="AB", data_size=2).serialise(),
            Frame(data="ABC", data_size=3).serialise(),
        ]

        for frame, size in zip(frames, [1, 2, 3]):
            reassembler.decode(frame, data_size=size)

        self.assertEqual(
            reassembler.get_data(),
            [0x41, 0x4142, 0x414243]
        )

    def test_corrupted_frame_is_reported(self):
        reassembler = Reassembler(data_type=0)
        frame = bytearray(Frame(data="A").serialise())
        frame[0] ^= 0b00000001

        result = reassembler.decode(
            bytes(frame),
            non_ideal_vc=True,
            data_size=1
        )

        self.assertIn("Corrupted Frame", result)


if __name__ == "__main__":
    unittest.main()