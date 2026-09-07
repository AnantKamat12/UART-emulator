import sys
from pathlib import Path    
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from uart_emulator.protocol.Segmenter import segmenter as SG
data = b"Hello, this is a test message for the Segmenter class."
class TestSegmenter:
    def __init__(self, max_segment_size):
        self.segmenter = SG(max_segment_size=max_segment_size)

    def test_segment_data(self, data):
        segments = self.segmenter.segment_data(data)
        print(f"Segments (max size {self.segmenter.max_segment_size}):")
        for i, segment in enumerate(segments):
            print(f"Segment {i + 1}: {segment}")
if __name__ == "__main__":
    test_segmenter = TestSegmenter(max_segment_size=16)

    test_segmenter.test_segment_data(data)
    test_segmenter2 = TestSegmenter(max_segment_size=8)
    test_segmenter2.test_segment_data(data)

