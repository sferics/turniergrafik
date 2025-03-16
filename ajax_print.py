#!/usr/bin/python3
# Programm zur Ausgabe von spielerweisen Turnierstatistiken per AJAX-Request
# von Felix Korthals
# Version 1.0

import re
import sys
import os
from requests import Session
from datetime import date
from datetime import datetime as dt

import numpy as np

import threading

import config as cfg

"""
import logging
logging.basicConfig() 
logging.getLogger().setLevel(logging.DEBUG)
requests_log = logging.getLogger("requests.packages.urllib3")
requests_log.setLevel(logging.DEBUG)
requests_log.propagate = True
"""

# zum Profilen:
# python -m cProfile ajax_print.py


#----------------------------------------------------------------------------#
import time

# Setzen des Startzeitpuntes zur Messung der Laufzeit des Programms
startTime = time.time()
#----------------------------------------------------------------------------#


def GetDate(HtmlSrc):

    """
    gibt Datum der Archivseite aus (anhand von Wetterturnier-Archiv-HTML)
    """

    DateLine = re.compile(\
       "               Aktuelles Turnier: <b>.*?, (?P<Date>\d+.\d+.\d+)<\/b>")
    matches = DateLine.findall(HtmlSrc)
    #print(matches)

    return matches[0]

    # Aktuelles Turnier: <b>Freitag, 14.09.2018</b>
    #VonText = "               Aktuelles Turnier: <b>"
    #iVon = self.WebPage.text.find(VonText) + len(VonText)
    #iBis = self.WebPage.text[iVon:].find("</b>")+ iVon
    #return self.WebPage.text[(iBis-10):iBis]


def CalcDay(InDate):

    """
    Tag-Index berechnen zum Websiteaufruf
    (der wievielte Tag, seit dem 02.01.1970)
    """

    # Date-Input-Format:
    #      DDMMYY
    # z.B: 180316

    #unsicher bezueglich fehlerhafter Eingabe (versch. lange Stellen)?
    #dd, mm, yy = str(InDate)[4:], str(InDate)[2:4], str(InDate)[:2]
    # datetime-objekt wird in date-obj. umgewandelt
    DayX = dt.strptime("20"+InDate, "%Y%m%d").date()

    # Tag 1:     Freitag, 02.01.1970
    # Tag 8:     Freitag, 09.01.1970
    # Tag 17837: Freitag, 02.11.2018
    Day1 = date(1970, 1, 1)
    #DayX = date(int("20"+yy), int(mm),  int(dd))
    DayDelta = DayX - Day1
    #print(DayDelta.days)
    return str(DayDelta.days)


def FindUserIDs(HtmlSrc):

    """
    nimmt einen string, analog zu einer der HTML-Messwerttabellen
    aus den Wetterturnierarchiven, die hauptsaechlich aus den
    Messwerttabellen bestehen, und gibt alle UserIDs darin zurueck
    """

    UserIDs = []

    # Beispielzeile: "    <tr class='day-1 player' userid='262'>"
    UserLine = re.compile(
               "    <tr class='day-\d \w+' userid='(?P<Date>\d+)'>")
    Matches = UserLine.findall(HtmlSrc)

    for Match in Matches:

        # pruefen, ob die gefundene ID valide ist und noch nicht
        # eingetragen wurde
        if Match not in ["", " ", "\n", "0"]:

            UserIDs.append(Match)

    # Duplikate entfernen und sortieren
    UserIDs = list(set(UserIDs))
    
    #print(UserIDs)
    
    return UserIDs


