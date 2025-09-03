#!/usr/bin/python3
# Programm zur Ausgabe der Wetterturnier-Spielerdaten aus der Datenbank
# von Juri Hubrig
# Version 1.0

import sys
import os
from datetime import date
from datetime import datetime as dt
import numpy as np
import mariadb
import config_loader as cfg

"""
import logging
logging.basicConfig() 
logging.getLogger().setLevel(logging.DEBUG)
requests_log = logging.getLogger("requests.packages.urllib3")
requests_log.setLevel(logging.DEBUG)
requests_log.propagate = True
"""

# zum Profilen:
# python -m cProfile db_read.py

from global_functions import date_2_index
# Datum der neuen Elemente in der Datenbank als Tag-Index
tdate_neue_elemente = date_2_index(cfg.datum_neue_elemente)


#----------------------------------------------------------------------------#
import time

# Setzen des Startzeitpuntes zur Messung der Laufzeit des Programms
startTime = time.time()
#----------------------------------------------------------------------------#

def sql_tuple(list_or_tuple):
    """
    Erstellt aus einer Liste oder einem Tupel ein SQL-Tupel
    """
    sql_tuple_str = ""
    for i in list_or_tuple:
        # Konvertiere die Elemente in Strings und fuege sie zum SQL-Tupel hinzu
        sql_tuple_str += str(i) + ", "
    
    # Entferne das letzte Komma und Leerzeichen
    sql_tuple_str = sql_tuple_str[:-2]
    
    # Füge Klammern hinzu, um das SQL-Tupel zu erstellen
    return "(" + sql_tuple_str + ")"


def sql_sort(list_or_tuple):
    """
    Erstellt aus einer Liste oder einem Tupel ein SQL-Sortier-Tupel
    """
    sql_sort_str = ""
    # Konvertiere die Elemente in Strings und fuege sie zum SQL-Sortier-Tupel hinzu
    for i in list_or_tuple:
        # Hier wird angenommen, dass die Elemente bereits in der richtigen Reihenfolge sind
        sql_sort_str += str(i) + ", "
    
    # Entferne das letzte Komma und Leerzeichen
    sql_sort_str = sql_sort_str[:-2]
    
    # Füge Klammern hinzu, um das SQL-Sortier-Tupel zu erstellen
    return sql_sort_str

def create_database_connection(user, password, host, database, port=3306):
    """
    Erstellt eine Verbindung zur Datenbank
    """
    # Verbindung zur Datenbank herstellen
    connection = mariadb.connect(user=user,
                                 password=password,
                                 host=host,
                                 database=database,
                                 port=port)
    # Verbindung zur Datenbank pruefen
    # Pruefen, ob die Verbindung erfolgreich war
    if connection is None:
        print("Fehler beim Verbinden zur Datenbank")
        sys.exit(1)

    # Gebe connection Objekt zurueck
    return connection


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


#----------------------------------------------------------------------------#

class db:
    def __init__(self, dictionary=False):
        """
        Initialisierung der Klasse, die die Datenbankverbindung herstellt
        """
        # Verbindung zur Datenbank herstellen
        self.con = create_database_connection(cfg.username, cfg.password, cfg.host, cfg.database)
        # Cursor-Objekt erstellen
        self.cur = self.con.cursor(dictionary=dictionary)
        
        # Pruefen, ob die Verbindung erfolgreich war
        if self.con is None:
            print("Fehler beim Verbinden zur Datenbank")
            sys.exit(1)
        
        # users aus der Konfiguration laden
        users = set(cfg.auswertungsteilnehmer) | set(cfg.punkteersetzung_spieler) | set(cfg.teilnehmerumbenennung.values())
        # Usernamen und User-IDs initialisieren
        self.user_ids  = self.get_user_ids(users)
         
        # Usernamen und User-IDs vertauschen https://stackoverflow.com/questions/483666/reverse-invert-a-dictionary-mapping
        self.user_names = dict((v, k) for k, v in self.user_ids.items())
        
        # Parameter IDs und Parameternamen initialisieren
        self.param_ids_new = self.get_param_ids(cfg.elemente_archiv_neu)
        # Parameternamen und Param-IDs vertauschen
        self.param_names_new = dict((v, k) for k, v in self.param_ids_new.items())
        
        # Alte Parameter IDs und Parameternamen initialisieren
        self.param_ids_old = self.get_param_ids(cfg.elemente_archiv_alt)
        # Parameternamen und Param-IDs vertauschen 
        self.param_names_old = dict((v, k) for k, v in self.param_ids_old.items())

    def get_user_ids(self, usernames, cfg=cfg):
        """
        Gibt die User-IDs zu den Usernamen zurueck
        """
        user_ids = {}
        # Pruefen, ob die Usernamen eine Liste oder ein Tupel sind
        for username in usernames:
            if username in cfg.teilnehmerumbenennung:
                username_new = cfg.teilnehmerumbenennung[username]
                # SQL-Abfrage, um die User-ID zu erhalten
                sql = f"SELECT id FROM `wp_users` WHERE user_login = '{username_new}' OR display_name = '{username_new}'"
            else:
                # SQL-Abfrage, um die User-ID zu erhalten
                sql = f"SELECT id FROM `wp_users` WHERE user_login = '{username}' OR display_name = '{username}'"
            # Ausfuehren der SQL-Abfrage
            self.cur.execute(sql)
            try:
                # Einlesen der User-ID aus der Datenbank
                user_ids[username] = self.cur.fetchone()[0]
            # Falls ein Fehler auftritt, wird der Username uebersprungen
            except:
                continue
        # Pruefen, ob die User-IDs erfolgreich aus der Datenbank gelesen wurden
        return user_ids


    def get_param_ids(self, param_names):
        """
        Gibt die Param-IDs zu den Parameternamen zurueck
        """
        # Pruefen, ob die Parameternamen eine Liste oder ein Tupel sind
        param_ids = {}
        # SQL-Abfrage, um die Param-IDs zu erhalten
        for param_name in param_names:
            # SQL-Abfrage, um die Param-ID zu erhalten
            sql = f"SELECT paramID FROM `wp_wetterturnier_param` WHERE paramName = '{param_name}' ORDER BY sort"
            # Ausfuehren der SQL-Abfrage
            self.cur.execute(sql)
            # Einlesen der Param-ID aus der Datenbank
            param_ids[param_name] = self.cur.fetchone()[0]
        # Pruefen, ob die Param-IDs erfolgreich aus der Datenbank gelesen wurden
        return param_ids


