import sys
from collections import deque
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from uart_emulator.infrastructure.All_APIs_for_custom_tests import *
Simulation_time= 10**6
Full_duplex_json={
	"simulation_time": Simulation_time,
	"transmissions": [
		{"sender": "HOST_A", "receiver": "HOST_B", "message": "Hi", "start_tick": 100},
		{"sender": "HOST_B", "receiver": "HOST_A", "message": "Hello", "start_tick": 3000},
		{"sender": "HOST_A", "receiver": "HOST_B", "message": "Hello", "start_tick": 4000},
		{"sender": "HOST_B", "receiver": "HOST_A", "message": "Hi", "start_tick": 6000},
		{"sender": "HOST_A", "receiver": "HOST_B", "message": "A3", "start_tick": 8000},
		{"sender": "HOST_B", "receiver": "HOST_A", "message": "B3", "start_tick": 10000},
		{"sender": "HOST_A", "receiver": "HOST_B", "message": "A4", "start_tick": 25000},
	],
}

class FullDuplexTest:
	"""Run a configurable full-duplex UART simulation."""

	def __init__(
		self,
		rcvd_json=None,
		baud_rate=9600,
		is_ideal=True,
		bit_flip_rate=0.0,
	):
		self.rcvd_json = Full_duplex_json if rcvd_json is None else rcvd_json
		self.baud_rate = baud_rate
		self.is_ideal = is_ideal
		self.bit_flip_rate = bit_flip_rate
		self.host_a = None
		self.host_b = None
		self.clock = None
		self.vc = None

	def run(self):
		"""Run the configured schedule and return received-data results."""
		self.host_a, self.host_b, self.clock, self.vc = Create_duplex_hosts(
			is_ideal=self.is_ideal,
			bit_flip_rate=self.bit_flip_rate,
			baud_rate=self.baud_rate,
		)
		hosts = {
			"HOST_A": self.host_a,
			"HOST_B": self.host_b,
		}

		pending_segments = {
			"HOST_A": deque(),
			"HOST_B": deque(),
		}

		for current_tick in range(self.rcvd_json["simulation_time"]):
			starting_transmissions = [
				transmission
				for transmission in self.rcvd_json["transmissions"]
				if transmission["start_tick"] == current_tick
			]

			if not starting_transmissions:
				noop()

			for transmission in starting_transmissions:
				segments = get_segmented_data(
					transmission["message"],
					max_segment_size=8,
				)
				pending_segments[transmission["sender"]].extend(segments)

			for hostname, sender in hosts.items():
				if sender.tx.active or not pending_segments[hostname]:
					continue #if frame transmission is active or no pending segments then skip start_send().

				segment = pending_segments[hostname].popleft()
				frame = Frame(data=segment, data_size=1)
				frame_value = int.from_bytes(frame.serialise(), byteorder="big")
				sender.start_send(
					frame=frame_value,
					start_tick=current_tick,
					line=sender.host_transmit_lane,
				)

			self.host_a.step()
			self.host_b.step()
			self.clock.tick()

		results = {
			"host_a_separate": self.host_a.get_rcvd_data(),
			"host_b_separate": self.host_b.get_rcvd_data(),
			"host_a_joined": self.host_a.get_joined_rcvd_data(),
			"host_b_joined": self.host_b.get_joined_rcvd_data(),
		}
		log_received_data(
			self.host_a,
			results["host_a_separate"],
			results["host_a_joined"],
			self.clock.curr_tick(),
		)
		log_received_data(
			self.host_b,
			results["host_b_separate"],
			results["host_b_joined"],
			self.clock.curr_tick(),
		)
		close_hosts(self.host_a, self.host_b)
		return results


if __name__ == "__main__":
	results = FullDuplexTest().run()
	print(f"Host A received data (separate): {results['host_a_separate']}")
	print(f"Host B received data (separate): {results['host_b_separate']}")
	print(f"Host A received data: {results['host_a_joined']}")
	print(f"Host B received data: {results['host_b_joined']}")

