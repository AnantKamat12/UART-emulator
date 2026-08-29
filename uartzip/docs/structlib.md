# Python `struct` Usage

The UART Emulator uses Python's `struct` module to convert between integer values and byte sequences.

The main purpose is to serialize and deserialize the 16-bit UART frame.

---

## Big-Endian 16-bit Integer

The frame is represented internally as a 16-bit unsigned integer.

To convert it into two bytes:

```python
import struct

value = 0x5412

data = struct.pack(">H", value)

print(data)
```

Result:

```text
b'T\x12'
```

The format string is:

```text
>H
```

where:

```text
> = big-endian
H = unsigned 16-bit integer
```

Therefore:

```text
16 bits → 2 bytes
```

---

## Unpacking

To convert the two bytes back into the original integer:

```python
value = struct.unpack(">H", data)[0]
```

`struct.unpack()` returns a tuple, so `[0]` retrieves the actual integer.

Example:

```python
import struct

data = b"\x54\x12"

value = struct.unpack(">H", data)[0]

print(hex(value))
```

Result:

```text
0x5412
```

---

# Usage in `Frames.py`

The `Frame.serialise()` method constructs the complete 16-bit frame:

```text
START | DATA | PARITY | STOP
```

The fields occupy:

```text
START  → bits 12–15
DATA   → bits 4–11
PARITY → bit 3
STOP   → bits 0–2
```

The fields are combined into one integer:

```python
packed_frame = (
    self.start << 12
    | self.data << 4
    | parity_bit << 3
    | self.stop
)
```

The resulting integer is then serialized:

```python
struct.pack(">H", packed_frame)
```

This produces exactly two bytes.

---

# Deserialization

`Deserialise.decode_frame()` expects exactly two bytes:

```python
if len(frame_bytes) != 2:
    raise ValueError("UART frame must contain exactly 2 bytes")
```

The bytes are converted back into the 16-bit integer:

```python
frame = struct.unpack(">H", frame_bytes)[0]
```

The individual fields are then extracted with bit operations.

For example:

```python
start = (frame >> 12) & 0xF
data = (frame >> 4) & 0xFF
parity_bit = (frame >> 3) & 0x01
stop = frame & 0x7
```

---

# Encoding Application Data

`Frame.encode_data()` also accepts byte-oriented input.

For one byte:

```python
data = b"A"

value = data[0]
```

For input containing two or more bytes, the current implementation takes the first two bytes, interprets them as a big-endian unsigned short, and then masks the result to 8 bits.

```python
val = struct.unpack(">H", b[:2])[0]
return val & 0xFF
```

Because the UART data field is currently only 8 bits, only the final 8-bit value is retained.

The normal end-to-end path uses the `Segmenter`, which supplies one-byte segments for the current 8-bit segment size.

---

# Example

```python
import struct

value = 0x5412

# Integer → bytes
packed = struct.pack(">H", value)

# bytes → integer
unpacked = struct.unpack(">H", packed)[0]

print(packed.hex())
print(hex(unpacked))
```

Output:

```text
5412
0x5412
```

The operation is therefore:

```text
16-bit integer
      │
      ▼
struct.pack(">H", ...)
      │
      ▼
  2 bytes
      │
      ▼
struct.unpack(">H", ...)[0]
      │
      ▼
16-bit integer
```

---

# Why `struct` Is Used

The UART emulator operates at the boundary between:

```text
Python application data
        │
        ▼
Integer bit representation
        │
        ▼
Serialized bytes
        │
        ▼
Individual transmitted bits
```

`struct` provides an explicit and predictable conversion between the integer representation used by the frame logic and the byte representation used during serialization/deserialization.
