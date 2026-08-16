# struct usage 

- struct.pack('>H', value)  
  Encode a 16-bit unsigned integer into 2 bytes (big-endian). Returns bytes.

- struct.unpack('>H', bytes2)[0]  
  Decode 2 bytes (big-endian) into a 16-bit unsigned integer. unpack returns a tuple; use [0].

- In Frames.py
  - Pack: pkd_frame is a 16-bit value (start/data/parity/stop) → struct.pack('>H', pkd_frame) to get 2 bytes for transmission.
  - Unpack for data encoding: take up to 2 input bytes, struct.unpack('>H', b[:2])[0] to interpret them as a single integer, then mask to needed bits.

Examples:
```python
import struct
val = 0x5412
b = struct.pack('>H', val)      # b'\x54\x12'
n = struct.unpack('>H', b)[0]   # 0x5412
```
```# struct usage (short)

- struct.pack('>H', value)  
  Encode a 16-bit unsigned integer into 2 bytes (big-endian). Returns bytes.

- struct.unpack('>H', bytes2)[0]  
  Decode 2 bytes (big-endian) into a 16-bit unsigned integer. unpack returns a tuple; use [0].

- In Frames.py
  - Pack: pkd_frame is a 16-bit value (start/data/parity/stop) → struct.pack('>H', pkd_frame) to get 2 bytes for transmission.
  - Unpack for data encoding: take up to 2 input bytes, struct.unpack('>H', b[:2])[0] to interpret them as a single integer, then mask to needed bits.

Examples:
```python
import struct
val = 0x5412
b = struct.pack('>H', val)      # b'\x54\x12'
n = struct.unpack('>H', b)[0]   # 0x5412
```