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

pip install -r requirements_pip.txt kann problematisch sein wegen den enthaltenen Links.
Im Zweifel muss pip install Module durchgeführt sein und die Module sind in der
Datei requirements.txt enthalten.

## Installation mit Conda
Alternativ kann das Programm auch mit Conda installiert werden. Dazu wird eine Conda-Umgebung mit den notwendigen Paketen erstellt.
```bash
conda create -n turniergrafik python=3.11
conda activate turniergrafik
conda install --file requirements_conda.txt
```

# Benötigte Python-Version
Das Programm wurde mit Python 3.11 entwickelt und getestet. Es wird empfohlen,
die Python-Version 3.11 zu verwenden, um Kompatibilitätsprobleme zu vermeiden.
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

Nur mit Python3.11 funktioniert das Prgramm ordnungsgemaäß.
Bei macOS gibt es eine weitere Alternative, wie Python heruntergeladen werden kann:
Mithilfe des Paketmanagers homebrew kann Python ebenfalls
mit brew install python3.11 installiert werden

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

## Kommandzeilen-Argumente
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

### Die verfügbaren Argumente sind:
```bash
python turniergrafik.py -h
usage: turniergrafik.py [-h] [-v] [-p PARAMS] [-c CITIES] [-d DAYS] [-t TOURNAMENTS] [-u USERS]

options:
-h, --help - show this help message and exit
-v, --verbose - increase output verbosity
-p, --params PARAMS - Set params
-c, --cities CITIES - Set cities
-d, --days DAYS - Set days
-t, --tournaments TOURNAMENTS - Set tournaments
-u, --users USERS - Set users
```

### Erklärung der einzelnen Optionen

```-h/--help``` Zeigt die Hilfe an und beendet das Programm.<br/>
```-v/--verbose``` Zeigt mehr (Debug)-Output bei der Ausführung an. Im Code erkennbar durch if ```verbose: print(x)```<br/>
```-p/--params``` Parameter, die ausgewertet werden sollen, getrennt durch Kommas [Bsp: ```-p Sd1,Sd24,RR24```]<br/>
```-c/--cities``` Städtenamen als ID, Kürzel oder ganzer Name [Bsp: -c ```BER,4,Zürich```]<br/>
```-d/--days``` Tage, die ausgewertet werden sollen (Sa = Samstag, So = Sonntag) [Bsp: ```-d Sa,So```]<br/>
```-t/--tournaments``` Start- und Enddatum (einschließlich!) der auszuwertenden Turniere [Bsp: ```-t 03.01.2023,08.08.2025```]<br/>
```-u/--user``` Namen der Spieler, die betrachtet werden sollen [Bsp: ```-u MSwr-MOS-Mix,MSwr-EZ-MOS,MSwr-GFS-MOS```]<br/>


## Konfiguration und Anpassung
Konfigurationen koennen, wie gehabt, in der 'config.py' geaendert werden.
Die genauere Dokumentation der Konfigurationsmoeglichkeiten
findet sich auf Nuclino unter:
```link
https://app.nuclino.com/mswr/Task-board/Turniergrafik-Programm-Dokumentation-7ec03150-ca38-4f98-947d-15d38f079cb8#c6b2e
```
## Einzelne Teilnehmer anzeigen lassen
In 'graphics.py' wird in der Funktion erstelleGrafik eine Rekurion durchgeführt werden, wenn jeder Auswertungsteilnehmer, definiert in config.py, einzeln betrachtet werden soll. Die Rekursion wird mit cfg.auswertungsteilnehmer_multi = False (cfg heißt config) gestoppt. erstelleGrafik wird rekursiv für jeden Teilnehmer einzeln aufgerufen. Wenn der Teilnehmer in keinem der beiden Dictionaries (langfrist_player_date_points und kurzfrist_player_date_points) vorhanden ist, wird eine Fehlermeldung erzeugt. Im else-Teil wird der Plot generiert. Das bedeutet: Beide Teile sind wichtig.

In 'config.py' bekommt jeder Teilnehmer einen Farbcode und eine Linieneigenschaft zugewiesen. Zum Beispiel: "DWD-MOS-Mix": ["#DEC000", "--"]. "--" ist nicht die einzige Linieneigenschaft. Es gibt auch noch "-" (durchgezogen), "-:" (Strich und Punkt) und ":" (gepunktet). Man kann die Farbcodes auch ändern. DWD-MOS-Mix und MSwr-MOS-Mix haben dicke Linien. Auch das kann in 'config.py' mittels der Zahlencodierung von 1 (sehr dünn) bis 4 (sehr dick) eingestellt werden.
