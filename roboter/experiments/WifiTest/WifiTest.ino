#include <WiFiS3.h>

char ssid[] = "IU-Study";               // your WiFi SSID
char pass[] = "studieren_an_der_IU";    // your WiFi password
int status = WL_IDLE_STATUS;

void setup() {
  Serial.begin(9600);
  while (!Serial) {
    ; // wait for serial port to connect (needed for native USB port)
  }

  if (WiFi.status() == WL_NO_MODULE) {
    Serial.println("WiFi module not found!");
    while (true); // stop here
  }

  // try to connect to WiFi
  while (status != WL_CONNECTED) {
    Serial.print("Connecting to WiFi: ");
    Serial.println(ssid);
    status = WiFi.begin(ssid, pass);
    delay(5000);
  }

  // once connected, print IP address
  Serial.print("Connected! IP Address: ");
  Serial.println(WiFi.localIP());
}

void loop() {
  // do nothing
}