class ArchiveParse:

    def __init__(self, db, City, TDate):
        """
        Initialisierung der Klasse, die die Daten aus der Datenbank ausliest
        """
        # Wenn TDate neuer oder gleich dem Datum der neuen Elemente ist,
        if TDate >= tdate_neue_elemente:
            # dann wird die Stadt-ID in einen String umgewandelt
            param_ids = db.param_ids_new.values()
        else:
            # ansonsten werden die alten Parameter-IDs verwendet
            param_ids = db.param_ids_old.values()
        
        # Wenn die Anzahl der Parameter-IDs 12 ist, wird param_ids = "all" gesetzt
        #if len(param_ids) == 12:
        #    param_ids = "all"

        # Wenn City eine Zahl ist, wird sie in einen String umgewandelt
        self.UserTables = self.get_user_tables(db, db.user_ids.values(), TDate, City, param_ids)
         
        # Name der Outputdatei erstellen
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


    def get_user_tables(self, db, user_ids, Tdate, City, param_ids):
        """
        Gibt die User-Tabellen zurueck, die fuer die Auswertung benoetigt werden.
        """
        # Pruefen, ob City eine Zahl ist
        user_ids_tuple  = sql_tuple(user_ids)
        # Wenn City eine Zahl ist, wird sie in einen String umgewandelt
        UserTables      = {}
        
        # Pruefen, ob alle User-IDs abgefragt werden sollen
        #TODO param_ids == "all" entfernen, da es nicht mehr benoetigt wird
        # oder nur wenn cfg.punkteersetzung_params == False
        if param_ids == "all":
            print("param_ids == 'all'")
            # SQL-Abfrage fuer die User-Tabellen
            sql = f"SELECT userID, points_d1, points_d2 FROM `wp_wetterturnier_betstat` WHERE userID IN {user_ids_tuple} AND cityID = {City} AND tdate = {Tdate}"
            # Ausfuehren der SQL-Abfrage
            db.cur.execute(sql)
            # Auslesen der User-Tabellen aus der Datenbank
            try:
                # Schleife zum Einlesen der User-Tabellen
                for userID, point_d1, points_d2 in db.cur.fetchall():
                    # Pruefen, ob der User in der Tabelle ist
                    UserTables[db.user_names[userID]] = np.array([point_d1, point_d2])
            # Falls ein Fehler auftritt, wird eine leere Tabelle fuer den User erstellt
            except:
                UserTables[db.user_names[userID]] = np.array([])
        # Pruefen, ob nur bestimmte Param-IDs abgefragt werden sollen
        else:
            # NEU: Erzeuge die UNION ALL-Teile der Abfrage
            # Erstellt eine Kette wie "SELECT 1 AS userID UNION ALL SELECT 2"
            user_union = " UNION ALL ".join([f"SELECT {uid} AS userID" for uid in user_ids])
            # Erstellt eine Kette wie "SELECT 1 AS betdate UNION ALL SELECT 2"
            date_union = f"SELECT {Tdate+1} AS betdate UNION ALL SELECT {Tdate+2} AS betdate"
            # Erstellt eine Kette wie "SELECT 1 AS paramID UNION ALL SELECT 2"
            param_union = " UNION ALL ".join([f"SELECT {pid} AS paramID" for pid in param_ids])

            # Deine bestehende Funktion zur Sortierung der Parameter
            param_ids_sort = sql_sort(param_ids)
            
            # SQL-Abfrage fuer die User-Tabellen
            sql = f"""
            SELECT -- Waehle die UserID und die Punkte
                scaffold.userID,
                MAX(bets.points) AS points
            FROM -- von der Scaffold-Tabelle
                (
                    -- Dieser dreiteilige Scaffold erzeugt eine Kombination aller User, aller Daten und aller Parameter
                    SELECT -- Waehle die UserID, Betdate und ParamID
                        users.userID,
                        dates.betdate,
                        params.paramID
                    FROM -- von der Kombination aller User, Daten und Parameter
                        ({user_union}) AS users
                    CROSS JOIN -- Kreuzprodukt der User mit den Turnierterminen
                        ({date_union}) AS dates
                    CROSS JOIN -- Kreuzprodukt der Betdaten mit den Parametern
                        ({param_union}) AS params
                ) AS scaffold -- als Scaffold-Tabelle
            LEFT JOIN -- Verknuepfen der Scaffold-Tabelle mit der Tipp-Tabelle
                wp_wetterturnier_bets AS bets
            ON -- die Verknuepfung erfolgt ueber UserID, ParamID und Betdate (Turnierdatum)
                scaffold.userID = bets.userID
                AND scaffold.paramID = bets.paramID
                AND scaffold.betdate = bets.betdate -- Hier wird die Turnierdaten-Tabelle mit der Scaffold-Tabelle verknuepft
                AND bets.cityID = '{City}'
            GROUP BY -- Gruppierung nach UserID, Betdate und ParamID
                scaffold.userID,
                scaffold.betdate,
                scaffold.paramID
            ORDER BY
                -- Diese ORDER BY-Klausel sortiert Ergebnisse nach UserID, Betdate und Parametern
                scaffold.userID,
                scaffold.betdate,
                FIELD(scaffold.paramID, {param_ids_sort})
            """
            #print(sql)
            # Ausfuehren der SQL-Abfrage
            try:
                db.cur.execute(sql)
            # Falls ein Fehler auftritt, wird eine leere Tabelle fuer den User erstellt
            except Exception as e:
                # Fehlerausgabe der SQL-Abfrage und des Fehlers
                import traceback
                traceback.print_exc()
                print(sql)
                print(e)
                return {}
            
            # Auslesen der User-Tabellen aus der Datenbank
            db.cur.execute(sql)
            # Initialisierung der User-Tabellen
            for userID, points in db.cur.fetchall():
                # user_name aus der Datenbank holen
                user_name = db.user_names[userID]
                # Wenn der User noch nicht in der Tabelle ist, wird er hinzugefuegt
                if user_name not in UserTables:
                    # Erstelle eine leere Liste fuer den User
                    UserTables[user_name] = []
                # Punkte fuer den User hinzufuegen
                UserTables[user_name] += [points]
            
            # Erstelle eine Kopie von UserTables, da wir das Dictionary modifizieren werden
            # Fuer alle user_names in UserTables pruefen ob 24 Nones in der Liste sind,
            # falls ja wird der User aus der Liste geloescht
            for user_name in UserTables.copy():
                # Pruefen, ob die Liste nur Nones enthaelt
                if all(p is None for p in UserTables[user_name]):
                    # Wenn die Liste nur Nones enthaelt, wird der User aus der Liste geloescht
                    del UserTables[user_name]

        #print(UserTables)

        # Gebe die User-Tabellen zurueck
        return UserTables


