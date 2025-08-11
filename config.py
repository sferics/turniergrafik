#!/usr/bin/env python3
# -*- coding: utf-8 -*-

##############################################################################
########## Grundlegende Konfiguration (i.d.R. so lassen) #####################
##############################################################################

# database credentials
username    = "readonly"
password    = "WPWTr34donly"
host        = "wetterturnier.de"
database    = "wpwt"
port        = 3306

## Städte
# Alle Städte, die es beim Wetterturnier gibt:
stadtnamen = ["Berlin", "Wien", "Zürich", "Innsbruck", "Leipzig"]

# Stadt zu ihrer ID konvertieren
stadt_zu_id = {
    "Berlin": 1,
    "Wien": 2,
    "Zürich": 3,
    "Innsbruck": 4,
    "Leipzig": 5,
}

# StadtID zu Abkuerzung konvertieren
id_zu_kuerzel = {
    1: "BER",
    2: "VIE",
    3: "ZUR",
    4: "IBK",
    5: "LEI",
}

# Name der Ordners, in dem die Archiv-Dateien geladert werden sollen
archive_dir_name = "archiv"

## URL
# url, von der die Archivdaten geladen werden (als Template)
# staedte_kuerzel siehe oben – Termin hier im Format JJMMTT!
url_template \
    = "https://wetterturnier.de/archiv/wert_{stadt_kuerzel}/wert{termin}.txt"

## Elemente
# Variablenreihenfolge(!) in den Archiv-Dateien zu Kontrollzwecken
elemente_archiv_alt     = ["N", "Sd", "dd", "ff", "fx", "Wv", "Wn", "PPP", "TTm","TTn", "TTd", "RR"]
elemente_archiv_neu     = ["Sd1","Sd24","dd12","ff12","fx24","PPP12","Tmin","T12","Tmax","Td12","RR1","RR24"]

# dazugehörige Einheiten
elemente_einheiten_alt  = ["", "%", "grad", "kn", "kn", "", "", "hPa", "°C", "°C","°C", "mm"]
elemente_einheiten_neu  = ["min","%","grad","m/s","m/s","hPa","°C","°C","°C","°C","mm","mm"]

# dazugehörigen, maximale Punktzahlen
elemente_max_punkte_alt     = [6.0, 5.0, 9.0, 6.0, 4.0, 10.0, 10.0, 10.0, 10.0, 10.0,10.0, 10.0]
elemente_max_punkte_neu     = [9, 9, 8, 8, 8, 8, 8, 8, 8, 8, 9, 9]

## Termin
# Freitagsdaten, die zusätzlich zu den Wochenenden, zu denen keine Archivdaten
# zur Verfügung stehen, nicht in die Auswertung eingehen sollen
# (staedteabhaengig), stadt bzw. key ist als ID dargestellt (stadt_zu_id)
zu_ignorierende_termine = {1: ["21.10.2005", "21.03.2008", "24.12.2004",
                               "25.03.2005", "30.12.2005", "14.04.2006",
                               "29.12.2006", "03.10.2014"],
                           3: ["24.05.2013", "31.05.2013", "14.06.2013",
                               "12.07.2013", "29.12.2006"],
                           4: ["02.08.2013", "16.07.2004"],
                           5: ["02.08.2013", "04.09.2009"],
                           2: ["05.04.2013", "31.12.2004"],}

# Allgemeine Termine, die nicht in die Auswertung eingehen sollen (z.B. Feiertage)
zu_ignorierende_termine_allgemein = ["07.04.2023"]

#TODO Statt Strings der Namen lieber die IDs nutzen
## Teilnehmerumbenennungen
# links jeweils der Name vor einer Änderung, rechts der Neue
# falls mehrere Änderungen stattfanden einfach beispielsweise das hier schreiben:
# stationsumbenennung = {"GanzAlterName" : "AlterName", "AlterName" : "NeuerName"}
# Diese Einstellung muss nicht geändert werden, wenn der Zeitraum geändert wird.
# Wenn ein alter Name gar nicht gefunden wird, der hier eingetragen wird,
# wird dieser Eintrag einfach ignoriert.
# Also einfach einmal alle Umbenennungen über den gesamten Wetterturnier-Zeitraum eintragen.

