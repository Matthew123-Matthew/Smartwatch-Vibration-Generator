# Smartwatch Vibration Generator

A Python-based CLI tool for generating precisely timed and calibrated haptic vibration waveforms, built to work around the lack of access to professional DAW software during an internship. Designed to pair with Logic Pro for synchronising vibration with sound design.

## Background

While designing the booting sound effect for a screenless smartwatch, I needed to produce vibration data with exact millisecond timing and intensity control to match the accompanying audio. As an intern, I did not have permission to install the studio's usual vibration design software, so I built this tool instead.

## Features

- **Standard Mode**: Generate a single vibration pulse by entering a duration (ms) and intensity (0–100).
- **Advanced Segment Mode**: Build multi-stage vibration sequences with custom fade-in and fade-out envelopes, entered as a sequence of duration/intensity pairs (e.g. `100,30; 200,30; 100,100; 100,0`).
- **Analysis Mode**: Inspect the duration and peak intensity of previously generated WAV files.
- **Quick Generate Mode**: Generate a vibration waveform from a single line of input.

## How It Works

The tool generates a base sine wave at a fixed carrier frequency (200Hz), then shapes its amplitude using either a fixed intensity value or a custom envelope built from user-defined time and intensity points. A short fade-in and fade-out is applied at the start and end of each waveform to protect the motor and avoid clicking artefacts. The result is exported as a 16-bit WAV file, ready to be imported into a DAW.

## Requirements

- Python 3
- NumPy
- SciPy

## Usage

```bash
python vibration_generator.py
```

Follow the on-screen prompts to select a mode and enter your parameters.

---

*This tool was developed independently as part of a personal portfolio project. It does not contain or reproduce any confidential material from prior work.*
