//This example drives the robot forwards, turns, drives back and then stops

#include <A4990MotorShield.h>

A4990MotorShield motors;

void stopIfFault()
{
  if (motors.getFault())
  {
    motors.setSpeeds(0,0);
    Serial.println("Fault");
    while(1);
  }
}

void setup() {

  motors.setSpeeds(0,0);
  
  // Forwards
  motors.setM1Speed(1000);
  motors.setM2Speed(600);
  delay(1500);

  motors.setSpeeds(0,0);
  
  // 180 Degree Turn
  motors.setM1Speed(200);   // left motor forwards
  motors.setM2Speed(-200);  // right motor backwards
  delay(790);

  motors.setSpeeds(0, 0);
  delay(1000);

  // Forwards
  motors.setM1Speed(1000);
  motors.setM2Speed(600);
  delay(1500);

  motors.setSpeeds(0,0);

  // Happy
  motors.setM1Speed(400);   // left motor forwards
  motors.setM2Speed(-400);  // right motor backwards
  delay(1200);

  motors.setSpeeds(0,0);
}

void loop() {

}