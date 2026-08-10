# UART-Emulator

A Python-based UART protocol emulator designed to model asynchronous serial communication without requiring physical hardware.

The project focuses on understanding UART from the bit level upward: frame generation, serialization, timing, finite state machines, error injection, and verification.

**Started:** 09/08/2026  
**Target completion:** 21/08/2026

---

## 🎯 Project Goals

- Model UART communication between two virtual hosts.
- Implement UART framing from first principles.
- Simulate TX and RX behavior using finite state machines.
- Model baud-rate-dependent timing.
- Simulate communication-channel delay and bit corruption.
- Build deterministic tests for normal and erroneous communication.

---

## 📚 Learning Objectives

- UART asynchronous communication
- Start, data, parity, and stop bits
- Bit serialization and deserialization
- Baud rate and timing
- TX/RX finite state machines
- Parity and framing errors
- Buffer behavior
- Protocol-oriented software architecture
- Firmware validation concepts

---

# 🏗 Architecture

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
   │ UART Frame   │                           │ UART Receiver│
   │  Generator   │                           │     FSM      │
   └──────┬───────┘                           └──────▲───────┘
          │                                          │
          ▼                                          │
   ┌──────────────┐                           ┌──────────────┐
   │ UART TX FSM  │                           │ UART RX FSM  │
   └──────┬───────┘                           └──────▲───────┘
          │                                          │
          └──────────────┐            ┌──────────────┘
                         ▼            │
                 ┌────────────────────────┐
                 │    Virtual Channel     │
                 │                        │
                 │  • Delay               │
                 │  • Bit Flip            │
                 │  • Noise (future)      │
                 └────────────────────────┘
```

---

## ⚙️ Configuration and Composition

`UARTConfig` defines the UART operating parameters:

```text
UARTConfig
├── baud_rate
├── data_bits
├── parity
└── stop_bits
```

Components **use** the configuration rather than inheriting from it.

```text
                    UARTConfig
                   /          \
                  ▼            ▼
              Host A         Host B
              /   \          /   \
            TX     RX       TX     RX
             │     │        │     │
             └─────┘        └──────┘
```

The main components are:

- `UARTConfig` — UART operating parameters
- `UARTFrame` — represents a UART frame
- `Segmenter` — converts application data into bytes
- `UARTTransmitter` — TX state machine and serialization
- `UARTReceiver` — RX state machine and deserialization
- `VirtualChannel` — models transmission delay and corruption
- `Host` — represents a UART communication endpoint

Composition is intentionally preferred over forcing unrelated components into an inheritance hierarchy.

---

## 📁 Project Structure

```text
UART-Emulator/
│
├── README.md
├── pyproject.toml
├── requirements.txt
├── .gitignore
│
├── uart/
│   ├── __init__.py
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

Tests mirror the implementation and verify individual components as well as end-to-end communication.

---

# 🚀 Development Roadmap

### V0.1 — Basic UART

- 8 data bits
- Start bit
- Stop bit
- Single-byte transmission
- TX/RX FSM
- Host A → Host B

### V0.2 — Multiple Bytes

- String transmission
- Segmentation and reassembly
- End-to-end tests

### V0.3 — UART Configuration

- Configurable baud rate
- Data-bit configuration
- Stop-bit configuration

### V0.4 — Error Handling

- Parity generation/checking
- Framing errors
- Bit corruption

### V0.5 — Channel Simulation

- Configurable delay
- Bit-flip injection
- Deterministic error injection

### V0.6 — Buffering

- TX buffer
- RX buffer
- Overrun simulation

### V0.7 — Full Duplex

```text
Host A TX ───────► Host B RX
Host A RX ◄─────── Host B TX
```

---

## 🧪 Validation

The emulator will be validated using `pytest`.

Tests will cover:

- Frame generation
- Frame parsing
- Parity
- TX FSM
- RX FSM
- Channel behavior
- Error injection
- End-to-end Host A → Host B communication

The final objective is not merely to transmit `"Hello"` successfully, but to demonstrate how the receiver behaves when communication conditions become imperfect.

---

## 🚫 Initial Scope

The project intentionally does not initially cover:

- DMA
- RS-232 / RS-485
- Hardware flow control
- Linux UART drivers
- MCU-specific UART peripherals
- Physical voltage-level simulation

The emulator models UART behavior at the **digital protocol and timing level**, not the electrical layer.

---

## 🎯 Final Outcome

A completed UART emulator should demonstrate:

```text
Application Data
       ↓
UART Framing
       ↓
TX FSM
       ↓
Timed Bit Stream
       ↓
Virtual Channel
       ↓
RX FSM
       ↓
Frame Validation
       ↓
Application Data
```

The project is intended as a practical exercise in **firmware architecture, communication protocols, finite state machines, and software-based validation**.
