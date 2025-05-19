# Risikobewertung
## Mögliche Risiken
| Art | intern | extern |
| --- | --- | --- |
| Projektmanagement | Anforderungsinflation (**AI**) <br> unzur. Dokumentation (**DOK**) <br> unklare Rollenverteilung (**RV**) | Fehlzeiten (**FZ**) <br> unzur. Dokumentation (**DOK**) <br> <br> |
| Technische Risiken <br> und Softwarerisiken| Verlust Quellcode (**SRC**) <br> Hardware-Schäden (**HW**) <br> Sicherheislücken (**CS**) <br> unzur. Sensorkalibrierung (**SK**) | Hacking (**H**) <br> GitHub Ausfall (**GH**) <br> Sicherheitslücken (**CS**) <br> Inkompatabilität (**IN**) |
| Supply-Chain Risiken | Verzögerung 3D-Druck (**3D**) | <br> |
| Umweltrisiken | Beleuchtung + Belüftung (**B**) <br> <br> | Hochwasser (**U**) <br> Stromausfall (**SA**) |

## Risiko-Matrix
| Einstufung | Unbedeutend | Gering | Kritisch | Existenziell |
| --- | --- | --- | --- | --- |
| Unwahrscheinlich | 🟢 **3D** | 🟢 | 🟢 **U**, **SA** | 🟡 **H**, **SRC**, **GH** |
| Selten | 🟢 **B** | 🟢 | 🟡 | 🟡 |
| Möglich | 🟢 **CS**, **RV** | 🟡 **AI**, **HW** | 🟡 | 🔴 **HW** |
| Sehr wahrscheinlich | 🟢 **SK** | 🟡 **FZ**, **IN**, **DOK** | 🔴 **FZ** | 🔴 |

### Priorisierung der Risikobewertung
| Status | Symbol |
| --- | --- |
| Hoch| 🔴 |
| Mittel | 🟡 |
| Niedrig | 🟢 |
