# UART Frame

The UART Emulator supports UART-like frames with 8-, 16-, or 24-bit data fields.
The start, parity, and stop fields add another 8 bits to each complete frame.

## Frame Format

```text
┌────────┬──────────┬────────┬────────┐
│ START  │   DATA   │ PARITY │  STOP  │
│ 4 bit  │ 8/16/24  │ 1 bit  │ 3 bits │
└────────┴──────────┴────────┴────────┘
```

The default values are:

```text
START  = 0101
DATA   = 8, 16, or 24 bits
PARITY = 1 bit
STOP   = 010
```

Total:

```text
4 + (8, 16, or 24) + 1 + 3 = 16, 24, or 32 bits
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

- `int`
- `str`
- `bytes`
- `bytearray`

`data_size` selects the data-field width in bytes: 1, 2, or 3.

```python
frame = Frame(
    start=0b0101,
    parity=0,
    data=b"AB",
    data_size=2,
    stop=0b010
)
```

The payload is converted to a big-endian integer and masked to the selected
data-field width.

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

The complete frame is represented internally as an integer and serialized to
`data_size + 1` bytes. The serialized lengths are 2, 3, and 4 bytes for
1-, 2-, and 3-byte data fields respectively. `>` means:

```text
Big-endian
```

For example:

```python
serialized_frame = frame.serialise()
```

The resulting bytes can be converted to an integer for transmission.

---

## Transmission

TX sends the configured frame width, calculated as `data_size * 8 + 8` bits.

The bits are extracted using:

```python
bit = (frame >> bit_index) & 1
```

with `bit_index` ranging from zero up to (but not including) the frame width.
For example, the supported widths are:

```text
data_size=1 → 16 frame bits
data_size=2 → 24 frame bits
data_size=3 → 32 frame bits
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

A complete frame requires approximately:

```text
frame_bits × 100 simulation ticks
```

of bit transmission time.

---

# Deserialization

`Deserialise` converts the serialized bytes back into an integer using the
configured `data_size`.

The fields are then extracted using bit operations:

```text
START  = the 4 bits immediately above the data field
DATA   = bits 4 through (data_size * 8 + 3)
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

- A data bit is changed.
- The parity bit is changed.

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

is divided into segments matching the selected data-field width. With a
one-byte data field, the segments are:

```text
A
N
A
N
T
```

Each segment is then placed into a UART frame whose total width is 16, 24, or
32 bits, depending on `data_size`.

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

- Configurable 16-, 24-, and 32-bit total frame widths.
- 4-bit start field.
- 8-, 16-, or 24-bit data field.
- 1-bit parity field.
- 3-bit stop field.
- Even/odd parity calculation.
- Serialization using Python `struct`.
- Deserialization.
- FS detection.
- PE detection.
- FE detection.
- Width-configurable bit-by-bit TX and RX.
- Simulation-clock timing.
- Application-data segmentation.
- Application-data reassembly.

Not currently implemented:

- Automatic retransmission.
- Configurable random bit corruption through `VirtualChannel`.
- Bit loss.
- Channel noise.
- Configurable channel delay.

Automatic retransmission and channel-delay simulation remain future work.
