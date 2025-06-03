# Docker Image Management - Anleitung

Dokumentation für den Umgang mit Docker Images entsprechend Issue #102. Diese Anleitung beschränkt sich auf die für das Projekt relevanten Schritte.

## 1. Download des Docker Images

### Von Docker Hub herunterladen
```bash
docker pull ghcr.io/iu-internationale-hochschule-augsburg/fallstudie-satn:sha-8cfab5a
```

**Übersicht Images:**
[SATN Containers](https://github.com/IU-Internationale-Hochschule-Augsburg/fallstudie-satn/pkgs/container/fallstudie-satn)

### Verfügbare Images anzeigen
```bash
docker images
docker image ls
```

### Image-Details prüfen
```bash
docker inspect [IMAGE_NAME]
```

**Wichtige Hinweise:**
- Aktuellsten Images bevorzugen (siehe [SATN Containers](https://github.com/IU-Internationale-Hochschule-Augsburg/fallstudie-satn/pkgs/container/fallstudie-satn) )
- Tag-Versionen spezifizieren statt "latest"

---

## 2. Installation und Konfiguration

### Container aus Image erstellen mit Kamerazugriff und Port-Mapping
```bash
docker run -d -p 5000:5000 --privileged --name ghcr.io/iu-internationale-hochschule-augsburg/fallstudie-satn:[IMAGE_NAME]
```

---

## 3. Anpassungen und Modifikationen

### 3.1 Container-Änderungen durchführen

#### Software installieren/konfigurieren
```bash
# Beispiel: libcamera-dev
apt-get install -y [PACKAGE_NAME]
```

#### Konfigurationsdateien bearbeiten
```bash
nano /etc/[CONFIG_FILE]
```

### 3.2 Änderungen als neues Image speichern
```bash
docker commit [OPTIONS] CONTAINER [REPOSITORY[:TAG]]
```

**Beispiel:**
```bash
docker commit c3f279d17e0a ghcr.io/iu-internationale-hochschule-augsburg/fallstudie-satn:latest
```

### 3.3 Dockerfile für reproduzierbare Builds

#### Dockerfile-Template erstellen
```dockerfile
FROM [BASE_IMAGE]
WORKDIR /app
COPY . .
RUN [INSTALLATION_COMMANDS]
EXPOSE [PORT]
CMD ["[START_COMMAND]"]
```

**Beispiel:**
[SATN-Dockerfile]([https://github.com/IU-Internationale-Hochschule-Augsburg/fallstudie-satn/pkgs/container/fallstudie-satn](https://github.com/IU-Internationale-Hochschule-Augsburg/fallstudie-satn/blob/main/computer_vision/Dockerfile))

**Best Practices für Anpassungen:**
- Minimale Base-Images verwenden
- .dockerignore für unnötige Dateien
- venv einrichten (siehe [Setup Raspberry Pi](https://github.com/IU-Internationale-Hochschule-Augsburg/fallstudie-satn/blob/feat/camera-optimizing/computer_vision/README.md))

---

## 4. Upload und Deployment

### 4.1 Image für Upload vorbereiten

#### Image taggen
```bash
docker tag [LOCAL_IMAGE] [REGISTRY_HOST]/[USERNAME]/[IMAGE_NAME]:[TAG]
```

**Beispiele:**
```bash
docker tag 0e5574283393 ghcr.io/iu-internationale-hochschule-augsburg/fallstudie-satn:prod-v1
```

### 4.2 Registry-Login
```bash
docker login ghcr.io -u [USER] --password-stdin
```

### 4.3 Image hochladen
```bash
docker push [REGISTRY_HOST]/[USERNAME]/[IMAGE_NAME]:[TAG]
```

**Beispiele:**
```bash
docker push ghcr.io/iu-internationale-hochschule-augsburg/fallstudie-satn:[TAG]
```

### 4.4 Upload-Optimierung

#### Image-Größe optimieren vor Upload
```bash
docker system prune
docker image prune
```

**Upload-Checklist:**
- [ ] Korrekte Registry-URL verwenden
- [ ] Authentifizierung überprüfen
- [ ] Tag-Konventionen einhalten

---

## 5. Troubleshooting

### Häufige Probleme und Lösungen

#### "Permission denied" Fehler
```bash
sudo docker [COMMAND]
```

#### "Port already in use"
```bash
docker ps -a
docker stop [CONTAINER_NAME]
```

#### "No space left on device"
```bash
docker system prune -a
```

#### "Network timeout"
- Proxy-Einstellungen prüfen
- Internetverbindung testen
- Registry-Erreichbarkeit überprüfen

### Container-Logs analysieren
```bash
docker logs [CONTAINER_NAME]
docker logs --tail 50 [CONTAINER_NAME]
```

### System-Status prüfen
```bash
docker system df
docker system info
```

---

## 6. Nützliche Links und Ressourcen

- **Docker Official Documentation:** [Docker Docs](https://docs.docker.com/)
- **Docker Hub Registry:** [Docker Hub Registry](https://hub.docker.com/_/registry)
- **SATN Registry:** [SATN-Registry](https://github.com/IU-Internationale-Hochschule-Augsburg/fallstudie-satn/pkgs/container/fallstudie-satn)
- **CI/CD Pipeline Integration:** [CICD Pipeline](https://github.com/IU-Internationale-Hochschule-Augsburg/fallstudie-satn/blob/main/.github/workflows/docker-publish.yml)

---

*Erstellt für Issue #102 | Milestone: 03.06.2025*
*Letzte Aktualisierung: [03.06.2025]*
