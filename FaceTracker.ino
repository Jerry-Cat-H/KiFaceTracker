#include <Servo.h>

// --- Configuration ---
const int PAN_PIN = 9;   // Pin for Pan Servo (horizontal)
const int TILT_PIN = 10; // Pin for Tilt Servo (vertical)
const int RELAY_PIN = 8; // Pin for Relay (light bulb)

Servo panServo;
Servo tiltServo;

int panAngle = 90;
int tiltAngle = 90;
int relayState = 0;

void setup() {
  Serial.begin(115200);
  
  // 等待 Python 連線 (Leonardo 等原生 USB 晶片必備)
  while (!Serial) {
    ; // wait for serial port to connect.
  }
  
  // Attach servos
  panServo.attach(PAN_PIN);
  tiltServo.attach(TILT_PIN);
  
  // Set initial positions
  panServo.write(panAngle);
  tiltServo.write(tiltAngle);
  
  // Setup relay
  pinMode(RELAY_PIN, OUTPUT);
  digitalWrite(RELAY_PIN, LOW); // Assume LOW is off. Change to HIGH if your relay is active-low
  
  // Wait a moment for servos to reach initial position
  delay(500);
  Serial.println("Arduino Face Tracker Ready");
}

void loop() {
  // Check if data is available to read
  if (Serial.available() > 0) {
    // Read the incoming string until newline character '\n'
    String data = Serial.readStringUntil('\n');
    
    // Expected format: P<pan>T<tilt>R<relay>
    // Example: P120T45R1
    
    if (data.startsWith("P")) {
      // Find the positions of 'T' and 'R' to parse the string
      int tIndex = data.indexOf('T');
      int rIndex = data.indexOf('R');
      
      if (tIndex != -1 && rIndex != -1) {
        // Extract the substrings and convert to integers
        String panStr = data.substring(1, tIndex);
        String tiltStr = data.substring(tIndex + 1, rIndex);
        String relayStr = data.substring(rIndex + 1);
        
        panAngle = panStr.toInt();
        tiltAngle = tiltStr.toInt();
        relayState = relayStr.toInt();
        
        // Constrain angles to safe ranges (0-180)
        panAngle = constrain(panAngle, 0, 180);
        tiltAngle = constrain(tiltAngle, 0, 180);

        Serial.println("OK P" + String(panAngle) + " T" + String(tiltAngle) + " R" + String(relayState));

        // Update servos
        panServo.write(panAngle);
        tiltServo.write(tiltAngle);
        
        // Update relay
        if (relayState == 1) {
          digitalWrite(RELAY_PIN, HIGH);
        } else {
          digitalWrite(RELAY_PIN, LOW);
        }
      }
    }
  }
}
