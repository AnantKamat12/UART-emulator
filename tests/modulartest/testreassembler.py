import testframe as tf
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import uart_emulator.protocol.Reassembler as RA

class TestReassembler:
    def __init__(self, data_type):
        self.reassembler = RA.Reassembler(data_type=data_type)

    def test_reassemble(self, serialized_frames, data_sizes):
        for frame, size in zip(serialized_frames, data_sizes):
            self.reassembler.decode(frame, data_size=size)
        return self.reassembler.get_data(), self.reassembler.rcvd_data_comb()
if __name__ == "__main__":
    test_reassembler = TestReassembler(data_type=1)  # 1 for string
    serialized_frames = [tf.serialized_frame1, tf.serialized_frame2, tf.serialized_frame3]
    data_sizes = [1, 2, 3]
    received_data, combined_data = test_reassembler.test_reassemble(serialized_frames, data_sizes)
    print("Received Data:", received_data)
    print("Combined Data:", combined_data)