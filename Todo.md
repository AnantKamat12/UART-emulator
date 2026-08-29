# UART Emulator — TODO

## Version 2

### 1. Reorganize project into proper folders/packages

- [x] Move currently scattered `.py` files into logical modules.
- [x] Keep protocol/core, simulation, UART, tests, etc. separated.
- [x] Fix all imports after relocation.
- [x] Run the existing end-to-end test after restructuring.
- [x] Do not change protocol behavior during this step.

### 2. Create a proper Logger module

- [x] Replace scattered `print()` statements with centralized logging.
- [x] Create separate log files for each host:
  - `host_a.log`
  - `host_b.log`
- [x] Create a third combined simulation log:
  - `simulation.log`
- [x] Include simulation tick and host information in logs.
- [x] Example:
  - `[tick=100] [HOST_A] TX bit=0`
  - `[tick=100] [HOST_B] RX bit=0`
- [x] The combined log should allow the complete interaction between both hosts to be reconstructed.
- [x] Keep diagnostic logs separate from user-facing CLI output.
- [x] Verify all three log files after implementation.

### 3. Build the CLI

- [ ] Allow the user to select the transmitting host:
  - Host A
  - Host B
- [ ] Allow the user to select data type:
  - String
  - Character
  - Integer
- [ ] Accept user input.
- [ ] Validate the input according to the selected type.
- [ ] Trim the input if it exceeds the current packet capacity.
- [ ] Send exactly **one packet/frame** for each CLI transmission.
- [ ] Do not implement multi-packet segmentation through the CLI yet.
- [ ] Pass the data through:
  - User Input
  - Frame
  - Serialization
  - TX
  - Virtual Channel
  - RX
  - Deserialization
  - Reassembler
- [ ] Print:
  - Transmitted data
  - Received data
  - Final success/failure status.
- [ ] Verify a complete user-driven transmission.

### 4. Configurable Frame Data Bits `[IMP]`

- [ ] Make the number of data bits configurable.
- [ ] Initially support:
  - 8 bits
  - 16 bits
  - 24 bits
- [ ] Ensure the complete pipeline respects the selected width:
  - Frame creation
  - Serialization
  - TX
  - RX
  - Deserialization
  - Reassembly
- [ ] Remove hardcoded assumptions such as fixed 2-byte frame handling.
- [ ] Add CLI configuration for data-bit width once the core supports it.
- [ ] Test each supported frame width independently.

### 5. Validate the project after each stage

- [ ] After restructuring → run current end-to-end test.
- [ ] After logger implementation → verify all three log files.
- [ ] After configurable frame width → test 8/16/24-bit frames.
- [ ] After CLI implementation → verify complete user-driven transmission.
- [ ] Ensure existing TX → VC → RX timing behavior remains unchanged.

---

# Version 3 — Flask Web UI

### 1. Flask Frontend

- [ ] Create a Flask-based web interface for the UART emulator.
- [ ] Allow the user to configure the simulation through the browser.
- [ ] Allow the user to enter transmission data through the UI.
- [ ] Allow configuration of:
  - Transmitting host
  - Data type
  - Baud rate
  - Data bits
  - Start tick
  - Other validated simulation parameters.
- [ ] Validate UI input using the same rules as the CLI.

### 2. Same Emulator Core

- [ ] **Do not duplicate UART logic inside Flask.**
- [ ] Keep the emulator core independent of Flask.
- [ ] Flask should only:
  - Receive user input.
  - Build simulation configuration.
  - Call the emulator.
  - Display results.
  - Display logs.
- [ ] CLI and Flask must use the **same emulator API/core**.

Target architecture:

```text
                    UART EMULATOR CORE
                           │
          ┌────────────────┼────────────────┐
          │                │                │
         CLI             Flask            Tests
          │                │                │
      Terminal          Browser         Automated
       Input             Input           Testing
```
