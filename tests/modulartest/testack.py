from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from uart_emulator.protocol.ACK import ACK
from uart_emulator.protocol.Frames import Deserialise, Frame


class TestAckNack(unittest.TestCase):
    def test_ack_frame_round_trip(self):
        frame = Frame.gen_ack_nack_frame(ack_nck=0)
        status, data = Deserialise().decode_frame(frame.serialise())

        self.assertEqual(status, "OK")
        self.assertEqual(data, ACK.ACK.value)

    def test_nack_frame_round_trip(self):
        frame = Frame.gen_ack_nack_frame(ack_nck=1)
        status, data = Deserialise().decode_frame(frame.serialise())

        self.assertEqual(status, "OK")
        self.assertEqual(data, ACK.NACK.value)

    def test_ack_factory_rejects_invalid_value(self):
        with self.assertRaises(ValueError):
            Frame.gen_ack_nack_frame(ack_nck=2)


def test_ack_factory_rejects_invalid_value():
    try:
        Frame.gen_ack_nack_frame(ack_nck=2)
    except ValueError:
        return

    raise AssertionError("Expected invalid ACK/NACK value to raise ValueError")


if __name__ == "__main__":
    unittest.main()
