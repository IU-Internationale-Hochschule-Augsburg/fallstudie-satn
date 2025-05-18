#include <WiFiS3.h>
#include <A4990MotorShield.h>
#include <Arduino_JSON.h>

// WLAN-Konfiguration
char ssid[] = "IU-Study";
char pass[] = "studieren_an_der_IU";

WiFiClient client;
A4990MotorShield motors;

int status = WL_IDLE_STATUS;

// IP und Port des Flask-Servers
const char* server = "7.32.120.137";
const int port = 5000;

unsigned long lastRequestTime = 0;
const long requestInterval = 10000;  // Intervall für Anfragen (in ms)

void setup() {
  Serial.begin(9600);

  // Prüfen, ob das WiFi-Modul vorhanden ist
  if (WiFi.status() == WL_NO_MODULE) {
    Serial.println("WiFi-Modul nicht gefunden!");
    while (true);
  }

  // Verbindung mit WLAN herstellen
  while (status != WL_CONNECTED) {
    Serial.print("Verbinde mit: ");
    Serial.println(ssid);
    status = WiFi.begin(ssid, pass);
    delay(5000);
  }

  Serial.print("Verbunden! IP-Adresse: ");
  Serial.println(WiFi.localIP());
}

void loop() {
  // Anfrage nur im festgelegten Intervall senden
  if (millis() - lastRequestTime > requestInterval) {
    lastRequestTime = millis();

    // Verbindung zum Flask-Server aufbauen
    if (client.connect(server, port)) {
      Serial.println("Verbunden mit Server");

      // HTTP-GET-Anfrage an /task/turn senden
      client.print("GET /task/turn HTTP/1.1\r\n");
      client.print("Host: ");
      client.print(server);
      client.print(":");
      client.print(port);
      client.print("\r\n");
      client.print("Connection: close\r\n\r\n");

      delay(500);  // kurze Wartezeit für Antwort

      // Antwort einlesen
      String response = "";
      while (client.available()) {
        response += (char)client.read();
      }

      Serial.println("______________HTTP______________");
      Serial.println("Antwort erhalten:");
      Serial.println(response);
      Serial.println("________________________________");

      // Nur den HTTP-Body extrahieren (nach \r\n\r\n beginnt der Body)
      int bodyStart = response.indexOf("\r\n\r\n");
      JSONVar myObject;

      if (bodyStart != -1) {
        String body = response.substring(bodyStart + 4);

        Serial.println("JSON-Body extrahiert:");
        Serial.println(body);

        // JSON parsen
        myObject = JSON.parse(body);

        if (JSON.typeof(myObject) == "undefined") {
          Serial.println("Fehler beim Parsen des JSON!");
          return;
        }
      } else {
        Serial.println("Kein HTTP-Body gefunden!");
        return;
      }

      // Typ aus JSON lesen
      String type = (const char*) myObject["type"];
      Serial.print("Typ: ");
      Serial.println(type);

      if (type == "forward") {
        // Dauer des Fahren auslesen
        String durationStr = (const char*) myObject["duration"];
        int duration = durationStr.toInt();

        Serial.print("Dauer: ");
        Serial.println(duration);

        // Geradeaus fahren
        motors.setM1Speed(900);
        motors.setM2Speed(1000);
        delay(duration);
        motors.setSpeeds(0, 0);

      } else if (type == "turn") {
        // Winkel auslesen
        String angleStr = (const char*) myObject["angle"];
        int angle = angleStr.toInt();

        Serial.print("Winkel: ");
        Serial.println(angle);

        // Drehen auf der Stelle
        motors.setM1Speed(1000);
        motors.setM2Speed(-1000);
        delay(angle);
        motors.setSpeeds(0, 0);

      } else {
        Serial.println("Unbekannter Typ!");
      }

      client.stop();
      Serial.println("Verbindung getrennt");

    } else {
      Serial.println("Verbindung zum Server fehlgeschlagen");
    }
  }
}
