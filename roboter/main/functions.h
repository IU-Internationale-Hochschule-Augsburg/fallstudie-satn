
#ifndef _FUNCTIONS_H    
#define _FUNCTIONS_H    

// Place your main header code here.
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

void calibrate() {
  // Make sure Zumo stands still
  motors.setSpeeds(0,0);

  // todo: Send request to /posistion and /direction endpoint
  // starting postion
  float x1 = 0.0;
  float y1 = 0.0;
  float dir1 = 0.0;

  // drive forward
  motors.setSpeeds(200, 200);
  delay(1000);
  motors.setSpeeds(0,0);

  // todo: Send request to /posistion and /direction endpoint
  // ending postion
  float x2 = 0.0;
  float y2 = 0.0;
  float dir2 = 0.0;


  float deltaAngle = fabs(dir2 - dir1)
  if (deltaAngle > 180) {
    deltaAngle = 360 - deltaAngle;
  }
  if (deltaAngle == 0) {
    return true;
  }

  bool turnLeft;
  if (
      (
       dir1 < 180 &&
       (dir2 < dir1 || dir2 > dir1 + 180)
      )||(
       dir1 > 180 && dir2 < dir1 && dir2 > dir1 - 180
      )
  ) {
    turnLeft = true;
  } else {
    turnLeft = false;
  }

  float dx = x2 - x1;
  float dy = y2 - y1;
  float directLength = sqrt((dx * dx) + (dy * dy));

  float theta = deltaAngle * PI / 180;
  float radius = directLength / (2 * sin(theta / 2));
  float radius1 = radius - 1; //replace 1 with half of distance between chains
  float radius2 = radius + 1;

  float length1 = radius1 * theta
  float length2 = radius2 * theta;
  float adjustment = length1 / length2;
  if (turnLeft) {
    // adjust right
  } else {
    //adjust left
  }
  // todo: set adjustment as environment variable
}
#endif 