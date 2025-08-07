
### Bibliotheken

# Zeit/Kalender
import time
import locale
from datetime import date
from datetime import timedelta
from datetime import datetime as dt

# einfachere Berechnungen und Umgang mit Fehlwerten
import numpy as np

# zur grafischen Darstellung
import matplotlib
# plotting without X server
matplotlib.use('Agg')
import matplotlib.pyplot as plt
# damit kann das Logo einfach auf dem Plot dargest. werden:
from matplotlib.cbook import get_sample_data

# Ermöglicht das Wechseln der Ordner
import os
# Ermöglicht das Einlesen von Dateien
import sys
# Ermöglicht das Sortieren von Listen
from operator import itemgetter

# replace ajax_print by db_read
#import ajax_print
import db_read
import graphics
# Ermöglicht das Einlesen von Konfigurationsdateien
import config as cfg

#----------------------------------------------------------------------------#
# Setzen des Startzeitpuntes zur Messung der Laufzeit des Programms
startTime = time.time()

# Liste der Turnier mit fehlenden Spielern
missing_list = []

#----------------------------------------------------------------------------#

def date_2_index(input_date):
    """
    Tag-Index (der wievielte Tag, seit dem 02.01.1970) aus einem gegebenen
    Datum berechnen    
    Beispiele:
    Tag 1:     Freitag, 02.01.1970
    Tag 8:     Freitag, 09.01.1970
    Tag 17837: Freitag, 02.11.2018
    """
    # wenn ein Datum eingegeben wurde, konvertiere es in ein datetime-Objekt
    if not input_date == "":
        
        # datetime-objekt wird in date-obj. umgewandelt
        day_x = dt.strptime(input_date, "%d.%m.%Y").date()
        
    # wenn das Datum leer gelassen wurde, nimm das aktuelle Datum
    else:
        day_x = dt.now().date()

        # pruefen ob der heutige tag sich zwischen Freitag und Montag befindet
        # dann muss der Freitag der letzten Woche als letzter Auswertungstag
        # gewaehlt werden, da der aktuelle noch nicht ausgewertet worden ist
        # Wochentags-Indizes: Monday := 0, Sunday := 6
        if day_x.weekday() >= 4 and day_x.weekday() != 0:

            # vier Tage abziehen um auf jeden Fall vor dem Freitag zu landen
            day_x -= timedelta(days = 4)

    # Tag 1 ist der 02.01.1970, der erste Freitag im Unix-Zeit-Kalender
    day_1 = date(1970, 1, 2)

    # pruefen, ob das Datum zu frueh angesetzt wurde
    if day_x > day_1:
        # Anzahl der Tage zwischen dem 02.01.1970 und dem eingegebenen Datum
        days_delta = day_x - day_1 #FIXME ?? + timedelta(days = 1)
        # Anzahl der Tage als Integer zurueckgeben
        return days_delta.days
    # wenn der Tag vor dem 02.01.1970 liegt, ist das Datum nicht valide
    else:
        raise ValueError("Der Starttermin ist nicht valide.")


def index_2_date(input_index):
    """
    Datum aus dem Tagesindex (der wievielte Tag, seit dem 02.01.1970)
    berechnen (Beispiele -> siehe date_2_index())
    """
    # wenn der Tagesindex groesser als 0 ist, kann das Datum berechnet werden
    if input_index > 0:

        # zur Berechnung des Datums muss nur der Tagesindex bzw. die Anzahl an
        # Tagen seit dem 02.01.1970 auf eben dieses Datum addiert werden
        return date(1970, 1, 2) + timedelta(days = input_index)
    # wenn der Tagesindex kleiner oder gleich 0 ist, ist das Datum nicht valide
    else:
        raise ValueError("Der Tagesindex ist nicht korrekt.")


def get_friday_range(begin, end):
    """
    bestimmt die Grenzen der zu bearbeitenden Freitags-Indizes
    (der wievielte Tag, seit dem 02.01.1970 etc. ..)
    """
    # wenn der Start- und Endtag groesser als 0 sind
    if begin > 0 and end > begin:

        # rundet den Starttag auf den naechsten Freitag auf
        # (Jeder 7. Tag ist ein Freitag, da die Zaehlung mit Freitag beginnt)
        begin += 7 - (begin % 7)

        # rundet den Endtag auf den naechsten Freitag ab
        end -= - 7 + (end % 7)

        # end+1, da range exklusive dem Ende zaehlt
        #return begin+1, end+1
        return begin, end
    # wenn der Start- oder Endtag kleiner oder gleich 0 ist, ist das Datum nicht valide
    else:
        raise ValueError("Der Start- oder End-Wert sind fehlerhaft.")

