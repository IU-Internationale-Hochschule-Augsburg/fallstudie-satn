#include <A4990MotorShield.h>

/* Fährt gleichmäßig durch for-Schleife und Erhöhung der Geschwindigkeit des rechten Motors, Drehwinkel ist kalibriert mit dem Wert 3.3*/

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

      for (int speed = 0; speed <= 25; speed++)
  {
    motors.setM1Speed(speed); //links
    motors.setM2Speed(speed +10); //rechts
  
  }

}

void loop() {
  // put your main code here, to run repeatedly:

}
