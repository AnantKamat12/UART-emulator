from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from uart_emulator.protocol.Frames import Frame
from uart_emulator.protocol.Reassembler import Reassembler
from uart_emulator.protocol.Segmenter import segmenter


class TestAllDataTypes(unittest.TestCase):

    def test_text_segments_are_decoded_as_ascii(self):
        chunks = segmenter(max_segment_size=16).segment_data("Anant")
        self.assertEqual(chunks, [b"An", b"an", b"t$"])

        for chunk in chunks:
            frame = Frame(data=chunk, data_size=2)
            decoded = Reassembler(data_type=1).decode(
                frame.serialise(),
                data_size=2,
            )
            expected = chunk.decode("ascii").rstrip("$")
            self.assertEqual(decoded, expected)

    def test_padding_marker_is_not_returned_or_stored(self):
        chunk = segmenter(max_segment_size=16).segment_data("Anant")[-1]
        reassembler = Reassembler(data_type=1)

        decoded = reassembler.decode(
            Frame(data=chunk, data_size=2).serialise(),
            data_size=2,
        )

        self.assertEqual(chunk, b"t$")
        self.assertEqual(decoded, "t")
        self.assertEqual(reassembler.get_data(), ["t"])

    def test_integer_frame_round_trip(self):
        payload = 0x41
        frame = Frame(data=payload, data_size=1)
        decoded = Reassembler(data_type=0).decode(
            frame.serialise(),
            data_size=1,
        )
        self.assertEqual(decoded, payload)

    def test_byte_frame_serialization_and_decode(self):
        payload = b"\x01\x02"
        frame = Frame(data=payload, data_size=2)
        self.assertEqual(len(frame.serialise()), 3)

        decoded = Reassembler(data_type=2).decode(
            frame.serialise(),
            data_size=2,
        )
        self.assertEqual(decoded, payload)


if __name__ == "__main__":
    unittest.main()
