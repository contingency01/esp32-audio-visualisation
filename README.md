# ESP32 Audio Visualisation

This project aims to **visualise the frequencies of audio input in real-time** using an ESP32 microcontroller setup, by computing targeted frequency components with the **Goertzel algorithm** and displaying them on a TFT screen.

---

## 🚀 Project Overview

This repository contains code that:

- Samples audio input (e.g., from a microphone or line-in)
- Computes selected frequency components using the **Goertzel algorithm**
- Visualises the computed frequency amplitudes on a small TFT display
- Is written primarily in **Python** with a Jupyter Notebook and accompanying scripts

This is ideal for **hardware music visualisation**, educational DSP experimentation, or embedded audio graphics.

---

## 🧠 How It Works

1. **Audio sampling** — audio signals are read from the hardware input
2. **Frequency extraction** — using the Goertzel algorithm to detect specific bands
3. **Display output** — results are drawn on a TFT using ESP32 GPIO mappings

> The Goertzel algorithm is efficient for computing a small set of frequency bins (e.g., “bass,” “mid,” “treble”), making it perfect for microcontrollers like the ESP32.

---

## 📦 Repository Structure

```
esp32-audio-visualisation/
│
├── README.md                  # Project summary
├── _Notes.ipynb               # Notes & exploratory notebook
├── audio.py                   # Audio sampling & processing
├── bands.py                   # Frequency band logic
├── config.py                  # TFT pin and screen config
├── display.py                 # Display drawing logic
├── main.py                   # Main application controller
└── processing.py              # Goertzel / FFT-like calculations
```

---

## 🧰 Key Files & Purpose

| File | Purpose |
|------|---------|
| `main.py` | Kicks off sampling, processing, and drawing loop |
| `audio.py` | Handles audio input acquisition |
| `processing.py` | Goertzel algorithm computations |
| `display.py` | TFT screen handling (draw bars, levels, etc.) |
| `config.py` | GPIO mappings & display resolution settings |
| `_Notes.ipynb` | Notebook with experiments / visualisation ideas |

---

## ⚙️ Configuration Example

In `config.py`, pin mappings for your ESP32’s TFT display are defined:

```python
SCREEN_WIDTH  = 160
SCREEN_HEIGHT = 128

# TFT pin mapping (ESP32 GPIO numbers)
TFT_SCK_PIN  = 27  # Serial clock
TFT_MOSI_PIN = 33  # Serial data
TFT_RES_PIN  = 12  # Reset
TFT_DC_PIN   = 32  # Data/Command
TFT_CS_PIN   = 26  # Chip select
```
*(Example extracted from the repo)*  [oai_citation:0‡GitHub](https://raw.githubusercontent.com/contingency01/esp32-audio-visualisation/main/config.py)

---

## 🛠️ Requirements & Setup

To work with this project:

1. Install a suitable Python environment (3.7+ recommended)
2. Ensure hardware libraries (e.g., TFT drivers) are installed
3. Connect microphone / ADC input to appropriate ESP32 pins
4. Flash Python code or embed in your ESP32 build chain

⚠️ *Exact setup steps depend on your ESP32 environment (MicroPython, Arduino, or other build systems).*

---

## 📌 Notes

- This project uses **Goertzel frequency detection** rather than full FFT for performance reasons on constrained hardware like the ESP32.
- Displays results in a **real-time visualisation** loop for live audio input.
- Configurations are adjustable for different screens and input sources.

---

## 🙋 Contributing

If you’d like to expand this project, consider adding:

- Support for more frequency bands
- LED strip visualisation alongside TFT
- Audio input calibration / filtering
- More display themes and visual effects

---

Thanks for checking out this project! 👏

## Authors
- [contingency01](https://github.com/contingency01)
- [Vladi700](https://github.com/Vladi700)