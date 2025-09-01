
### Bibliotheken

# Zeit/Kalender
import time
import locale
from datetime import date
from datetime import timedelta
from datetime import datetime as dt
# fuer die Umwandlung von Strings in Datumsobjekte
from copy import copy

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
# Systemfunktionen
import sys

from operator import itemgetter

# replace ajax_print by db_read
#import ajax_print
import db_read
import graphics
import config_loader as cfg

from global_functions import index_2_year, date_2_index, index_2_date, get_friday_range, stadtname, city_to_id

#----------------------------------------------------------------------------#
# Setzen des Startzeitpuntes zur Messung der Laufzeit des Programms
startTime = time.time()

# Liste der Turnier mit fehlenden Spielern
missing_list = []

#----------------------------------------------------------------------------#

def old_2_new_players(players, rename_dict):
    """
    Ersetzt in einer Teilnehmerliste alle alten durch neuere Teilnehmernamen
    (siehe cfg.teilnehmerumbenennung) und gibt sie als Tupel zurueck

    :param players: Liste der Teilnehmernamen
    :param rename_dict: Dictionary mit alten Teilnehmernamen als Keys und
    den neuen Teilnehmernamen als Values

    :return: Tupel der Teilnehmernamen, in denen alle alten Namen durch
    die neuen ersetzt wurden, ohne Duplikate
    """
    # Iterieren ueber die Teilnehmerliste und ersetzen
    # der alten Namen durch die neuen Namen
    for i, p in enumerate(players):
        if p in rename_dict:
           players[i] =  rename_dict[p]

    # Doppelte Spieler entfernen und als Tupel zurueckgeben
    return tuple(set(players))


def short_term_mean(points, dates, mean_weaks, max_nan_ratio, cities=5):
    """
    Berechnet aus einer Liste von Punktzahlen, die (arithmetischen)
    Mittelwerte ueber gewaehlte Zeitspannen am Ende der Liste
    
    :param points: Liste der Punktzahlen
    :param dates: Liste der Tagesindizes (der wievielte Tag, seit dem 02.01.1970)
    :param mean_weaks: Liste der Zeitspannen, ueber die der Mittelwert gebildet
    werden soll (in Wochen)
    :param max_nan_ratio: Maximaler Anteil an NaN-Werten, der erlaubt ist, um
                          einen Mittelwert zu berechnen
    :param cities: Anzahl der Staedte, die in der Liste enthalten sind (default: 5)

    :return: Liste von Tupeln, die das Datum des letzten Tages des Mittelungszeitraums
    """
    # Initialisiere eine Liste fuer die Mittelwerte und die zugehoerigen Daten
    mean_date_list = []
    
    # Iteriere ueber die gewaehlten Zeitspannen
    for i in mean_weaks:
    
        # "schneidet" immer bestimmt grosse Stuecke heraus
        # (dafuer gedacht immer kleinere Stuecke zu bekommen)
        points_span = points[-i:]
        #print(points_span)

        # gib Nan als Summe aus, wenn ein bestimmter Prozentsatz
        # (cfg.anteil_datenverfuegbarkeit) an NaNs ueberschritten wurde
        if (np.isnan(points_span).sum() / i) < max_nan_ratio:

            # bilde mittelwert (arithmetisch) ohne NaNs
            mean = np.nanmean(points_span)
        # wenn der Prozentsatz an NaNs ueberschritten wurde, gib Nan aus
        else:
            mean = np.nan

        # von max(dates) ziehen wir (i-1)*7 Tage ab,
        # da in Wochen gezaehlt wurde und Tage gesucht sind
        # (wir ziehen eine Woche ab, damit das Enddatum stimmt)
        date = max(dates) - (i-1)*7

        # Datum fuer Mittelungszeitraum aus Liste ausschneiden
        # Haenge den Mittelwert und das Datum des letzten Tages
        # des Mittelungszeitraums an die Liste an
        mean_date_list.append((date, mean))

    #print(len(mean_date_list))
    return mean_date_list


