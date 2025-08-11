#include <QTRSensors.h>

QTRSensors qtr;  // Hauptobjekt für alle Sensoren

const uint8_t NUM_SENSORS = 3;
const uint8_t SENSOR_PINS[NUM_SENSORS] = {4,5,11};

uint16_t sensorValues[NUM_SENSORS];
const uint16_t THRESHOLD = 30; // 0 = weiß, höher = schwarz

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
  // Kalibrierte Werte lesen (0 = hell, 1000 = schwarz)
  qtr.readCalibrated(sensorValues);

  bool lineDetected = true;
  for (uint8_t i = 0; i < NUM_SENSORS; i++) {
    if (sensorValues[i] > THRESHOLD) {
      lineDetected = false;
      break;
    }
  }

  // Ausgabe
  Serial.print("Werte: ");
  for (uint8_t i = 0; i < NUM_SENSORS; i++) {
    Serial.print(sensorValues[i]);
    if (i < NUM_SENSORS - 1) Serial.print(", ");
  }

  if (lineDetected) {
    Serial.println("  -> LINIE erkannt!");
  } else {
    Serial.println("  -> keine Linie");
  }

  delay(1000);
}