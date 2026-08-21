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
Yes. One important terminology point: **FS, PE, and FE are detected by the receiver**, while the Virtual Channel merely corrupts the bit stream. Also, if *any* of these errors occurs, the receiver should reject the frame and request retransmission.

Here is the updated README section in the same concise style:

# UART Emulator

A Python-based emulator for asynchronous UART communication between virtual hosts without physical UART hardware.

## Architecture

```text
Host A
  │
  ▼
 TX
  │
  ▼
UART Frame
  │
  ▼
Virtual Channel
  │
  ▼
 RX
  │
  ▼
Frame Validation
  │
  ├── Valid ───────► Host B
  │
  └── Error ───────► Re-request Frame
```

The current implementation focuses on **Host A → Host B** communication. Full-duplex communication will be added later.

## UART Frame

The emulator currently uses:

```text
START | DATA | PARITY | STOP
```

Current frame format:

```text
START  = 0101
DATA   = 8 bits
PARITY = 1 bit
STOP   = 010
```

Therefore:

```text
4 + 8 + 1 + 3 = 16 bits
```

Frame example:

```text
0101 | XXXXXXXX | P | 010
```

The parity bit is placed immediately after the data bits and before the stop sequence.

## Components

### Host

Represents a UART endpoint.

```text
Host
├── baud_rate
├── is_ideal
├── host_type
├── TX
└── RX
```

`host_type`:

```text
0 → TX only
1 → RX only
2 → TX + RX
```

### TX

Responsible for:

* Generating the UART frame
* Serializing the frame
* Transmitting bits sequentially
* Applying baud-rate timing

### RX

Responsible for:

* Detecting the start sequence
* Receiving data bits
* Checking parity
* Validating the stop sequence
* Detecting frame errors
* Requesting retransmission when an error occurs
* Reconstructing the transmitted byte

### UART Config

```text
baud_rate
data_bits
parity
stop_bits
```

Configuration is composed into UART components rather than inherited.

## Virtual Channel

The Virtual Channel represents the communication medium.

```text
TX
 │
 ▼
Virtual Channel
 │
 ├── Delay
 ├── Bit Flip
 ├── Noise
 └── Bit Loss (future)
 │
 ▼
RX
```

The channel operates only on the **digital bit stream**.

It does not understand:

* UART frames
* Start/stop bits
* Parity
* Application data
* UART errors

## Error Detection

The receiver currently detects three types of frame errors.

### 1. False Start — FS

The expected start sequence is:

```text
0101
```

If the received start sequence is corrupted, the receiver detects a **False Start (FS)**.

```text
Expected:
0101

Received:
0111

→ FS
```

The frame is rejected and a retransmission is requested.

### 2. Parity Error — PE

A **Parity Error (PE)** occurs if either:

* A data bit is corrupted
* The parity bit itself is corrupted

The receiver recalculates parity from the received data and compares it with the received parity bit.

```text
DATA + PARITY
     │
     ▼
Parity Check
     │
     ├── Match ──► Continue
     │
     └── Mismatch ► PE
```

On `PE`, the frame is rejected and a retransmission is requested.

### 3. Framing Error — FE

The expected stop sequence is:

```text
010
```

If the last three stop bits are corrupted, the receiver detects a **Framing Error (FE)**.

```text
Expected STOP:
010

Received STOP:
111

→ FE
```

On `FE`, the frame is rejected and a retransmission is requested.

## Error Handling

All detected frame errors follow the same recovery mechanism:

```text
                Received Frame
                       │
                       ▼
                 Frame Validation
                       │
          ┌────────────┴────────────┐
          │                         │
        Valid                     Error
          │                         │
          ▼                         ▼
       Accept                 Reject Frame
          │                         │
          ▼                         ▼
      Host B Data             Re-request
                                    │
                                    ▼
                              Retransmission
```

The receiver must **not deliver corrupted data to the application**.

Error types:

```text
FS → False Start
PE → Parity Error
FE → Framing Error
```

Any of these errors causes:

```text
Reject → Re-request → Retransmit
```

## Error Injection

The Virtual Channel can intentionally corrupt individual bits.

Possible faults:

```text
Bit Flip
Bit Loss
Delay
Noise
```

Example:

```text
Original:

0101 | 10110010 | 1 | 010

             ↓
          Bit Flip

0101 | 10100010 | 1 | 010
             │
             ▼
             PE
```

A corrupted start sequence produces:

```text
FS
```

A corrupted data/parity region produces:

```text
PE
```

A corrupted stop sequence produces:

```text
FE
```

Errors should be configurable and reproducible using a deterministic random seed.

## Retransmission

When `FS`, `PE`, or `FE` is detected, the receiver requests the transmitter to resend the frame.

```text
TX
 │
 ▼
Frame
 │
 ▼
Channel
 │
 ▼
RX
 │
 ├── Valid ───────► Accept
 │
 └── FS/PE/FE
          │
          ▼
      Re-request
          │
          ▼
      Retransmit
```

The corrupted frame must be discarded before retransmission.

## Current Goal

The first milestone is:

```text
Host A
  ↓
TX
  ↓
START + DATA + PARITY + STOP
  ↓
Virtual Channel
  ↓
RX
  ↓
Frame Validation
  ↓
Host B
```

With error handling:

```text
Corruption
    ↓
FS / PE / FE
    ↓
Frame Rejected
    ↓
Re-request
    ↓
Retransmission
    ↓
Successful Reception
```

## Development Versions

```text
v0.1
- Host → TX → Channel → RX → Host
- Ideal channel
- Correct frame transmission

v0.2
- Start-bit corruption
- False Start (FS)
- Parity Error (PE)
- Framing Error (FE)
- Frame rejection
- Retransmission request

v0.3
- Channel delay
- Bit loss
- More realistic timing

v0.4
- Message segmentation/reassembly

v0.5
- Full-duplex communication
```

## Design Principles

* **Separation of concerns** — Host, UART and Channel remain independent.
* **Protocol-independent channel** — the channel operates on raw bits.
* **Receiver validates frames** — corrupted frames never reach the application.
* **Explicit error types** — FS, PE and FE identify the failure location.
* **Automatic recovery** — detected errors trigger frame retransmission.
* **Deterministic testing** — injected errors should be reproducible.
* **Incremental development** — introduce complexity only after the basic communication path works.
