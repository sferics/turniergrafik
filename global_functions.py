# Globale Funktionen, die in mehreren Modulen verwendet werden

from datetime import datetime as dt, date, timedelta

def date_2_index(input_date):
    """
    Tag-Index (der wievielte Tag, seit dem 02.01.1970) aus einem gegebenen
    Datum berechnen    
    Beispiele:
    Tag 1:     Freitag, 02.01.1970
    Tag 8:     Freitag, 09.01.1970
    Tag 17837: Freitag, 02.11.2018

    :param input_date: Datum als String im Format "dd.mm.yyyy" oder

    :return: Tagesindex (der wievielte Tag, seit dem 02.01.1970)
    """

    if type(input_date) is str:
        # String in ein Datum umwandeln
        day_x = dt.strptime(input_date, "%d.%m.%Y").date()
    elif type(input_date) is date:
        # wenn ein Datum uebergeben wurde, dann direkt verwenden
        day_x = copy(input_date)

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

    :param input_index: Tagesindex (der wievielte Tag, seit dem 02.01.1970)

    :return: Datum des Tagesindex
    """
    # pruefen, ob der Tagesindex gueltig ist
    if input_index > 0:

        # zur Berechnung des Datums muss nur der Tagesindex bzw. die Anzahl an
        # Tagen seit dem 02.01.1970 auf eben dieses Datum addiert werden
        return date(1970, 1, 2) + timedelta(days = input_index)

    else:
        raise ValueError("Der Tagesindex ist nicht korrekt.")


def index_2_year(date_index):
    """
    Gibt das Jahr des Tagesindex zurueck

    :param date_index: Tagesindex (der wievielte Tag, seit dem 02.01.1970)

    :return: Jahr des Tagesindex
    """
    if date_index > 0:
        return index_2_date(date_index).year
    else:
        raise ValueError("Der Tagesindex ist nicht korrekt.")


def get_friday_range(begin, end):
    """
    Bestimmt die Grenzen der zu bearbeitenden Freitags-Indizes
    (der wievielte Tag, seit dem 02.01.1970 etc. ..)
    
    :param begin: Start-Index (der wievielte Tag, seit dem 02.01.1970)
    :param end: End-Index (der wievielte Tag, seit dem 02.01.1970)

    :return: Tupel mit den Start- und End-Indizes der Freitage
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


def stadtname(stadt, cfg):
    """
    Liefert den Namen der Stadt, die in der Konfiguration
    hinterlegt ist, zurück.

    :param stadt: entweder eine Stadt-ID (int) oder ein 3-stelliges Kürzel

    :return: Name der Stadt (String)
    """
    # Wenn die Stadt eine ID ist, wird der Name direkt aus cfg.stadtnamen geholt
    if type(stadt) == int:
        return cfg.stadtnamen[stadt]
    # Wenn die Stadt ein 3-stelliges Kürzel ist, wird die ID aus kuerzel_zu_id geholt
    elif len(stadt) == 3:
        return cfg.stadtnamen[kuerzel_zu_id[stadt] - 1 ]
    # Wenn die Stadt ein String ist, wird die ID aus stadt_zu_id geholt
    return cfg.stadtnamen[ cfg.stadt_zu_id[stadt] - 1 ]


def city_to_id(city, cfg):
    """
    Konvertiert eine Stadt in eine ID, die in der Datenbank verwendet wird.
    Wenn die Stadt eine ID ist, wird sie direkt zurueckgegeben.
    Wenn die Stadt ein Kuerzel ist, wird es in eine ID umgewandelt.
    Wenn die Stadt ein Name ist, wird der Name in eine ID umgewandelt.

    param city: Stadtname, Kuerzel oder ID
    return: ID der Stadt
    :rtype: int
    """
    # Konvertierung von Kürzeln in IDs
    # (z.B. "BER" -> 1, "HAM" -> 2, ...)
    kuerzel = cfg.id_zu_kuerzel.values()
    ids     = cfg.id_zu_kuerzel.keys()
    kuerzel_zu_id = {}
    for k, i in zip(kuerzel, ids):
        kuerzel_zu_id[k] = i

    try: return int(city)
    except ValueError:
        if len(city) == 3:
            return kuerzel_zu_id[city]
        else: return cfg.stadt_zu_id[city]