#FIXME
def old_2_new_players(players, rename_dict):

    """
    ersetzt in einer Teilnehmerliste alle alten durch neuere Teilnehmernamen
    (siehe cfg.teilnehmerumbenennung) und gibt sie als Tupel zurueck
    """

    for i, p in enumerate(players):

        if p in rename_dict:

           players[i] =  rename_dict[p]

    # Doppelte Spieler entfernen und als Tupel zurueckgeben
    return tuple(set(players))
#FIXME

def short_term_mean(points, dates, mean_weaks, max_nan_ratio, cities=5):
    """
    berechnet aus einer Liste von Punktzahlen, die (arithmetischen)
    Mittelwerte ueber gewaehlte Zeitspannen am Ende der Liste

    Argumente:
    Punkteliste, Mittelungszeitspannen(Liste), Enddatum(Index),
    max Anteil an NaNs

    Rueckgabe: [(<Tagesindex(Ende jeder Zeitspanne)>,<Punkteverlust>)]
    """
    # Liste der Mittelungszeitspannen
    mean_date_list = []
    #print( "points", points )
    #print( "dates", dates )
    #print( "mean_weaks", mean_weaks )
    for i in mean_weaks:
    
        # "schneidet" immer bestimmt grosse Stuecke heraus
        # (dafuer gedacht immer kleinere Stuecke zu bekommen)
        points_span = points[-i:]
        print(points_span)

        # gib Nan als Summe aus, wenn ein bestimmter Prozentsatz
        # (cfg.anteil_datenverfuegbarkeit) an NaNs ueberschritten wurde
        if (np.isnan(points_span).sum() / i) < max_nan_ratio:

            # bilde mittelwert (arithmetisch) ohne NaNs
            mean = np.nanmean(points_span)
        # wenn der Anteil an NaNs zu hoch ist, gib Nan als Mittelwert aus
        else:
            mean = np.nan

        # i*7, da in Wochen gezaehlt wurde und Tage gesucht sind
        date = max(dates) - i*7

        # Datum fuer Mittelungszeitraum aus Liste ausschneiden
        #print(dates)
        #print(len(dates))
        #print(cities, i)
        #print(cities*i)
        #date = dates[- (cities*i)]
        
        mean_date_list.append((date, mean))
    
    #print(len(mean_date_list))
    return mean_date_list


def long_term_mean(points, dates, mean_time_span, max_nan_ratio, cities=5):
    """
    berechnet aus einer Liste von Punktzahlen, die (arithmetischen)
    Mittelwerte ueber eine gewaehlte Zeitspanne, welche die Liste in
    Abschnitte gleicher Groesse unterteilt (der Rest wird verworfen, falls er
    kuerzer ist als die gewaehlte Zeitspanne):
    [...|...|...|..] -> [...|...|...] (. = Eintraege, | = Abschnittsende)

    Argumente:
    Punkteliste, Mittelungszeitspanne, Anfangsdatum(Index), max Anteil an NaNs

    Rueckgabe: [(<Tagesindex(Ende jeder Zeitspanne)>,<Punkteverlust>)]
    """
    
    # Liste der Mittelungszeitspannen
    long_term_means = []
    ii = 0

    # geht in Schritten mit der definierten Zeitspannengroesse durch die Tage
    # (z.B. 7 fuer eine Woche, 14 fuer zwei Wochen, 30 fuer einen Monat)
    if mean_time_span == "a":
        pass
        #TODO count weeks in year    
    
    for i in range(0, len(points)+1, mean_time_span ):
            
        # "schneidet" immer gleich grosse Stuecke heraus
        points_span = points[i:i+mean_time_span]

        # falls der letzte Teil kleiner als die gewaehlte Zeitspanne ist
        # faellt er weg
        if len(points_span) < mean_time_span:
            break

        # gib Nan als Summe aus, wenn ein bestimmter Prozentsatz
        # (cfg.anteil_datenverfuegbarkeit) an NaNs ueberschritten wurde
        if (np.isnan(points_span).sum() / mean_time_span) < max_nan_ratio:

            # bilde mittelwert (arithmetisch) ohne NaNs
            mean = np.nanmean(points_span)
        # wenn der Anteil an NaNs zu hoch ist, gib Nan als Mittelwert aus
        else:
            mean = np.nan

        # 7*x, da in Wochen gezaehlt wurde und Tage gesucht sind
        #end_date = begin_date + 7*i + 7*mean_time_span #TODO CHECKME!
        
        # Datum fuer Mittelungszeitraum aus Liste ausschneiden
        #print(mean_time_span)
        end_date = dates[ cities * ii * mean_time_span ]
        #print( "end_date", end_date )
        ii += 1
        
        long_term_means.append( (end_date, mean) )
    
    return long_term_means


