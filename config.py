# TFT display resolution
SCREEN_WIDTH = 128
SCREEN_HEIGHT = 160

# TFT pin mapping (ESP32 GPIO numbers)
TFT_SCK_PIN = 27     # SCL on the TFT
TFT_MOSI_PIN = 33    # SDA on the TFT (data from ESP32 to TFT)
TFT_RES_PIN = 12     # RES
TFT_DC_PIN = 32      # DC
TFT_CS_PIN = 26      # CS

# If later you wire BL to a GPIO, we can add TFT_BL_PIN here.
