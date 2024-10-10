# Generate instruction mapping
cargo run --manifest-path ./BitVMX-CPU/Cargo.toml -p emulator -- instruction-mapping > ./execution_files/instruction_mapping.txt
# Generate instruction commitment
cargo run --manifest-path ./BitVMX-CPU/Cargo.toml -p emulator -- generate-rom-commitment --elf ./BitVMX-CPU/docker-riscv32/plainc.elf > ./execution_files/instruction_commitment.txt

cargo run --manifest-path ./BitVMX-CPU/Cargo.toml -p emulator -- execute --elf ./BitVMX-CPU/docker-riscv32/plainc.elf --input 01 -t > ./verifier_files/execution_trace.txt
cargo run --manifest-path ./BitVMX-CPU/Cargo.toml -p emulator -- execute --elf ./BitVMX-CPU/docker-riscv32/plainc.elf --input 01 -t > ./prover_files/execution_trace.txt