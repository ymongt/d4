import os
import subprocess
import platform

# -------------------------------
# UAD class for impl0
# -------------------------------
class Uad():
    def __init__(self):
        self.inst = "impl0"  # Day 4 only
        self.is_windows = platform.system() == "Windows"

    # --- Common Channel ---
    def halt(self):
        csr = self.read_CSR()
        if csr is not None:
            self.write_CSR(csr | (1 << 5))  # HALT=1

    # --- Configuration Channel ---
    def read_CSR(self):
        cmd = f'{self.inst}.exe cfg --address 0x0' if self.is_windows else f'./{self.inst} cfg --address 0x0'
        try:
            csr_bytes = subprocess.check_output(cmd, shell=True)
            return int(csr_bytes.strip(), 16)
        except:
            print("error: interface unavailable, cannot read CSR")
            return None

    def write_CSR(self, value):
        cmd = f'{self.inst}.exe cfg --address 0x0 --data {hex(value)}' if self.is_windows else f'./{self.inst} cfg --address 0x0 --data {hex(value)}'
        return os.system(cmd)

    def write_register(self, address, value):
        cmd = f'{self.inst}.exe cfg --address {hex(address)} --data {hex(value)}' if self.is_windows else f'./{self.inst} cfg --address {hex(address)} --data {hex(value)}'
        return os.system(cmd)

    # --- Signal Channel ---
    def drive_signal(self, value):
        cmd = f'{self.inst}.exe sig --data {hex(value)}' if self.is_windows else f'./{self.inst} sig --data {hex(value)}'
        try:
            output = subprocess.check_output(cmd, shell=True)
            return int(output.strip(), 16) if output.strip() else None
        except:
            print(f"error: cannot drive signal {hex(value)}")
            return None

# -------------------------------
# Read coefficients from CSV
# -------------------------------
def read_coefficients(cfg_file):
    coeffs = []
    try:
        with open(cfg_file, 'r') as f:
            lines = f.readlines()[1:]  # skip header
            for line in lines:
                parts = line.strip().split(',')
                val_str = parts[2].strip()
                val = int(val_str, 16) if '0x' in val_str else int(val_str)
                coeffs.append(val & 0xFF)
        while len(coeffs) < 4:
            coeffs.append(0)
        packed = (coeffs[3] << 24) | (coeffs[2] << 16) | (coeffs[1] << 8) | coeffs[0]
        return packed
    except FileNotFoundError:
        print(f"error: {cfg_file} not found")
        return 0

# -------------------------------
# Read input vector file
# -------------------------------
def read_vector(vec_file):
    vec = []
    try:
        with open(vec_file, 'r') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                val = int(line, 16) if '0x' in line else int(line)
                vec.append(val & 0xFF)
        return vec
    except FileNotFoundError:
        print(f"error: {vec_file} not found")
        return []

# -------------------------------
# Signal processing test
# -------------------------------
def signal_processing_test(uad, cfg_file, vec_file):
    print(f"\n=== Signal Processing Test with {cfg_file} ===")

    # 1. Halt filter
    uad.halt()
    print("Filter halted.")

    # 2. Load coefficients
    coef_value = read_coefficients(cfg_file)
    uad.write_register(0x4, coef_value)
    print(f"Coefficients loaded: 0x{coef_value:08X}")

    # 3. Clear taps
    csr = uad.read_CSR()
    if csr is not None:
        uad.write_CSR(csr | (1 << 18))  # TCLR
        print("Filter taps cleared.")

    # 4. Unhalt and enable filter + all coefficients
    csr = uad.read_CSR()
    if csr is not None:
        # Enable filter
        csr |= (1 << 0)   # FEN

        # Enable all coefficients
        csr |= (1 << 1)   # C0EN
        csr |= (1 << 2)   # C1EN
        csr |= (1 << 3)   # C2EN
        csr |= (1 << 4)   # C3EN

        # Unhalt filter
        csr &= ~(1 << 5)  # HALT = 0

        uad.write_CSR(csr)
        print("Filter unhalted and all coefficients enabled.")


    # 5. Drive input vector
    inputs = read_vector(vec_file)
    if not inputs:
        print("No input vector found, skipping signal drive.")
        return []

    print("\n-- Driving input signals --")
    outputs = []
    for val in inputs:
        out = uad.drive_signal(val)
        outputs.append(out)
        print(f"Input {hex(val)} → Output {hex(out) if out is not None else 'Error'}")

    return outputs

# -------------------------------
# Main
# -------------------------------
if __name__ == "__main__":
    uad = Uad()
    cfg_files = ["p0.cfg", "p4.cfg", "p7.cfg", "p9.cfg"]
    vec_file = "sqr.vec"

    for cfg in cfg_files:
        outputs = signal_processing_test(uad, cfg, vec_file)