teilnehmerumbenennung = {"MM-UKMO-MOS": "Eugenia",
                         "MM-MOS": "EmJay",
                         "MM-MOS-Mix": "Enova",
                         "MM-EZ-MOS": "Echinacin",
                         "MM-GFS-MOS": "Egeria",
                         "DWD-ICON-MOS": "GME-MOS",
                         "DWD-EZ-MOS": "EZ-MOS",
                         "DWD-MOS-Mix": "DWD-MOSMixEZGME",#{"DWD-MOSMix(EZ+GME)","DWD-MOSMixEZGME"}
                         "MSwr-GFS-MOS": "MeteoService-GFS-MOS",
                         "MSwr-MOS-Mix": "MSwr-MOSMixGFSHIR", #{"MSwr-MOSMix(GFS+HIR)","MSwr-MOSMixGFSHIR"},
                         "MOS-Mix" : "GRP_MOS"
}

# laut Papierliste => "MOS-T" : "DWD-MOS-T" – das stimmt gar nicht oder?

## Teilnehmerstartzeitpunkte
# Dictionary ALLER MOS-Systeme (um Fehler zu vermeiden sowohl alte als auch
# neue Namen). Zuweisung entspricht dem Datum des Einstiegs des MOS-Systems,
# das angenommen werden soll. Manuelle Eingabe ist sinnvoller und einfacher.
# Wenn ein leerer String zugeordnet wird, geht die Auswertung davon aus, dass
# das MOS- System eigentlich im gesamten Zeitraum mitspielen hätte sollen und
# gibt je nach Einstellungen in punkteersetzung Ersatzpunktzahlen für Fehltage
mos_namen_starttermine = {"DWD-ICON-MOS": "03.03.2000",
                          "DWD-EZ-MOS": "04.06.2004",
                          "DWD-MOS-Mix": "05.12.2003",
                          "MOS-T": "03.09.2010", 
                          "MSwr-GFS-MOS": "30.01.2004",
                          "MSwr-MOS-Mix": "21.03.2014",
                          "MOS-Mix": "03.03.2000", # Starttermin vom DWD-ICON-MOS uebernommen
                          "Ms.Os": "03.03.2000", # Starttermin vom DWD-ICON-MOS uebernommen
                          "MSwr-EZ-MOS": "19.06.2015",
                          "Grisuji-GFS-L1-MOS": "24.11.2017",
                          "Grisuji-GFS-L2-MOS": "24.11.2017",
                          "Grisuji-EZ-L1-MOS": "09.11.2018",
                          }

# Ignorieren. Ist nur dafür, um die Variable "auswertungsteilnehmer"
# entspannter ausfüllen zu können.
mos_teilnehmer = list(mos_namen_starttermine.keys())

##############################################################################
########## Spezifische Konfiguration #########################################
##############################################################################


### Auswertung ###

## Zeitspanne der Datenauswertung (jeweils Format TT.MM.JJJJ !!!)
# Termine müssen jeweils nicht einem Freitag (Prognosetage) entsprechen.
# Beim Starttermin wird ansonsten einfach der nächste Freitag genommen,
# beim Endtermin der letzte Freitag vor dem angegebenen Datum.
# Wenn Endtermin den Wert "" hat, wird der aktuellste, verfügbare Termin
# genommen
#starttermin  = "22.06.2001"
#starttermin  = "01.07.2005"
#starttermin  = "22.10.2016"
#starttermin  = "10.12.2008"
#starttermin  = "15.11.2008"
#starttermin  = "19.06.2015"
#starttermin  = "01.09.2016"
#starttermin  = "19.09.2016"
#starttermin  = "19.06.2017"
#endtermin    = "01.01.2023"
starttermin  = "26.07.2025"
endtermin    = "01.08.2025"

## Auswertungstage (Auswertungszeitraum wäre irreführend, denn das ist es
# gerade nicht): Soll jeweils das ganze Wochenende oder sollen nur die
# Samstage/Sonntage ausgewerten werden?
#auswertungstage = ["Sa"] #nur für Samstag
auswertungstage = ["So"] #nur für Sonntag
#auswertungstage = ["Sa", "So"] #für beide Tage
#auswertungstage = ["Sa", "So"]

