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
relay = 0

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

    # --- 每 1 秒送一次，繼電器慢速開/關交替 ---
    now = time.time()
    if now - last_send >= 1.0:
        relay = 1 - relay  # 0 -> 1 -> 0 交替
        msg = f"P90T90R{relay}\n"
        ser.write(msg.encode())
        last_send = now
        count += 1
        print(f"--> sent #{count}: {msg.strip()}  (繼電器應該每秒喀一聲)")
