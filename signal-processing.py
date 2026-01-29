# -----------------------------
# FIR Filter Simulation for impl0
# Robust + Terminal Prints
# -----------------------------

class FIRFilter:
    def __init__(self):
        self.coeffs = []
        self.buffer = []

    def set_coefficients(self, coeffs):
        self.coeffs = coeffs
        self.buffer = [0.0] * len(coeffs)

    def filter(self, sample):
        # Shift buffer: newest sample first
        self.buffer = [sample] + self.buffer[:-1]
        # Multiply each buffered value by its coefficient and sum
        return sum(c * x for c, x in zip(self.coeffs, self.buffer))


# Load coefficients from a .cfg file (ignore text, only take numbers)
def load_coefficients(filename):
    coeffs = []
    try:
        with open(filename, 'r') as f:
            for line in f:
                for x in line.replace(',', ' ').split():
                    try:
                        coeffs.append(float(x))
                    except ValueError:
                        pass  # ignore non-numeric entries
        if not coeffs:
            print(f"Warning: No numeric coefficients found in {filename}")
    except FileNotFoundError:
        print(f"Error: Configuration file '{filename}' not found!")
    return coeffs


# Load input signal from .vec file (handles hex like 0xd0)
def load_vector(filename):
    vector = []
    try:
        with open(filename, 'r') as f:
            for line in f:
                for x in line.split():
                    x = x.strip()
                    if not x:
                        continue
                    try:
                        if x.lower().startswith('0x'):
                            vector.append(float(int(x, 16)))
                        else:
                            vector.append(float(x))
                    except ValueError:
                        pass  # ignore invalid entries
        if not vector:
            print(f"Warning: No valid numbers found in {filename}")
    except FileNotFoundError:
        print(f"Error: Input vector file '{filename}' not found!")
    return vector


# Save filtered output to a file
def save_output(output, filename):
    try:
        with open(filename, 'w') as f:
            f.write(', '.join(map(str, output)))
        print(f"Saved output to {filename}")
    except Exception as e:
        print(f"Error saving output: {e}")


# -----------------------------
# Main Task
# -----------------------------
if __name__ == "__main__":
    # Initialize the filter machine (impl0)
    impl0 = FIRFilter()

    # Load input signal
    input_file = 'sqr.vec'  # Make sure this file exists in the same folder
    input_signal = load_vector(input_file)
    if not input_signal:
        print("No input signal loaded. Exiting.")
        exit(1)

    print(f"Input signal ({len(input_signal)} samples), first 20 values: {input_signal[:20]}")

    # List of configuration files
    cfg_files = ['p0.cfg', 'p4.cfg', 'p7.cfg', 'p9.cfg']

    for cfg_file in cfg_files:
        coeffs = load_coefficients(cfg_file)
        if not coeffs:
            print(f"Skipping {cfg_file} due to no valid coefficients.")
            continue

        # Print loaded coefficients
        print(f"\nUsing coefficients from {cfg_file}: {coeffs}")

        impl0.set_coefficients(coeffs)

        # Filter the input signal
        output_signal = []
        for i, sample in enumerate(input_signal):
            y = impl0.filter(sample)
            output_signal.append(y)
            # Print first 10 samples to terminal
            if i < 10:
                print(f"x[{i}]={sample} -> y[{i}]={y}")

        # Save the filtered output
        output_filename = cfg_file.replace('.cfg', '.out')
        save_output(output_signal, output_filename)

    print("\nAll filtering done!")
