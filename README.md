# Turniergrafik-Programm
Dies ist ein (spartanisches) README fuer das Programm zu Auswertung
der Turnierdaten. Die vollständige Dokumentation findet sich auf Nuclino unter:
```link
https://app.nuclino.com/mswr/Task-board/Turniergrafik-Programm-Dokumentation-7ec03150-ca38-4f98-947d-15d38f079cb8
```

# Installation

## Installation mit venv
Es wird empfohlen, dieses Programm in einer virtuellen Umgebung auszuführen. Dies setzt mindestens Python 3.10 voraus, funktioniert aber auch mit neueren Versionen. Je nachdem, welche Version in den Paketquellen verfügbar ist, wird eine andere installiert, was aber für die Funktion des Programms unerheblich ist. Die benötigten Python-Pakete werden isoliert vom System-Python in einer virtuellen Umgebung (venv) installiert.

### Abhängigkeiten installieren (wichtig!)
```bash
sudo apt install python3-pip python3-venv python3-dev mariadb-server libmariadb-dev
```

### Virtuelle Python-Umgebung erstellen.
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements_pip.txt
```

Stattdessen kann auch nur das Kommando `pip install -r requirements_pip.txt`
verwendet werden, um die benötigten Python-Pakete zu installieren.
Dann wird das Programm in der aktuellen Umgebung installiert, was aber
zu Konflikten mit anderen Python-Projekten und dem System-Python
führen kann. Daher wird die Verwendung einer virtuellen Umgebung
empfohlen, um die Abhängigkeiten isoliert zu halten.

## Installation mit Conda

Alternativ kann das Programm auch mit Conda ([Link für alle Betriebssysteme](https://www.anaconda.com/docs/getting-started/miniconda/install)) installiert werden.
Nach der Installation von Miniconda (empfohlen) oder Anaconda wird eine Conda-Umgebung mit den notwendigen Paketen erstellt.

```bash
# Installieren von Miniconda in Linux (falls noch nicht installiert)
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh | bash
# Erstelle eine Conda-Umgebung namens 'turniergrafik' mit den notwendigen Paketen
conda env create -f environment.yml
# Aktiviere die Conda-Umgebung
conda activate turniergrafik
```

# Benötigte Python-Version
Das Programm wurde mit Python 3.11 entwickelt und getestet. Mit Conda wird empfohlen,
eine Python-Version ab 3.11 zu verwenden, um Kompatibilitätsprobleme zu vermeiden.

Die Installation dieser Version kann je nach Betriebssystem unterschiedlich
aussehen. Für die meisten Linux-Distributionen kann Python über den
Paketmanager installiert werden. Für Windows und macOS kann es
von der offiziellen Python-Website heruntergeladen und installiert werden.

Minimal sollte Python 3.10 installiert sein, was mit venv getestet ist.
Falls diese Version nicht verfügbar ist, kann auch eine neuere Version
installiert werden, da das Programm auch mit neueren Python-Versionen
kompatibel ist. Es muss jedoch mindestens Python 3.10 verwenden werden,
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
`archiv.zip` gepackt sind. Diese Datei kann aus dem Repository
geladen werden, oder sie kann bei Bedarf angefordert werden.

```bash
# Entpacken der archiv.zip-Datei in den Programmordner
unzip archiv.zip -d archiv/
# archiv.zip neu packen, falls neue Daten hinzugefügt wurden
zip -r archiv.zip archiv/
```

## Erzeugen der Turniergrafiken
-> Vor dem (allerersten) Start bzw. im Falle dessen, dass kein 'archiv'-Ordner
   im Programmordner liegt: Die gepackte Datei 'archiv.tar.xz' direkt in den
   Programmordner entpacken! Ansonsten muessen alle Daten der letzten Jahre
   neu geladen werden. Diese Datei liegt aktuell nicht im Repository, da sie
   zu gross ist. Sie kann aber bei Bedarf angefordert werden.

-> Zum Starten des Programms einfach die Datei 'turniergrafik.py' ausführen.
   Dies kann entweder durch einen Doppelklick auf die Datei oder durch
   Eingabe des Befehls in einem Terminal geschehen:

```bash
python3 turniergrafik.py
```

**WICHTIG!** Falls eine virtuelle Umgebung verwendet wird, muss diese
zuerst vor dem jeweils Start des Programms aktiviert werden.
Wenn ein neues Terminal geöffnet wird, muss die virtuelle Umgebung
doch erneut aktiviert werden, da sie nur für die Dauer des Terminalfensters aktiv bleibt.

```bash
source venv/bin/activate
```
Analog, falls Conda zur Installation benutzt wurde, muss vor (jedem)
ersten Start die entsprechende Environment geladen werden:

```bash
conda activate turniergrafik
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
usage: turniergrafik.py [-h] [-v] [-q QUOTIENT] [-p PARAMS] [-c CITIES] [-d DAYS] [-t TOURNAMENTS]
                        [-u USERS]

options:
  -h, --help            show this help message and exit
  -v, --verbose         increase output verbosity
  -q QUOTIENT, --quotient QUOTIENT
                        calculate quotients etc (enter 2 players for quotient calculation)
  -p PARAMS, --params PARAMS
                        Set params
  -c CITIES, --cities CITIES
                        Set cities
  -d DAYS, --days DAYS  Set days
  -t TOURNAMENTS, --tournaments TOURNAMENTS
                        Set tournaments
  -u USERS, --users USERS
                        Set users
```

### Erklärung der einzelnen Optionen

```-h/--help``` Zeigt die Hilfe an und beendet das Programm.<br/>
```-v/--verbose``` Zeigt mehr (Debug)-Output bei der Ausführung an. Im Code erkennbar durch if ```verbose: print(x)```<br/>
```-q/--quotient``` Namen von zwei Spielern, fuer die Quoten, Differenzen und Summen in separaten Dateien ausgegeben werden sollen [Bsp: ```-q MSwr-MOS-Mix,MSwr-EZ-MOS```]<br/>
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
