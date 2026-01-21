import math

_prev = 0.0  # for smoothing

def rms_level(samples, rms_ref=5000.0, alpha=0.25):

    # Returns a smoothed loudness level in [0,1].
    # DC-removes samples
    # Computes RMS
    # Normalizes by rms_ref
    # Smooths with alpha

    global _prev

    n = len(samples)
    if n == 0:
        return 0.0

    # mean (DC offset)
    s = 0
    for x in samples:
        s += x
    mean = s / n

    # RMS of (x - mean)
    ss = 0.0
    for x in samples:
        d = x - mean
        ss += d * d

    rms = math.sqrt(ss / n)

    # normalize to 0..1
    level = rms / rms_ref
    if level > 1.0:
        level = 1.0
    if level < 0.0:
        level = 0.0

    # smooth
    level = alpha * level + (1.0 - alpha) * _prev
    _prev = level
    return level
