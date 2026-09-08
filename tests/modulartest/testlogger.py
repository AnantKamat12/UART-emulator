import sys
from pathlib import Path
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from uart_emulator.infrastructure.Logger import HostType, logger


class TestLogger(unittest.TestCase):
	def test_logger_writes_and_closes(self):
		log = logger(3, "rxhost", 0, HostType.RxHost)
		log.write("anant", 2)
		log.write("abcd")
		log.close()

		self.assertTrue(log.file.closed)


if __name__ == "__main__":
	unittest.main()