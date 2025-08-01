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
pip install -r requirements.txt
```
Stattdessen kann auch das Kommando `pip install .` verwendet werden, um
das Programm direkt zu installieren. In diesem Fall wird die virtuelle
Umgebung nicht automatisch erstellt, und es wird empfohlen, eine
virtuelle Umgebung zu verwenden, um Konflikte mit anderen Python-Paketen
zu vermeiden.

## Installation mit Conda
Alternativ kann das Programm auch mit Conda installiert werden. Dazu
kann eine Conda-Umgebung erstellt werden, in der das Programm installiert wird.
```bash
conda create -n turniergrafik python=3.10
conda activate turniergrafik
pip install -r requirements.txt
```

# Benötigte Python-Version
Das Programm wurde mit Python 3.10 entwickelt und getestet. Es wird empfohlen,
eine Python-Version ab 3.10 zu verwenden, um Kompatibilitätsprobleme zu vermeiden.
Die Installation von Python 3.10 kann je nach Betriebssystem unterschiedlich
aussehen. Für die meisten Linux-Distributionen kann Python 3.10 über den
Paketmanager installiert werden. Für Windows und macOS kann Python 3.10
von der offiziellen Python-Website heruntergeladen und installiert werden.
Für die Installation von Python 3.10 auf Ubuntu kann der folgende Befehl
verwendet werden:
```bash
sudo apt install python3.10
```

# Abhängigkeiten
Die Abhängigkeiten des Programms sind in der Datei `requirements.txt`
aufgelistet. Diese Datei enthält alle benötigten Pakete, die für die
Ausführung des Programms erforderlich sind. Sie können die Abhängigkeiten
mit dem folgenden Befehl installieren:

```bash
pip install -r requirements.txt
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

## Konfiguration und Anpassung
Konfigurationen koennen, wie gehabt, in der 'config.py' geaendert werden.
Die genauere Dokumentation der Konfigurationsmoeglichkeiten
findet sich auf Nuclino unter:
```link
https://app.nuclino.com/mswr/Task-board/Turniergrafik-Programm-Dokumentation-7ec03150-ca38-4f98-947d-15d38f079cb8#c6b2e
```
