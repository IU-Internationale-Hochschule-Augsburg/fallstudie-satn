#include <Zumo32U4.h>


Zumo32U4Motors motors;
Zumo32U4LineSensors lineSensors;
Zumo32U4Encoders encoders;
int zufallszahl;

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


unsigned int sensorValues[5];  // Platz für 5 Sensoren


// Schwellenwert zwischen "hell" und "dunkel"
     
const unsigned int BLACK_THRESHOLD = 188;

void setup() {
  Serial.begin(9600);
  lineSensors.initFiveSensors();
  zufallszahl = random(100, 260);
  delay(1000);  
  
}

void loop() {
  
  lineSensors.read(sensorValues);  // Lese Sensoren ein

  bool seesBlack = false;


    
    // Prüfe, ob Sensorwert unter dem Schwellenwert liegt (→ dunkel)
    if (sensorValues[0] > BLACK_THRESHOLD) {
      Serial.println(sensorValues[0]);

       motors.setLeftSpeed(0);
      motors.setRightSpeed(0);
      turnOnSpot(zufallszahl);
    } else {
      seesBlack = false;
      Serial.println(sensorValues[0]);
      motors.setLeftSpeed(50);
      motors.setRightSpeed(50);
    }
  

  //Serial.println(seesBlack ? "true" : "false");
  delay(200);  
}



