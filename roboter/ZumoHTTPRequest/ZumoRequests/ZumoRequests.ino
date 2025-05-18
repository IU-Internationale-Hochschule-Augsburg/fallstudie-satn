#include <WiFiS3.h>
#include <A4990MotorShield.h>

char ssid[] = "IU-Study";  // WLAN Config
char pass[] = "studieren_an_der_IU";

WiFiClient client;
A4990MotorShield motors;

int status = WL_IDLE_STATUS;
const char* server = "192.168.178.34";  // IP Flask-Server
const int port = 5000;                  // Port Flask-Server

unsigned long lastRequestTime = 0;
const long requestInterval = 10000;  // Request alle 10 Sekunden

void setup() {
  Serial.begin(9600);

  if (WiFi.status() == WL_NO_MODULE) { // Check WLAN Modul
    Serial.println("WiFi-Modul nicht gefunden!");
    while (true);
  }

  while (status != WL_CONNECTED) {  // WLAN Vervindung herstellen
    Serial.print("Verbinde mit: ");
    Serial.println(ssid);
    status = WiFi.begin(ssid, pass);
    delay(5000);
  }

  Serial.print("Verbunden! IP-Adresse: ");  // IP des Zumo ausgeben
  Serial.println(WiFi.localIP());
}

void loop() {
  if (millis() - lastRequestTime > requestInterval) { // Zähler für Request alle 10 Sekunden
    lastRequestTime = millis();

    if (client.connect(server, port)) { // Verbindung zu Flask-Server
      Serial.println("Verbunden mit Server");

      client.print("GET /data HTTP/1.1\r\n"); // HTTP Request
      client.print("Host: ");
      client.print(server);
      client.print(":");
      client.print(port);
      client.print("\r\n");
      client.print("Connection: close\r\n\r\n");

      delay(500);  // Warten auf Antwort

      String response = ""; // Leerer String für Antwort
      while (client.available()) {
        response += (char)client.read();  // Antwort String Zeichen für Zeichen einlesen
      }
      
      Serial.println("______________HTTP______________");
      Serial.println("Antwort erhalten:");
      Serial.println(response); // Antwort ausgeben (Header + Body)
      Serial.println("________________________________");

      int xPos = 0, yPos = 0;
      int xStart = response.indexOf("\"coord_x\":"); // Position von coord_x in Antwort in int speichern
      int yStart = response.indexOf("\"coord_y\":"); // Position von coord_y in Antwort in int speichern

      if (xStart != -1 && yStart != -1) { // Prüft ob beides gefunden wurde
        xPos = response.substring(xStart + 10, response.indexOf(",", xStart)).toInt(); // Schneidet xPos aus und toInt ("coord_x":) hat 10 Zeichen
        yPos = response.substring(yStart + 10, response.indexOf(",", yStart)).toInt(); // Schneidet yPos aus und toInt ("coord_y":) hat 10 Zeichen

        Serial.print("x = ");
        Serial.print(xPos);
        Serial.print(", y = ");
        Serial.println(yPos);

        // Einfache Fahr-Logik
        if (xPos > 0) {
          Serial.println("Vorwärts fahren");
          motors.setM1Speed(1000);
          motors.setM2Speed(1000);
        } else if (xPos < 0) {
          Serial.println("Rückwärts fahren");
          motors.setM1Speed(-1000);
          motors.setM2Speed(-1000);
        } else if (yPos > 0) {
          Serial.println("Rechts drehen");
          motors.setM1Speed(1000);
          motors.setM2Speed(-1000);
        } else if (yPos < 0) {
          Serial.println("Links drehen");
          motors.setM1Speed(-1000);
          motors.setM2Speed(1000);
        } else {
          Serial.println("Stop");
          motors.setSpeeds(0, 0);
        }

        delay(500); // Nur 0,5 Sekunden Bewegung als Demo
        motors.setSpeeds(0, 0);
      }

      client.stop();
      Serial.println("Verbindung getrennt");
    } else {
      Serial.println("Verbindung zum Server fehlgeschlagen");
    }
  }
}
