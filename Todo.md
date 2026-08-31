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

#### 5. Final Polish & Quality (Priority 2)

- [ ] **README.md**
  - [ ] Explain UART emulator purpose and what it demonstrates
  - [ ] How to run tests: `python tests\primitive_test.py`
  - [ ] How to run CLI (once completed)
  - [ ] Document frame structure for 8/16/24-bit modes
  - [ ] Example transmission flow with expected output

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
  - [ ] Primitive test passes after all changes
  - [ ] Logs are created and contain correct format
  - [ ] Each frame width (8/16/24) transmits and receives correctly

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
