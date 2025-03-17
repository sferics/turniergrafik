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
# python -m cProfile db_read.py


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
        sql_tuple_str += str(i) + ", "

    sql_tuple_str = sql_tuple_str[:-2]
    
    return "(" + sql_tuple_str + ")"


def sql_sort(list_or_tuple):
    """
    Erstellt aus einer Liste oder einem Tupel ein SQL-Sortier-Tupel
    """
    sql_sort_str = ""
    for i in list_or_tuple:
        sql_sort_str += str(i) + ", "

    sql_sort_str = sql_sort_str[:-2]
    
    return sql_sort_str

def create_database_connection(user, password, host, database, port=3306):
    """
    Erstellt eine Verbindung zur Datenbank
    """

    connection = mariadb.connect(user=user,
                                 password=password,
                                 host=host,
                                 database=database,
                                 port=port)

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
    def __init__(self):
        self.con = create_database_connection(cfg.username, cfg.password, cfg.host, cfg.database)
        # Cursor-Objekt erstellen
        self.cur = self.con.cursor()
        
        users = set(cfg.auswertungsteilnehmer) | set(cfg.punkteersetzung_menschen_ersatzspieler) | set(cfg.teilnehmerumbenennung.values())

        self.user_ids  = self.get_user_ids(users)
         
        # Usernamen und User-IDs vertauschen https://stackoverflow.com/questions/483666/reverse-invert-a-dictionary-mapping
        self.user_names = dict((v, k) for k, v in self.user_ids.items())

        self.param_ids = self.get_param_ids(cfg.auswertungselemente)
        # Parameternamen und Param-IDs vertauschen
        self.param_names = dict((v, k) for k, v in self.param_ids.items())
        
        self.param_ids_old = self.get_param_ids(cfg.auswertungselemente_alt)
        # Parameternamen und Param-IDs vertauschen 
        self.param_names_old = dict((v, k) for k, v in self.param_ids_old.items())

    def get_user_ids(self, usernames):
        """
        Gibt die User-IDs zu den Usernamen zurueck
        """
        user_ids = {}
        for username in usernames:
            sql = f"SELECT id FROM `wp_users` WHERE user_login = '{username}' OR display_name = '{username}'"
            self.cur.execute(sql)
            try:
                user_ids[username] = self.cur.fetchone()[0]
            except:
                continue
        return user_ids


    def get_param_ids(self, param_names):
        """
        Gibt die Param-IDs zu den Parameternamen zurueck
        """
        param_ids = {}
        for param_name in param_names:
            sql = f"SELECT paramID FROM `wp_wetterturnier_param` WHERE paramName = '{param_name}' ORDER BY sort"
            self.cur.execute(sql)
            param_ids[param_name] = self.cur.fetchone()[0]
        return param_ids


class ArchiveParse:

    def __init__(self, db, City, TDate):
        """
        Initialisierung der Klasse, die die Daten aus der Datenbank ausliest
        """
        if TDate >= 19363:
            param_ids = db.param_ids.values()
        else:
            param_ids = db.param_ids_old.values()
        
        self.UserTables = self.get_user_tables(db, db.user_ids.values(), TDate, City, param_ids)
         
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


    def get_user_tables(self, db, user_ids, Tdate, City, param_ids):
        """
        Gibt die User-Tabellen zurueck, die fuer die Auswertung benoetigt werden.
        """
        user_ids_tuple  = sql_tuple(user_ids)
        UserTables      = {}
        
        if param_ids == "all":
            sql = f"SELECT userID, points_d1, points_d2 FROM `wp_wetterturnier_betstat` WHERE userID IN {user_ids_tuple} AND cityID = {City} AND tdate = {Tdate}"
            db.cur.execute(sql)
            try:
                for userID, point_d1, points_d2 in db.cur.fetchall():
                    UserTables[db.user_names[userID]] = np.array([point_d1, point_d2])
            except:
                UserTables[db.user_names[userID]] = np.array([])
        else:
            param_ids_tuple = sql_tuple(param_ids)
            param_ids_sort  = sql_sort(param_ids)
            sql = f"SELECT userID, points FROM `wp_wetterturnier_bets` WHERE userID IN {user_ids_tuple} AND cityID = '{City}' AND betdate BETWEEN '{Tdate+1}' AND '{Tdate+2}' AND paramID IN {param_ids_tuple} GROUP BY `userID`,betdate, FIELD(paramID, {param_ids_sort}) ORDER BY userID"
            try:
                db.cur.execute(sql)
            except Exception as e:
                import traceback
                traceback.print_exc()
                print(sql)
                print(e)
                return {}
            
            db.cur.execute(sql)
            for userID, points in db.cur.fetchall():
                user_name = db.user_names[userID]
                if user_name not in UserTables:
                    UserTables[user_name] = []
                UserTables[user_name] += [points]
        
        return UserTables


#----------------------------------------------------------------------------#

if __name__ == "__main__":

    #------------------------------------------------------------------------#
    import time

    # Setzen des Startzeitpuntes zur Messung der Laufzeit des Programms
    startTime = time.time()
    #------------------------------------------------------------------------#
    
    db = db()

    Test = ArchiveParse(db,1,20154) 

    # Tests:    

    #Test = ArchiveParse("b","180316")
    #Test = ArchiveParse("i","180316")
    #Test = ArchiveParse("z","181026")
    #Test = ArchiveParse("b", "17998")
    #Test = ArchiveParse(1, 17998)
    
    #------------------------------------------------------------------------#
    #print ("Benoetigte Laufzeit fuer ajax_print: {0} Sekunden"\
    #       .format(time.time() - startTime))
    #------------------------------------------------------------------------#

    npzfile = np.load(Test.OutFilePath + ".npz")
    #npzfile_bak = np.load(Test.OutFilePath + ".npz.bak")
    #npzfile = np.load("BER_17739.npz")
    print('npzfile.files: {}'.format(npzfile.files))
    #print('npzfile["Schneegewitter"]: {}'.format(npzfile["ErrorTest"]))
    #print(Test.DayIndex, Test.Date)

    #for s in npzfile.files:
    #    #print('npzfile[{}]: {}'.format(s, npzfile[s]))
    #    print(npzfile[s] == npzfile_bak[s])

