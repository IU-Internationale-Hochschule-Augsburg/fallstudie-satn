# Setup Raspberry Pi

## Raspberry OS vorbereiten
1. Raspberry Pi Imager öffnen
2. Raspberry Pi Model Zero 2 Auswählen
3. Raspberry PI OS Lite (64-Bit) auswählen
4. Hostname: raspberrypi.local
5. Benutzername: pi
6. Passwort: raspberry
7. SSID: IU-Study
8. PW: studieren_an_der_IU
9. Unter Dienste SSH Aktivieren
10. Auf SD Karte Flashen

## Host Vorbereiten
11. >sudo apt update && apt upgrade
12. >sudo apt install -y git python3-picamera2
## Projekt Setup
11. Per SSH mit Pi verbinden, um IP Herauszufinden booten und mit Screen verbinden. Beim Boot wird die Lokale IP angezeigt
12. Git Repo Clonen mittels
> git clone https://github.com/IU-Internationale-Hochschule-Augsburg/fallstudie-satn.git app

13. Ins App/computer_vision verzeichnis Wechseln
14. .venv anlegen
> python3 -m venv .venv --system-site-packages
> source .venv/bin/activate

14. Python dependencies installieren
> pip install -r requirements.txt