## Teilnehmer der Auswertung
# Entweder eine Liste mit den Namen schreiben auswertungsteilnehmer = ["spielerA", "spielerB"]
# oder auswertungsteilnehmer = mos_teilnehmer schreiben, wenn alle Mos-Systeme ausgewertet werden sollen
# oder eine Mischung aus beidem auswertungsteilnehmer = mos_teilnehmer + ["Moses", "Petrus"]
# Wenn menschliche Spieler ausgewählt werden, sollten diese mindestens 32 Wochen mitgespielt haben,
# damit das Plot-Verhalten auf dem "Recent Weeks"-Plot sinnvoll ist, bei MOS-Teilnehmer wird dies durch
# die Eingabe eines Startdatums in mos_namen_starttermine geregelt.
# in der Einstellung "linieneigenschaften" unten in der config, müssen manuell hinzugefügte Teilnehmer
# auch Farben und Linieneigenschaften zugewiesen bekommen

auswertungsteilnehmer = ["MSwr-MOS-Mix","MSwr-EZ-MOS","MSwr-GFS-MOS","DWD-MOS-Mix","DWD-MOS-Mix-test","DWD-EZ-MOS","DWD-ICON-MOS","MOS-Mix"]
#auswertungsteilnehmer = ["MSwr-MOS-Mix","MSwr-EZ-MOS","MSwr-GFS-MOS","DWD-MOS-Mix","DWD-EZ-MOS","DWD-ICON-MOS","MOS-Mix"]

# fuer mehrere Grafiken mit unterschiedlichen Teilnehmern
auswertungsteilnehmer_multi = ["MSwr-MOS-Mix","MSwr-EZ-MOS","MSwr-GFS-MOS","DWD-MOS-Mix","DWD-EZ-MOS","DWD-ICON-MOS","MOS-Mix"]

## Elemente für die Auswertung
# mögliche Werte:
auswertungselemente_alt = elemente_archiv_alt[:] # damit alle verwendet werden
#auswertungselemente_neu = elemente_archiv_neu[:] # neue Elemente
#auswertungselemente_neu = ["PPP12"] # nur die Sd1-Werte verwenden
#auswertungselemente_alt = [e for e in elemente_archiv_alt if e not in ("Wv", "Wn")]
#auswertungselemente_neu  = [e for e in elemente_archiv_neu if "Sd" not in e]
#auswertungselemente_neu = ("Sd1", "Sd24")
auswertungselemente_neu = ("Sd1",)
# auswertungselemente = ["N", "Sd"]       #  um bestimmte zu verwenden

## Städte für die Auswertung
# Einfach in der Liste als Strings auflisten
# Beispiel:
#auswertungsstaedte = stadtnamen
auswertungsstaedte = ["Berlin"]
#auswertungsstaedte = ["Berlin", "Leipzig"]
#auswertungsstaedte = ["Innsbruck", "Wien", "Zürich"]


## Auswertungsmittelung in Wochen
# Über welchen Zeitraum sollen die Wertungen gemittelt werden?
# Abhängig von "auswertungstage", werden dann zum Beispiel bei
# auswertungsmittelungszeitraum = 4 entweder die mittlere Punktzahl von vier
# Gesamtwochenendswertungen berechnet oder eben von den vier Sams- oder
# Sonntagen in den vier Wochen
#auswertungsmittelungszeitraum = 13  # Vierteljare
#auswertungsmittelungszeitraum = 25  # Halbjahre
#auswertungsmittelungszeitraum = 50 # Wochen
auswertungsmittelungszeitraum = "a" #Jahre

# Wenn Auswertungsmittelungszeitraum = "a" (Jahre) ist, dann wird der
# Zeitraum automatisch auf die Jahre des Auswertungszeitraums gesetzt.
# Die Mindestanzahl an Wochen, die für eine Jahresmittelung
# vorhanden sein muss, kann hier eingestellt werden.
mindestanzahl_wochen_jahresmittelung = 25

