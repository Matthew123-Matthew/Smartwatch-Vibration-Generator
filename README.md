# Haptic Audio Workflow Tools

A collection of Python-based CLI tools designed to bridge the gap between UI/UX haptic feedback design and digital audio workstations (DAWs) like Logic Pro. These tools streamline the workflow for Technical Audio Designers and Haptic Engineers.

## Tools Included

### 1. AHAP to WAV Converter (`ahap_to_wav.py`)
In iOS development, haptic feedback is often designed using `.ahap` (JSON) files. However, DAWs do not support importing this format, making it extremely difficult to sync visual UI animations with haptic feedback for demo videos. 

This script parses `HapticContinuous`, `HapticTransient`, and `ParameterCurve` JSON data and synthesizes it into a playable `.wav` file.
* **Dynamic Mapping**: Maps AHAP "Sharpness" to a frequency variance (40Hz - 120Hz).
* **Envelope Generation**: Converts AHAP "Intensity" into an audio amplitude envelope.

### 2. Precision Haptic Waveform Generator & Analyzer (`qirca_vibration.py`)
Designing vibration audio in a DAW based on musical time (Bars/Beats) is unintuitive when hardware motors require millisecond (ms) precision. This interactive CLI tool allows designers to generate, edit, and analyze haptic audio files with exact ms/intensity metrics for hardware testing.
* **Mode 1 | Normal Vibration**: Generate a base sine wave with custom duration and intensity.
* **Mode 2 | Multi-segment Sequence**: Input a sequence of time/intensity markers to create complex haptic patterns.
* **Mode 3 | WAV Analysis**: Read existing `.wav` files to automatically calculate total duration and peak intensity.
* **Mode 4 | Quick Generate**: A streamlined command-line input for rapid ms/intensity generation.
* **Motor Protection**: Automatically applies a 2ms fade-in/out to prevent popping sounds and protect hardware testing motors.

## Requirements
Ensure you have Python 3 installed along with the following libraries:
```bash
pip install numpy scipy