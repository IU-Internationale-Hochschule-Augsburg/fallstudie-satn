#include <QTRSensors.h>
#include <A4990MotorShield.h>

A4990MotorShield motors;

QTRSensors qtr;  // Hauptobjekt für alle Sensoren

const uint8_t NUM_SENSORS = 1;
const uint8_t SENSOR_PINS[NUM_SENSORS] = {11}; 

uint16_t sensorValues[NUM_SENSORS];
const uint16_t THRESHOLD = 100; // 0 bis 100 hell, höher = dunkel

void turnOnSpot(int angleInt) {

  motors.setSpeeds(0, 0);
  // Gültigkeit prüfen
  if (angleInt < -360 || angleInt > 360) {
    Serial.println("Ungültiger Winkel!");
    return;
  }

  // Drehrichtung bestimmen
  int leftSpeed = 0;
  int rightSpeed = 0;

  if (angleInt > 0) {
    // Rechtsdrehung
    leftSpeed = -255;
    rightSpeed = 255;
  } else if (angleInt < 0) {
    // Linksdrehung
    leftSpeed = 255;
    rightSpeed = -255;
  } else {
    return; // Kein Drehen nötig
  }

  int duration = round(abs(angleInt) * 3.3);  // ms = Winkel * Kalibrierwert

  motors.setSpeeds(leftSpeed, rightSpeed);
  delay(duration);
  motors.setSpeeds(0, 0);
}

void setup() {
  Serial.begin(9600);
  delay(500);

  motors.setSpeeds(0,0);

  // Forwards
 


  // RC-Sensoren konfigurieren
  qtr.setTypeRC();
  qtr.setSensorPins(SENSOR_PINS, NUM_SENSORS);

  // Kalibrieren: Roboter über hell und dunkel bewegen
  Serial.println(F("Kalibriere Sensoren..."));

  for (uint16_t i = 0; i < 500; i++) {
    qtr.calibrate();
    delay(20);
  }
  Serial.println(F("Kalibrierung fertig."));
}

void loop() {

qtr.readCalibrated(sensorValues);
 for (int speed = 0; speed <= 40; speed++)
  {
    motors.setM1Speed(speed); //links
    motors.setM2Speed(speed +10); //rechts
    
  }
  bool lineDetected = false;
    if (sensorValues[0] > THRESHOLD) {
      lineDetected = true;
    }

  // Ausgabe
  Serial.print("Werte: ");
  Serial.print(sensorValues[0]);
    
  if (lineDetected) {
    Serial.println("  -> Linie erkannt!");
    turnOnSpot(90);
     for (int speed = 0; speed <= 25; speed++)
  {
    motors.setM1Speed(speed); //links
    motors.setM2Speed(speed +10); //rechts
  
  }
  } else {
    Serial.println("  -> keine Linie");
  }
}