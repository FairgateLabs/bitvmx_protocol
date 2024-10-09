# Example Files

This folder contains example files for execution:

1. An `.elf` file: This is an executable and linkable format file containing the program to be executed.
2. A `.txt` file: This file contains the commitment instructions for the corresponding `.elf` file in a processable format.

## Running the Examples

To run the examples, rename the folder to `execution_files`.

Once you've changed the name of the folder, the system will be able to read the commitment instructions.

Important Notes:
- The `.txt` file can be generated with the command `cargo run --release --bin emulator -- generate-rom-commitment --elf docker-riscv32/test_input.elf --sections > ../execution_files/instruction_commitment_input.txt` in the folder `BitVMX-CPU`.

For detailed information on how to use these files and run the examples, please refer to the main project documentation.

