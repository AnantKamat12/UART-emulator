# UART Emulator

A Python-based emulator for asynchronous UART communication between virtual hosts without physical UART hardware.

The project models communication from application data down to individual transmitted bits: frame construction, serialization, parity validation, simulated timing, virtual transport, reception, reassembly, logging, and noisy-channel experiments.

**Started:** 09/08/2026
**Version 1 completed:** 21/08/2026
**Current version:** Version 2 — Core simulation complete

---

## Project Status

**Version 2 core is complete.** Configurable 8-, 16-, and 24-bit payload widths are supported end-to-end through frame serialization, TX, the virtual channel, RX, and reassembly. The project includes a menu-driven CLI, reusable test APIs, host/session-specific logs, modular tests, full-duplex tests, and a dedicated ACK/NACK retransmission experiment.

The completion checklist is in [`Todo.md`](Todo.md). Known boundaries—such as baud-rate-dependent bit timing and generic ACK/NACK integration into every host transfer—are listed near the end of this README.

---

## Package Structure

```text
UART-emulator/
├── uart_emulator/
│   ├── infrastructure/
│   │   ├── ACK_NCK_logger.py
│   │   ├── All_APIs_for_custom_tests.py
│   │   ├── CLI_logger.py
│   │   ├── FULL_DUPLEX_Logger.py
│   │   └── Logger.py
│   ├── protocol/
│   │   ├── ACK.py
│   │   ├── Feedback.py
│   │   ├── FSM.py
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
│   ├── ACK_NCK_test.py
│   ├── Full_Duplex_test.py
│   ├── primitive_test.py
│   └── modulartest/
│       ├── runallunittest.py
│       ├── testliveframewidths.py
│       └── ...
├── mainCLI.py
├── docs/
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

The frame factory is tested independently. `tests/ACK_NCK_test.py` also exercises feedback, FSM transitions, and retransmission over a noisy channel. This is a dedicated test flow; ACK/NACK is not automatically enabled in every generic CLI or `Host` transmission.

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

TX sends `data_size * 8 + 8` bits per frame, and RX collects the same configured width. The host factory accepts `data_size=1`, `2`, or `3` and passes it to both endpoints.

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

Host logs contain each host's local activity. The shared simulation log contains combined activity. CLI, ACK/NACK, and full-duplex runs have distinct labels in the shared log; each run starts a fresh simulation log. Log files are written under the workspace's `UARTlogs/` directory, regardless of the current working directory.

Example:

```text
[tick=100] [HOST_A] TX bit=0
[tick=100] [HOST_B] RX bit=0
```

---

## Setup

From the project root, create and activate a virtual environment and install the project dependency:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

## CLI Usage

Run the menu from the project root:

```powershell
python mainCLI.py
```

Choose:

- `0` — run the complete modular unit-test suite.
- `1` — configure and run a UART transmission.

The transmission prompts ask for host (`A`/`B`), type (`string`/`integer`/`bytes`), data width (1/2/3 bytes), and the payload. Invalid answers are rejected at the current prompt and requested again.

The selected width is the **maximum payload bytes in one frame**, not a required input length. Longer strings and byte sequences are split across successive frames. The 8-/16-/24-bit payload fields create total frame lengths of 16/24/32 bits respectively.

### Payload examples

| Type    | Example input     | Meaning                                                                                                                  |
| ------- | ----------------- | ------------------------------------------------------------------------------------------------------------------------ |
| String  | `ab`              | Two ASCII characters. At width 2, they fit in one frame.                                                                 |
| Integer | `4660` at width 2 | One decimal integer, encoded as `0x1234`. Integers range from 0 to $2^{8w}-1$, where $w$ is the selected width in bytes. |
| Bytes   | `41 42`           | Hexadecimal bytes `0x41 0x42`, which are ASCII `AB`.                                                                     |
| Bytes   | `AB`              | One byte, `0xAB`; it is not the two-character text `AB`.                                                                 |

Direct invocation is also supported; when command-line arguments are supplied, the menu is skipped:

```powershell
python mainCLI.py --host B --data-type string --data-size 2 --data ab
python mainCLI.py --host A --data-type integer --data-size 2 --data 4660
python mainCLI.py --host B --data-type bytes --data-size 2 --data "41 42"
```

The result reports transmitted data, number of received frames, reassembled data, simulation ticks, and success/failure. In a final partial bytes frame, the data field is zero-padded for transmission and the CLI removes that padding from the returned payload.

## Test Commands

Run commands from the workspace root:

```powershell
python tests/modulartest/runallunittest.py
python tests/ACK_NCK_test.py
python tests/Full_Duplex_test.py
python tests/primitive_test.py
```

The modular suite includes frame serialization/deserialization, all data widths and types, live TX/channel/RX width checks, logger behavior, timing, host setup, edge cases, and virtual-channel tests. The separate ACK/NACK test exercises noisy-channel feedback and retransmission; the full-duplex test exercises simultaneous bidirectional traffic.

## Known Scope Boundaries

- TX/RX currently use a fixed 100 simulation ticks per bit. The `--baud-rate` argument is accepted, but does not yet change TX/RX bit spacing.
- ACK/NACK retransmission is implemented and tested in the dedicated ACK/NACK flow; ordinary CLI sends do not automatically request feedback or retry.
- Plotting and a graphical/web interface are optional extensions, not required to run or test the UART core.

See [`Todo.md`](Todo.md) for the completed Version 2 checklist and scope notes.