# für die Kurzeitmittelungen im rechten Plot
# beschreibt den Raum der Mittelung in Form von Wochen Abstand zum
# Endzeitpunkt ([letzte Woche, letzte 2 Wochen, letzte 4 Wochen,..])
mittelungszeitspannen = [50, 20, 10, 5, 2, 1]

## Prozenthürde der Datenverfügbarkeit für Auswertungszeitraum
# Wenn beispielsweise über 4 Wochen gemittelt werden soll, wie viele Daten
# müssen für diesen Zeitraum mindestens vorhanden sein, sodass die Daten
# gemittelt angezeigt werden sollen? (dimensionslos: [0-1])
datenluecken_langfrist = 0.2

# Wie viel Prozent der Daten müssen für die Kurzfristgrafik (also die rechte
# Teilgrafik) vorhanden sein? (dimensionslos: [0-1])
datenluecken_kurzfrist = 0.75

#----------------------------------------------------------------------------#
## Ersetzung Datenlücken bei einzelnen Tagen oder Parametern

# Sollen Datenlücken bei einzelnen Tagen ersetzt werden?
# True fuehrt zu Ersetzung, False zu keiner Ersetzung
punkteersetzung_spieler = True # True oder False

# Sollen Datenlücken bei einzelnen Parametern ersetzt werden?
# True fuehrt zu Ersetzung, False zu keiner Ersetzung
# Bei fehlenden einzelnen Parametern fuehrt False zu
# einer Ersetzung von fehlenden Punkten durch 0
punkteersetzung_params = True # True oder False

# Welche Spieler sollen zur Ersetzung verwendet werden?
# Ist der Name nicht in der Liste, wird der Standardwert
# (0) verwendet. TODO Mittelwert von allen Teilnehmern?
punkteersetzung_ersatz = {"GRP_MOS": ("MOS-Mix"),
                          "MOS-Mix": ("GRP_MOS"),
                          "MSwr-MOS-Mix": ("MSwr-EZ-MOS", "MSwr-GFS-MOS"),
                          "MSwr-EZ-MOS": ("MSwr-GFS-MOS"),
                          "MSwr-GFS-MOS": ("MSwr-EZ-MOS"),
                          "DWD-MOS-Mix": ("DWD-EZ-MOS", "DWD-ICON-MOS"),
                          "DWD-EZ-MOS": ("DWD-ICON-MOS"),
                          "DWD-ICON-MOS": ("DWD-EZ-MOS"),
                          "DWD-MOS-Mix-test": ("DWD-MOS-Mix")}

#FIXME nicht mehr implementiert:
# wie viel Prozent des jeweiligen Zeitraums muss der Spieler mindestens
# mitgetippt haben, damit die Punkte ersetzt werden?
punkteersetzung_mindestprozentzahl = 50

#----------------------------------------------------------------------------#


### Grafikeinstellungen ###

## Sprache der Beschriftung
sprache = "de" # "de" oder "en"

# einzelne beschriftungen (außer der untersten Zeile, dort wohl kaum
# notwendig)
beschriftungen = {"en" : {"titel": "MOS AUTOMATS COMPARISON",
                          "titel_links": "Recent Years",
                          "titel_rechts": "Recent Year",
                          "achse_links": "Lost points per individual "\
                                         "forecast\n(per day, city and "\
                                         "element)",
                          "achse_rechts": "Lower values: Better"},

                  "de" : {"titel": "VERGLEICH MOS-SYSTEME",
                          "titel_links": "Letzte Jahre",
                          "titel_rechts": "Letzte Wochen",
                          "achse_links": "Verlorene Punkte pro "\
                                         "individueller Vorhersage\n(pro "\
                                         "Tag, Stadt und Element)",
                          "achse_rechts": "Niedrigere Werte: Besser"}}

## Anzahl der Spalten in der Legende der Grafik
# Je nach Anzahl der Auswertungsteilnehmer möchte man mit der Spaltenanzahl
# herumspielen. 4 oder 5 scheint ein guter Mittelweg zu sein.
grafik_spaltenanzahl = 4


