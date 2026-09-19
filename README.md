# UART Emulator

A Python-based emulator for asynchronous UART communication between virtual hosts without physical UART hardware.

The project models communication from application data down to individual transmitted bits: frame construction, serialization, parity validation, simulated timing, virtual transport, reception, reassembly, logging, and noisy-channel experiments.

**Started:** 09/08/2026
**Version 1 completed:** 21/08/2026
**Current version:** Version 2 — Core simulation complete

---

## Project Status

The original end-to-end UART path is working. Version 2 is improving the organization, observability, configurability, and usability of the simulation.

### Completed

- Reorganized the project into Python packages.
- Corrected imports after relocation.
- Added host-specific and combined simulation logs.
- Added protocol-layer frame data sizes of 8, 16, and 24 bits.
- Added ACK/NACK frame generation through `Frame.gen_ack_nack_frame()`.
- Added optional random bit flipping to `VirtualChannel`.
- Added primitive, logger, noisy-channel, edge-case, and full-duplex tests.
- Added an interactive CLI for one-byte transmissions.

### Remaining protocol work

- Make the selected frame width consistent through TX and RX.
- Add complete ACK/NACK response and retransmission behavior.
- Expand error handling and edge-case coverage.
- Finish documentation and naming cleanup.

The detailed task list is in [`Todo.md`](Todo.md).

---

## Package Structure

```text
UART-emulator/
├── uart_emulator/
│   ├── infrastructure/
│   │   └── Logger.py
│   ├── protocol/
│   │   ├── ACK.py
│   │   ├── Frames.py
│   │   ├── Reassembler.py
│   │   └── Segmenter.py
│   ├── simulation/
│   │   ├── Timing.py
│   │   ├── VirtualChannel.py
│   │   └── Waveframe.py
│   └── uart/
│       ├── Host.py
│       ├── Receiver.py
│       ├── Transmitter.py
│       └── UARTConnection.py
├── tests/
│   ├── primitive_test.py
│   └── modulartest/
│       ├── noisychanneltest.py
│       └── testlogger.py
├── mainCLI.py
├── Todo.md
└── README.md
```

Use package-qualified imports:

```python
from uart_emulator.protocol.Frames import Frame
from uart_emulator.simulation.VirtualChannel import VirtualChannel
```

---

## Architecture

Two virtual hosts communicate through a shared two-line channel and a singleton simulation clock.

```text
                         UART EMULATOR

              HOST A                         HOST B
          ┌─────────────┐                ┌─────────────┐
          │ Application │                │ Application │
          └──────┬──────┘                └──────▲──────┘
                 │                              │
                 ▼                              │
            Segmenter                      Reassembler
                 │                              ▲
                 ▼                              │
              Frame                            │
                 │                              │
                 ▼                              │
           Serialization                       │
                 │                              │
                 ▼                              │
                TX                              RX
                 │                              ▲
                 └──────────┐ --------┌─────────┘
                            ▼
                      Virtual Channel
```

The simulation loop is controlled by the test or connection layer:

```text
current tick
     │
     ├── Host A step
     ├── Host B step
     │
     ▼
clock.tick()
```

TX and RX operate at the current tick but do not advance the clock themselves. Host A transmits on line 0 and receives on line 1. Host B transmits on line 1 and receives on line 0.

---

## Frame Format

The protocol uses this general structure:

```text
START | DATA | PARITY | STOP
```

```text
START  = 4 bits
DATA   = 8, 16, or 24 bits
PARITY = 1 bit
STOP   = 3 bits
```

`data_size` is expressed in bytes:

| Data width | `data_size` | Serialized frame size |
| ---------: | ----------: | --------------------: |
|     8 bits |           1 |               2 bytes |
|    16 bits |           2 |               3 bytes |
|    24 bits |           3 |               4 bytes |

For example:

```python
frame = Frame(data="AB", data_size=2)
```

`frame.data` is an integer containing `0x4142`. Input bytes are interpreted in big-endian order. Serialization converts the complete frame into bytes; deserialization converts those bytes back into an integer and validates the fields.

Default values:

```text
START  = 0101
PARITY = even
STOP   = 010
```

Validation statuses:

```text
OK = valid frame
FS = false start
PE = parity error
FE = framing error
```

---

## Implemented Components

### Protocol

#### `Frames.py`

Provides `Frame` and `Deserialise`.

- Accepts integers, strings, bytes, and bytearrays.
- Encodes data as a big-endian integer.
- Supports 8-, 16-, and 24-bit data widths at the frame layer.
- Calculates even or odd parity.
- Serializes and deserializes variable-size frames.
- Provides `Frame.gen_ack_nack_frame()` for ACK and NACK control frames.

