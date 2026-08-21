# UART Emulator — TODO

- [ ] Reorganize project into proper folders/packages
  - Move currently scattered `.py` files into logical modules.
  - Keep protocol/core, simulation, UART, tests, etc. separated.
  - Fix all imports after relocation.
  - Run the existing end-to-end test after restructuring.
  - Do not change protocol behavior during this step.

- [ ] Create a proper Logger module
  - Replace scattered `print()` statements with centralized logging.
  - Create separate log files for each host:
    - `host_a.log`
    - `host_b.log`
  - Create a third combined simulation log:
    - `simulation.log`
  - Include simulation tick and host information in logs.
  - Example:
    - `[tick=100] [HOST_A] TX bit=0`
    - `[tick=100] [HOST_B] RX bit=0`
  - The combined log should allow the complete interaction between both hosts to be reconstructed.
  - Keep diagnostic logs separate from user-facing CLI output.

- [ ] Build the CLI
  - Allow the user to select the transmitting host:
    - Host A
    - Host B
  - Allow the user to select data type:
    - String
    - Character
    - Integer
  - Accept user input.
  - Validate the input according to the selected type.
  - Trim the input if it exceeds the current packet capacity.
  - Send exactly **one packet/frame** for each CLI transmission.
  - Do not implement multi-packet segmentation through the CLI yet.
  - Pass the data through:
    - User Input
    - Frame
    - Serialization
    - TX
    - Virtual Channel
    - RX
    - Deserialization
    - Reassembler
  - Print the transmitted data, received data, and final success/failure status.

- [ ] Validate the project after each stage
  - After restructuring: run the current end-to-end test.
  - After logger implementation: verify all three log files.
  - After CLI implementation: verify a complete user-driven transmission.

- [ ] Final target
  - Run the UART Emulator entirely through the CLI.
  - Maintain the existing working TX → VC → RX timing architecture.
  - Keep the internal simulation testable independently of the CLI.