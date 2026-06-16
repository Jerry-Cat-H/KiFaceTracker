import cv2
import serial
import time
import sys
  
# --- Configuration ---
SERIAL_PORT =  '/dev/cu.usbmodemFX2348N1'   # Change this to your Arduino's COM port!
BAUD_RATE = 115200
CAMERA_INDEX = 0      # 1 代表外接 USB 鏡頭 (如果抓不到畫面，可以改回 0 試試看)

# --- Initialize Serial Communication ---
arduino = None
try:
    arduino = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=0.1)
    print(f"Successfully connected to Arduino on {SERIAL_PORT}")
    time.sleep(2)  # Wait for Arduino to reset after serial connection
except Exception as e:
    print(f"Error opening serial port {SERIAL_PORT}: {e}")
    print("Running in 'Camera Only' mode (no serial communication).")

# --- Initialize OpenCV Face Detection ---
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# --- Setup Camera ---
cap = cv2.VideoCapture(CAMERA_INDEX)
if not cap.isOpened():
    print("Error: Could not open camera.")
    sys.exit()

# Servo Angle Limits (adjust these based on your mechanical setup)
PAN_MIN, PAN_MAX = 0, 180
TILT_MIN, TILT_MAX = 0, 180

# Current Servo Angles (start at center)
pan_angle = 90
tilt_angle = 90

# Tuning parameters for smoothing movement
SMOOTHING = 0.2

def map_value(value, in_min, in_max, out_min, out_max):
    """Maps a value from one range to another."""
    return int((value - in_min) * (out_max - out_min) / (in_max - in_min) + out_min)

print("Starting face tracking...")

while cap.isOpened():
    success, image = cap.read()
    if not success:
        print("Ignoring empty camera frame.")
        continue

    # Convert to grayscale for Haar Cascades
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Detect faces
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
    
    h, w, _ = image.shape
    relay_state = 0

    if len(faces) > 0:
        # We only track the first detected face for simplicity
        (x, y, fw, fh) = faces[0]
        
        # Draw bounding box
        cv2.rectangle(image, (x, y), (x + fw, y + fh), (255, 0, 0), 2)
        
        # Calculate center of the face in pixels
        cx = x + fw // 2
        cy = y + fh // 2
        
        # Calculate relative position (0.0 to 1.0)
        face_center_x = cx / w
        face_center_y = cy / h
        
        # Draw a circle at the center
        cv2.circle(image, (cx, cy), 5, (0, 0, 255), -1)

        # --- Calculate Servo Angles ---
        # X coordinate controls Pan. Usually, left on screen means servo moves right
        target_pan = map_value(face_center_x, 0.0, 1.0, PAN_MAX, PAN_MIN) 
        
        # Y coordinate controls Tilt.
        target_tilt = map_value(face_center_y, 0.0, 1.0, TILT_MAX, TILT_MIN) 
        
        # Smooth the movement
        pan_angle = int(pan_angle + (target_pan - pan_angle) * SMOOTHING)
        tilt_angle = int(tilt_angle + (target_tilt - tilt_angle) * SMOOTHING)
        
        # Clamp values
        pan_angle = max(PAN_MIN, min(PAN_MAX, pan_angle))
        tilt_angle = max(TILT_MIN, min(TILT_MAX, tilt_angle))
        
        relay_state = 1
        
        # Display Text
        cv2.putText(image, f"Pan: {pan_angle} Tilt: {tilt_angle} Relay: ON", (10, 30), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.putText(image, f"Face XY: ({cx}, {cy})", (10, 60), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
    else:
        cv2.putText(image, "No Face - Relay: OFF", (10, 30), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

    # --- Send Data to Arduino ---
    if arduino:
        try:
            # Format: P<pan>T<tilt>R<relay>\n
            data_string = f"P{pan_angle}T{tilt_angle}R{relay_state}\n"
            arduino.write(data_string.encode('utf-8'))
            if arduino.in_waiting:
                print(arduino.readline().decode('utf-8', errors='ignore').strip())
        except Exception as e:
            print(f"Serial write error: {e}")
            arduino = None # Stop trying to write if disconnected

    # Show the image
    cv2.imshow('Face Tracker', image)
    
    # Press 'q' to quit
    if cv2.waitKey(5) & 0xFF == ord('q'):
        break

# Cleanup
cap.release()
cv2.destroyAllWindows()
if arduino:
    try:
        # Turn off relay when exiting
        arduino.write(b"P90T90R0\n")
        arduino.close()
    except:
        pass