def GetHeaderFooterStats(DaySplt):

    """
    Parsen von Kopf- und Fusszeile der jeweiligen Spielerwertungen
    Ausgabe: [Name, Punkte(Samstag), Punkte(Sonntag), ges.Punkte, Rang]
    """

    Stats = []

    for S in ["Name: ",
              "Punkte&nbsp;Samstag: ",
              "Punkte&nbsp;Sonntag: ",
              "Gesamtpunkte: ",
              "Rang: "]:

        # Ort im string finden, wo gesuchter string steht (Index)
        StartP = DaySplt.find(S) + len(S)
        String = DaySplt[StartP:]

        # Finden wo interessanter Teil endet
        EndP = String.find("<")
        String = String[:EndP]
        String = String.replace("\\","")
        Stats.append(String)

    # Liste: [Name, Punkte(Samstag), Punkte(Sonntag), ges.Punkte, Rang]
    return Stats


def GetName(DaySplt):

    """
    Parsen von Kopf- und Fusszeile der jeweiligen Spielerwertungen
    Ausgabe: Name
    """

    NameMarker = "Name: "

    # Ort im string finden, wo gesuchter string steht (Index)
    StartP = DaySplt.find(NameMarker) + len(NameMarker)

    # Teilstring vor dem Namen wegschneiden
    Name = DaySplt[StartP:]
    
    # Finden wo interessanter Teil endet
    EndP = Name.find("<")

    # Teilstring nach dem Namen wegschneiden
    Name = Name[:EndP]

    Name = Name.replace("\\","")

    # Name ohne (Gruppe) dahinter
    Name = Name.split(" ")[0]

    return Name


def ReadHTMLTablePoints(ResponseHTML):

    """
    Gibt Punkte und Spieler aus Tabellen fuer ein Dictionary aus
    Ausgabe: Spieler, [np.array von Punkten (N,Sd,)]
    """

    # Tabelle (HTML-string) zwischen Samstag und Sonntag teilen
    # [0: Header/Spieler-Statistiken, 1: Samstag, 2: Sonntag]
    # (Bsp.: n<b>Samstag<\/b>)
    Header, Saturday, Sunday = ResponseHTML.split("\\n<b>")

    Name = GetName(Header).replace("\\", "\\\\")

    # Teilnehmer mit altem Namen umbenennen (siehe config)
    if Name in cfg.teilnehmerumbenennung:
        Name = cfg.teilnehmerumbenennung[Name]

    # Array von Punkten fuer die unterschiedlichen Parameter (N, Sd, d,..)
    Points = []

    for Day in Saturday, Sunday:

        # Tages-Tabelle in Zeilen spalten
        DayLines = Day.split("<\/tr>\\n  <tr>\\n")

        for i, Line in enumerate(DayLines):

            # Zeilen in Elemente spalten (Bsp.: <td>0.0<\/td>\n\n)
            Line = Line.split("<td>")

            # Zeichen nach den Elementen (ab <) loeschen (Bsp.: 0.0<\/td>\n\n)
            Line = [El[:El.find("<")] for El in Line]

            #DEBUG# [print(i) for i in Line]

            # pruefen, ob sich die Elementeliste geaendert hat
            # (siehe cfg.elemente_archiv)
            if Line[1] == (cfg.elemente_archiv*2)[i]:

                # Wert auslesen
                Value = float( str(Line[-1]).replace(",","." ) )

                # testen, ob der Wert valide ist
                if Value <= (cfg.elemente_max_punkte*2)[i]:

                    # Am Schluss jeder Zeile stehen die Punkte, der Rest
                    # wird verworfen (alle Vorhersagen, Werte, etc.)
                    Points.append(Value)

                else:
                    raise ValueError("mindestens ein Element liegt "\
                                     "ausserhalb der moeglichen Grenzen und "\
                                     "ist fehlerhaft (Value:{},Max:{})"\
                                     .format(Value,
                                             (cfg.elemente_max_punkte*2)[i]))
                                    #TODO genau spezifizieren, wekcher Tag, 
                                    #TODO Spieler etc. den Fehler aufweist
            else:
                raise ValueError("Die Elementeliste oder ihre Reihenfolge "\
                                 "hat sich geaendert")

    return Name, np.array(Points)


#----------------------------------------------------------------------------#

