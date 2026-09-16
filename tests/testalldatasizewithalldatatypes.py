from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from uart_emulator.protocol.Frames import Frame
from uart_emulator.protocol.Reassembler import Reassembler
from uart_emulator.protocol.Segmenter import segmenter

data_sizes = [1, 2, 3]
data_types = [0, 1, 2]  # 0: integer, 1: text, 2: bytes

class test_all_data_sizes_with_all_data_types(unittest.TestCase):
    def setUp(self):
        self.data_sizes = [1, 2, 3]
        self.data_types = [0, 1, 2]  # 0: integer, 1: text, 2: bytes
        self.text_data = "Anant Loves Philosophy"

    def test_integer_round_trip_for_every_data_size(self):
        for data_size in self.data_sizes:
            for data_type in self.data_types:
                if data_type == 0:
                    payload = 123456 & ((1 << (data_size * 8)) - 1)
                    frame = Frame(data=payload, data_size=data_size)
                    decoded = Reassembler(data_type=0).decode(
                        frame.serialise(),
                        data_size=data_size,
                    )
                    self.assertEqual(decoded, payload)

                elif data_type == 1:
                    chunks = segmenter(
                        max_segment_size=data_size * 8
                    ).segment_data(self.text_data)
                    reassembler = Reassembler(data_type=1)

                    for chunk in chunks:
                        frame = Frame(data=chunk, data_size=data_size)
                        decoded = reassembler.decode(
                            frame.serialise(),
                            data_size=data_size,
                        )
                        expected = chunk.decode("ascii").rstrip("$")
                        self.assertEqual(decoded, expected)

                    self.assertEqual(
                        reassembler.rcvd_data_comb(),
                        self.text_data,
                    )

                else:
                    payload = bytes(range(1, data_size + 1))
                    frame = Frame(data=payload, data_size=data_size)
                    decoded = Reassembler(data_type=2).decode(
                        frame.serialise(),
                        data_size=data_size,
                    )
                    self.assertEqual(decoded, payload)


if __name__ == "__main__":
    unittest.main()
