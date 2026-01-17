# bands.py
import math

def _prepare(freqs, sample_rate, n):
    """
    Precompute Goertzel parameters for each target frequency.
    """
    params = []
    for f in freqs:
        k = int(0.5 + (n * f) / sample_rate)
        w = (2.0 * math.pi * k) / n
        cos_w = math.cos(w)
        sin_w = math.sin(w)
        coeff = 2.0 * cos_w
        params.append((cos_w, sin_w, coeff))
    return params


def _goertzel_power_with_params(samples, mean, cos_w, sin_w, coeff):
    """
    Goertzel power using precomputed parameters and shared mean.
    """
    s0 = 0.0
    s1 = 0.0
    s2 = 0.0

    for x in samples:
        x = x - mean
        s0 = x + coeff * s1 - s2
        s2 = s1
        s1 = s0

    real = s1 - s2 * cos_w
    imag = s2 * sin_w
    return real * real + imag * imag


def compute_bars(samples, sample_rate, freqs, ref_power=1e6, alpha=0.35, _state=None):
    """
    Compute normalized 0..1 levels for each frequency in freqs.
    Optimized:
      - precomputes trig/coeff once per (freqs, sample_rate, block_size)
      - computes mean once per block
    Returns: (levels, state)
    """
    n = len(samples)
    if n == 0:
        return [], _state if _state is not None else {"prev": []}

    if _state is None:
        _state = {}

    # Initialize / refresh cached parameters if needed
    sig = (tuple(freqs), sample_rate, n)
    if _state.get("sig") != sig:
        _state["sig"] = sig
        _state["params"] = _prepare(freqs, sample_rate, n)
        _state["prev"] = [0.0] * len(freqs)

    params = _state["params"]
    prev = _state["prev"]

    # Mean once (DC removal)
    s = 0
    for x in samples:
        s += x
    mean = s / n

    out = []
    for i, (cos_w, sin_w, coeff) in enumerate(params):
        p = _goertzel_power_with_params(samples, mean, cos_w, sin_w, coeff)

        lvl = p / ref_power
        if lvl > 1.0:
            lvl = 1.0
        elif lvl < 0.0:
            lvl = 0.0

        # Smooth per band
        lvl = alpha * lvl + (1.0 - alpha) * prev[i]
        prev[i] = lvl
        out.append(lvl)

    return out, _state
