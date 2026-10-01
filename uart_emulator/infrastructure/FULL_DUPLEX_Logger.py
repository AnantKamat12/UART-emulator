from uart_emulator.infrastructure.Logger import UART_LOG_DIR, logger


class FULL_DUPLEX_Logger(logger):
	"""Logger for full-duplex tests, distinct from regular and CLI logs."""
	simulation_label = "FULL-DUPLEX TEST"

	def __init__(self, log_id, hostname, start_tick, host_type, logger_name=None):
		super().__init__(log_id, hostname, start_tick, host_type, logger_name)
		self.file.write("Logger type : Full-duplex test logger\n\n")
		self.file.flush()

	@classmethod
	def mark_simulation_log(cls):
		"""Add a full-duplex test header to the shared simulation log."""
		UART_LOG_DIR.mkdir(parents=True, exist_ok=True)
		with open(UART_LOG_DIR / "simulation.log", "w", encoding="utf-8") as file:
			file.write("\n========== FULL-DUPLEX TEST LOGGER SESSION ==========\n")
			file.flush()
