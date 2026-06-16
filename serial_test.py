import serial
import time

# --- 與 face_tracker.py 相同的設定 ---
SERIAL_PORT = '/dev/cu.usbmodemFX2348N1'
BAUD_RATE = 115200

print(f"Connecting to {SERIAL_PORT} ...")
ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=0.1)
time.sleep(2)  # 等 Arduino reset 完成
print("Connected. Sending fixed command 'P90T90R0' twice per second.\n")

buf = ""
count = 0
last_send = 0.0

while True:
    # --- 讀取 Arduino 回傳 ---
    data = ser.read(ser.in_waiting or 1)
    if data:
        buf += data.decode('utf-8', errors='ignore')
        while '\n' in buf:
            line, buf = buf.split('\n', 1)
            line = line.strip()
            if line:
                print(f"    [Arduino] {line}")

    # --- 每 0.5 秒送一次固定指令 (繼電器固定關，不切換) ---
    now = time.time()
    if now - last_send >= 0.5:
        ser.write(b"P90T90R0\n")
        last_send = now
        count += 1
        print(f"--> sent #{count}: P90T90R0")
