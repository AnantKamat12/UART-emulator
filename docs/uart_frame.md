# UART Emulator Architecture

## 1. System Overview

The UART Emulator models asynchronous serial communication between two virtual hosts without requiring physical UART hardware.

The system separates:

1. Application behavior
2. UART protocol behavior
3. Timing
4. Channel behavior
5. Error injection
6. Verification

The primary communication path is:

```text
Host A
   │
   ▼
Segmenter
   │
   ▼
UART Frame Generator
   │
   ▼
UART Transmitter FSM
   │
   ▼
Virtual Channel
   │
   ▼
UART Receiver FSM
   │
   ▼
UART Frame Parser
   │
   ▼
Reassembler
   │
   ▼
Host B
```

---

## 2. High-Level Architecture

```text
                         UART EMULATOR

        HOST A                                      HOST B
   ┌──────────────┐                           ┌──────────────┐
   │ Application  │                           │ Application  │
   └──────┬───────┘                           └──────▲───────┘
          │                                          │
          ▼                                          │
   ┌──────────────┐                           ┌──────────────┐
   │  Segmenter   │                           │  Reassembler │
   └──────┬───────┘                           └──────▲───────┘
          │                                          │
          ▼                                          │
   ┌──────────────┐                           ┌──────────────┐
   │ UART Frame   │                           │ UART Frame   │
   │  Generator   │                           │    Parser    │
   └──────┬───────┘                           └──────▲───────┘
          │                                          │
          ▼                                          │
   ┌──────────────┐                           ┌──────────────┐
   │ UART TX FSM  │                           │ UART RX FSM  │
   └──────┬───────┘                           └──────▲───────┘
          │                                          │
          │       Timed Digital Bit Stream           │
          │                                          │
          └──────────────┐            ┌──────────────┘
                         ▼            │
                 ┌────────────────────────┐
                 │    Virtual Channel     │
                 │                        │
                 │  • Delay               │
                 │  • Bit Flip            │
                 │  • Noise               │
                 │  • Bit Loss (future)   │
                 └────────────────────────┘
```

---

## 3. Configuration

`UARTConfig` contains the parameters that define UART operation.

```text
UARTConfig
├── baud_rate
├── data_bits
├── parity
└── stop_bits
```

Example:

```text
UARTConfig
baud_rate = 9600
data_bits = 8
parity = NONE
stop_bits = 1
```

### Composition

Components use `UARTConfig` rather than inheriting from it.

```text
                    UARTConfig
                   /          \
                  ▼            ▼
              Host A         Host B
              /   \          /   \
            TX     RX       TX     RX
```

This keeps configuration separate from component behavior.

---

## 4. Host

A `Host` represents an endpoint in the UART communication system.

Conceptually:

```text
Host
├── Application Data
├── UARTConfig
├── UARTTransmitter
└── UARTReceiver
```

Host A and Host B are independent endpoints.

For the initial half-duplex implementation:

```text
Host A ───────────────► Host B
```

Full-duplex communication can later be modeled as:

```text
Host A TX ───────────► Host B RX

Host A RX ◄─────────── Host B TX
```

---

## 5. UART Frame

The frame generator converts an application byte into a UART frame.

For 8N1:

```text
START | D0 | D1 | D2 | D3 | D4 | D5 | D6 | D7 | STOP
```

The frame generator does not control transmission timing.

Its responsibility is to construct the logical frame.

```text
Byte
 │
 ▼
UARTFrame
 │
 ▼
START + DATA + PARITY + STOP
```

---

## 6. Transmitter

The transmitter is responsible for serializing the UART frame.

The TX FSM initially contains:

```text
IDLE
  ↓
START_BIT
  ↓
DATA_BITS
  ↓
PARITY_BIT
  ↓
STOP_BIT
  ↓
IDLE
```

For configurations without parity:

```text
IDLE
  ↓
START_BIT
  ↓
DATA_BITS
  ↓
STOP_BIT
  ↓
IDLE
```

The transmitter uses `UARTConfig.baud_rate` to determine the time between transmitted bits.

---

## 7. Receiver

The receiver reconstructs UART frames from the incoming bit stream.

The RX FSM initially contains:

```text
IDLE
  ↓
START_DETECTED
  ↓
DATA_BITS
  ↓
PARITY_CHECK
  ↓
STOP_BIT
  ↓
BYTE_RECEIVED
  ↓
IDLE
```

For configurations without parity:

```text
IDLE
  ↓
START_DETECTED
  ↓
DATA_BITS
  ↓
STOP_BIT
  ↓
BYTE_RECEIVED
  ↓
IDLE
```

The receiver uses its configured baud rate to determine sampling timing.

---

## 8. Virtual Channel

The Virtual Channel represents the communication medium between the UART transmitter and receiver.

It does not understand UART frame semantics.

It operates on the transmitted digital signal.

```text
TX
 │
 │ 0 / 1
 ▼
Virtual Channel
 │
 ├── Delay
 ├── Bit Flip
 └── Noise
 │
 ▼
RX
```

### Responsibilities

The channel may:

- Delay bits
- Flip bits
- Inject noise
- Drop bits in future versions

### Non-responsibilities

The channel does not:

- Generate UART frames
- Calculate parity
- Interpret start/stop bits
- Run UART FSM logic
- Determine baud rate

This separation keeps the communication medium independent from the protocol.

---

## 9. Baud Rate and Timing

Baud rate belongs to the UART configuration rather than the Virtual Channel.