def long_term_mean(points, dates, mean_time_span, max_nan_ratio, cities=5):
    """
    Berechnet aus einer Liste von Punktzahlen, die (arithmetischen)
    Mittelwerte ueber eine gewaehlte Zeitspanne, welche die Liste in
    Abschnitte gleicher Groesse unterteilt (der Rest wird verworfen, falls er
    kuerzer ist als die gewaehlte Zeitspanne):
    [...|...|...|..] -> [...|...|...] (. = Eintraege, | = Abschnittsende)

    :param points: Liste der Punktzahlen
    :param dates: Liste der Tagesindizes (der wievielte Tag, seit dem 02.01.1970)
    :param mean_time_span: Zeitspanne, ueber die der Mittelwert gebildet werden soll
    :param max_nan_ratio: Maximaler Anteil an NaN-Werten, der erlaubt ist, um
                          einen Mittelwert zu berechnen
    :param cities: Anzahl der Staedte, die in der Liste enthalten sind (default: 5)

    :return: Liste von Tupeln, die das Datum des letzten Tages des Mittelungszeitraums
    """

    long_term_means = []
    
    # Wenn Jahre individuell ausgewertet werden sollen
    if mean_time_span == "a":
        # Berechne für jedes Jahr die Mittelungszeitspanne individuell
        # Berechne die Anzahl der Tage im Jahr
        year_start = index_2_year(dates[0])
        year_end   = index_2_year(dates[-1])
        # Anzahl der Wochen und Spieltage für jedes Jahr in Dictionary speichern
        weeks_in_year = {}
        dates_in_year = {}

        # Die Mittelungszeitspanne ist für jedes Jahr unterschiedlich
        for d in dates:
            # Berechne das Jahr des Tagesindex
            year = index_2_year(d)
            # Wenn das Jahr noch nicht in der Liste ist, dann
            # initialisiere es mit der Anzahl der Wochen und dem Datum
            if year not in weeks_in_year:
                # Anzahl der Wochen im Jahr auf 1 setzen
                weeks_in_year[year] = 1
                # Initialisiere das Datum für das Jahr
                dates_in_year[year] = []
            # Wenn das Datum im Jahr liegt, dann zaehle die Woche hoch
            weeks_in_year[year] += 1
            # Füge das Datum zur Liste der Daten im Jahr hinzu
            dates_in_year[year].append(d)

        # Die Spieltage in der Liste sind in Schritten abhängig von der Anzahl der Städte
        # (d.h. die Liste ist in Blöcke unterteilt, die jeweils die Daten
        # für eine Stadt enthalten)
        dates = dates[::cities]
        first_tournament_of_year    = {}
        last_tournament_of_year     = {}
        long_term_means             = []
        
        # Gehe durch die Jahre und berechne die Mittelwerte
        for year in range(year_start, year_end+1):
            
            # Erstes Tournier des Jahres finden
            first_tournament_of_year[year] = min(dates_in_year[year])
            # Letztes Tournier des Jahres finden
            last_tournament_of_year[year] = max(dates_in_year[year])

            # Finde den Index des ersten Turniers des Jahres in dates
            idx         = dates.index(first_tournament_of_year[year])
            points_span = points[idx:idx+weeks_in_year[year]+1]
            
            # Falls die Anzahl der Punkte kleiner ist als die
            # Mindestanzahl an Wochen für die Jahresmittelung, dann
            # wird das Jahr übersprungen
            if len(points_span) < cfg.mindestanzahl_wochen_jahresmittelung:
                if verbose: print(f"Nicht genug Daten für Jahr {year}!")
                continue
            # Berechne den Mittelwert der Punkte, wenn der Anteil an NaNs
            # kleiner als der maximale Anteil an NaNs ist
            if (np.isnan(points_span).sum() / len(points_span)) < max_nan_ratio:
                mean = np.nanmean(points_span)
            else:
                mean = np.nan
            # Haenge den Mittelwert und das Datum des letzten Turniers
            # des Jahres an die Liste an
            long_term_means.append( (last_tournament_of_year[year], mean) )
        
        return long_term_means
    
    # Else kann hier weggelassen werden, da die Funktion nur
    # aufgerufen wird, wenn mean_time_span != "a"
    
    # Laufvariable fuer die Anzahl der Mittelungszeitraeume
    ii = 1
    
    anzahl_punkte = len(points)
    # Wenn eine Mindestanzahl an Wochen definiert ist,
    # dann wird diese verwendet, um die Anzahl der Punkte zu
    # vergleichen, die fuer die Berechnung des Mittelwerts
    # benoetigt werden. Ansonsten wird der Mittelwert
    # immer dann berechnet, wenn die Anzahl der Punkte
    # groesser ist als mean_time_span
    if cfg.mindestanzahl_wochen_definiert:
        if max(range(0, anzahl_punkte+1, mean_time_span)) < anzahl_punkte:
            anzahl_punkte += mean_time_span
    
    # geht in Schritten mit der definierten Zeitspannengroesse durch die Tage
    for i in range(0, anzahl_punkte+1, mean_time_span ):
        
        # Wenn die Anzahl der Punkte kleiner ist als die
        # Zeitspanne, die fuer die Mittelung benoetigt wird
        if i+mean_time_span >= len(points):
            # Wenn eine Mindestanzahl an Wochen definiert ist,
            # dann wird diese verwendet, um die Anzahl der Punkte zu
            # vergleichen, die fuer die Berechnung des Mittelwerts
            # benoetigt werden.
            if cfg.mindestanzahl_wochen_definiert:
                # Wenn i plus die Mindestanzahl an Wochen
                # kleiner ist als die Anzahl der Punkte, dann
                # wird mean_time_span auf die Differenz zwischen
                # der Anzahl der Punkte und i gesetzt, um die
                # Mittelung auf die verbleibenden Punkte zu beschraenken
                if i + cfg.mindestanzahl_wochen < len(points):
                    mean_time_span = len(points) - i
                # Sonst wird die Schleife abgebrochen
                else: break
            # Wenn keine Mindestanzahl an Wochen definiert ist,
            # dann wird die Schleife abgebrochen, da nicht genug
            # Punkte fuer die Mittelung vorhanden sind
            else: break
        
        # "schneidet" immer gleich grosse Stuecke heraus
        points_span = points[i:i+mean_time_span]
    
        # gib Nan als Summe aus, wenn ein bestimmter Prozentsatz
        # (cfg.anteil_datenverfuegbarkeit) an NaNs ueberschritten wurde
        if (np.isnan(points_span).sum() / mean_time_span) < max_nan_ratio:
            # bilde mittelwert (arithmetisch) ohne NaNs
            mean = np.nanmean(points_span)

        else:
            # wenn der Prozentsatz an NaNs ueberschritten wurde, gib Nan aus
            mean = np.nan

        # Datum fuer Mittelungszeitraum aus Liste ausschneiden
        end_date = dates[ cities * (ii) * mean_time_span ] + 7
        #end_date = dates[ ii * (mean_time_span * cities) ]
        ii += 1
        
        # Haenge den Mittelwert und das Datum des letzten Tages
        # des Mittelungszeitraums an die Liste an
        long_term_means.append( (end_date, mean) )
    
    return long_term_means