def get_player_mean(pointlist,
                    auswertungstage,
                    auswertungselemente,
                    elemente_archiv,
                    elemente_max_punkte,
                    eval_indexes):
    """
    Berechnet das Tagesmittel eines einzelnen Spielers fuer einen gewaehlten
    Turniertag oder fuer das ganze Wochenende. Gibt NaN zurueck, falls der
    Spieler fuer den Tag nicht auffindbar ist.
    """

    # wenn beide Tage ausgewertet werden sollen
    if auswertungstage == ["Sa", "So"]:

        # wenn alle Elemente gewaehlt wurden
        if auswertungselemente == elemente_archiv:
            #print("Alle Elemente")

            # elementweisen Punkteverlust berechnen
            # maximal-Punkte-Liste wird 2mal hintereinander
            # genommen, da Samstag und Sonntag nacheinander
            # aufsummiert werden
            PointsLost = np.array((elemente_max_punkte * 2)) - np.array(pointlist)

            #print( pointlist )
            #print(np.round(PointsLost,1))

        # wenn nur bestimmte Elemente ausgewertet werden sollen
        else:

            # gibt aus der Liste die genannten (Index) Elemente aus
            # (es werden die Indizes der zu evaluierenden Elemente genommen,
            # sowie die gleichen Indizes um 12 nach oben verschoben, um auch
            # die Werte fuer Sonntag mit einzulesen)
            Points = itemgetter(*(eval_indexes+[i+12 for i in eval_indexes]))\
                                 (pointlist)

            # Punkte von den elementweisen maximalen Punktzahlen
            # elementweise abziehen
            PointsLost = [((elemente_max_punkte * 2)[i] - v)
                          for i, v in enumerate(Points)]

    else:

        # wenn nur Samstag ausgewertet werden soll
        if auswertungstage == ["Sa"]:

            # gibt aus der Liste die genannten (Index) Elemente aus
            Points = itemgetter(*eval_indexes)(pointlist)

        # wenn nur Sonntag ausgewertet werden soll
        elif auswertungstage == ["So"]:

            # gibt aus der Liste die genannten (Index) Elemente aus
            # (da die Listen immer Samstag und Sonntag hintereinander
            # beinhalten, muss hier auf den Index immer 12 aufgerechnet werden
            # um die Samstags-Werte zu ueberspringen)
            Points = itemgetter(*[i+12 for i in eval_indexes])(pointlist)

        else:
            raise ValueError("Nur Samstag (Sa) und Sonntag (So) sind valide "\
                             "Auswertungstage {}".format(auswertungstage))


        # Punkte von den elementweisen maximalen Punktzahlen
        # elementweise abziehen
        PointsLost = [(elemente_max_punkte[i] - v)
                      for i, v in enumerate(Points)]


    # Durchschnittlich verlorene Punkte berechnen (ohne NaNs)
    
    #print( "MEAN:", np.round( np.nanmean(PointsLost),1 ) )
    #print( "PointsLost:", np.round(PointsLost,1) )
    return np.nanmean(PointsLost)

#----------------------------------------------------------------------------#
# Konfigurationen laden
kuerzel = cfg.id_zu_kuerzel.values()
ids     = cfg.id_zu_kuerzel.keys()
kuerzel_zu_id = {}

# Konvertiere die Abkuerzungen in IDs
for k, i in zip(kuerzel, ids):
    kuerzel_zu_id[k] = i


def city_to_id(city):
    """
    Konvertiert eine Stadt in eine ID, die in der Datenbank verwendet wird.
    Wenn eine ID (int) uebergeben wird, wird sie direkt zurueckgegeben.
    Wenn eine Abkuerzung (3 Buchstaben) uebergeben wird, wird die ID aus dem
    kuerzel_zu_id-Dictionary geholt.
    Wenn eine Stadt (String) uebergeben wird, wird die ID aus der
    cfg.stadt_zu_id-Liste geholt.
    """
    # wenn eine ID uebergeben wurde, gib sie direkt zurueck
    try: return int(city)
    # wenn eine Abkuerzung uebergeben wurde, gib die ID aus dem Dictionary
    except ValueError:
        # wenn die Abkuerzung in kuerzel_zu_id vorhanden ist, gib die ID zurueck
        if len(city) == 3:
            if city in kuerzel_zu_id:
                return kuerzel_zu_id[city]
        # wenn die Abkuerzung nicht in kuerzel_zu_id vorhanden ist, gib stadt_zu_id zurueck
        else: return cfg.stadt_zu_id[city]