#----------------------------------------------------------------------------#

if __name__ == "__main__":

    #------------------------------------------------------------------------#
    import time

    # Setzen des Startzeitpuntes zur Messung der Laufzeit des Programms
    startTime = time.time()
    #------------------------------------------------------------------------#
    
    # Herstellen der Datenbankverbindung
    db = db()
    
    # Pruefen, ob die Verbindung erfolgreich war
    Test = ArchiveParse(db,1,20154) 

    # Tests:    

    #Test = ArchiveParse("b","180316")
    #Test = ArchiveParse("i","180316")
    #Test = ArchiveParse("z","181026")
    #Test = ArchiveParse("b", "17998")
    #Test = ArchiveParse(1, 17998)
    
    #------------------------------------------------------------------------#
    print ("Benoetigte Laufzeit fuer db_read: {0} Sekunden"\
           .format(time.time() - startTime))
    #------------------------------------------------------------------------#

    # Laden der Ausgabedatei
    npzfile = np.load(Test.OutFilePath + ".npz", allow_pickle=True)
    #npzfile_bak = np.load(Test.OutFilePath + ".npz.bak")
    #npzfile = np.load("BER_17739.npz")
    # Ausgabe der User-Tabellen
    print('npzfile.files: {}'.format(npzfile.files))
    #print('npzfile["Schneegewitter"]: {}'.format(npzfile["ErrorTest"]))
    #print(Test.DayIndex, Test.Date)

    #for s in npzfile.files:
    #    #print('npzfile[{}]: {}'.format(s, npzfile[s]))
    #    print(npzfile[s] == npzfile_bak[s])
    
