# UART-emulator — Frame helper

Small helper for building 14-bit frames (1401 style): start (3 bits) + data (12 bits) + parity (1 bit).

## Frame format
- start: 3 bits (0..7)
- data: 12 bits (0..0xFFF)
- parity: 1 bit (even=0, odd=1)
- Packed into a 16-bit unsigned big-endian value: bits 15..0 = [start:3][data:12][parity:1].

## Quick usage
```python
from Frames import Frame
f = Frame(start=0b101, parity=0, data="he")   # data accepts int, str, bytes
print(f)                                      # readable representation
raw = f.serialise()                           # returns bytes (2 bytes)
print(raw.hex())                              # hex string of packed 16-bit value
```

Examples:
- data = "" → data = 0, parity = 0 → packed value = 0xA000 → hex "a000"
- data = "he" → first two bytes b"he" -> 0x6865 & 0x0FFF = 0x865 -> packed -> e.g. "b0cb"

## What struct.pack/unpack do here
- struct.pack('>H', value): encode the 16-bit unsigned integer `value` into 2 bytes, big-endian (most-significant byte first). Returned type: bytes.
- struct.unpack('>H', bytes2)[0]: decode 2 bytes as a big-endian unsigned 16-bit integer. unpack returns a tuple; use [0] to get the integer.

## How _encode_data works
- If int: value & 0x0FFF (keeps lower 12 bits).
- If str: encodes ASCII, takes the first up to 2 bytes.
- If bytes/bytearray: uses the first up to 2 bytes.
- Those bytes are interpreted as a big-endian 16-bit value via struct.unpack and masked to 12 bits.

## Parity
- serialise() counts 1-bits in the 12-bit data.
- parity==0 -> even parity: parity bit set to 1 only if data has odd number of 1s.
- parity==1 -> odd parity: parity bit set to 1 only if data has even number of 1s.

## Return types
- Frame.__str__() -> str
- Frame.serialise() -> bytes (2 bytes, big-endian representation of the packed frame)

## Notes
- The top nibble of the 2-byte hex can look like a single hex digit (e.g., 'a' == 0xA == 0b1010) because the 3 start bits plus the next data bit produce that nibble.
- Ensure start fits in 3 bits and data in 12 bits to avoid unexpected results.