class ArchiveParse:

    def __init__(self, City, TDate):

        self.Session = Session()
        #self.Session.head('https://wetterturnier.de/archiv/')
        self.Session.head('https://wetterturnier.de/wertungen/wochenendwertungen/')
	#self.Session.head('http://160.45.76.35/archive/')

        self.CityShort = cfg.id_zu_kuerzel[City]

        #FIXME Archivdateien sollen nur den Freitagsindex als Datumsangabe
        # nutzen, programmintern werden keine datetime oder date-objekte
        # genutzt
        """self.DayIndex = CalcDay(asTDate)"""

        self.WebAdress = 'https://wetterturnier.de/wertungen/wochenendwertungen/'\
                                      '?wetterturnier_city={}'\
                                      '&tdate={}'.format(self.CityShort,
                                                         TDate)
        
        self.ArchiveAdress = 'https://wetterturnier.de/archiv/?wetterturnier_city={}'\
                                      '&tdate={}'.format(self.CityShort,
                                                         TDate)

        #DEBUG# 
        #print(self.ArchiveAdress)

        self.WebPage = self.Session.get(self.WebAdress, stream=False)
        self.ArchivePage = self.Session.get(self.ArchiveAdress, stream=False)

        # Seitenquelltext auslesen
        self.HtmlSrc = self.WebPage.text
        self.HtmlSrcArchive = self.ArchivePage.text

        #print(self.HtmlSrc)

        """self.Date = GetDate(self.HtmlSrc)"""

        # UserIDs aus der HTML suchen #FIXME jedes mal? Cache? Vergleichen?
        self.UserIDs = FindUserIDs(self.HtmlSrcArchive)

        # Spieler-spezifische Tabellen (UserID ist key) #TODO jedes Mal lesen?
        self.UserTables = {}

        # Threading wird genutzt, um mehrere Anfragen gleichzeitig zu stellen
        # um die Geschwindigkeit zu erhoehen
        threads = [threading.Thread(target=self.get_data,
                                    args=(City, TDate, user_id,)) \
                                    for user_id in self.UserIDs]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()

        for UserID in self.UserIDs:

            # Daten beim Server anfragen
            ResponseHTML = self.GetResponseIndivTable(City, TDate, UserID)

            # Name und Punkte aus Antwort-Tabelle auslesen
            # ACHTUNG: Wenn die Daten unvollstaendig oder falsch sind,
            #          werden die gesamten Daten zu dieser Person fuer
            #          diesen Tag verworfen! (aus Vergleichbarkeitsgruenden)
            try:
                Name, Points = ReadHTMLTablePoints(ResponseHTML)

            except ValueError as e:
                print(e)
                continue

            # Eintragen in ein Dictionary {Spieler:[Punkte],..}
            self.UserTables[Name] = Points

        #DEBUG#
        #print(self.UserTables)

        # Name der Outputdatei
        self.OutFileName = "{}_{}".format(City, TDate)

        #FIXME testen und schreiben in ap.py auslagern!
        # Pruefen, ob das Ausgabeverzeichnis existiert
        if not os.path.exists(cfg.archive_dir_name): #TODO Name als Argument?

            # Erstelle den Ausgabeordner (wenn noch nicht existent)
            os.makedirs(cfg.archive_dir_name)

        # kompletter Ausgabepfad
        self.OutFilePath = cfg.archive_dir_name + "/" + self.OutFileName

        # Schreiben der Datei in den Unterordner 'archivdateien'
        np.savez(self.OutFilePath, **self.UserTables)


    def GetResponseIndivTable(self, cityID, tDate, userID):

        """
        Gibt eine HTML-Tabelle als Antwort auf eine Staedte- und Spieler-
        spezifische Nachfrage an den Wetterturnier-Server.
        Aus der Tabelle lassen sich die individuellen Punkte, Vorhersagen etc.
        ablesen.
        """

        #DEBUG# print(CityID, asTDate, userID, self.Date)

        response = self.Session.post(stream=False, #FIXME Test ob stream True
                                                   #FIXME oder false

            ##################################################################
            # Zum Herausfinden der Adressen und Daten:
            # -> Im Browser (Firefox) auf 'Element untersuchen'
            # -> in den Reiter 'Netzwerkanalyse'
            # -> auf die Schaltflaeche klicken, die simuliert werden soll
            # -> auf den erscheinenden Befehl (z.B. POST) klicken
            # -> Adressen und Daten aus den Reitern 'Kopfzeilen' und
            #    'Parameter' auslesen
            ##################################################################

            # 'Angefragte Adresse' der POST Methode (in 'Kopfzeilen')
            # ACHTUNG http != https -> pruefen!
            url='https://wetterturnier.de/wp-admin/admin-ajax.php',

            # Anfrage-Parameter (in 'Parameter')
            data={
                'action': 'wttable_show_details_ajax',
                'cache':  'false',
                'cityID': cityID,
                'tdate':  tDate,
                'userID': userID,
            },

            # Anfragekopfzeilen in 'Kopfzeilen' (nicht alle werden benoetigt)
            headers={
                'Host': 'wetterturnier.de',
                'Accept': 'application/json, text/javascript, */*; q=0.01',
                'Referer': 'https://wetterturnier.de/wertungen/wochenendwertungen/?tdate={}?cityID={}'\
                           .format(tDate, cityID)
            }
        )

        # pruefen ob die Anfrage erfolgreich war
        # (200: erfolgreich, andernfalls(z.B. 400): fehlgeschlagen)
        if response.status_code != 200:

            raise ValueError('<Response [{}]>\nFEHLER: Adressen und '\
                             'Parameter pruefen!'\
                             .format(response.status_code))

            sys.exit()

        #DEBUG
        #print(response.text)
        #print(userID)
        #DEBUG

        return response.text

    def get_data(self, City, TDate, UserID):

        # Daten beim Server anfragen
        ResponseHTML = self.GetResponseIndivTable(City, TDate, UserID)

        # Name und Punkte aus Antwort-Tabelle auslesen
        # ACHTUNG: Wenn die Daten unvollstaendig oder falsch sind,
        #          werden die gesamten Daten zu dieser Person fuer
        #          diesen Tag verworfen! (aus Vergleichbarkeitsgruenden)
        try:
            Name, Points = ReadHTMLTablePoints(ResponseHTML)

            # Eintragen in ein Dictionary {Spieler:[Punkte],..}
            self.UserTables[Name] = Points

        except ValueError as e:
            print(e)



