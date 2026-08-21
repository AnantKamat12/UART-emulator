# UART Frame

The UART Emulator currently models a fixed 16-bit UART-like frame.

## Frame Format

```text
┌────────┬──────────┬────────┬────────┐
│ START  │   DATA   │ PARITY │  STOP  │
│ 4 bit  │  8 bits  │ 1 bit  │ 3 bits │
└────────┴──────────┴────────┴────────┘
```

The default values are:

```text
START  = 0101
DATA   = 8 bits
PARITY = 1 bit
STOP   = 010
```

Total:

```text
4 + 8 + 1 + 3 = 16 bits
```

Example:

```text
0101 | 01000001 | 0 | 010
```

The data field above represents the character `A`.

---

## Frame Construction

`Frames.py` contains the `Frame` class.

A frame can be constructed from:

* `int`
* `str`
* `bytes`
* `bytearray`

The input is converted to an 8-bit data value.

```python
frame = Frame(
    start=0b0101,
    parity=0,
    data=b"A",
    stop=0b010
)
```

The current implementation masks the resulting data value to 8 bits.

---

## Parity

The emulator supports:

```text
parity = 0 → even parity
parity = 1 → odd parity
```

The parity bit is calculated during serialization.

For even parity:

```text
Number of 1s in DATA + PARITY
must be even
```

For odd parity:

```text
Number of 1s in DATA + PARITY
must be odd
```

The final frame is assembled as:

```text
START | DATA | PARITY | STOP
```

---

## Serialization

The complete frame is represented internally as a 16-bit integer.

It is serialized using:

```python
struct.pack(">H", value)
```

`>` means:

```text
Big-endian
```

`H` means:

```text
Unsigned short = 16 bits
```

Therefore the result is exactly:

```text
2 bytes
```

For example:

```python
serialized_frame = frame.serialise()
```

The resulting bytes can then be converted to an integer for the current TX implementation.

---

## Transmission

The current TX implementation transmits the serialized frame as a 16-bit integer.

The bits are extracted using:

```python
bit = (frame >> bit_index) & 1
```

with:

```text
bit_index = 0 ... 15
```

Therefore transmission occurs:

```text
LSB first
```

The TX schedules one bit at each configured bit boundary.

At the current default configuration:

```text
9600 baud
100 simulation ticks / bit
```

A complete 16-bit frame therefore requires approximately:

```text
16 × 100 = 1600 simulation ticks
```

of bit transmission time.

---

# Deserialization

`Deserialise` converts the two serialized bytes back into a 16-bit integer.

```python
frame = struct.unpack(">H", frame_bytes)[0]
```

The fields are then extracted using bit operations:

```text
START  = bits 12–15
DATA   = bits 4–11
PARITY = bit 3
STOP   = bits 0–2
```

The receiver validates the extracted fields.

---

# Frame Validation

The deserializer returns a status together with the decoded data.

Possible statuses:

```text
OK
FS
PE
FE
```

## FS — False Start

The received start field does not match the expected start sequence.

```text
Expected:
0101

Received:
different value

→ FS
```

---

## PE — Parity Error

The received parity bit does not match the parity calculated from the received data.

This can occur when:

* A data bit is changed.
* The parity bit is changed.

The deserializer reports:

```text
PE
```

---

## FE — Framing Error

The received stop field does not match the expected stop sequence.

```text
Expected:
010

Received:
different value

→ FE
```

---

# Current Error Handling Boundary

An important architectural distinction is that **frame validation and frame recovery are separate responsibilities**.

`Deserialise` currently detects:

```text
FS
PE
FE
```

but the current implementation does **not yet implement the retransmission protocol**.

The existing code therefore performs:

```text
RX
 │
 ▼
Deserialise
 │
 ├── OK ──► decoded data
 │
 └── FS/PE/FE ──► error status
```

Retransmission handling is not part of the current Version 1 implementation.

---

# Application Data Flow

For the current end-to-end test, application data first passes through the `Segmenter`.

For example:

```text
"ANANT"
```

is divided into 8-bit segments:

```text
A
N
A
N
T
```

Each segment is then placed into a separate 16-bit UART frame.

At the receiving side:

```text
Frame
  │
  ▼
Deserialise
  │
  ▼
Data byte
  │
  ▼
Reassembler
  │
  ▼
"ANANT"
```

This allows the current implementation to demonstrate both frame-level transmission and application-level reconstruction.

---

# Current Scope

Implemented:

* Fixed 16-bit frame.
* 4-bit start field.
* 8-bit data field.
* 1-bit parity field.
* 3-bit stop field.
* Even/odd parity calculation.
* Serialization using Python `struct`.
* Deserialization.
* FS detection.
* PE detection.
* FE detection.
* Bit-by-bit TX.
* Bit-by-bit RX.
* Simulation-clock timing.
* Application-data segmentation.
* Application-data reassembly.

Not currently implemented:

* Automatic retransmission.
* Error injection.
* Random bit corruption.
* Bit loss.
* Channel noise.
* Configurable channel delay.

These should not be treated as current UART Emulator capabilities.
