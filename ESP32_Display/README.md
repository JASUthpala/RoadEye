# ESP32 Bluetooth Image Converter & Sender

This Python script monitors a folder for PNG images, converts them into a **128×64 monochrome XBM format**, and transmits the image data to an **ESP32 over Bluetooth (Serial)** using a custom packet protocol.

It is ideal for projects such as **HUD helmet displays, OLED screens, or embedded ESP32 graphics applications**.

---

## Features

- Watches a directory for new PNG images  
- Automatically resizes images to 128×64  
- Converts images to monochrome using dithering  
- Generates XBM (C-compatible bitmap) files  
- Sends images to ESP32 via Bluetooth Serial  
- Uses chunked transfer with CRC checking  
- Automatically deletes processed images  

---

## Folder Structure

```
image_input/     → Place PNG images here
image_output/    → Converted BMP images (preview/debug)
c_code_output/   → Generated XBM C files
```

All directories are created automatically if missing.

---

## Requirements

### Software
- Python 3.8 or newer
- ESP32 paired with the computer via Bluetooth (Serial profile)

### Python Dependencies

Install required libraries:

```
pip install pyserial pillow
```

---

## Configuration

Edit the CONFIG section at the top of the script:

```python
INPUT_DIR  = Path("path/to/image_input")
OUTPUT_DIR = Path("path/to/image_output")
XBM_DIR    = Path("path/to/c_code_output")

WIDTH  = 128
HEIGHT = 64

DEVICE_NAME = "ESP32"
```

### Notes
- `DEVICE_NAME` must match the Bluetooth name of your ESP32
- Image resolution is fixed at **128×64**
- Image buffer size is **1024 bytes**

---

## How It Works

1. Automatically detects the ESP32 Bluetooth COM port
2. Monitors the input directory for PNG images
3. Converts images:
   - Grayscale
   - Resize to 128×64
   - Floyd–Steinberg dithering
   - 1-bit monochrome
4. Generates an XBM bitmap file
5. Sends image data to ESP32:
   - Start packet (resolution)
   - Data packets (128-byte chunks)
   - End packet
6. Deletes the PNG after successful transfer

---

## Bluetooth Packet Format

```
[STX][CMD][LEN_L][LEN_H][PAYLOAD][CRC][ETX]
```

### Commands

| Command | Value | Description |
|-------|-------|-------------|
| IMG_START | 0x10 | Start image transfer |
| IMG_DATA  | 0x11 | Image data chunk |
| IMG_END   | 0x12 | End image transfer |

CRC is calculated using XOR over the payload.

---

## Running the Script

```
python bluetooth_converter.py
```

Copy PNG images into the input directory while the script is running.

Stop execution using:

```
Ctrl + C
```

---

## ESP32 Firmware Requirements

Your ESP32 code should:
- Read Bluetooth Serial packets
- Validate CRC
- Reassemble image data
- Display the bitmap on a 128×64 screen

---

## Common Issues

### ESP32 not detected
- Ensure Bluetooth pairing is complete
- Verify device name matches `DEVICE_NAME`
- Check Bluetooth Serial is enabled

### Display issues
- Confirm display resolution
- Check bit ordering compatibility
- Verify chunk offsets and buffer handling

---

## Applications

- HUD helmet displays
- OLED dashboards
- Embedded UI prototyping
- Wireless ESP32 image updates

---

## License

This project is intended for educational and prototyping purposes.
