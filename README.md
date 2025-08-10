# Turniergrafik-Programm
Dies ist ein (spartanisches) README fuer das Programm zu Auswertung
der Turnierdaten. Die vollständige Dokumentation findet sich auf Nuclino unter:
```link
https://app.nuclino.com/mswr/Task-board/Turniergrafik-Programm-Dokumentation-7ec03150-ca38-4f98-947d-15d38f079cb8
```

# Installation

## Installation mit venv
Es wird empfohlen, dieses Programm in einer virtuellen Umgebung zu installieren.
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements_pip.txt
```
Stattdessen kann auch nur das Kommando `pip install requirements_pip.txt`
verwendet werden, um die Abhängigkeiten zu installieren.
Dann wird das Programm in der aktuellen Umgebung installiert, was aber
zu Konflikten mit anderen Python-Projekten und dem System-Python
führen kann. Daher wird die Verwendung einer virtuellen Umgebung
empfohlen, um die Abhängigkeiten isoliert zu halten.

## Installation mit Conda
Alternativ kann das Programm auch mit Conda installiert werden. Dazu wird eine Conda-Umgebung mit den notwendigen Paketen erstellt.
```bash
conda create -n turniergrafik python=3.11
conda activate turniergrafik
conda install --file requirements_conda.txt
```

# Benötigte Python-Version
Das Programm wurde mit Python 3.11 entwickelt und getestet. Es wird empfohlen,
eine Python-Version ab 3.11 zu verwenden, um Kompatibilitätsprobleme zu vermeiden.
Die Installation dieser Version kann je nach Betriebssystem unterschiedlich
aussehen. Für die meisten Linux-Distributionen kann Python über den
Paketmanager installiert werden. Für Windows und macOS kann es
von der offiziellen Python-Website heruntergeladen und installiert werden.
Für die Installation von Python 3.11 auf Ubuntu kann der folgende Befehl
verwendet werden:
```bash
sudo apt install python3.11
# Optional: Installation von pip (Python-Paketverwaltung) und venv (virtuelle Umgebung)
sudo apt install python3-pip python3.11-venv
```
Falls diese Version nicht verfügbar ist, kann auch eine neuere Version
installiert werden, da das Programm auch mit neueren Python-Versionen
kompatibel ist. Es wird jedoch empfohlen, mindestens Python 3.11 zu verwenden,
um sicherzustellen, dass das Programm ordnungsgemäß funktioniert.

# Abhängigkeiten
Die Abhängigkeiten des Programms sind in der Datei `requirements_pip.txt`
(für pip) und `requirements_conda.txt` (für conda) aufgelistet.
Diese Dateien enthalten alle benötigten Pakete, die für die korrekte
Ausführung des Programms erforderlich sind. Sie können die Abhängigkeiten
mit dem folgenden Befehl installieren:

```bash
# Für pip
pip install -r requirements_pip.txt
# Für conda
conda install --file requirements_conda.txt
```

# Hinweise zur Benutzung
Das Programm ist so konzipiert, dass es die Daten der letzten Jahre
automatisch aus dem 'archiv'-Ordner im Programmordner lädt. Dieser Ordner
sollte die Daten der letzten Jahre enthalten, die in der Datei
`archiv.tar.xz` gepackt sind. Diese Datei kann aus dem Repository
geladen werden, oder sie kann bei Bedarf angefordert werden.

## Erzeugen der Turniergrafiken
-> Vor dem (allerersten) Start bzw. im Falle dessen, dass kein 'archiv'-Ordner
   im Programmordner liegt: Die gepackte Datei 'archiv.tar.xz' direkt in den
   Programmordner entpacken! Ansonsten muessen alle Daten der letzten Jahre
   neu geladen werden. Diese Datei liegt aktuell nicht im Repository, da sie
   zu gross ist. Sie kann aber bei Bedarf angefordert werden.

-> Zum starten des Programms einfach die Datei 'turniergrafik.py' ausfuehren.
   Dies kann entweder durch einen Doppelklick auf die Datei oder durch
   Eingabe des Befehls in einem Terminal geschehen:

```bash
python3 turniergrafik.py
```

## Kommandzeilenargumente
Das Programm kann mit verschiedenen Kommandozeilenargumenten gestartet werden,
um bestimmte Funktionen auszuführen oder das Verhalten des Programms zu ändern.
Wenn keine Argumente angegeben werden, wird das Programm mit den Einstellungen
aus der Konfigurationsdatei `config.py` gestartet und versucht, die
Turniergrafiken für den in der Konfiguration angegebenen Zeitraum zu erzeugen.
Wenn Argumente angegeben werden, haben diese Vorrang vor den
Einstellungen in der Konfigurationsdatei. Das Programm wird dann mit den
angegebenen Argumenten gestartet und versucht, die Turniergrafiken
für den angegebenen Zeitraum zu erzeugen. Wenn die Argumente nicht korrekt
sind oder nicht den erwarteten Werten entsprechen, wird eine Fehlermeldung
ausgegeben und das Programm wird beendet. Die Argumente können verwendet werden,
um den Zeitraum für die Turniergrafiken zu ändern oder um die zu betrachteten
Spieler zu ändern. Es ist wichtig, die Argumente korrekt anzugeben,
um sicherzustellen, dass das Programm die gewünschten Ergebnisse liefert.

Die verfügbaren Argumente sind:
TODO: Hier sollten die verfügbaren Kommandozeilenargumente aufgelistet und
beschrieben werden. Diese finden sich in der Datei `turniergrafik.py`
im Teil `if __name__ == "__main__":`.

## Konfiguration und Anpassung
Konfigurationen koennen, wie gehabt, in der 'config.py' geaendert werden.
Die genauere Dokumentation der Konfigurationsmoeglichkeiten
findet sich auf Nuclino unter:
```link
https://app.nuclino.com/mswr/Task-board/Turniergrafik-Programm-Dokumentation-7ec03150-ca38-4f98-947d-15d38f079cb8#c6b2e
```