#----------------------------------------------------------------------------#

if __name__ == "__main__":

    #------------------------------------------------------------------------#
    import time

    # Setzen des Startzeitpuntes zur Messung der Laufzeit des Programms
    startTime = time.time()
    #------------------------------------------------------------------------#

    # Tests:    

    #Test = ArchiveParse("b","180316")
    #Test = ArchiveParse("i","180316")
    #Test = ArchiveParse("z","181026")
    #Test = ArchiveParse("b", "17998")
    Test = ArchiveParse(1, 17998)

    #------------------------------------------------------------------------#
    print ("Benoetigte Laufzeit fuer ajax_print: {0} Sekunden"\
           .format(time.time() - startTime))
    #------------------------------------------------------------------------#

    npzfile = np.load(Test.OutFilePath + ".npz")
    #npzfile_bak = np.load(Test.OutFilePath + ".npz.bak")
    #npzfile = np.load("BER_17739.npz")
    print('npzfile.files: {}'.format(npzfile.files))
    print('npzfile["Schneegewitter"]: {}'.format(npzfile["Schneegewitter"]))
    print('npzfile["Schneegewitter"]: {}'.format(npzfile["Schneegewitter"][0]))
    #print('npzfile["Schneegewitter"]: {}'.format(npzfile["ErrorTest"]))
    #print(Test.DayIndex, Test.Date)

    #for s in npzfile.files:
    #    #print('npzfile[{}]: {}'.format(s, npzfile[s]))
    #    print(npzfile[s] == npzfile_bak[s])