## Hervorzuhebende Teilnehmer
# Welche Teilnehmerlinien sollen im Plot fett gedruckt werden?
teilnehmerlinien_dickgedruckt = ["DWD-MOS-Mix","MSwr-MOS-Mix","Ms.Os"]


## Liniendicke
# Welche Liniendicke soll standardmäßig udn welche für hervorgehobene Teilnehmer im linken bzw. rechten Plot verwendet werden?
# Zwischen 1 und 4 sind empfehlenswerte Größen, 1 ist sehr dünn und 4 schon ziemlich dick
liniendicke = {"linker_plot": {"normal": 2, "dick": 4},
               "rechter_plot": {"normal": 1, "dick" : 3}}


## Farbe und Linienart
# Welche Farbe und Linienart sollen die jeweiligen Teilnehmer haben? Hier bitte immer den neuesten Namen angeben,
# wie in "teilnehmerumbenennung" angegeben. In die Liste immer zunächst den Farbcode und dann die Strichart.
# Farbcodes können von hier entnommen werden http://html-color-codes.info/webfarben_hexcodes/ oder nach "html Farbcodes" googlen
# Stricharten können sein: "-","--",":","-." Bedeutung: durchgezogen, gestrichelt, gepunktet oder "gestrichpunktet"
linieneigenschaften = {"MOS-T": ["#9CC349", "--"],
                       "MM-UKMO-MOS": ["#E076C0", "-"],
                       "MM-MOS": ["#F03FBB", "--"],
                       "MM-EZ-MOS": ["#FFB49B", "-"],
                       "MM-GFS-MOS": ["#A5007C", "-"],
                       "DWD-ICON-MOS": ["#FFE813", "-"],
                       "DWD-EZ-MOS": ["#5B1400", "-"],
                       "DWD-MOS-Mix": ["#DEC000", "--"],
                       "DWD-MOS-Mix-test": ["#EDB000", "--"],
                       "MSwr-GFS-MOS": ["#00B7FF", "-"],
                       "MSwr-MOS-Mix": ["#000000", "--"],
                       "MOS-Mix": ["#007C11", "--"],
                       "GRP_MOS": ["#007C11", "--"],
                       "MSwr-HIR-MOS": ["#3FCBA8", "-"],
                       "Ms.Os": ["#DF0000", "--"],
                       "MSwr-EZ-MOS": ["#0700C5", "-"],
                       "MM-MOS-Mix": ["#FF3939", "--"],
                       "Moses": ["#EF6800", "-."],
                       "Petrus": ["#FFBE4C", "-."],
                       "Georg": ["#0068EF", "-."],
                       "Schneegewitter": ["#6800EF", "--"],
                       "Pfingstochse": ["#68EF00", "-."],
                       "WB-Berlin": ["#0000FF", "-."],
                       "Grisuji-GFS-L1-MOS": ["#81F781", "-"],
                       "Grisuji-GFS-L2-MOS": ["#00FF80", "-"],
                       "Grisuji-EZ-L1-MOS": ["#00FF90", "-"],
                       }

## Marker-Einstellungen
# Es kann vorkommen, dass für die linke Grafik nur der neueste Wert zur Verfügung steht.
# In dem Fall, wird ein Zeichen mit einer bestimmten Größe ganz rechts im linken Plot angezeigt.
# Hier kann die Art des Markers und die Größe eingestellt werden.
# Für die Art des Markers siehe: http://matplotlib.org/examples/lines_bars_and_markers/marker_reference.html
# Standard war marker = "o" und marker_groesse = 12
marker = "D"
marker_groesse = 12


## Skalenfaktor
# Der Faktor, der die y-Achsen Limits bestimmt anhand dieser Formel:
# abs(ymax["linker_plot"]-ymax["rechter_plot"]) + abs(ymin["linker_plot"]-ymin["rechter_plot"]) < cfg.skalenfaktor*(ymax["linker_plot"]-ymin["linker_plot"])
# Wenn Bedingung wahr ist, haben beide Plots die gleichen Limits auf der y-Achse
# Wenn sie falsch ist oder Skalenfaktor == 0, haben sie unterschiedliche Limits.
skalenfaktor = 0
