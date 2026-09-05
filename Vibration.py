import numpy as np
import scipy.io.wavfile as wav
import os

# --- Base Parameters ---
FREQUENCY = 200  # Frequency (Hz)
SAMPLE_RATE = 48000  # Sample rate
OUTPUT_FOLDER = "Vibration_sample"  # Output folder name

# Create output folder
if not os.path.exists(OUTPUT_FOLDER):
    os.makedirs(OUTPUT_FOLDER)


# ===========================
#      Utility Functions
# ===========================

def generate_sine_wave(duration_ms):
    """Generate a clean sine wave base"""
    num_samples = int((duration_ms / 1000) * SAMPLE_RATE)
    if num_samples == 0: return np.array([]), 0
    t = np.linspace(0, duration_ms / 1000, num_samples, endpoint=False)
    base_wave = np.sin(2 * np.pi * FREQUENCY * t)
    return base_wave, num_samples


def save_wav(filename, audio_data):
    """Save the data as a WAV file"""
    # Ensure the data stays within -1 to 1
    audio_data = np.clip(audio_data, -1.0, 1.0)
    audio_int16 = (audio_data * 32767).astype(np.int16)
    filepath = os.path.join(OUTPUT_FOLDER, filename)
    wav.write(filepath, SAMPLE_RATE, audio_int16)
    print(f"✅ File exported: {filepath}")


# ===========================
#      Mode 1: Standard Vibration
# ===========================

def mode_normal():
    print("\n--- Entering [Standard Mode] ---")
    try:
        ms = int(input("Enter duration (ms) [e.g. 200]: "))
        intensity_input = float(input("Enter intensity (0 ~ 100) [e.g. 90]: "))
        intensity = intensity_input / 100.0

        base_wave, num_samples = generate_sine_wave(ms)
        audio = base_wave * intensity

        # Fade in/out at start and end (to avoid clicking artefacts)
        fade_samples = int((2 / 1000) * SAMPLE_RATE)
        if num_samples > 2 * fade_samples:
            fade_in = np.linspace(0, 1, fade_samples)
            fade_out = np.linspace(1, 0, fade_samples)
            audio[:fade_samples] *= fade_in
            audio[-fade_samples:] *= fade_out

        filename = f"Normal_{ms}ms_Vol{int(intensity_input)}.wav"
        save_wav(filename, audio)
    except ValueError:
        print("❌ Invalid input")


# ===========================
#      Mode 2: Advanced Custom Segments
# ===========================

def mode_advanced_segments():
    print("\n--- Entering [Advanced Segment Mode] ---")
    print("Instructions: Enter the 'duration' and 'target intensity' for each segment, in order.")
    print("Format example: 100,30; 200,30; 100,100; 100,0")

    try:
        input_str = input("\nEnter your sequence: ")
        # Remove spaces and split by semicolon
        segments = input_str.replace(" ", "").split(';')

        time_points = [0]
        intensity_points = [0.0]
        current_time_ms = 0

        for seg in segments:
            if not seg: continue
            parts = seg.split(',')
            if len(parts) != 2:
                print(f"⚠️ Invalid format, skipped: {seg}")
                continue

            dur = float(parts[0])
            target_vol = float(parts[1]) / 100.0

            current_time_ms += dur
            time_points.append(current_time_ms)
            intensity_points.append(target_vol)

        total_ms = time_points[-1]
        if total_ms <= 0:
            print("❌ Total duration is 0, cannot generate.")
            return

        base_wave, total_samples = generate_sine_wave(total_ms)

        # Build the envelope
        x_points = np.array(time_points) / 1000 * SAMPLE_RATE
        y_points = np.array(intensity_points)
        x_target = np.arange(total_samples)
        envelope = np.interp(x_target, x_points, y_points)

        audio = base_wave * envelope

        filename_clean = input_str.replace(" ", "").replace(",", "_").replace(";", "-")
        if len(filename_clean) > 30: filename_clean = "Advanced_Sequence"
        filename = f"{filename_clean}_{int(total_ms)}ms.wav"
        save_wav(filename, audio)

    except ValueError:
        print("❌ Invalid numeric format.")