def get_player_mean(pointlist,
                    auswertungstage,
                    auswertungselemente,
                    elemente_archiv,
                    elemente_max_punkte,
                    eval_indexes,
                    Player,
                    npzfile):
    """
    Berechnet das Tagesmittel eines einzelnen Spielers fuer einen gewaehlten
    Turniertag oder fuer das ganze Wochenende. Gib ein leeres Array zurueck,
    wenn der Spieler nicht gefunden wurde oder die Punkteliste nur aus None-
    Werten besteht.
    
    :param pointlist: Punkteliste des Spielers
    :param auswertungstage: Liste der auszuwertenden Tage (z.B. ["Sa", "So"])
    :param auswertungselemente: Liste der auszuwertenden Elemente (z.B. ["A", "B"])
    :param elemente_archiv: Liste der Elemente im Archiv
    :param elemente_max_punkte: Liste der maximalen Punkte pro Element
    :param eval_indexes: Indizes der auszuwertenden Elemente in elemente_archiv
    :param Player: Name des Spielers
    :param npzfile: Numpy-Datei, die die Punktelisten der Spieler enthaelt
    
    :return: Tagesmittel des Spielers als Numpy-Array oder NaN, wenn der Spieler
    """
    # Wenn die Punkteliste nur aus None-Werten besteht, dann
    # gib NaN zurueck, da der Spieler nicht gefunden wurde
    # Dies sollte eigentlich nicht passieren, leere Tipps schon vorher
    # in db_read.py abfangen werden. Sicher ist sicherer.
    if all(v is None for v in pointlist):
        if verbose:
            print("Punkteliste nur aus None-Werten:", Player)
        if cfg.punkteersetzung_spieler:
            # Wenn cfg.punkteersetzung_spieler == True, dann
            # versuche den Ersatzspieler zu finden und dessen Punkteliste
            # zu verwenden
            ersatzspieler = find_replacement_players(cfg.punkteersetzung_spieler, Player)
            
            for e in ersatzspieler:
                try:
                    # Punkteliste des Ersatzspielers aus Datei einlesen
                    pointlist = npzfile[e]
                    # Wenn der Ersatzspieler gefunden wurde, dann
                    # verwende dessen Punkteliste, sofern sie nicht
                    # nur aus None-Werten besteht
                    if all(v is None for v in pointlist):
                        if verbose:
                            print("Punkteliste des Ersatzspielers nur aus None-Werten:", e)
                        continue
                    else:
                        # Wenn der Ersatzspieler gefunden wurde und seine
                        # Punkteliste nicht nur aus None-Werten besteht,
                        # dann verwende diese Punkteliste
                        return np.array(pointlist)
                except KeyError:
                    # Wenn der Ersatzspieler nicht gefunden wurde, dann gib NaN zurueck
                    if verbose:
                        print("Ersatzspieler nicht gefunden:", e)
                    continue
            
            # Wenn alle Ersatzspieler keine Werte hatten, gib NaN zurueck
            if verbose:
                print("Ersatzspieler haben keine Werte oder wurden nicht gefunden:", ersatzspieler)
            # Gib NaN zurueck, da der Spieler nicht gefunden wurde
            #TODO stattdessen den Mittelwert der Punkteliste aller Spieler
            return np.nan
    
    # Wenn die Punkteliste einzelne None-Werte enthaelt, dann
    # ersetze diese entweder durch Null oder wenn
    # punkteersetzung_elemente == True fuehre eine Ersetzung durch
    elif None in pointlist:
        #TODO Wenn wir ein nested Dictionary haben, dann
        # prufe, ob der Spieler einen Ersatzspieler hat,
        # und wenn ja, dann die Punkteliste des Ersatzspielers verwenden,
        # bis in die letzte Ebene des Dictionaries
        
        # wenn die Punkteliste None-Werte enthaelt, dann
        # ersetze diese durch die Werte des Ersatzspielers
        if cfg.punkteersetzung_elemente:
            # Wenn die Punkteliste elementweise ersetzt werden soll
            if cfg.punkteersetzung_elementweise:
                print(cfg.punkteersetzung_elemente_spieler)
                print("Noch nicht implementiert!")
                sys.exit()
                # TODO hier die Punkteliste des Ersatzspielers
                # bei einzelnen Elementen ersetzen
            # Im Fall das alle Elemente durch den gleichen Ersatzspieler ersetzt werden sollen
            else:
                ersatzspieler = find_replacement_players(cfg.punkteersetzung_spieler, Player)
                for e in ersatzspieler:
                    try:
                        # Punkteliste des Ersatzspielers aus Datei einlesen
                        pointlist_ersatz = npzfile[e]
                    except KeyError:
                        if verbose:
                            print("Ersatzspieler nicht gefunden:", e)
                        continue
                    # Wenn der Ersatzspieler gefunden wurde, dann
                    # ersetze die None-Werte in der Punkteliste des Spielers
                    pointlist_neu = []
                    for i, v in enumerate(pointlist):
                        if v is None:
                            pointlist_neu.append(pointlist_ersatz[i])
                        else:
                            pointlist_neu.append(v)
                    pointlist = np.array(pointlist_neu)
                    break
    
    # TODO Wenn immer noch None-Werte in der Punkteliste sind, nehme den
    # den Mittelwert der Punkteliste aller Spieler, die an diesem Tag
    # teilgenommen haben, und ersetze die None-Werte damit
    
    # wenn die Punkteliste (immer noch) None-Werte enthaelt
    # dann ersetze diese durch Null (0)
    pointlist = [0 if v is None else v for v in pointlist]
    pointlist = np.array(pointlist)
    #print("None-Werte durch Null ersetzt")
    #print("Punkteliste:", pointlist)

    #print("Maximale Punkte:", elemente_max_punkte)
    #print("Punkteliste:", pointlist)
    
    n_elements = len(elemente_archiv)

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
            
        # wenn nur bestimmte Elemente ausgewertet werden sollen
        else:
            #print("Nur bestimmte Elemente:", auswertungselemente)
            # Dann gib aus der Liste die genannten (Index) Elemente aus
            # (es werden die Indizes der zu evaluierenden Elemente genommen,
            # sowie die gleichen Indizes um n_elements nach oben verschoben, um auch
            # die Werte fuer Sonntag mit einzulesen)
            Points = itemgetter(*(eval_indexes+[i+n_elements for i in eval_indexes]))\
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
            # beinhalten, muss hier auf den Index immer n_elements aufgerechnet
            # werden um die Samstags-Werte zu ueberspringen)
            Points = itemgetter(*[i+n_elements for i in eval_indexes])(pointlist)

        else:
            raise ValueError("Nur Samstag (Sa) und Sonntag (So) sind valide "\
                             "Auswertungstage {}".format(auswertungstage))

        # Wenn wir nur einen Wert haben, hat Points kein Attribut
        # __len__ und wir muessen es in eine Liste umwandeln
        if not hasattr(Points, '__len__'):
            Points = [Points]
        
        # Punkte von den elementweisen maximalen Punktzahlen
        # elementweise abziehen
        PointsLost = [(elemente_max_punkte[i] - v)
                      for i, v in enumerate(Points)]


    # Durchschnittlich verlorene Punkte berechnen (ohne NaNs)
    
    #print( "MEAN:", np.round( np.nanmean(PointsLost),1 ) )

    return np.nanmean(PointsLost)


