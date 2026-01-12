import time
import re
import serial
import serial.tools.list_ports
from pathlib import Path
from PIL import Image

# ===================== CONFIG =====================
INPUT_DIR = Path("C:/Users/NAMINDU SANJULA/Desktop/Semester 5/CO Project/Prototypes/HUD Helmet/esp32 Display/png to c code converter/image_input")
OUTPUT_DIR = Path("C:/Users/NAMINDU SANJULA/Desktop/Semester 5/CO Project/Prototypes/HUD Helmet/esp32 Display/png to c code converter/image_output")
XBM_DIR = Path("C:/Users/NAMINDU SANJULA/Desktop/Semester 5/CO Project/Prototypes/HUD Helmet/esp32 Display/png to c code converter/c_code_output")

WIDTH = 128
HEIGHT = 64
IMAGE_BYTES = 1024
CHUNK_SIZE = 128

DEVICE_NAME = "ESP32"   # Put your ESP32 Bluetooth name here

CHECK_INTERVAL = 1.0
# ==================================================

STX = 0x02
ETX = 0x03
CMD_IMG_START = 0x10
CMD_IMG_DATA  = 0x11
CMD_IMG_END   = 0x12

INPUT_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)
XBM_DIR.mkdir(exist_ok=True)

processed = set()

# ---------- Auto-detect ESP32 COM port ----------
def find_esp32_comport(device_name: str):
    ports = serial.tools.list_ports.comports()
    for p in ports:
        if device_name.lower() in p.description.lower():
            print(f" Found ESP32 Bluetooth port: {p.device}")
            return p.device
    raise RuntimeError(f"ESP32 device '{device_name}' not found. Make sure it's paired.")

BT_COM_PORT = find_esp32_comport(DEVICE_NAME)
BT_BAUDRATE = 115200

# ---------- Bluetooth helpers ----------
def crc8(data: bytes) -> int:
    c = 0
    for b in data:
        c ^= b
    return c

def send_packet(ser, cmd: int, payload: bytes):
    length = len(payload)
    packet = bytearray()
    packet.append(STX)
    packet.append(cmd)
    packet.append(length & 0xFF)
    packet.append((length >> 8) & 0xFF)
    packet.extend(payload)
    packet.append(crc8(payload))
    packet.append(ETX)
    ser.write(packet)
    time.sleep(0.02)  # small pacing delay

# ---------- XBM handling ----------
def load_xbm_raw(path: Path) -> bytes:
    with open(path) as f:
        data = f.read()
    hex_bytes = re.findall(r'0x[0-9A-Fa-f]{2}', data)
    raw = bytes(int(b, 16) for b in hex_bytes)
    if len(raw) != IMAGE_BYTES:
        raise ValueError("Invalid XBM size")
    return raw

def send_xbm_to_esp32(ser, xbm_path: Path):
    print(f" Sending: {xbm_path.name}")
    raw = load_xbm_raw(xbm_path)
    send_packet(ser, CMD_IMG_START, bytes([WIDTH, HEIGHT]))
    for offset in range(0, IMAGE_BYTES, CHUNK_SIZE):
        chunk = raw[offset:offset + CHUNK_SIZE]
        payload = offset.to_bytes(2, "little") + chunk
        send_packet(ser, CMD_IMG_DATA, payload)
    send_packet(ser, CMD_IMG_END, b"")
    print(" Image sent\n")

# ---------- Image processing ----------
def image_to_xbm(img, name):
    pixels = img.load()
    bytes_out = []
    for y in range(HEIGHT):
        for x_byte in range(0, WIDTH, 8):
            byte = 0
            for bit in range(8):
                x = x_byte + bit
                if pixels[x, y] == 0:
                    byte |= (1 << bit)
            bytes_out.append(byte)
    xbm_path = XBM_DIR / f"{name}.xbm"
    with open(xbm_path, "w") as f:
        f.write(f"#define {name}_width {WIDTH}\n")
        f.write(f"#define {name}_height {HEIGHT}\n")
        f.write(f"static unsigned char {name}_bits[] = {{\n")
        for i, b in enumerate(bytes_out):
            f.write(f"  0x{b:02X}")
            if i < len(bytes_out) - 1:
                f.write(",")
            if (i + 1) % 12 == 0:
                f.write("\n")
        f.write("\n};\n")
    return xbm_path

def process_image(ser, image_path: Path):
    print(f"➡ Processing: {image_path.name}")
    img = Image.open(image_path)
    img = img.convert("L")
    img = img.resize((WIDTH, HEIGHT), Image.LANCZOS)
    img = img.convert("1", dither=Image.FLOYDSTEINBERG)
    bmp_path = OUTPUT_DIR / (image_path.stem + ".bmp")
    img.save(bmp_path)
    xbm_path = image_to_xbm(img, image_path.stem)
    send_xbm_to_esp32(ser, xbm_path)
    image_path.unlink()
    print(f" Deleted: {image_path.name}\n")

# ---------- Main loop ----------
print(" Connecting to ESP32...")
ser = serial.Serial(BT_COM_PORT, BT_BAUDRATE, timeout=2)
print(" Bluetooth connected\n")
print(" Watching for images...\n")

while True:
    try:
        for img_file in INPUT_DIR.glob("*.png"):
            if img_file not in processed:
                processed.add(img_file)
                process_image(ser, img_file)
        time.sleep(CHECK_INTERVAL)
    except KeyboardInterrupt:
        print("\n Stopped")
        ser.close()
        break


