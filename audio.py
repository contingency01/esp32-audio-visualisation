# audio.py
from machine import I2S, Pin

# Pin mapping (your wiring)
_I2S_BCK = 14   # SCK
_I2S_WS  = 25   # WS / LRCLK
_I2S_SD  = 34   # SD (input-only is fine)

# Audio settings
_RATE = 16000
_SAMPLES = 64
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
        ibuf=_SAMPLES * 4,
    )


def read_block():
    if _i2s is None:
        raise RuntimeError("Call init_audio() first")

    n = _i2s.readinto(_BUF)
    if not n:
        return [0] * _SAMPLES

    count = min(n // 2, _SAMPLES)
    out = []

    for i in range(count):
        lo = _BUF[2*i]
        hi = _BUF[2*i + 1]
        val = (hi << 8) | lo
        if val & 0x8000:
            val -= 0x10000
        out.append(val)

    if count < _SAMPLES:
        out.extend([0] * (_SAMPLES - count))

    return out


def deinit_audio():
    global _i2s
    if _i2s:
        _i2s.deinit()
        _i2s = None
