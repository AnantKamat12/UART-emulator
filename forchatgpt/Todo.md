date: 17/8/2026
## TODO

- [ ] **Virtual Channel**
  - Bit-level transmission
  - Configurable bit flip
  - Deterministic random seed
  - Delay and bit loss support

- [ ] **Timing Module**
  - Simulation clock
  - Convert baud rate → simulation ticks/bit
  - Track current tick and bit timing
  - Support TX/RX sampling timing

- [ ] **Logger**
  - Protocol-level logging only
  - Timestamp / simulation tick
  - TX/RX events
  - Channel errors
  - FS / PE / FE
  - ACK / NACK / retransmission events

- [ ] **UART FSM**
  - TX FSM: IDLE → START → DATA → PARITY → STOP → WAIT_ACK
  - RX FSM: IDLE → START → DATA → PARITY → STOP → VALIDATE
  - FS / PE / FE handling
  - ACK / NACK
  - Frame retransmission
  - Integrate Timing + Channel + Logger

### Implementation Order

Virtual Channel → Timing → Logger → FSM