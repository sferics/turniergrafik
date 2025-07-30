
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

import sys

from operator import itemgetter

# replace ajax_print by db_read
#import ajax_print
import db_read
import graphics
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

    day_1 = date(1970, 1, 2)

    # pruefen, ob das Datum zu frueh angesetzt wurde
    if day_x > day_1:

        days_delta = day_x - day_1 #FIXME ?? + timedelta(days = 1)

        return days_delta.days

    else:
        raise ValueError("Der Starttermin ist nicht valide.")


def index_2_date(input_index):

    """
    Datum aus dem Tagesindex (der wievielte Tag, seit dem 02.01.1970)
    berechnen (Beispiele -> siehe date_2_index())
    """

    if input_index > 0:

        # zur Berechnung des Datums muss nur der Tagesindex bzw. die Anzahl an
        # Tagen seit dem 02.01.1970 auf eben dieses Datum addiert werden
        return date(1970, 1, 2) + timedelta(days = input_index)

    else:
        raise ValueError("Der Tagesindex ist nicht korrekt.")


def get_friday_range(begin, end):

    """
    bestimmt die Grenzen der zu bearbeitenden Freitags-Indizes
    (der wievielte Tag, seit dem 02.01.1970 etc. ..)
    """

    if begin > 0 and end > begin:

        # rundet den Starttag auf den naechsten Freitag auf
        # (Jeder 7. Tag ist ein Freitag, da die Zaehlung mit Freitag beginnt)
        begin += 7 - (begin % 7)

        # rundet den Endtag auf den naechsten Freitag ab
        end -= - 7 + (end % 7)

        # end+1, da range exklusive dem Ende zaehlt
        #return begin+1, end+1
        return begin, end

    else:

        raise ValueError("Der Start- oder End-Wert sind fehlerhaft.")

#FIXME
'''
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
'''#FIXME

def short_term_mean(points, dates, mean_weaks, max_nan_ratio, cities=5):

    """
    berechnet aus einer Liste von Punktzahlen, die (arithmetischen)
    Mittelwerte ueber gewaehlte Zeitspannen am Ende der Liste

    Argumente:
    Punkteliste, Mittelungszeitspannen(Liste), Enddatum(Index),
    max Anteil an NaNs

    Rueckgabe: [(<Tagesindex(Ende jeder Zeitspanne)>,<Punkteverlust>)]
    """

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

        else:
            mean = np.nan

        # i*7, da in Wochen gezaehlt wurde und Tage gesucht sind
        date = max(dates) - i*7

        # Datum fuer Mittelungszeitraum aus Liste ausschneiden
        print(dates)
        print(len(dates))
        print(cities, i)
        print(cities*i)
        #date = dates[- (cities*i)]

        mean_date_list.append((date, mean))

    print(len(mean_date_list))
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

    long_term_means = []
    ii = 0

    # geht in Schritten mit der definierten Zeitspannengroesse durch die Tage

    if mean_time_span == "a":
        
        # calculate the average number of weeks in all years from number of dates and cities
        # and set it as mean_time_span. This is done to get the same number of weeks for all years
        mean_time_span = int( len(dates) / cities / 52 ) #FIXME

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

        else:
            # wenn der Prozentsatz an NaNs ueberschritten wurde, gib Nan aus
            mean = np.nan

        # 7*x, da in Wochen gezaehlt wurde und Tage gesucht sind
        #end_date = begin_date + 7*i + 7*mean_time_span #TODO CHECKME!
        
        # Datum fuer Mittelungszeitraum aus Liste ausschneiden
        #print(mean_time_span)
        end_date = dates[ cities * (ii+1) * mean_time_span ]
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

    return np.nanmean(PointsLost)


kuerzel = cfg.id_zu_kuerzel.values()
ids     = cfg.id_zu_kuerzel.keys()
kuerzel_zu_id = {}
for k, i in zip(kuerzel, ids):
    kuerzel_zu_id[k] = i


def city_to_id(city):
    
    try: return int(city)
    except ValueError:
        if len(city) == 3:
            return kuerzel_zu_id[city]
        else: return cfg.stadt_zu_id[city]


