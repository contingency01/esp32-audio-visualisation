import math
from ulab import numpy as np


def _prepare(freqs, sample_rate, n):

    # Prepare cosine/sine basis matrices
    # Returns:
    # cos_mat: shape (nbands, n)
    # sin_mat: shape (nbands, n)

    t = np.arange(n, dtype=np.float)
    cos_rows = []
    sin_rows = []

    for f in freqs:
        # k-rounding
        k = int(0.5 + (n * f) / sample_rate)
        w = (2.0 * math.pi * k) / n

        ang = w * t
        cos_rows.append(np.cos(ang))
        sin_rows.append(np.sin(ang))

    # ulab: np.array(list_of_rows) produces a 2D array
    cos_mat = np.array(cos_rows)
    sin_mat = np.array(sin_rows)
    return cos_mat, sin_mat


def compute_bars(samples, freqs, sample_rate, ref_power=1e9, alpha=0.35, _state=None):
    

    #Inputs:
    #samples: ulab numpy 1D array 
    #freqs: list of target frequencies
    #sample_rate
    #ref_power: tuning 
    #alpha: smoothing factor per band
    #_state: pass-through cache dict


    if _state is None:
        _state = {}

    if samples is None:
        nb = len(freqs)
        if "prev" not in _state or len(_state["prev"]) != nb:
            _state["prev"] = np.zeros(nb, dtype=np.float)
        return _state["prev"].tolist(), _state

    # Causes errors if not
    if not hasattr(samples, "astype"):
        # Keep it int16 to minimize RAM for now
        samples = np.array(samples, dtype=np.int16)

    n = len(samples)
    nb = len(freqs)

    sig = (tuple(freqs), int(sample_rate), int(n))
    if _state.get("sig") != sig:
        _state["sig"] = sig
        _state["cos_mat"], _state["sin_mat"] = _prepare(freqs, sample_rate, n)
        _state["prev"] = np.zeros(nb, dtype=np.float)

    cos_mat = _state["cos_mat"]
    sin_mat = _state["sin_mat"]
    prev = _state["prev"]

    # Convert once to float and remove DC (mean)
    # NOTE: apparently some ulab firmware builds don't provide ndarray.astype()

    x = np.array(samples, dtype=np.float)
    x = x - np.mean(x)

    # Vectorized Goertzel energy at each band frequency:
    # real_i = sum x[t]*cos(w_i t)
    # imag_i = sum x[t]*sin(w_i t)
    # power_i = real_i^2 + imag_i^2
    
    real = np.dot(cos_mat, x)
    imag = np.dot(sin_mat, x)
    p = real * real + imag * imag

    # Normalization
    lvl = p / ref_power
    lvl = np.clip(lvl, 0.0, 1.0)

    # Smooth per band: lvl = alpha*lvl + (1-alpha)*prev
    lvl = alpha * lvl + (1.0 - alpha) * prev
    _state["prev"] = lvl

    return lvl.tolist(), _state