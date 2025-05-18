#include <Zumo32U4.h>

Zumo32U4Motors motors;
Zumo32U4Encoders encoders;

void turnOnSpot(int angle) {
  // Prüfen, ob ein gültiger Winkel übergeben wurde.
  if (angle < -360 || angle > 360) {
    return;
  }

  // Umrechnung des gewünschten Winkels in Encoder-Schritte
  // 1 Umdrehung des Motors = 360 Grad -> 4 Motor-Umdrehungen = 2700 Encoder-Schritte
  // Es gibt 2700 Encoder-Schritte für eine vollständige Drehung um 360 Grad.
  long targetSteps = map(angle, -360, 360, -2700, 2700);

  //Bei negativem Winkel dreht sich der Roboter auf der Stelle nach links
  if(angle < 0) {
     motors.setRightSpeed(255);  // Rechter Motor vorwärts
     motors.setLeftSpeed(-255);  // Linker Motor rückwärts
  }
  //Bei positivem Winkel dreht sich der Roboter auf der Stelle nach rechts
  else {
  motors.setLeftSpeed(255);  // Linker Motor vorwärts
  motors.setRightSpeed(-255);  // Rechter Motor rückwärts
  }

  long initialLeft = encoders.getCountsLeft();
  long initialRight = encoders.getCountsRight();

  // Drehen, bis der gewünschte Winkel erreicht ist
  while ((abs(encoders.getCountsLeft() - initialLeft) < abs(targetSteps) && 
         abs(encoders.getCountsRight() - initialRight) < abs(targetSteps))) {
    delay(10);  // Kurze Pause, um das Drehmoment zu stabilisieren
  }

  // Motoren stoppen, wenn der Winkel erreicht ist
  motors.setLeftSpeed(0);  // Stoppe linken Motor
  motors.setRightSpeed(0);  // Stoppe rechten Motor
  
}

void setup() {

  // Beispiel: Drehe um 90 Grad gegen den Uhrzeigersinn
  turnOnSpot(180);
}

void loop() {

}