```text
UARTConfig
     │
     ├── baud_rate
     │
     ▼
TX timing              RX sampling timing
```

The relationship is:

```text
Bit Period = 1 / Baud Rate
```

Example:

```text
9600 baud
≈ 104.17 µs / bit
```

The simulator may initially use logical simulation ticks instead of real wall-clock time.

Example:

```text
Tick 0 → Start Bit
Tick 1 → Data Bit 0
Tick 2 → Data Bit 1
...
```

A higher-resolution simulation clock can later be introduced for realistic baud-rate relationships.

---

## 10. Error Injection

The Virtual Channel provides controlled fault injection.

Example:

```text
Original:

1 0 1 1 0 0 1

        ↓

Channel bit flip

        ↓

1 0 0 1 0 0 1
```

The receiver should detect the resulting protocol error where applicable.

The objective is to make errors:

- Configurable
- Reproducible
- Testable

A deterministic random seed may be used during tests.

---

## 11. Data Flow

For an application message:

```text
"Hello"
```

the flow is:

```text
Application
     │
     ▼
UTF-8 Bytes
     │
     ▼
Segmenter
     │
     ▼
Individual Bytes
     │
     ▼
UART Frame Generator
     │
     ▼
Start + Data + Parity + Stop
     │
     ▼
TX FSM
     │
     ▼
Timed Bit Stream
     │
     ▼
Virtual Channel
     │
     ▼
RX FSM
     │
     ▼
UART Frame Parser
     │
     ▼
Bytes
     │
     ▼
Reassembler
     │
     ▼
"Hello"
```

---

## 12. Component Relationships

```text
                   UARTConfig
                       │
          ┌────────────┼────────────┐
          ▼            ▼            ▼
       Host A       UARTFrame    Host B
        /  \                       /  \
       ▼    ▼                     ▼    ▼
      TX    RX                   TX    RX
       │    │                     │    │
       └────┼────── Channel ──────┼────┘
            │                     │
            ▼                     ▼
         A → B                  B → A
```

The first implementation only requires:

```text
Host A → Host B
```

The reverse direction will be added when full-duplex support is implemented.

---

## 13. Project Structure

```text
UART-Emulator/
│
├── README.md
│
├── uart/
│   ├── __init__.py
│   │
│   ├── frame/
│   │   ├── __init__.py
│   │   ├── frame.py
│   │   └── parity.py
│   │
│   ├── fsm/
│   │   ├── __init__.py
│   │   ├── states.py
│   │   ├── events.py
│   │   ├── transmitter.py
│   │   └── receiver.py
│   │
│   ├── channel/
│   │   ├── __init__.py
│   │   └── virtual_channel.py
│   │
│   ├── host/
│   │   ├── __init__.py
│   │   └── host.py
│   │
│   └── core/
│       ├── __init__.py
│       └── segmenter.py
│
├── tests/
│   ├── test_frame.py
│   ├── test_parity.py
│   ├── test_transmitter.py
│   ├── test_receiver.py
│   ├── test_channel.py
│   └── test_host.py
│
├── examples/
│   └── basic_communication.py
│
└── docs/
    ├── architecture.md
    └── uart_frame.md
```

---

## 14. Design Principles

### Separation of Concerns

Each component should have one primary responsibility.

```text
Frame       → Frame representation
TX FSM      → Transmission behavior
RX FSM      → Reception behavior
Channel     → Communication medium
Config      → UART parameters
Host        → Endpoint behavior
```

### Composition Over Unnecessary Inheritance

`UARTConfig` is a configuration object.

Components use it:

```text
Host ────────► UARTConfig
Frame ───────► UARTConfig
TX ──────────► UARTConfig
RX ──────────► UARTConfig
```

They do not inherit from it.

### Protocol-Specific Design

The emulator is intentionally designed around UART rather than attempting to create one abstraction covering fundamentally different protocols such as UART, I²C, SPI, TCP, and UFS.

Future protocols should be implemented independently first. Shared abstractions should only be extracted after multiple concrete implementations reveal genuine common behavior.

---

## 15. Development Strategy

Implementation will proceed incrementally.

### V0.1 — Basic UART

```text
Host A
  ↓
UART Frame
  ↓
TX FSM
  ↓
Virtual Channel
  ↓
RX FSM
  ↓
Host B
```

Transmit one byte successfully.

### V0.2 — Multiple Bytes

Transmit strings and implement segmentation/reassembly.

### V0.3 — UART Configuration

Introduce configurable:

- Baud rate
- Data bits
- Parity
- Stop bits

### V0.4 — Error Handling

Introduce:

- Parity checking
- Framing errors
- Bit corruption

### V0.5 — Channel Simulation

Introduce:

- Configurable delay
- Bit-flip injection
- Deterministic error injection

### V0.6 — Buffering

Introduce:

- TX buffer
- RX buffer
- Overrun behavior

### V0.7 — Full Duplex

```text
Host A TX ───────► Host B RX
Host A RX ◄─────── Host B TX
```

---

## 16. Verification Strategy

Each component should have unit tests.

```text
tests/
├── test_frame.py
├── test_parity.py
├── test_transmitter.py
├── test_receiver.py
├── test_channel.py
└── test_host.py
```

Integration testing should verify:

```text
Host A
   ↓
UART TX
   ↓
Channel
   ↓
UART RX
   ↓
Host B
```

Both normal operation and injected faults should be tested.

The final end-to-end test should verify:

```text
Original Application Data
          ==
Received Application Data
```

when the communication channel is operating normally, while corrupted communication produces the expected UART error behavior.