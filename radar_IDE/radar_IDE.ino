#include <Servo.h>

const int TRIG_PIN   = 9;
const int ECHO_PIN   = 10;
const int SERVO_PIN  = 6;
const int REDLED_PIN = 2;
const int YLWLED_PIN = 3;  
const int BUZZER_PIN = 5;
const int POT_PIN    = A0; 

const int SWEEP_MIN = 15;
const int SWEEP_MAX = 165;
const int SWEEP_STEP = 2;
const int SERVO_MOVE_DELAY = 30; 

int servoAngle = SWEEP_MIN;
int sweepDir = 1;
Servo radarServo;

enum SystemState { NORMAL, WARNING, DANGER };
SystemState state = NORMAL;

bool isMuted = false;
bool repairMode = false;

void setup() {
  Serial.begin(9600);
  pinMode(TRIG_PIN, OUTPUT);
  pinMode(ECHO_PIN, INPUT);
  pinMode(REDLED_PIN, OUTPUT);
  pinMode(YLWLED_PIN, OUTPUT);
  pinMode(BUZZER_PIN, OUTPUT);
  
  radarServo.attach(SERVO_PIN);
  radarServo.write(servoAngle);
  delay(500); 
}

float getRawDistance() {
  digitalWrite(TRIG_PIN, LOW);
  delayMicroseconds(2);
  digitalWrite(TRIG_PIN, HIGH);
  delayMicroseconds(10);
  digitalWrite(TRIG_PIN, LOW);

  long duration = pulseIn(ECHO_PIN, HIGH, 25000);
  if (duration == 0) return 999.0;
  return duration * 0.034 / 2;
}

float readDistanceCM() {
  float d1 = getRawDistance();
  delay(10); 
  float d2 = getRawDistance();
  delay(10);
  float d3 = getRawDistance();

  if ((d1 >= d2 && d1 <= d3) || (d1 >= d3 && d1 <= d2)) return d1;
  if ((d2 >= d1 && d2 <= d3) || (d2 >= d3 && d2 <= d1)) return d2;
  return d3;
}

void loop() {
  if (Serial.available() > 0) {
    char cmd = Serial.read();
    if (cmd == 'M') isMuted = true;   
    if (cmd == 'U') isMuted = false;  
    if (cmd == 'R') repairMode = true; 
    if (cmd == 'N') repairMode = false;
  }

  int potValue = analogRead(POT_PIN);
  float dangerThreshold = map(potValue, 0, 1023, 10, 40);
  float warningThreshold = dangerThreshold + 20;

  float distance = readDistanceCM();

  if (distance <= dangerThreshold) {
    state = DANGER;
  } else if (distance <= warningThreshold) {
    state = WARNING;
  } else {
    state = NORMAL;
  }

  if (state == DANGER) {
    digitalWrite(REDLED_PIN, HIGH);
    digitalWrite(YLWLED_PIN, LOW);
  } 
  else if (state == WARNING) {
    digitalWrite(REDLED_PIN, LOW);
    digitalWrite(YLWLED_PIN, HIGH);
  } 
  else {
    digitalWrite(REDLED_PIN, LOW);
    digitalWrite(YLWLED_PIN, LOW);
  }

  if (isMuted) {
    analogWrite(BUZZER_PIN, 0); 
  } else {
    if (state == DANGER)      analogWrite(BUZZER_PIN, 110); 
    else if (state == WARNING) analogWrite(BUZZER_PIN, 5);
    else                      analogWrite(BUZZER_PIN, 0); 
  }

  if (state != DANGER || repairMode) {
    radarServo.write(servoAngle);
    delay(SERVO_MOVE_DELAY); 
    
    servoAngle += sweepDir * SWEEP_STEP;
    if (servoAngle >= SWEEP_MAX) { servoAngle = SWEEP_MAX; sweepDir = -1; }
    if (servoAngle <= SWEEP_MIN) { servoAngle = SWEEP_MIN; sweepDir = 1; }
  } else {
    delay(50); 
  }

  Serial.print(servoAngle);
  Serial.print(",");
  Serial.print(distance);
  Serial.print(",");
  Serial.print((int)state);
  Serial.print(",");
  Serial.println(isMuted ? 1 : 0);
}