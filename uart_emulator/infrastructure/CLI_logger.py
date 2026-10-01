from uart_emulator.infrastructure.Logger import UART_LOG_DIR, logger


class CLI_logger(logger):
	"""Logger used by CLI-created hosts, with an explicit CLI marker."""
	simulation_label = "CLI"

	def __init__(self, log_id, hostname, start_tick, host_type, logger_name=None):
		super().__init__(log_id, hostname, start_tick, host_type, logger_name)
		self.file.write("Logger type : CLI logger\n\n")
		self.file.flush()

	@classmethod
	def mark_simulation_log(cls):
		"""Append a clear CLI-session marker to the shared simulation log."""
		UART_LOG_DIR.mkdir(parents=True, exist_ok=True)
		with open(UART_LOG_DIR / "simulation.log", "w", encoding="utf-8") as file:
			file.write("\n========== CLI LOGGER SESSION ==========\n")
			file.flush()
