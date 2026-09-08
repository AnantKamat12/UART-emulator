import sys
from pathlib import Path
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from uart_emulator.protocol.Segmenter import segmenter as SG
class TestSegmenter(unittest.TestCase):
    def test_segments_respect_maximum_size(self):
        segmenter = SG(max_segment_size=16)
        segments = segmenter.segment_data(b"ABCDEF")

        self.assertEqual(segments, [b"AB", b"CD", b"EF"])
        segmenter2 = SG(max_segment_size=8)
        segments2 = segmenter2.segment_data(b"ABCD")  
        self.assertEqual(segments2, [b"A", b"B", b"C", b"D"])

    def test_rejects_non_byte_aligned_size(self):
        with self.assertRaises(ValueError):
            SG(max_segment_size=7)


if __name__ == "__main__":
    unittest.main()

