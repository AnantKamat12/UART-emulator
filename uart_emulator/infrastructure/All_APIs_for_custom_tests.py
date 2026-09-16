from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
	sys.path.insert(0, str(ROOT))

from uart_emulator.protocol.ACK import ACK
from uart_emulator.protocol.Frames import Deserialise, Frame
from uart_emulator.protocol.Reassembler import Reassembler
from uart_emulator.simulation.Timing import Clock
from uart_emulator.simulation.VirtualChannel import VirtualChannel
from uart_emulator.uart.Host import Host
import numpy as np

def get_bit_stream(size=8):
	
	"""return a random bit stream of the given size as a list of 0s and 1s"""
	arr=np.random.randint(0, 2, size=size).tolist()
	return arr
def get_random_integer(start,end,size):
	"""return random integers in given range as a list of integers"""	
	return np.random.randint(start, end, size=size).tolist()
def get_random_bytes(size):
    """return random bytes of the given size as a list of bytes"""
    arr=np.random.randint(0, 256, size=size).tolist()
    return arr
def get_random_string(strings=None, size=1):
	"""Return random strings from the provided list or a built-in default list."""
	if strings is None or len(strings) == 0:
		strings = [
			"Anant-Kamat",
			"Loves",
			"Dante-wrote-divine-comedy",
			"UART",
			"Emulator",
		]
	return np.random.choice(strings, size=size).tolist()


def reset_simulation():
	"""Reset the singleton clock and virtual channel for a fresh test."""
	Clock._instance = None
	if hasattr(Clock, "_initialized"):
		del Clock._initialized

	VirtualChannel._instance = None
	if hasattr(VirtualChannel, "_initialized"):
		del VirtualChannel._initialized


def create_duplex_hosts(
	baud_rate=9600,
	data_type=1,
	is_ideal=True,
	bit_flip_rate=0.0,
):
	"""Create two connected hosts and return ``(host_a, host_b, clock)``."""
	reset_simulation()
	VirtualChannel(
		is_ideal=is_ideal,
		bit_flip_rate=bit_flip_rate,
		baud_rate=baud_rate,
	)

	host_a = Host(
		host_type=2,
		baud_rate=baud_rate,
		data_type=data_type,
		host_transmit_lane=0,
		hostname="HOST_A",
	)
	host_b = Host(
		host_type=2,
		baud_rate=baud_rate,
		data_type=data_type,
		host_transmit_lane=1,
		hostname="HOST_B",
	)
	host_a.setuphost()
	host_b.setuphost()
	return host_a, host_b, host_a.clk


def build_frame(data, data_size=1, parity=0):
	"""Build and serialize one frame for custom tests or the CLI."""
	return Frame(data=data, data_size=data_size, parity=parity).serialise()


def decode_frame(frame_bytes, data_type=1, data_size=1, non_ideal=False):
	"""Decode one serialized frame and return the application data."""
	return Reassembler(data_type=data_type).decode(
		frame_bytes,
		data_size=data_size,
		non_ideal_vc=non_ideal,
	)


def get_ack_nack_from_frame(ack_nck=0, data_size=1, status="PE"):
	"""Generate feedback for a frame status.

	``status="OK"`` returns no feedback. Any other status returns the
	requested ACK/NACK frame, where ``ack_nck=0`` is ACK and ``1`` is NACK.
	"""
	if status == "OK":
		return None

	return Frame.gen_ack_nack_frame(
		ack_nck=ack_nck,
		data_size=data_size,
	)


def transmit_one_frame(
	sender,
	receiver,
	data,
	data_type=1,
	data_size=1,
	start_tick=100,
	max_ticks=5000,
):
	"""Transmit one frame and return its received and decoded values.

	The returned dictionary is intentionally simple for assertions and CLI
	output. The current ``Tx`` implementation transmits 16 bits per frame.
	"""
	frame_bytes = build_frame(data, data_size=data_size)
	frame_value = int.from_bytes(frame_bytes, byteorder="big")
	sender.start_send(
		frame=frame_value,
		start_tick=start_tick,
		line=sender.host_transmit_lane,
	)

	clock = sender.clk
	received_frame = None
	while received_frame is None and clock.curr_tick() < max_ticks:
		tick = clock.curr_tick()
		sender.tx.step(tick)
		received_frame = receiver.rx.step(tick, receiver.host_receive_lane)
		clock.tick()

	result = {
		"sent_data": data,
		"frame_bytes": frame_bytes,
		"received_frame": received_frame,
		"received_data": None,
		"start_tick": start_tick,
		"end_tick": clock.curr_tick(),
		"success": False,
	}

	if received_frame is not None:
		received_bytes = received_frame.to_bytes(
			data_size + 1,
			byteorder="big",
		)
		result["received_data"] = decode_frame(
			received_bytes,
			data_type=data_type,
			data_size=data_size,
		)
		result["success"] = result["received_data"] is not None

	return result


def close_hosts(*hosts):
	"""Close host loggers after a custom test or CLI run."""
	for host in hosts:
		host.logger.close()
if __name__ == "__main__":
        
        
        str=get_random_string(strings=None)
        print(f"Random string: {str}")
        print(get_bit_stream(size=10))