#### `ACK.py`

Defines the current control values:

```python
ACK.ACK.value   # 0b0001
ACK.NACK.value  # 0b0010
```

The frame factory is implemented and tested independently. Receiver-driven ACK/NACK responses and retransmission are still planned work.

#### `Segmenter.py`

Splits application data into byte segments. The existing end-to-end tests use it to transmit longer messages one frame at a time.

#### `Reassembler.py`

Converts decoded raw values into integers, characters, or bytes and accumulates received application data. It can report a corrupted frame in non-ideal-channel mode.

### Simulation

#### `Timing.py`

Provides the singleton `Clock`, including the current tick, tick advancement, reset, and ticks-per-bit calculation.

#### `VirtualChannel.py`

Maintains two independent communication lines. Each queued item contains a simulation tick and a bit:

```text
(tick, bit)
```

The channel supports ideal mode and optional random bit flipping:

```python
vc = VirtualChannel(is_ideal=False, bit_flip_rate=0.5)
```

Because it is a Singleton, tests must deliberately reset or configure the shared instance when switching channel modes.

#### `Waveframe.py`

Provides a square-wave view of the simulation clock. It is a foundation for optional waveform visualization and timing analysis.

### UART

#### `Transmitter.py` and `Receiver.py`

TX schedules and sends frame bits at bit boundaries. RX collects bits from the selected channel line and returns a complete received frame.

The current TX/RX path still contains fixed-width assumptions from the original 16-bit flow. Making the selected 8/16/24-bit width fully dynamic through this path is tracked in [`Todo.md`](Todo.md).

#### `Host.py`

Represents a TX-only, RX-only, or duplex UART endpoint:

```text
0 → TX only
1 → RX only
2 → TX + RX
```

Each host owns a logger, transmitter, receiver, clock reference, and reassemblers.

#### `UARTConnection.py`

Creates two duplex hosts on opposite channel lines and provides a tick-by-tick simulation runner.

---

## Logging

Core UART modules write host events through the centralized logger. A run produces:

```text
UARTlogs/
├── host_a.log
├── host_b.log
└── simulation.log
```

Host logs contain each host's local activity. The shared simulation log contains combined chronological activity and is also printed to the terminal through `logger.logprint()`.

Example:

```text
[tick=100] [HOST_A] TX bit=0
[tick=100] [HOST_B] RX bit=0
```

---

## Tests

```text
tests/
├── primitive_test.py
└── modulartest/
    ├── noisychanneltest.py
    └── testlogger.py
```

The primitive test verifies:

```text
Application Data → Segmenter → Frame → Serialization → TX
→ Virtual Channel → RX → Deserialization → Reassembler
→ Received Application Data
```

The modular tests exercise logger behavior and ideal/noisy virtual-channel behavior. `tests/ACK_NCK.py` demonstrates NACK feedback followed by retransmission and successful decoding; automatic receiver-driven retransmission remains future protocol work.

---

## Setup and Usage

Run the interactive CLI from the project root:

```text
python mainCLI.py
```

Or provide options directly:

```text
python mainCLI.py --host A --data Z --data-type string --data-size 1
```

The current live TX/RX path supports one-byte CLI frames. The emulator still contains protocol-level 8/16/24-bit frame support, but multi-byte live transport remains planned work.

For the test suite:

- Cloning the repository.
- Creating and activating a Python virtual environment.
- Installing dependencies.
- Running primitive and modular tests.
- Running the CLI.
- Inspecting generated logs.
- Configuring ideal and noisy channel simulations.

For now, run commands from the project root so the `uart_emulator` package can be resolved correctly. Package-aware execution is preferred for tests and modules.

---

## Remaining Work

The remaining Version 2 work is tracked in [`Todo.md`](Todo.md):

1. Make selected frame width consistent through live TX and RX.
2. Integrate automatic ACK/NACK response and retransmission.
3. Add FS, timeout, and complete edge-case coverage.
4. Finish documentation and naming cleanup.

Waveform visualization and a Flask web interface are optional future enhancements. They are not required for the core UART emulator to be complete.

---

## Project Direction

The goal is a clear, testable UART simulation with a usable command-line interface, not a dependency on a graphical interface.

```text
Working UART Core
       │
       ├── Package organization
       ├── Configurable frame protocol
       ├── Logging
       ├── Noisy-channel experiments
       ├── CLI
       └── Tests
```
