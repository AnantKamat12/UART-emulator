# UART Emulator — TODO

## Core Work (Version 2)

### ✅ Completed

#### 1. Reorganize project into proper folders/packages

- [x] Move scattered files into logical modules
- [x] Keep protocol/core, simulation, UART, tests separated
- [x] Fix all imports after relocation
- [x] Run end-to-end test after restructuring

#### 2. Create a proper Logger module

- [x] Replace print() with centralized logging
- [x] Create host-specific logs: host_a.log, host_b.log
- [x] Create shared simulation log: simulation.log
- [x] Include tick and host information in logs
- [x] Verify all three log files after implementation

#### 4. Configurable Frame Data Bits

- [x] Make data_size configurable (8/16/24 bits)
- [x] Update Frame.encode_data(), serialise(), decode_frame()
- [x] Test 8-bit, 16-bit, 24-bit frames independently
- [x] Full pipeline respects selected width

---

### 🚧 To Do (Priority Order)

#### 3. Build the CLI (Priority 1)

- [ ] Accept user input:
  - [ ] Select transmitting host (Host A or Host B)
  - [ ] Select data type (string, byte, integer)
  - [ ] Select frame width (8/16/24 bits)
  - [ ] Enter data to transmit
- [ ] Input validation:
  - [ ] Validate data matches selected type
  - [ ] Trim input if exceeds packet capacity
  - [ ] Show clear error messages
- [ ] Transmission flow:
  - [ ] Send exactly one frame per CLI invocation
  - [ ] Route through: User Input → Frame → TX → VC → RX → Reassembler
  - [ ] Display: transmitted data, received data, success/failure status
- [ ] Test with all three frame widths (8/16/24-bit)
- [] Implement a test case for ACk/NACK also put error in Vc

#### 5. Final Polish & Quality (Priority 2)

- [x] **README.md**
  - [x] Explain UART emulator purpose and what it demonstrates
  - [x] How to run tests: `python tests\primitive_test.py`
  - [x] How to run CLI
  - [x] Document frame structure for 8/16/24-bit modes
  - [x] Example transmission flow with expected output

- [ ] **Error Handling & Edge Cases**
  - [ ] Test corrupted frames (false start, parity error, framing error)
  - [ ] Handle timeout scenarios (missing RX)
  - [ ] Test edge cases: all 1's, all 0's, back-to-back frames
  - [ ] Test max frame sizes for each data_size
  - [ ] Graceful error messages (no cryptic crashes)

- [ ] **Code Documentation**
  - [ ] Add docstrings to all public methods
  - [ ] Explain complex logic: bit-shifting in Frame.serialise()
  - [ ] Document singleton Clock behavior
  - [ ] Add type hints to function parameters

- [ ] **Validation Checklist**
  - [x] Primitive test passes after all changes
  - [x] Logs are created and contain correct format
  - [ ] Each frame width (8/16/24) transmits and receives correctly

1. Build the test matrix
2. Integrate ACK/NACK retransmission
3. Finish the CLI
4. Complete documentation3
5. Rename and polish the project
6. Run the complete test suite

---

#### 6. Final Protocol Test Coverage

- [x] Add a full-duplex communication test
  - [x] Schedule Host A and Host B transmissions at independent ticks
  - [x] Verify both hosts can transmit and receive in the same simulation
  - [x] Verify messages are reassembled correctly in both directions
  - [x] Cover overlapping and back-to-back transmissions
- [ ] Add ACK/NACK testing with a non-ideal VirtualChannel
  - [ ] Inject bit errors through the configured noise rate
  - [ ] Verify corrupted frames produce NACK feedback
  - [ ] Verify valid frames produce ACK feedback
  - [ ] Verify the feedback frame uses the correct data size
  - [ ] Add retransmission coverage after NACK
- [x] Create a small public test/CLI API module
  - [x] Expose simple host, frame, channel, and clock setup helpers
  - [x] Expose a function to transmit one message and return the result
  - [x] Expose received data, frame status, ACK/NACK status, and simulation ticks
  - [x] Keep the API independent from command-line input/output
  - [x] Reuse the same API from custom tests and the upcoming CLI

### Remaining Work

- [ ] Rebuild and improve `ACK_NCK.py` retransmission test
- [ ] Rebuild and improve `mainCLI.py` interactive CLI//step by step show frame creation-segmentation-trasnsmission status-ack/nck(in cli test clock can be sidelined trasnmitting data till user wills todo, dont ask closk as input/no start tick/end tick, ask baud rate,ideal/non ideal,ack-nack,data-size,data-type etc etc)
- [ ] Integrate ACK/NACK feedback into Host and Receiver/or make another file which will handle ack/nck mechanism not the individaul test case itself
- [ ] Implement retransmission after NACK
- [ ] Add noisy-channel ACK/NACK tests
- [ ] Complete CLI input validation and transmission flow
- [ ] Rename files consistently
- [ ] Fix imports after file renaming
- [ ] Run and document the complete test suite

---

## Optional / Future (Version 3+)

These are nice enhancements but not required for a solid project:

### Waveform Visualization

- Build 3D plot: X-axis (simulation ticks), Y-axis (wave state: 1 or -1)
- Mark data transmission points with dots/markers
- Show timing alignment between TX and RX
- Export plots to file (matplotlib/plotly)

### Flask Web UI

- Create web interface for the UART emulator
- Allow browser-based configuration and data entry
- Reuse the same emulator core (do NOT duplicate logic)
- Display simulation results and logs in the browser

---
