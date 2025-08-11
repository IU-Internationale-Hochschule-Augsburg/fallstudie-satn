#include <QTRSensors.h>

QTRSensors qtr;  // Hauptobjekt für alle Sensoren

const uint8_t NUM_SENSORS = 1;
const uint8_t SENSOR_PINS[NUM_SENSORS] = {11};

uint16_t sensorValues[NUM_SENSORS];
const uint16_t THRESHOLD = 100; // 0 bis 100 = hell, höher = schwarz

void setup() {
  Serial.begin(9600);
  delay(500);

  // RC-Sensoren konfigurieren
  qtr.setTypeRC();
  qtr.setSensorPins(SENSOR_PINS, NUM_SENSORS);

  // Kalibrieren: Roboter über hell und dunkel bewegen
  Serial.println(F("Kalibriere Sensoren..."));
  for (uint16_t i = 0; i < 1000; i++) {
    qtr.calibrate();
    delay(20);
  }
  Serial.println(F("Kalibrierung fertig."));
}

void loop() {
  // Kalibrierte Werte lesen 
  qtr.readCalibrated(sensorValues);

  bool lineDetected = true;
  if (sensorValues[0] > THRESHOLD) {
    lineDetected = false;
  }
  

  // Ausgabe
  Serial.print("Werte: ");
  Serial.print(sensorValues[i]);

  if (lineDetected) {
    Serial.println("  -> LINIE erkannt!");
  } else {
    Serial.println("  -> keine Linie");
  }
}