from machine import Pin, SPI
import time
import config

class ST7735:
    def __init__(self, spi, cs, dc, rst, width, height):
        self.spi = spi
        self.cs = cs
        self.dc = dc
        self.rst = rst
        self.width = width
        self.height = height
        self.x_offset = 1
        self.y_offset = 2

        # Set control pins
        self.cs.init(Pin.OUT, value=1)
        self.dc.init(Pin.OUT, value=0)
        self.rst.init(Pin.OUT, value=1)

        # Hardware reset
        self.reset()

        # Init sequence (this is a typical one for 1.8" 128x160 ST7735)
        self.init_display()

    def reset(self):
        self.rst.value(1)
        time.sleep_ms(50)
        self.rst.value(0)
        time.sleep_ms(50)
        self.rst.value(1)
        time.sleep_ms(50)

    def write_cmd(self, cmd):
        self.cs.value(0)
        self.dc.value(0)  # command
        self.spi.write(bytearray([cmd]))
        self.cs.value(1)

    def write_data(self, data):
        self.cs.value(0)
        self.dc.value(1)  # data
        self.spi.write(data)
        self.cs.value(1)

    def init_display(self):
       # Hard reset
       self.rst.value(1)
       time.sleep_ms(50)
       self.rst.value(0)
       time.sleep_ms(50)
       self.rst.value(1)
       time.sleep_ms(150)

       # Try standard ST7735R init (red tab)
       self.write_cmd(0x01)  # Software reset
       time.sleep_ms(150)

       self.write_cmd(0x11)  # Sleep out
       time.sleep_ms(150)

       self.write_cmd(0x3A)  # COLMOD: Pixel Format
       self.write_data(bytearray([0x05]))  # 16-bit color

       self.write_cmd(0x36)  # MADCTL (Memory Data Access Control)
       self.write_data(bytearray([0x60]))  # rotate 90° (typical)

       # Display inversion OFF
       self.write_cmd(0x20)

       # Display ON
       self.write_cmd(0x29)
       time.sleep_ms(100)

       # Clear screen white for visibility
       self.fill(0x0000)  # clear to black (no flashing here)



    def set_window(self, x0, y0, x1, y1):
        # Apply panel-specific offsets
        x0 += self.x_offset
        x1 += self.x_offset
        y0 += self.y_offset
        y1 += self.y_offset

        # Column address set
        self.write_cmd(0x2A)
        self.write_data(bytearray([
            0x00, x0,
            0x00, x1
        ]))
        # Row address set
        self.write_cmd(0x2B)
        self.write_data(bytearray([
            0x00, y0,
            0x00, y1
        ]))
        # Write to RAM
        self.write_cmd(0x2C)


    def fill(self, color):
        # Fill entire screen with a single 16-bit color
        self.set_window(0, 0, self.width - 1, self.height - 1)
        hi = (color >> 8) & 0xFF
        lo = color & 0xFF
        # One pixel = 2 bytes
        line = bytes([hi, lo]) * self.width  # use bytes, not bytearray
        for _ in range(self.height):
            self.write_data(line)


    def fill_rect(self, x, y, w, h, color):
        # Simple clipping
        if x < 0:
            w += x
            x = 0
        if y < 0:
            h += y
            y = 0
        if x + w > self.width:
            w = self.width - x
        if y + h > self.height:
            h = self.height - y
        if w <= 0 or h <= 0:
            return

        self.set_window(x, y, x + w - 1, y + h - 1)
        hi = (color >> 8) & 0xFF
        lo = color & 0xFF
        line = bytes([hi, lo]) * w  # use bytes
        for _ in range(h):
            self.write_data(line)



_tft = None  # global internal instance


_prev_heights = None


