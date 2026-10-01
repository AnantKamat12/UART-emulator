from uart_emulator.infrastructure.Logger import UART_LOG_DIR, logger


class ACK_NCK_logger(logger):
	"""Logger for ACK/NACK tests, marked separately from normal and CLI logs."""
	simulation_label = "ACK/NACK TEST"

	def __init__(self, log_id, hostname, start_tick, host_type, logger_name=None):
		super().__init__(log_id, hostname, start_tick, host_type, logger_name)
		self.file.write("Logger type : ACK/NACK test logger\n\n")
		self.file.flush()

	@classmethod
	def mark_simulation_log(cls):
		"""Add an identifying header to the shared simulation log."""
		UART_LOG_DIR.mkdir(parents=True, exist_ok=True)
		with open(UART_LOG_DIR / "simulation.log", "w", encoding="utf-8") as file:
			file.write("\n========== ACK/NACK TEST LOGGER SESSION ==========\n")
			file.flush()
