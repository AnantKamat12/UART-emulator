import sys
from pathlib import Path
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from uart_emulator.infrastructure.All_APIs_for_custom_tests import (
	build_frame,
	decode_frame,
)


class TestReassemblerStatuses(unittest.TestCase):
	"""Verify valid and corrupted frames through the public test API."""

	def test_ok_status_decodes_data(self):
		frame = build_frame("A", data_size=1)

		result = decode_frame(
			frame,
			data_type=1,
			data_size=1,
			non_ideal=True,
		)

		self.assertEqual(result, "A")

	def test_pe_status_is_reported(self):
		frame = bytearray(build_frame("A", data_size=1))
		frame_value = int.from_bytes(frame, byteorder="big") ^ (1 << 3)
		corrupted_frame = frame_value.to_bytes(2, byteorder="big")

		result = decode_frame(
			corrupted_frame,
			data_type=1,
			data_size=1,
			non_ideal=True,
		)

		self.assertEqual(result, "Corrupted Frame due to PE,data lost")

	def test_fe_status_is_reported(self):
		frame = bytearray(build_frame("A", data_size=1))
		frame_value = int.from_bytes(frame, byteorder="big") ^ 0b001
		corrupted_frame = frame_value.to_bytes(2, byteorder="big")

		result = decode_frame(
			corrupted_frame,
			data_type=1,
			data_size=1,
			non_ideal=True,
		)

		self.assertEqual(result, "Corrupted Frame due to FE,data lost")

	def test_all_zero_and_all_one_integer_round_trips(self):
		for data_size in (1, 2, 3):
			all_one_payload = (1 << (data_size * 8)) - 1

			for payload in (0, all_one_payload):
				frame = build_frame(payload, data_size=data_size)
				received = decode_frame(
					frame,
					data_type=0,
					data_size=data_size,
				)

				self.assertEqual(received, payload)


if __name__ == "__main__":
	unittest.main()