# ===========================
#      Mode 3: Analysis
# ===========================

def mode_analyze_sequence():
    print("\n--- Entering [WAV Sequence Analysis Mode] ---")
    files = [f for f in os.listdir(OUTPUT_FOLDER) if f.endswith(".wav")]
    if not files:
        print(f"❌ No WAV files found in the {OUTPUT_FOLDER} folder.")
        return

    print("Select a file to analyse:")
    for idx, f in enumerate(files):
        print(f"{idx + 1}. {f}")

    try:
        selection = int(input("Enter the file number: ")) - 1
        if selection < 0 or selection >= len(files): return

        target_file = os.path.join(OUTPUT_FOLDER, files[selection])
        sr, data = wav.read(target_file)
        if len(data.shape) > 1: data = data[:, 0]

        # Analysis logic (simplified display)
        abs_data = np.abs(data.astype(np.float32) / 32768.0)
        THRESHOLD = 0.05
        is_active = abs_data > THRESHOLD

        # Calculate total duration and peak intensity
        file_ms = (len(data) / sr) * 1000
        max_vol = np.max(abs_data) * 100

        print(f"\n📊 File: {files[selection]}")
        print(f"⏱️  Duration: {file_ms:.1f} ms | Peak intensity: {max_vol:.1f}")
        print("-" * 30)

    except Exception as e:
        print(f"❌ Error: {e}")


# ===========================
#      Mode 4: Quick Generate
# ===========================

def mode_quick_generate():
    print("\n--- Entering [Quick Generate Mode] ---")
    print("Instructions: Enter 'duration' and 'intensity', separated by a space or comma.")
    print("Example: 200 100  (means 200ms, intensity 100)")

    try:
        raw_input = input("Enter values: ")
        # Replace commas with spaces, then split the string
        parts = raw_input.replace(',', ' ').split()

        if len(parts) < 2:
            print("❌ Invalid format. Please enter at least two numbers (duration intensity)")
            return

        ms = int(parts[0])
        intensity_val = float(parts[1])
        intensity = intensity_val / 100.0

        # 1. Generate the waveform
        base_wave, num_samples = generate_sine_wave(ms)
        audio = base_wave * intensity

        # 2. Fade in/out (to protect the motor)
        fade_samples = int((2 / 1000) * SAMPLE_RATE)
        if num_samples > 2 * fade_samples:
            fade_in = np.linspace(0, 1, fade_samples)
            fade_out = np.linspace(1, 0, fade_samples)
            audio[:fade_samples] *= fade_in
            audio[-fade_samples:] *= fade_out

        # 3. Export the file
        filename = f"Quick_{ms}ms_Vol{int(intensity_val)}.wav"
        save_wav(filename, audio)

    except ValueError:
        print("❌ Invalid input. Please make sure you entered numbers.")


# ===========================
#      Main Program
# ===========================
if __name__ == "__main__":
    while True:
        print("\n==============================")
        print(" Smartwatch Vibration Generator")
        print("==============================")
        print("1. Standard vibration (enter duration and intensity separately)")
        print("2. Advanced custom sequence (set duration and volume per segment)")
        print("3. Read a WAV file")
        print("4. Quick generate (single line: duration, intensity)")
        print("q. Quit")

        choice = input("Select a mode (1/2/3/4/q): ").lower()

        if choice == '1':
            mode_normal()
        elif choice == '2':
            mode_advanced_segments()
        elif choice == '3':
            mode_analyze_sequence()
        elif choice == '4':
            mode_quick_generate()
        elif choice == 'q':
            print("Bye Bye! 👋")
            break
        else:
            print("Invalid selection, please try again")
