#include <WiFiS3.h>
#include <A4990MotorShield.h>

char ssid[] = "IU-Study";
char pass[] = "studieren_an_der_IU";

WiFiServer server(80);
A4990MotorShield motors;
int status = WL_IDLE_STATUS;

void setup() {
  Serial.begin(9600);

  // Check WiFi module
  if (WiFi.status() == WL_NO_MODULE) {
    Serial.println("WiFi-Modul nicht gefunden!");
    while (true);
  }

  // Connect to WiFi
  while (status != WL_CONNECTED) {
    Serial.print("Verbinde mit: ");
    Serial.println(ssid);
    status = WiFi.begin(ssid, pass);
    delay(5000);
  }

  // Show IP
  Serial.print("Verbunden! IP-Adresse: ");
  Serial.println(WiFi.localIP());

  // Start Webserver
  server.begin();  
}

void loop() {
  WiFiClient client = server.available(); // Connected?

  if (client) {
    Serial.println("Client verbunden");
    String request = client.readStringUntil('\r');
    Serial.println("Request: " + request);
    client.flush();

    // Action
    if (request.indexOf("/forward") != -1) {
      motors.setM1Speed(900);
      motors.setM2Speed(1000);
    } else if (request.indexOf("/backward") != -1) {
      motors.setM1Speed(-1000);
      motors.setM2Speed(-1000);
    } else if (request.indexOf("/left") != -1) {
      motors.setM1Speed(1000);
      motors.setM2Speed(-1000);
      delay(179);
      motors.setSpeeds(0, 0);
    } else if (request.indexOf("/right") != -1) {
      motors.setM1Speed(-1000);
      motors.setM2Speed(1000);
      delay(190);
      motors.setSpeeds(0, 0);
    } else if (request.indexOf("/stop") != -1) {
      motors.setSpeeds(0, 0);
    }

    // Answer
    client.println("HTTP/1.1 200 OK");
    client.println("Content-Type: text/plain");
    client.println("Connection: close");
    client.println();
    client.println("Command received");
    client.stop();
    Serial.println("Client getrennt\n");
  }
}
