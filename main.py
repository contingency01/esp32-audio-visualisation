# main.py
import time
import display
import audio
import bands

print("Init display...")
display.init_display()

print("Init audio...")
audio.init_audio()

# 8 band center frequencies (Hz) — tuned to react to voice/music
FREQS = [100, 100 + 192, 100 + 192 + 192, 100 + 3 * 192, 100 + 4 * 192, 100 + 5*192, 100 + 6 * 192]

state = None

# Frame pacing for smooth display
FRAME_MS = 16  # ~60 FPS
next_frame = time.ticks_ms()

print("Running frequency bars (Ctrl+C to stop)")
try:
    while True:
        samples = audio.read_block()        # --- software mic gain ---
        GAIN = 10.0
        samples = [max(-32768, min(32767, int(x * GAIN))) for x in samples]

        levels, state = bands.compute_bars(
            samples,
            sample_rate=16000,
            freqs=FREQS,
            ref_power=1e9,   # tuning knob
            alpha=0.35,      # smoothing per band
            _state=state
        )

        now = time.ticks_ms()
        if time.ticks_diff(now, next_frame) >= 0:
            display.draw_bars(levels)
            next_frame = time.ticks_add(next_frame, FRAME_MS)

except KeyboardInterrupt:
    print("Stopping...")

audio.deinit_audio()
