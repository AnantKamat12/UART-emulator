# UART Emulator

A Python-based emulator for asynchronous UART communication between virtual hosts without requiring physical UART hardware.

The project models UART communication from the application-data level down to individual transmitted bits, including frame construction, serialization, simulated timing, transmission through a virtual channel, reception, frame validation, and data reconstruction.

**Started:** 09/08/2026
**Version 1 completed:** 21/08/2026
**Current version:** Version 2 — In Progress

---

## Project Status

### Version 1 — Completed

Version 1 established a working end-to-end UART simulation.

The implemented communication path is:

```text
Application Data
      │
      ▼
  Segmenter
      │
      ▼
    Frame
      │
      ▼
Serialization
      │
      ▼
     TX
      │
      ▼
Virtual Channel
      │
      ▼
     RX
      │
      ▼
Deserialization
      │
      ▼
 Reassembler
      │
      ▼
Application Data
```

The current implementation successfully demonstrates transmission of application data between two virtual hosts using a shared simulation clock.

### Version 2 — In Progress

Version 2 focuses on making the existing implementation cleaner and usable through a command-line interface.

The planned work is:

1. Reorganize the project into proper packages/modules.
2. Add centralized logging.
3. Build the CLI.
4. Validate the complete system after each stage.

The detailed Version 2 work is tracked in [`Todo.md`](Todo.md).

---

# Architecture

The current implementation consists of two virtual hosts connected through a singleton virtual channel.

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
                 └──────────┐        ┌─────────┘
                            ▼        │
                      Virtual Channel
```

The simulation is driven by a shared `Clock`.

```text
                 Shared Clock
                      │
          ┌───────────┴───────────┐
          ▼                       ▼
         TX                       RX
          │                       ▲
          └── Virtual Channel ────┘
```

The clock is advanced by the simulation/test code. TX and RX only perform their work for the current simulation tick; neither component advances time independently.

---

# UART Frame

The current frame format is a fixed 16-bit frame:

```text
START | DATA | PARITY | STOP
```

```text
START  = 4 bits
DATA   = 8 bits
PARITY = 1 bit
STOP   = 3 bits
```

Therefore:

```text
4 + 8 + 1 + 3 = 16 bits
```

The default frame is:

```text
0101 | XXXXXXXX | P | 010
```

where:

* `0101` is the start sequence.
* `XXXXXXXX` is the 8-bit data field.
* `P` is the calculated parity bit.
* `010` is the stop sequence.

The serialized frame is represented as **2 bytes in big-endian order**.

---

# Implemented Components

## `Frames.py`

Contains the `Frame` and `Deserialise` classes.

### `Frame`

Responsible for:

* Accepting integer, string, byte, or byte-array input.
* Converting the input into an 8-bit data value.
* Calculating the parity bit.
* Constructing the 16-bit UART frame.
* Serializing the frame into two bytes.

### `Deserialise`

Responsible for:

* Converting the two serialized bytes back into a 16-bit frame.
* Extracting start, data, parity, and stop fields.
* Validating the frame.
* Reporting frame status.

Possible validation results are:

```text
OK
FS
PE
FE
```

where:

```text
FS = False Start
PE = Parity Error
FE = Framing Error
```

---

## `Segmenter.py`

Converts application data into segments.

The current segment size is expressed in bits.

For the current configuration:

```text
max_segment_size = 8 bits
```

which results in one data byte per segment.

For example:

```text
"ANANT"
```

becomes approximately:

```text
[b'A', b'N', b'A', b'N', b'T']
```

The segmenter therefore allows the end-to-end test to transmit a larger application message one UART frame at a time.

---

## `Reassembler.py`

Receives decoded frame data and reconstructs the application-level data.

For string data, individual received byte values are converted back into characters and stored in:

```text
rcvd_data
```

For example:

```text
A
N
A
N
T
```

can be accumulated into:

```text
ANANT
```

---

## `Transmitter.py`

The `Tx` class performs timed bit transmission.

A frame is scheduled using:

```text
start_tick
```

At each simulation tick, TX checks whether a bit should be transmitted.

The current implementation uses:

```text
100 simulation ticks = 1 UART bit at 9600 baud
```

Bits are transmitted **LSB first**.

TX does not advance the simulation clock.

---

## `Receiver.py`

The `Rx` class checks the Virtual Channel at each simulation tick.

When a bit is available:

1. The bit is read from the selected channel line.
2. The bit is inserted into the received frame.
3. The bit counter is incremented.
4. After 16 bits, the complete frame is returned.

RX does not advance the simulation clock.

Frame validation is performed subsequently through `Deserialise`.

---

## `VirtualChannel.py`

The Virtual Channel provides the simulated communication medium.

It currently maintains two independent communication lines:

```text
line 0
line 1
```

Each transmitted bit is stored together with its simulation tick:

```text
(tick, bit)
```

The receiver can retrieve a bit once its scheduled tick has been reached.

The channel therefore provides the basic timing/transport abstraction between TX and RX.

### Current scope

The current Virtual Channel does **not** yet implement:

* Bit flipping
* Packet/bit loss
* Noise
* Random corruption
* Configurable propagation delay

These are outside the current Version 2 TODO and are not documented as implemented features.

---

## `Timing.py`

Contains the singleton `Clock`.

The clock provides:

```text
current simulation tick
tick()
curr_tick()
reset()
```

The clock is shared by the hosts so that TX and RX operate against the same simulation time.

The simulation follows:

```text
current tick
     │
     ├── Host A step
     ├── Host B step
     │
     ▼