if __name__ == "__main__":

    faulty_dates = set()

    from argparse import ArgumentParser as ap

    # Parse command line arguments
    ps = ap()
    ps.add_argument("-v", "--verbose", help="increase output verbosity",
                        action="store_true")
    options = ("params", "cities", "days", "times", "users")
    for option in options:
        ps.add_argument("-"+option[0], "--"+option, type=str, help="Set "+option)
    args = ps.parse_args()

    if args.verbose:
        verbose = True

    for option in options:
        try: exec( option + "=" + "args." + option + ".split(',')" )
        except: exec(option + "=" + "None")
        #print( eval(option), type(eval(option)) )

    # Anfangs- und Endtermin zum jeweiligen Tagesindex konvertieren
    begin, end = get_friday_range(date_2_index(cfg.starttermin),
                                  date_2_index(cfg.endtermin))

    cfg.auswertungselemente   = params if params else cfg.auswertungselemente
    #print(cfg.auswertungselemente)

    # Indizes der zu verwendenden Auswertungselemente finden
    try:
        eval_el_indexes = [cfg.elemente_archiv.index(s)
                           for s in cfg.auswertungselemente]

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
    for p in cfg.auswertungsteilnehmer:
        UserValueLists[p] = []

    #TODO Archiv-Ordner checken und erstellen hierher verschieben
    
    # Datenbankverbindung herstellen
    db = db_read.db()

    # Freitags-Indizes durchgehen (+1/+2: Iteration ab 1, inklusive Ende)
    for i in range(begin+1, end+1, 7):
        
        #print( index_2_date( i-1 ) )
        if i >= 19363:
            #TODO funktioniert nur, wenn alle Element gewaehlt wurden. Was tun bei spezifischen Elementen?
            cfg.auswertungselemente = cfg.auswertungselemente_alt

        FileName = "{}/{}_{}.npz".format(cfg.archive_dir_name, 1, i)
        
        # erstelle die Datei, wenn die sie noch nicht angelegt wurde
        if not os.path.isfile(FileName) or os.path.getsize(FileName) == 22:
            # Erstellen und einlesen
            #ajax_print.ArchiveParse(1, i)
            db_read.ArchiveParse(db, 1, i)

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

            FileName = "{}/{}_{}.npz".format(cfg.archive_dir_name, city_id, i)

            # erstelle die Datei, wenn die sie noch nicht angelegt wurde
            if not os.path.isfile(FileName):

                # Erstellen und einlesen
                #ajax_print.ArchiveParse(city_id, i)
                db_read.ArchiveParse(db, city_id, i)
                    #TODO Dateipfad als Eingabe
                    #TODO Datei hier schreiben

            # Datei einlesen
            npzfile = np.load(FileName)
            
            missing = 0
            
            for Player in cfg.auswertungsteilnehmer:

                # Starttermin des Spielers auslesen
                try:
                    start_date = date_2_index(cfg.mos_namen_starttermine[Player])
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
                        faulty_dates.add(i)
                        # alternativen Namen probieren
                        try: 
                            alternative_name = cfg.teilnehmerumbenennung[Player]
                            #print("%s nicht gefunden! Alternativer Name: %s"
                            #      % (Player, alternative_name) )
                            # Punkte des Spielers aus Datei einlesen
                            player_point_list = npzfile[alternative_name]

                        # eine leere Liste vom naechsten try mit 'NameError'
                        # abgefangen
                        except (KeyError, ValueError):
                            faulty_dates.add(i)
                            #Ersatzspieler
                            try:
                                ersatz_name = cfg.punkteersetzung_menschen_ersatzspieler
                                player_point_list = npzfile[ersatz_name]
                            
                            except (KeyError, ValueError):
                                missing += 1
                                player_point_list = [np.nan] * 24
                                #sys.exit("%s nicht gefunden - kein Ersatz!" % Player)
                                
                                # add NaN to list
                                UserValueLists[Player].append( np.nan )
                                UserValueLists[Player].append( i-1 )

                                # delete all files of this tdate
                                from pathlib import Path
                                for p in Path(cfg.archive_dir_name).glob(f"?_{i}.nz"):
                                    p.unlink()
                                continue
                    except Exception as e:
                        faulty_dates.add(i)
                        import traceback
                        traceback.print_exc()
                        print(FileName)
                        missing += 1
                        player_point_list = [np.nan] * 24
                        #sys.exit("%s nicht gefunden - kein Ersatz!" % Player)
                        # add NaN to list
                        UserValueLists[Player].append( np.nan )
                        UserValueLists[Player].append( i-1 )

                        # delete all files of this tdate
                        from pathlib import Path
                        for p in Path(cfg.archive_dir_name).glob("?_{i}.nz"):
                            p.unlink()
                        continue
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
                        faulty_dates.add(i)
                        #continue
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

            if 0 < missing < len(cfg.auswertungsteilnehmer):
                
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
    long_term_data = []
    short_term_data = []

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

        userpoints = np.nanmean( \
            userpoints.reshape(-1, len(cfg.auswertungsstaedte)), axis=1)

        #print( np.round(userpoints,1) )

        # Langfrist und Kurzfristberechnungen
        cities = len(cfg.auswertungsstaedte)

        long_term_data.append((player, long_term_mean(userpoints, userdates,
                                            cfg.auswertungsmittelungszeitraum,
                                            cfg.anteil_datenverfuegbarkeit,
                                            cities)))
        
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

    # Grafik erstellen
    graphics.erstelleGrafik(long_term_data, short_term_data, cfg)

    #------------------------------------------------------------------------#
    # Ausgabe der Laufzeit des Programms
    print ("Benoetigte Laufzeit des Scriptes: {0} Sekunden"
           .format(time.time() - startTime))
    #------------------------------------------------------------------------#
    
    #print("Turniere mit fehlenden Spielern")
    #print( missing_list )

    print("Turniertage mit fehlenden Spielern")
    print(faulty_dates)
