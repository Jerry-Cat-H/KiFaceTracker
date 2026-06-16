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
  Serial.setTimeout(50);

  while (!Serial) {
    ;
  }

  panServo.attach(PAN_PIN);
  tiltServo.attach(TILT_PIN);

  panServo.write(panAngle);
  tiltServo.write(tiltAngle);

  pinMode(RELAY_PIN, OUTPUT);
  digitalWrite(RELAY_PIN, HIGH); // Active-LOW relay: HIGH = off

  delay(500);
  Serial.println("Arduino Face Tracker Ready");
}

void loop() {
  if (Serial.available() > 0) {
    char buf[32];
    int len = Serial.readBytesUntil('\n', buf, sizeof(buf) - 1);
    buf[len] = '\0';

    int p = -1, t = -1, r = -1;
    if (sscanf(buf, "P%dT%dR%d", &p, &t, &r) == 3) {
      panAngle   = constrain(p, 0, 180);
      tiltAngle  = constrain(t, 0, 180);
      relayState = r;

      panServo.write(panAngle);
      tiltServo.write(tiltAngle);

      // Active-LOW relay: LOW = on, HIGH = off
      digitalWrite(RELAY_PIN, relayState == 1 ? LOW : HIGH);

      Serial.print("OK P");
      Serial.print(panAngle);
      Serial.print(" T");
      Serial.print(tiltAngle);
      Serial.print(" R");
      Serial.println(relayState);
    }
  }
}
