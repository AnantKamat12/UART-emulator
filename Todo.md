# UART Emulator — Completion Checklist

## Version 2 Core: Complete

- [x] Organize protocol, simulation, UART, infrastructure, and tests into packages.
- [x] Implement configurable 8-, 16-, and 24-bit payload fields (1/2/3 bytes).
- [x] Carry the selected width through `Frame`, `Host`, TX, RX, `Create_duplex_hosts`, and `UARTConnection`.
- [x] Serialize and deserialize variable-width frames; calculate parity and validate start/parity/stop fields.
- [x] Segment and reassemble string and byte payloads across frames; support width-sized integers.
- [x] Provide reusable APIs for constructing hosts, frames, and simulations.
- [x] Add the interactive CLI menu: run modular tests or run a transmission.
- [x] Validate CLI host, type, width, and payload inputs; show examples for strings, integers, and hexadecimal bytes.
- [x] Queue multi-frame CLI payloads correctly and report received frames, payload, and status.
- [x] Write host and combined simulation logs to the workspace `UARTlogs` directory, with CLI/ACK-NACK/full-duplex identification.
- [x] Test TX→virtual channel→RX for strings, integers, and bytes at all three frame widths.
- [x] Test zero and maximum integer payloads at each width and report incomplete-frame timeout as failure.
- [x] Cover frame errors, noisy-channel behavior, full-duplex traffic, and ACK/NACK retransmission in tests.
- [x] Document setup, architecture, frame formats, CLI usage, tests, and known scope boundaries in `README.md` and `docs/`.
- [x] Run modular, ACK/NACK, full-duplex, and CLI integration checks.

## Deliberate Scope Boundaries

These are not blockers for the completed Version 2 core:

- ACK/NACK retransmission is exercised by the dedicated ACK/NACK test flow; it is not automatically enabled in every generic `Host` transmission.
- The CLI currently uses the emulator's fixed 100-tick bit interval; full baud-rate-dependent TX/RX timing remains future work.
- Exhaustive type annotations and docstrings across every legacy module are not part of the completed core.
- Waveform visualization and a web UI are optional future enhancements.
