from machine import I2S, Pin
from ulab import numpy as np

# Pin mapping (your wiring)
_I2S_BCK = 14   # SCK
_I2S_WS  = 25   # WS / LRCLK
_I2S_SD  = 34   # SD (input-only is fine)

# Audio settings
_RATE = 16000
_SAMPLES = 128
_BUF = bytearray(_SAMPLES * 2)  # 16-bit mono

_i2s = None


def init_audio():
    global _i2s
    _i2s = I2S(
        0,
        sck=Pin(_I2S_BCK),
        ws=Pin(_I2S_WS),
        sd=Pin(_I2S_SD),
        mode=I2S.RX,
        bits=16,
        format=I2S.MONO,
        rate=_RATE,
        ibuf=_SAMPLES * 4,   # small buffer; you can raise later if needed
    )


def _bytes_to_int16_vec(buf, nbytes):
    """
    Convert first nbytes of buf into an int16 ulab vector (little-endian).
    Returns a ulab numpy array dtype=int16.
    """
    # nbytes must be multiple of 2 for int16
    nbytes &= ~1
    if nbytes <= 0:
        return np.zeros(_SAMPLES, dtype=np.int16)

    # Try fastest path first (if your ulab build supports it)
    try:
        x = np.frombuffer(buf, dtype=np.int16)
        n = nbytes // 2
        if n < len(x):
            x = x[:n]
    except AttributeError:
        # Fallback: memoryview cast to signed short ('h') then copy into ulab array
        mv = memoryview(buf)[:nbytes].cast("h")
        x = np.array(mv, dtype=np.int16)

    # Ensure exact length _SAMPLES (pad with zeros if short; trim if long)
    if len(x) < _SAMPLES:
        x = np.concatenate((x, np.zeros(_SAMPLES - len(x), dtype=np.int16)))
    elif len(x) > _SAMPLES:
        x = x[:_SAMPLES]

    return x


def read_block():
    """
    Returns: ulab numpy vector of length _SAMPLES (dtype int16).
    """
    if _i2s is None:
        raise RuntimeError("Call init_audio() first")

    n = _i2s.readinto(_BUF)
    if not n:
        return np.zeros(_SAMPLES, dtype=np.int16)

    return _bytes_to_int16_vec(_BUF, n)


def deinit_audio():
    global _i2s
    if _i2s:
        _i2s.deinit()
        _i2s = None