def draw_bars(levels):

    # Multi-bar draw with per-frame capped movement (prevents big wipes).

    global _prev_heights
    if _tft is None:
        return

    n = len(levels)
    if n == 0:
        return

    W = _tft.width
    H = _tft.height

    left = 2
    right = 2
    top = 6
    bottom = 6
    gap = 1

    usable_w = W - left - right
    usable_h = H - top - bottom

    gap = 2
    bar_w = (usable_w - gap * (n - 1)) // n
    bar_w = max(1, bar_w - 1)  # make bars slightly thinner
    if bar_w < 1:
        bar_w = 1

    if _prev_heights is None or len(_prev_heights) != n:
        _prev_heights = [0] * n
        _tft.fill(0x0000)

    bg = 0x0000

    # Cap how much each bar can move per frame to avoid huge wipes
    STEP_UP = 12    # pixels per frame up
    STEP_DOWN = 12   # pixels per frame down

    y_bot = top + usable_h

    for i, lvl in enumerate(levels):
        if lvl < 0: lvl = 0
        if lvl > 1: lvl = 1

        target_h = int(lvl * usable_h)
        old_h = _prev_heights[i]

        # Instant rise but still capped to reduce chunky bus bursts
        if target_h > old_h:
            new_h = target_h
        elif target_h < old_h:
            new_h = old_h - min(STEP_DOWN, old_h - target_h)
        else:
            new_h = old_h

        x = left + i * (bar_w + gap)

        color = _color_gradient(i, n, lvl)

        if new_h > old_h:
            added = new_h - old_h
            y_added = y_bot - new_h
            _tft.fill_rect(x, y_added, bar_w, added, color)
        elif new_h < old_h:
            removed = old_h - new_h
            y_removed = y_bot - old_h
            _tft.fill_rect(x, y_removed, bar_w, removed, bg)

        _prev_heights[i] = new_h



def init_display():
    
    # Initialize SPI and TFT display.
    # Must be called once from main.py

    global _tft

    # SPI bus
    spi = SPI(
        1,
        baudrate=20_000_000, 
        polarity=0,
        phase=0,
        sck=Pin(config.TFT_SCK_PIN),
        mosi=Pin(config.TFT_MOSI_PIN),
        miso=None,
    )

    cs = Pin(config.TFT_CS_PIN, Pin.OUT)
    dc = Pin(config.TFT_DC_PIN, Pin.OUT)
    rst = Pin(config.TFT_RES_PIN, Pin.OUT)

    _tft = ST7735(
        spi=spi,
        cs=cs,
        dc=dc,
        rst=rst,
        width=config.SCREEN_WIDTH,
        height=config.SCREEN_HEIGHT,
    )

    _tft.fill(0x0000)  # start with a clean black screen



_last_h = 0

def draw_vu(level):
    global _last_h
    if _tft is None:
        return

    if level < 0: level = 0
    if level > 1: level = 1

    W = _tft.width
    H = _tft.height

    x0 = 10
    x1 = W - 10
    bar_w = x1 - x0

    y_top = 6
    y_bot = H - 6
    max_h = y_bot - y_top

    target_h = int(level * max_h)

    STEP_DOWN = 5  # smooth fall speed

    # Instant rise, slow fall
    if target_h > _last_h:
        new_h = target_h
    elif target_h < _last_h:
        new_h = _last_h - min(STEP_DOWN, _last_h - target_h)
    else:
        new_h = _last_h

    bg = 0x0000
    fg = 0x07E0

    if new_h > _last_h:
        added = new_h - _last_h
        y_added = y_bot - new_h
        _tft.fill_rect(x0, y_added, bar_w, added, fg)

    elif new_h < _last_h:
        removed = _last_h - new_h
        y_removed = y_bot - _last_h
        _tft.fill_rect(x0, y_removed, bar_w, removed, bg)

    _last_h = new_h



def _color_gradient(pos, total, level=1.0):
    # Color gradient for the bars

    if total <= 1:
        t = 0.0
    else:
        t = pos / (total - 1)  # 0..1 left->right

    # Green -> Yellow -> Red
    if t < 0.5:
        # green to yellow
        r = int(255 * (t * 2))
        g = 255
    else:
        # yellow to red
        r = 255
        g = int(255 * (1 - (t - 0.5) * 2))

    # optional brightness scaling by level
    r = int(r * (0.4 + 0.6))
    g = int(g * (0.4 + 0.6))

    # clamp
    if r > 255: r = 255
    if g > 255: g = 255

    # RGB565
    return ((r & 0xF8) << 8) | ((g & 0xFC) << 3)