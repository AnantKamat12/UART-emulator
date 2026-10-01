from contextlib import redirect_stdout
import io
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from uart_emulator.infrastructure.All_APIs_for_custom_tests import (
    Create_duplex_hosts,
    close_hosts,
    transmit_one_frame,
)


class TestLiveFrameWidths(unittest.TestCase):
    def transmit_and_decode(self, payload, data_type, data_size, max_ticks=5000):
        host_a, host_b, _, _ = Create_duplex_hosts(
            data_type=data_type,
            data_size=data_size,
        )
        try:
            with redirect_stdout(io.StringIO()):
                return transmit_one_frame(
                    host_a,
                    host_b,
                    payload,
                    data_type=data_type,
                    data_size=data_size,
                    start_tick=100,
                    max_ticks=max_ticks,
                )
        finally:
            close_hosts(host_a, host_b)

    def test_integer_frames_at_all_widths(self):
        values = {1: 0x41, 2: 0x4142, 3: 0x414243}
        for data_size, value in values.items():
            with self.subTest(data_size=data_size):
                result = self.transmit_and_decode(value, 0, data_size)
                self.assertTrue(result["success"], result)
                self.assertEqual(result["received_data"], value)

    def test_zero_and_maximum_integer_frames_at_all_widths(self):
        for data_size in (1, 2, 3):
            maximum = (1 << (data_size * 8)) - 1
            for value in (0, maximum):
                with self.subTest(data_size=data_size, value=value):
                    result = self.transmit_and_decode(value, 0, data_size)
                    self.assertTrue(result["success"], result)
                    self.assertEqual(result["received_data"], value)

    def test_string_frames_at_all_widths(self):
        values = {1: "A", 2: "AB", 3: "ABC"}
        for data_size, value in values.items():
            with self.subTest(data_size=data_size):
                result = self.transmit_and_decode(value, 1, data_size)
                self.assertTrue(result["success"], result)
                self.assertEqual(result["received_data"], value)

    def test_incomplete_frame_times_out_as_failure(self):
        result = self.transmit_and_decode(
            0x41,
            data_type=0,
            data_size=1,
            max_ticks=200,
        )

        self.assertFalse(result["success"], result)
        self.assertIsNone(result["received_frame"])

    def test_byte_frames_at_all_widths(self):
        values = {
            1: b"A",
            2: b"AB",
            3: b"ABC",
        }
        for data_size, value in values.items():
            with self.subTest(data_size=data_size):
                result = self.transmit_and_decode(value, 2, data_size)
                self.assertTrue(result["success"], result)
                self.assertEqual(result["received_data"], value)


if __name__ == "__main__":
    unittest.main()