def find_replacement_players(UserValueLists, Player):
    """
    Findet Ersatzspieler fuer einen Spieler, der in der
    UserValueLists-Dictionary.
    """
    # Wenn der Spieler nicht gefunden wurde, dann versuche Ersatzspieler
    # in der Konfiguration zu finden
    try:
        ersatzspieler = cfg.punkteersetzung_spieler[Player]
    except KeyError:
        if verbose:
            print("Keine Ersatzspieler gefunden fuer:", Player)
        ersatzspieler = tuple()
    return ersatzspieler


if __name__ == "__main__":
    
    # Fehlerhafte Daten, die nicht ausgewertet werden konnten
    # (z.B. Spieler nicht gefunden, Datei nicht vorhanden etc.)
    faulty_dates = set()

    from argparse import ArgumentParser as ap

    # Parse command line arguments
    ps = ap()
    ps.add_argument("-v", "--verbose", help="increase output verbosity",
                        action="store_true")
    options = ("params", "cities", "days", "tournaments", "users")
    for option in options:
        ps.add_argument("-"+option[0], "--"+option, type=str, help="Set "+option)
    args = ps.parse_args()
     
    # Wenn verbose als Argument angegeben wurde, dann setze verbose auf True
    # um mehr Informationen auszugeben
    if args.verbose:
        verbose = True
    else: verbose = False
    
    # Konfiguration der Auswertungselemente, Staedte, Tage, Turniere und
    # Teilnehmer laden, explizit ohne exec (schneller und sicherer)
    params = args.params.split(',') if args.params else None
    cities = args.cities.split(',') if args.cities else None
    days   = args.days.split(',') if args.days else None
    tournaments = args.tournaments.split(',') if args.tournaments else None
    users  = args.users.split(',') if args.users else None
    
    # Wenn Start- und Endttermine angegeben wurden, dann konvertiere sie in Tagesindizes
    if tournaments:
        # Beispiel: "02.01.2023,09.01.2025"
        if len(tournaments) == 2:
            # Start- und Endtermin in Tagesindizes umwandeln
            cfg.starttermin = tournaments[0]
            cfg.endtermin   = tournaments[1]
        else:
            raise ValueError("Die Datumsangabe ist nicht korrekt. "\
                             "Bitte im Format 'dd.mm.yyyy,dd.mm.yyyy' eingeben.")
    
    # Anfangs- und Endtermin zum jeweiligen Tagesindex konvertieren
    begin, end = get_friday_range(date_2_index(cfg.starttermin)-1,
                                  date_2_index(cfg.endtermin))
    
    # Datum, an dem die Elemente gewechselt wurden in Tagesindex umwandeln
    tdate_neue_elemente = date_2_index(cfg.datum_neue_elemente)
    
    # Alte und neue Auswertungselemente setzen
    cfg.auswertungselemente_alt   = params if params else cfg.auswertungselemente_alt
    cfg.auswertungselemente_neu   = params if params else cfg.auswertungselemente_neu
    cfg.auswertungselemente       = cfg.auswertungselemente_neu[:] if begin >= tdate_neue_elemente else cfg.auswertungselemente_alt[:]
    
    # Die Städte können entweder als IDs, Kürzel oder Namen angegeben werden.
    if cities:
        for i, c in enumerate(cities):
            cities[i] = stadtname(c, cfg)
    
    # Konfiguration der Auswertungselemente, Staedte, Tage und Teilnehmer
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
        # Ausgabe des aktuellen Datums
        if verbose: print( index_2_date( i-1 ) )
        # wenn das Datum vor dem 06.01.2023 liegt, dann die alten
        # Auswertungselemente verwenden
        # Ausgabe der Tagesindizes
        if verbose: print(i)
        
        if i < tdate_neue_elemente:
            #TODO funktioniert nur, wenn alle Elemente gewaehlt wurden. Was tun bei spezifischen Elementen?
            cfg.auswertungselemente = cfg.auswertungselemente_alt[:]
            cfg.elemente_archiv     = cfg.elemente_archiv_alt[:]
            cfg.elemente_max_punkte = cfg.elemente_max_punkte_alt[:]
        else:
            cfg.auswertungselemente = cfg.auswertungselemente_neu[:]
            cfg.elemente_archiv     = cfg.elemente_archiv_neu[:]
            cfg.elemente_max_punkte = cfg.elemente_max_punkte_neu[:]
        
        # Indizes der zu verwendenden Auswertungselemente finden
        try:
            eval_el_indexes = [cfg.elemente_archiv.index(s)
                               for s in cfg.auswertungselemente]
            #eval_el_indexes = list(range(len(cfg.auswertungselemente)))
        except ValueError:
            print("Die Auswertungselemente sind nicht valide bzw. nicht "\
                  "oder nur teilweise in der Elementeliste vorhanden")
            sys.exit()

        # zu den Auswertungselementen passende Liste an maximalen Punkten fuer die
        # jeweiligen Elemente berechnen
        max_points_elements = [cfg.elemente_max_punkte[i]
                                for i in eval_el_indexes]

        FileName = "{}/{}_{}.npz".format(cfg.archive_dir_name, 1, i)
        
        # erstelle die Datei, wenn die sie noch nicht angelegt wurde
        if not os.path.isfile(FileName) or os.path.getsize(FileName) == 22:
            # Erstellen und einlesen
            #ajax_print.ArchiveParse(1, i)
            db_read.ArchiveParse(db, 1, i)

        #Dateigroesse prüfen (Ist Turniertag)?
        if os.path.getsize(FileName) == 22:
            if verbose: print("Kein Turniertag!")
            continue

        for city in cfg.auswertungsstaedte:
            
            # Stadt in ID konvertieren
            city_id = city_to_id(city, cfg)
            
            # zu ignorierende Termine der entsprechenden Stadt in IDs umwandeln
            # (wird fuer jede Stadt einmal neu berechnet)
            zu_ignorierende_tage = \
                [date_2_index(s) for s in cfg.zu_ignorierende_termine[city_id]]
            
            # Allgemeine zu ignorierende Termine hinzufuegen fuer alle Staedte
            zu_ignorierende_tage += cfg.zu_ignorierende_termine_allgemein
             
            FileName = "{}/{}_{}.npz".format(cfg.archive_dir_name, city_id, i)

            # erstelle die Datei, wenn die sie noch nicht angelegt wurde
            if not os.path.isfile(FileName):

                # Erstellen und einlesen
                #ajax_print.ArchiveParse(city_id, i)
                db_read.ArchiveParse(db, city_id, i)
                    #TODO Dateipfad als Eingabe
                    #TODO Datei hier schreiben

            # Datei einlesen
            npzfile = np.load(FileName, allow_pickle=True)
            
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
                                ersatz_name = cfg.punkteersetzung_spieler[Player]
                                player_point_list = npzfile[ersatz_name]
                            
                            except (KeyError, ValueError):
                                missing += 1
                                player_point_list = [np.nan] * 24
                                if verbose:
                                    print(f"'{Player}' nicht gefunden - kein Ersatz!")
                                
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
                        print(f"Fehler beim Einlesen von '{Player}' am Tag {i}: {e}")
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
                        UserValueLists[Player].append(
                            get_player_mean(player_point_list,
                                            cfg.auswertungstage,
                                            cfg.auswertungselemente,
                                            cfg.elemente_archiv,
                                            max_points_elements,
                                            eval_el_indexes,
                                            Player,
                                            npzfile) )
                        
                    # der Spieler wurde fuer den Tag nicht gefunden
                    except NameError:
                        # wenn der Spieler nicht gefunden wurde, dann finde
                        # Ersatzspieler aus Konfiguration
                        ersatzspieler = find_replacement_players(UserValueLists, Player)
                        
                        for e in ersatzspieler:
                            try:
                                # Punkte des Ersatzspielers aus Datei einlesen
                                player_point_list = npzfile[e]
                                
                                # Tagesmittel des Ersatzspielers an die jeweilige
                                # Liste anfuegen
                                UserValueLists[Player].append(
                                    get_player_mean(player_point_list,
                                                    cfg.auswertungstage,
                                                    cfg.auswertungselemente,
                                                    cfg.elemente_archiv,
                                                    max_points_elements,
                                                    eval_el_indexes,
                                                    Player,
                                                    npzfile) )
                                
                                break  # Ersatzspieler gefunden, Schleife verlassen
                            except KeyError:
                                #TODO wenn kein Ersatzspieler gefunden wurde,
                                # dann versuche den Mittelwert der anderen Spieler
                                # zu verwenden
                                # wenn der Ersatzspieler nicht gefunden wurde,
                                # dann gib NaN zurueck
                                UserValueLists[Player].append( np.nan )
                    
                    UserValueLists[Player].append( i-1 )
                    #FIXME entfernen oder verschieben weiter nach oben
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
                                            cfg.datenluecken_langfrist,
                                            cities)))
        
        short_term_data.append((player, short_term_mean(userpoints, userdates,
                                            cfg.mittelungszeitspannen,
                                            cfg.datenluecken_kurzfrist,
                                            cities)))

        #print( "short term" )
        #print( short_term_data[0] )
        # Spielerliste
        players = [p for p, _ in long_term_data]

        # Funktion, um Tabellen zu drucken
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
    userpoints = np.nanmean( \
        userpoints.reshape(-1, len(cfg.auswertungsstaedte)), axis=1)

    # Langfrist und Kurzfristberechnungen
    cities = len(cfg.auswertungsstaedte)

    long_term_data.append((player, long_term_mean(userpoints, userdates,
                                        cfg.auswertungsmittelungszeitraum,
                                        cfg.datenluecken_langfrist,
                                        cities)))
    
    short_term_data.append((player, short_term_mean(userpoints, userdates,
                                        cfg.mittelungszeitspannen,
                                        cfg.datenluecken_kurzfrist,
                                        cities)))
    
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

    print("Turniertage mit fehlenden Spielern / Tipps:")
    print( sorted(faulty_dates) )


    #------------------------------------------------------------------------#
    # Funktion, um Tabellen zu drucken
    # Spieler, die angezeigt werden sollen
    # Falls params gesetzt, nur diese Spieler anzeigen
    
    def drucke_tabelle_png_mit_summe_und_diff_text(
            data, title, langfrist=False,
            filename="tabelle.png",
            sum_indices=[1,4],
            selected_cities,
            selected_params,
            selected_day):
        """
        Druckt Tabelle in der Konsole UND speichert sie als PNG UND als TXT.
        Zeigt als Text unterhalb der Tabelle:
        - Summe nur der ausgewählten Spieler,
        - Differenz und Quotient der Summen der beiden Spieler.
        - Zusätzlich die gewählten Städte, Parameter und Tage
        """

        print("\n" + title)
        if not data:
            print("   (Keine Daten vorhanden)")
            return

        players = [p for p, _ in data]
        all_dates = sorted({d for _, lst in data for d, _ in lst})
        if not all_dates:
            print("   (Keine Datumswerte gefunden)")
            return

        datum_width = max(15, max(len(index_2_date(d).strftime("%d.%m.%Y")) for d in all_dates))
        points_width = 18

        # Konsolen-Kopf
        print(f"{'Datum':<{datum_width}}", end="")
        for player in players:
            print(f"{player:>{points_width}}", end=" ")
        print()
        print(" " * datum_width, end="")
        for _ in players:
            print("-" * points_width, end=" ")
        print()

        # Summen vorbereiten
        sums = {players[i]: 0 for i in sum_indices if i < len(players)}

        # Zeilen ausgeben
        for d in all_dates:
            date_obj = index_2_date(d)
            date_str = date_obj.strftime("%b %Y") if langfrist else date_obj.strftime("%d.%m.%Y")
            print(f"{date_str:<{datum_width}}", end="")
            for i, player in enumerate(players):
                lst = next(lst for p, lst in data if p == player)
                points = next((p for date, p in lst if date == d), float('nan'))
                if i in sum_indices and not np.isnan(points):
                    sums[player] += points
                print(f"{np.round(points,1) if not np.isnan(points) else 'NaN':>{points_width}}", end=" ")
            print()
        print("\n")

        # Differenz & Quotient
        if len(sum_indices) >= 2 and all(i < len(players) for i in sum_indices[:2]):
            p1_sum = sums[players[sum_indices[0]]]
            p2_sum = sums[players[sum_indices[1]]]
            diff_sum = p1_sum - p2_sum
            quot_sum = p1_sum / p2_sum if p2_sum != 0 else np.nan
        else:
            diff_sum = quot_sum = np.nan

        city_text = f"Städte: {', '.join(selected_cities)}" if selected_cities else ""
        param_text = f"Parameter: {', '.join(selected_params)}" if selected_params else ""
        day_text = f"Tag: {', '.join(selected_day)}" if selected_day else ""

        sum_text = " | ".join(filter(None, [
            "Summen: " + ", ".join(f"{player} = {np.round(sums[player],1)}" for player in sums),
            f"Differenz = {np.round(diff_sum,1) if not np.isnan(diff_sum) else 'NaN'}",
            f"Quotient = {np.round(quot_sum,2) if not np.isnan(quot_sum) else 'NaN'}",
            city_text,
            param_text,
            day_text
        ]))
        # -----------------------------
        # Dynamischer Dateiname ohne re, inkl. Tag
        def make_safe_name(parts):
            safe_parts = []
            for p in parts:
                p = p.replace(" ", "_")  # Leerzeichen ersetzen
                p = "".join(c for c in p if c.isalnum() or c == "_")  # nur alphanumerisch + Unterstrich
                safe_parts.append(p)
            return "_".join(safe_parts)

        name_parts = []
        if selected_cities:
            name_parts += selected_cities
        if selected_params:
            name_parts += selected_params
        if selected_day:
            name_parts += selected_day  # Tag hinzufügen

        base_name = filename.replace(".png","")
        if name_parts:
            dynamic_filename = f"{base_name}_{make_safe_name(name_parts)}.png"
        else:
            dynamic_filename = filename
        dynamic_txt_filename = dynamic_filename.replace(".png", ".txt")
                
        # -----------------------------
        # PNG-Ausgabe
        table_data = []
        for d in all_dates:
            date_obj = index_2_date(d)
            date_str = date_obj.strftime("%b %Y") if langfrist else date_obj.strftime("%d.%m.%Y")
            row = [date_str]
            for player in players:
                lst = next(lst for p, lst in data if p == player)
                points = next((p for date, p in lst if date == d), float('nan'))
                row.append(np.round(points,1) if not np.isnan(points) else "NaN")
            table_data.append(row)

        col_labels = ["Datum"] + players
        fig, ax = plt.subplots(figsize=(len(col_labels)*2, (len(all_dates)+1)*0.6))
        ax.axis('off')
        table = ax.table(cellText=table_data,
                         colLabels=col_labels,
                         cellLoc='center',
                         loc='center')
        table.auto_set_font_size(False)
        table.set_fontsize(10)
        table.auto_set_column_width(col=list(range(len(col_labels))))
        plt.figtext(0.1, 0.01, sum_text, fontsize=10, ha='left')
        plt.title(title)
        plt.savefig(filename, bbox_inches='tight')
        plt.close()

        # -----------------------------
        # TXT-Ausgabe
        txt_filename = filename.replace(".png", ".txt")
        with open(txt_filename, "w") as f:
            f.write(f"{'Datum':<{datum_width}}")
            for player in players:
                f.write(f"{player:>{points_width}} ")
            f.write("\n")
            f.write(" " * datum_width + "".join("-"*points_width + " " for _ in players) + "\n")
            for d in all_dates:
                date_obj = index_2_date(d)
                date_str = date_obj.strftime("%b %Y") if langfrist else date_obj.strftime("%d.%m.%Y")
                f.write(f"{date_str:<{datum_width}}")
                for player in players:
                    lst = next(lst for p, lst in data if p == player)
                    points = next((p for date, p in lst if date == d), float('nan'))
                    f.write(f"{np.round(points,1) if not np.isnan(points) else 'NaN':>{points_width}} ")
                f.write("\n")
            f.write("\n" + sum_text + "\n")


    # -----------------------------
    # Beispielaufrufe für Kurz- und Langfrist-Daten
   # drucke_tabelle_png_mit_summe_und_diff_text(
   #     short_term_data,
   #     "Rechte Grafik Tabelle",
   #     langfrist=False,
   #     filename="kurzfrist.png",
   #     sum_indices=[1,4],
   #     selected_cities=cfg.auswertungsstaedte,
   #     selected_params=cfg.auswertungselemente_neu,
   #     selected_day=cfg.auswertungstage
   # )

    drucke_tabelle_png_mit_summe_und_diff_text(
        long_term_data,
        "Linke Grafik Tabelle",
        langfrist=True,
        filename="langfrist.png",
        sum_indices=[1,4],
        selected_cities=cfg.auswertungsstaedte,
        selected_params=cfg.auswertungselemente_neu,
        selected_day=cfg.auswertungstage
    )
