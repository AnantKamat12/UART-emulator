import sys
from pathlib import Path
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from uart_emulator.protocol.Frames import Frame, Deserialise as DS
class TestFrame(unittest.TestCase):
    def setUp(self):
        self.frames = [
            Frame(data="A", data_size=1),
            Frame(data="AB", data_size=2),
            Frame(data="ABC", data_size=3),
        ]

    def test_data_sizes(self):
        self.assertEqual([frame.data_size for frame in self.frames], [1, 2, 3])

    def test_serialization_lengths(self):
        self.assertEqual(
            [len(frame.serialise()) for frame in self.frames],
            [2, 3, 4]
        )

    def test_deserialization(self):
        expected = [
            int.from_bytes(b"A", byteorder="big"),
            int.from_bytes(b"AB", byteorder="big"),
            int.from_bytes(b"ABC", byteorder="big"),
        ]

        for frame, expected_data in zip(self.frames, expected):
            decoder = DS(data_size=frame.data_size)
            status, data = decoder.decode_frame(frame.serialise())
            self.assertEqual(status, "OK")
            self.assertEqual(data, expected_data)


if __name__ == "__main__":
    unittest.main()