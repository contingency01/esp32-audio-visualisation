import time
import display
import audio
import bands

print("Init display...")
display.init_display()

print("Init audio...")
audio.init_audio()

# Band center frequencies (Hz)
FREQS = [80, 300, 500, 700, 900, 1100, 1600, 2500, 4000, 6000]
WEIGHTS = [1.0] * len(FREQS)

state = None

# Frame pacing for smooth display
FRAME_MS = 16  # ~60 FPS
next_frame = time.ticks_ms()

print("Running frequency bars (Ctrl+C to stop)")
try:
    while True:
        samples = audio.read_block()

        # Software mic gain (kept as-is; we can vectorize later)
        GAIN = 10.0
        samples = [max(-32768, min(32767, int(x * GAIN))) for x in samples]

        # Use a lower alpha to reduce jitter (smoother bars)
        levels, state = bands.compute_bars(
            samples,
            sample_rate=16000,
            freqs=FREQS,
            ref_power=1e9,
            alpha=0.20,
            _state=state,
        )

        levels = [min(1.0, levels[i] * WEIGHTS[i]) for i in range(len(levels))]

        now = time.ticks_ms()
        if time.ticks_diff(now, next_frame) >= 0:
            display.draw_bars(levels)
            next_frame = time.ticks_add(next_frame, FRAME_MS)

except KeyboardInterrupt:
    print("Stopping...")

audio.deinit_audio()