if __name__ == "__main__":
    """
    Hauptprogramm, welches die Auswertung durchfuehrt.
    """
    # Importiere die Konfiguration
    from argparse import ArgumentParser as ap
    
    # Parse command line arguments
    ps = ap()
    ps.add_argument("-v", "--verbose", help="increase output verbosity",
                        action="store_true")
    options = ("params", "cities", "days", "times", "users")
    # Optionen, die in der Konfiguration gesetzt werden koennen
    for option in options:
        # Argumente mit dem Namen der Option, die in der Konfiguration gesetzt
        ps.add_argument("-"+option[0], "--"+option, type=str, help="Set "+option)
    # Verarbeite die Argumente
    args = ps.parse_args()
    
    # Wenn verbose gesetzt wurde, wird die Ausgabe erweitert
    if args.verbose:
        verbose = True
    
    # TODO Umschreiben ohne exec und eval (ist unsicher und langsam)
    for option in options:
        # versuche die Option aus den Argumenten zu lesen
        try: exec( option + "=" + "args." + option + ".split(',')" )
        # wenn die Option nicht gesetzt wurde, wird sie auf None gesetzt
        except: exec(option + "=" + "None")
        # wenn die Option nicht gesetzt wurde, wird sie auf None gesetzt
        #print( eval(option), type(eval(option)) )

    # Anfangs- und Endtermin zum jeweiligen Tagesindex konvertieren
    begin, end = get_friday_range(date_2_index(cfg.starttermin),
                                  date_2_index(cfg.endtermin))
    #print("Begin:", begin, "End:", end)
    cfg.auswertungselemente   = params if params else cfg.auswertungselemente
    #print(cfg.auswertungselemente)

    # Indizes der zu verwendenden Auswertungselemente finden
    try:
        eval_el_indexes = [cfg.elemente_archiv.index(s)
                           for s in cfg.auswertungselemente]
    # wenn die Auswertungselemente nicht in der Elementeliste vorhanden sind
    except ValueError:
        print("Die Auswertungselemente sind nicht valide bzw. nicht "\
              "oder nur teilweise in der Elementeliste vorhanden")
        sys.exit()

    # zu den Auswertungselementen passende Liste an maximalen Punkten fuer die
    # jeweiligen Elemente berechnen
    max_points_elements = [cfg.elemente_max_punkte[i]
                            for i in eval_el_indexes]
	
    cfg.auswertungsstaedte    = cities if cities else cfg.auswertungsstaedte
    cfg.auswertungsteilnehmer = users if users else cfg.auswertungsteilnehmer
    cfg.auswertungstage       = days if days else cfg.auswertungstage

    # Dictionary von Teilnehmern und dazugehoerige Punktelisten initialisieren
    UserValueLists = {}
    # Teilnehmernamen in UserValueLists als Keys anlegen
    for p in cfg.auswertungsteilnehmer:
        UserValueLists[p] = []

    #TODO Archiv-Ordner checken und erstellen hierher verschieben

    # Freitags-Indizes durchgehen (+1/+2: Iteration ab 1, inklusive Ende)
    for i in range(begin+1, end+1, 7):
        # Ausgabe des aktuellen Tages
        #print( index_2_date( i-1 ) )
        # Dateiname der Datei, die den Tagesmittelwert des Spielers enthaelt
        FileName = "{}/{}_{}.npz".format(cfg.archive_dir_name, 1, i)
        
        # erstelle die Datei, wenn die sie noch nicht angelegt wurde
        if not os.path.isfile(FileName) or os.path.getsize(FileName) == 22:
            # Erstellen und einlesen
            #ajax_print.ArchiveParse(1, i)
            db_read.ArchiveParse(1, i)

        #Dateigroesse prüfen (Ist Turniertag)?
        if os.path.getsize(FileName) == 22:
            print("Kein Turniertag!")
            continue
        
        for city in cfg.auswertungsstaedte:

            # Stadt in ID konvertieren
            city_id = city_to_id(city)

            # zu ignorierende Termine der entsprechenden Stadt in IDs umwandeln
            # (wird fuer jede Stadt einmal neu berechnet)
            zu_ignorierende_tage = \
                [date_2_index(s) for s in cfg.zu_ignorierende_termine[city_id]]
            # Dateiname der Datei, die den Tagesmittelwert des Spielers enthaelt
            FileName = "{}/{}_{}.npz".format(cfg.archive_dir_name, city_id, i)

            # erstelle die Datei, wenn die sie noch nicht angelegt wurde
            if not os.path.isfile(FileName):

                # Erstellen und einlesen
                #ajax_print.ArchiveParse(city_id, i)
                db_read.ArchiveParse(city_id, i)
                    #TODO Dateipfad als Eingabe
                    #TODO Datei hier schreiben

            # Datei einlesen
            npzfile = np.load(FileName, allow_pickle=True)
            missing = 0
            
            for Player in cfg.auswertungsteilnehmer:

                # Starttermin des Spielers auslesen
                try:
                    start_date = date_2_index(cfg.mos_namen_starttermine[Player])
                # wenn der Spieler keinen Starttermin hat, wird der Index 0
                except KeyError:
                    start_date = 0

                # zu ignorierende Termine abfangen
                # TODO pruefen
                if i >= start_date and i not in zu_ignorierende_tage:

                    # Try-Except ist performancemaessig besser als eine
                    # Abfrage, ob der Name in der Datei enthalten ist (-> IO)

                    # versuche den Spieler fuer den Tag auszulesen
                    try:
                        # Punkte des Spielers aus Datei einlesen
                        player_point_list = npzfile[Player]

                    # der Spieler wurde fuer den Tag nicht gefunden
                    except KeyError:
                        # alternativen Namen probieren
                        try:
                            # wenn der Spieler umbenannt wurde, wird der alternative Name genommen
                            alternative_name = cfg.teilnehmerumbenennung[Player]
                            #print("%s nicht gefunden! Alternativer Name: %s"
                            #      % (Player, alternative_name) )
                            # Punkte des Spielers aus Datei einlesen
                            player_point_list = npzfile[alternative_name]

                        # eine leere Liste vom naechsten try mit 'NameError'
                        # abgefangen
                        except KeyError:
                            #Ersatzspieler
                            try:
                                ersatz_name = cfg.punkteersetzung_ersatz[Player]
                                player_point_list = npzfile[ersatz_name]
                            # wenn der Ersatzspieler auch nicht gefunden wurde
                            except KeyError:
                                missing += 1
                                player_point_list = [np.nan] * 24
                                #sys.exit("%s nicht gefunden - kein Ersatz!" % Player)
                                # delete all files of this tdate
                                from pathlib import Path
                                for p in Path(cfg.archive_dir_name).glob("?_"+i+".nz"):
                                    p.unlink()
                                break
                    # falls der Spieler gefunden wurde, aber keine Punkte hatte
                    try:
                        # Tagesmittel des Spielers an die jeweilige Liste anfuegen
                        #print(Player, "Tagesmittel")
                        UserValueLists[Player].append(
                            get_player_mean(player_point_list,
                                            cfg.auswertungstage,
                                            cfg.auswertungselemente,
                                            cfg.elemente_archiv,
                                            max_points_elements,
                                            eval_el_indexes) )
                        UserValueLists[Player].append( i-1 )

                    # der Spieler wurde fuer den Tag nicht gefunden
                    except NameError:
                        #continue
                        #print("NameError: %s nicht gefunden!" % Player)
                        UserValueLists[Player].append( np.nan )
                        UserValueLists[Player].append( i-1 )

                    """
                    players_in_file = npzfile.keys()
                    name = "" #FIXME ACHTUNG: So darf es keinen Spieler mit
                              #      leerem Namen geben!

                    if Player in players_in_file:
                        name = Player

                    # sonst pruefen, ob einer der alternativen Namen des
                    # Spielers in der Datei auftaucht
                    elif Player in cfg.teilnehmerumbenennung.keys():
                        alt_name = cfg.teilnehmerumbenennung[Player] \
                            .intersection( set(players_in_file) )

                        # wenn einer der alternativen Namen auftaucht
                        if alt_name != set():

                            # set zu string konvertieren
                            name = list(alt_name)[0]

                    # versuche den Spieler fuer den Tag auszulesen
                    try:

                        # Punkte des Spielers aus Datei einlesen
                        player_point_list = npzfile[name]

                        # Tagesmittel des Spielers an die jeweilige Liste anfuegen
                        UserValueLists[Player].append(
                            get_player_mean(player_point_list,
                                            cfg.auswertungstage,
                                            cfg.auswertungselemente,
                                            cfg.elemente_archiv,
                                            max_points_elements,
                                            eval_el_indexes) )

                    # der Spieler wurde fuer den Tag nicht gefunden
                    except KeyError:
                        UserValueLists[Player].append(np.nan)
                    """
                # zu ignorierende Termine abfangen und mit NaN beschreiben
                else:
                    UserValueLists[Player].append( (np.nan, i-1) )
            
            # Anzahl der fehlenden Spieler in der Datei
            if 0 < missing < len(cfg.auswertungsteilnehmer):
                #print("Fehlende Spieler in Datei {}: {}".format(FileName, missing))
                if i not in missing_list:
                    missing_list.append(i)
                    #print(city)
                    #print(i)
                    #print( index_2_date(i) )

    #------------------------------------------------------------------------#
    print ("Benoetigte Laufzeit fuer Einlesen und Tagesmitteln: {0} Sekunden"
           .format(time.time() - startTime))
    #------------------------------------------------------------------------#

    # Kurzfrist- und Langfrist-Listen initialisieren
    # Typ: [(string Player, [(datetime Date, float LostPoints)])]
    long_term_data  = []
    short_term_data = []
    
    # Iteriere ueber alle Spieler in der UserValueLists
    for player in UserValueLists.keys():

        # Die Liste enthält abwechselnd Punktzahl und das zugehoerige Datum.
        # Wir schneiden beides nun aus um sie von einander zu trennen.
        userpoints = np.array(UserValueLists[player][::2])
        userdates  = UserValueLists[player][1::2]

        # Die Listen bestehen nun aus mehreren Staedten hintereinander
        # ([BER|VIE|ZUR|IBK|LEI]) und es muss noch ueber die Staedte gemittelt
        # werden.
 
        # die lange Datenliste in eine numpy-'Matrix' konvertieren, die so
        # viele Zeilen hat, wie Staedte verarbeitet wurden und anschließendes
        # mitteln ueber die Spalten (BER[1]+VIE[1]+../Staedteanzahl)
        # [BER|VIE|ZUR|IBK|LEI] -> [[BER],[VIE],[ZUR],[IBK],[LEI]]
        #print( player )
        #print( np.round(userpoints,1) )
        #print( len(userpoints) )

        #print( "MATRIX" )
        #print( np.round( userpoints.reshape(-1, len(cfg.auswertungsstaedte)), 1) )

        # reshape der Punkteliste in eine Matrix, die so viele Zeilen hat,
        # wie es Teilnehmer gibt und so viele Spalten, wie es Auswertungsstaedte
        # gibt, und anschließendes mitteln ueber die Spalten
        # (BER[1]+VIE[1]+../Staedteanzahl)
        #print( "reshape" )
        userpoints = np.nanmean( \
            userpoints.reshape(-1, len(cfg.auswertungsstaedte)), axis=1)
        #print( "userpoints" )
        #print( np.round(userpoints,1) )
        
        # Langfrist und Kurzfristberechnungen
        cities = len(cfg.auswertungsstaedte)
        # berechne die Langfristmittelwerte
        long_term_data.append((player, long_term_mean(userpoints, userdates,
                                            cfg.auswertungsmittelungszeitraum,
                                            cfg.anteil_datenverfuegbarkeit,
                                            cities)))
        # berechne die Kurzfristmittelwerte
        short_term_data.append((player, short_term_mean(userpoints, userdates,
                                            cfg.mittelungszeitspannen,
                                            cfg.datenluecken_kurzfrist,
                                            cities)))

        #print( "short term" )
        #print( short_term_data[0] )

    #------------------------------------------------------------------------#
    print ("Benoetigte Laufzeit der Rechnungen ohne Grafik: {0} Sekunden"
           .format(time.time() - startTime))
    #------------------------------------------------------------------------#

    # Grafik erstellen ueber die Langfrist- und Kurzfristmittelwerte
    graphics.erstelleGrafik(long_term_data, short_term_data, cfg)

    #------------------------------------------------------------------------#
    # Ausgabe der Laufzeit des Programms
    print ("Benoetigte Laufzeit des Scriptes: {0} Sekunden"
           .format(time.time() - startTime))
    #------------------------------------------------------------------------#
    
    #print("Turniere mit fehlenden Spielern")
    #print( missing_list )
