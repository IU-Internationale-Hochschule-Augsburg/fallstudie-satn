# Projekt Dokumentation

Diese Dokumentation beschreibt die grundlegenden Richtlinien und Strukturen für das GitHub-Projekt, an dem mehrere Personen gemeinsam arbeiten. Das Projektziel ist es, mittels eines Raspberry Pi Pico und eines Kameramoduls Objekte auf einem Tisch zu erkennen, diese Informationen an einen Roboter zu übermitteln und anschließend den Roboter dazu zu bringen, alle Objekte zu einem Haufen zu schieben.

---

## Inhaltsverzeichnis
- [Projektübersicht](#projektübersicht)
- [Ordnerstruktur](#ordnerstruktur)
- [Branching-Strategie](#branching-strategie)
- [Commit-Konventionen](#commit-konventionen)
- [Issue Management](#issue-management)
- [Merge und Code-Review](#merge-und-code-review)
- [Code Qualität und Standards](#code-qualität-und-standards)

---

## Projektübersicht

Das Projekt kombiniert Computer-Vision und Robotik:
- **Computer Vision:** Der Raspberry Pi Pico mit einem Kameramodul erkennt Objekte auf einem Tisch.
- **Robotik:** Die erkannten Informationen werden an den Roboter weitergeleitet, der die Objekte zu einem Haufen schiebt.

Die Kommunikation zwischen den Komponenten erfolgt über klar definierte Schnittstellen, sodass sowohl die Erkennung als auch die Robotersteuerung effizient zusammenarbeiten.

---

## Ordnerstruktur

Das Repository ist in drei Hauptordner unterteilt:

1. **Projektmanagement:**  
   Enthält allgemeine Projektdokumentationen, Planungsdokumente, und Konfigurationsdateien.

2. **Roboter:**  
   Enthält den Quelltext, der für die Steuerung des Roboters zuständig ist.

3. **Computer_Vision:**  
   Enthält den Quelltext für die Software, die auf dem Raspberry Pi Pico läuft und für die Objekterkennung verantwortlich ist.

---

## Branching-Strategie

Das Repository nutzt drei Hauptbranches:

- **main:**  
  Dieser Branch enthält die finale Softwareversion, die für Präsentationen verwendet wird. Änderungen dürfen nicht direkt gepusht werden.

- **roboter:**  
  Dieser Branch verwaltet den Quelltext und die Entwicklung der Roboter-Software.

- **computer_vision:**  
  Dieser Branch enthält den Quelltext und die Entwicklung der Software für den Raspberry Pi Pico.

**Hinweis:**  
Für jedes Issue, das bearbeitet wird, soll ein neuer Branch von entweder `roboter` oder `computer_vision` erstellt werden. Dies erleichtert die Nachverfolgung und Integration von neuen Features oder Bugfixes.

---

## Commit-Konventionen

Alle Commits müssen einem festen Schema folgen, um eine konsistente und nachvollziehbare Versionshistorie zu gewährleisten:

- **Commit-Nachrichtenformat:**  
  Jeder Commit beginnt mit `feat` oder `fix`, gefolgt von der Issue-ID in Klammern, einem Doppelpunkt und einer kurzen Beschreibung in Englisch.

  **Beispiele:**
  - `feat(issue-1): projekt init`
  - `fix(issue-2): resolve camera calibration issue`

Dieses Format stellt sicher, dass alle Änderungen klar dokumentiert und einfach zuzuordnen sind.

---

## Issue Management

- Alle Aufgaben und Fehler werden in den **Issues** des GitHub-Repositories erfasst.
- Jeder Issue sollte ein klar definiertes Ziel und Akzeptanzkriterien haben.
- Für jede Bearbeitung eines Issues ist ein eigener Branch zu erstellen, der von dem entsprechenden Entwicklungsbranch (`roboter` oder `computer_vision`) abzweigt.

---

## Merge und Code-Review

- Änderungen dürfen nicht direkt in den `main`-Branch gepusht werden.
- Alle Merges in den `main`-Branch müssen dem **4-Augen-Prinzip** folgen. Das bedeutet, dass ein Merge erst dann erfolgen darf, wenn eine zweite Person den Code geprüft und freigegeben hat.
- Ebenso dürfen Änderungen von den Entwicklungsbranches nicht ohne eine gründliche Überprüfung in den `roboter` oder `computer_vision`-Branch gemergt werden.

Diese Maßnahmen stellen sicher, dass die Codequalität stets gewährleistet ist und Fehler frühzeitig erkannt werden.

---

## Code Qualität und Standards

- **Code Qualität:**  
  Es ist essenziell, dass alle Teammitglieder Code in hoher Qualität schreiben. Dies umfasst klare Kommentare, verständliche Namensgebungen und sauberen, wartbaren Code.
  
- **Standard Code Sprache:**  
  Die primäre Sprache im Code ist **Englisch**. Dies betrifft Variablennamen, Kommentare und Dokumentation im Code, um eine einheitliche und international verständliche Codebasis zu gewährleisten.

---

Diese Richtlinien sind essentiell, um die Zusammenarbeit im Team zu strukturieren, den Entwicklungsprozess transparent zu gestalten und die Qualität des Endprodukts sicherzustellen. Änderungen an dieser Dokumentation sollten ebenfalls über Issues und nach dem 4-Augen-Prinzip in den `main`-Branch integriert werden.