clock.tick()
```

---

## `Host.py`

`Host` represents a UART endpoint.

A host can be configured as:

```text
0 → TX only
1 → RX only
2 → TX + RX
```

For a full host:

```text
Host
├── TX
├── RX
├── Clock
├── Receive Reassembler
└── Send Reassembler
```

Host A and Host B use opposite channel lines:

```text
Host A TX → line 0
Host A RX ← line 1

Host B TX → line 1
Host B RX ← line 0
```

---

## `UARTConnection.py`

Provides a higher-level connection containing two hosts.

It creates:

```text
Host A
Host B
Shared Clock
```

and can run the simulation tick by tick.

The detailed end-to-end transmission test currently exists in `test_uart.py`.

---

# Version 1 End-to-End Test

The current test demonstrates the complete data path.

```text
"ANANT has created this"
          │
          ▼
      Segmenter
          │
          ▼
   Individual bytes
          │
          ▼
        Frame
          │
          ▼
     Serialize
          │
          ▼
      Host A TX
          │
          ▼
   Virtual Channel
          │
          ▼
      Host B RX
          │
          ▼
     Deserialize
          │
          ▼
     Reassembler
          │
          ▼
"ANANT has created this"
```

The test also verifies that the reconstructed application data matches the original message.

---

# Version 2 — TODO

Version 2 is intentionally limited to improving the existing implementation rather than expanding the protocol scope.

## 1. Project Restructuring

Move the currently scattered Python files into logical packages/modules.

Goals:

```text
Logical project structure
        │
        ├── UART components
        ├── Simulation components
        ├── Core/protocol components
        └── Tests
```

Imports must be corrected after relocation.

The existing protocol behavior should remain unchanged.

---

## 2. Centralized Logging

Replace scattered `print()` statements with a Logger module.

The simulation should produce:

```text
host_a.log
host_b.log
simulation.log
```

Logs should contain information such as:

```text
[tick=100] [HOST_A] TX bit=0
[tick=100] [HOST_B] RX bit=0
```

The combined simulation log should make it possible to reconstruct the interaction between the hosts.

Diagnostic logging should remain separate from user-facing CLI output.

---

## 3. Command-Line Interface

The CLI will allow the user to:

* Select Host A or Host B as the transmitting host.
* Select the data type.
* Enter the data.
* Validate the input.
* Trim data if it exceeds the current frame capacity.
* Transmit exactly **one frame per CLI transmission**.

The CLI path will be:

```text
User Input
    │
    ▼
Frame
    │
    ▼
Serialization
    │
    ▼
TX
    │
    ▼
Virtual Channel
    │
    ▼
RX
    │
    ▼
Deserialization
    │
    ▼
Reassembler
    │
    ▼
Result
```

Multi-packet segmentation through the CLI is **not part of Version 2**.

---

# Version 2 Validation

Each stage will be validated independently.

### After restructuring

Run the existing end-to-end test and verify that protocol behavior remains unchanged.

### After logging

Verify:

```text
host_a.log
host_b.log
simulation.log
```

and confirm that the communication can be reconstructed from the logs.

### After CLI

Perform a complete user-driven transmission and verify:

```text
Transmitted data
Received data
Success / Failure
```

---

# Project Direction

The project is being developed incrementally.

```text
Version 1
   │
   ├── Frame
   ├── Serialization
   ├── Timing
   ├── TX
   ├── Virtual Channel
   ├── RX
   ├── Deserialization
   ├── Segmentation
   └── Reassembly
          │
          ▼
Version 2
   │
   ├── Project restructuring
   ├── Logging
   ├── CLI
   └── Validation
```

The immediate objective is **not** to add more protocol features.

The objective is to turn the existing working simulation into a clean, organized, testable, CLI-driven UART emulator.
