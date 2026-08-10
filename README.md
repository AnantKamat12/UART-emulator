````markdown
# UART-Emulator

A modular UART protocol simulator built in Python to model asynchronous serial communication without requiring physical hardware.

The goal of this project is to understand how UART communication works internally by building every component from first principles—including framing, transmission, reception, finite state machines, timing, and error injection.

Rather than interacting with a real UART peripheral, this emulator focuses on accurately modeling UART behavior in software, making it suitable for learning embedded systems, firmware architecture, and communication protocol design.

---
#Started 9/8/2026
#Deadline 21/8/2026

# 🎯 Project Goals

- Build a complete UART communication simulator entirely in Python.
- Understand UART protocol from the bit level rather than using existing libraries.
- Model realistic communication between two virtual hosts.
- Implement sender and receiver finite state machines.
- Simulate timing, latency, and communication errors.
- Build reusable protocol infrastructure that can later support other communication protocols.

---

# 📚 Learning Objectives

This project focuses on understanding:

- UART asynchronous communication
- TX and RX communication
- UART frame generation
- Bit serialization
- Receiver synchronization
- Baud rate and timing
- Error detection
- Finite State Machines (FSM)
- Software architecture for communication protocols

---

# 🛠 Technology Stack

- Python 3.x
- Object-Oriented Programming
- Finite State Machines
- Binary Data Manipulation
- Git & GitHub
- Pytest (future)

---

# 🏗 Planned Architecture

```text
Application

        │

        ▼

UART Driver

        │

        ▼

UART Transmitter FSM

        │

        ▼

UART Frame Generator

        │

        ▼

Virtual Wire / Channel

        │

        ▼

UART Receiver FSM

        │

        ▼

Application
```

The communication channel will later support configurable delay, corruption, and transmission errors to emulate real-world communication.

---

# 🚀 Development Roadmap

## Phase 1 — Learn UART

Before writing code, understand the protocol completely.

Topics:

- UART asynchronous communication
- TX/RX lines
- Idle line
- Start bit
- Data bits
- Parity
- Stop bit
- Baud rate
- UART timing
- Framing errors
- Parity errors
- Overrun errors
- Basic UART registers

---

## Phase 2 — Design

Design the software architecture before implementation.

Planned components:

- UARTFrame
- UARTHost
- UARTDriver
- UARTChannel
- UARTTransmitterFSM
- UARTReceiverFSM

---

## Phase 3 — Implementation

### Version 1

Transmit a single byte.

```text
'A'

↓

UART Frame

↓

Virtual Wire

↓

Receiver

↓

'A'
```

---

### Version 2

Transmit complete strings.

---

### Version 3

Introduce baud-rate simulation.

---

### Version 4

Add parity generation and checking.

---

### Version 5

Simulate framing errors.

---

### Version 6

Introduce communication noise and corruption.

---

### Version 7

Implement receive/transmit buffers.

---

### Version 8

Simulate UART interrupts.

---

# 🔧 Planned Features

- UART Frame generation
- UART Frame parsing
- Sender FSM
- Receiver FSM
- Virtual communication channel
- Configurable baud rate
- Delay simulation
- Noise injection
- Framing error simulation
- Parity error simulation
- Buffer simulation
- Logging
- Unit tests

---

# 📦 Reused Components

This project builds upon reusable infrastructure developed previously.

Planned reusable utilities include:

- VirtualChannel
- FSM framework
- CRC utilities (where applicable)
- Host abstraction
- Data conversion utilities

These components may be adapted as the UART implementation evolves.

---

# 📖 Recommended Study Order

1. UART fundamentals
2. UART frame format
3. UART timing and baud rate
4. UART errors
5. Basic UART hardware registers

---

# 📺 Learning Resources

- Wikipedia — UART
- Ben Eater (YouTube)
- Phil's Lab (YouTube)
- Controllerstech (YouTube)

---

# 🚫 Out of Scope (Initial Versions)

The first versions intentionally avoid advanced topics such as:

- DMA
- RS-232
- RS-485
- Hardware flow control
- Linux UART drivers
- MCU-specific UART peripherals

These can be explored as future extensions once the simulator reaches maturity.

---

# 🎯 Long-Term Vision

Rather than creating a simple UART library, the objective is to build a protocol simulator capable of modeling realistic communication behavior.

The architecture developed here is expected to provide experience with:

- Embedded firmware concepts
- Communication protocol design
UART-Emulator/
│
├── README.md
├── pyproject.toml
├── requirements.txt
├── .gitignore
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
- Event-driven software architecture
- Finite State Machines
- Software validation techniques

The lessons learned from this project can later inform implementations of additional protocols such as SPI, I²C, TCP/IP, and storage-oriented communication protocols.
````

