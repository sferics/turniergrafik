import numpy as np
import db_read as dbr
import config_loader as cfg
from datetime import datetime as dt, timedelta as td, timezone as tz
from datetime import date
from argparse import ArgumentParser as ap
from global_functions import index_2_date, date_2_index, city_to_id, get_list_of_weekends

# Datenbankverbindung aufbauen
db = dbr.db()

# Start- und Enddatum festlegen
datum_von = cfg.datum_neue_elemente
datum_bis = cfg.endtermin

def get_obs_data(staedte, tage, elemente):
    """Lädt Beobachtungsdaten aus der Datenbank für die angegebenen Städte, Daten und Elemente."""
    obs_data = {}
    table_name = "wp_wetterturnier_obs"
    
    cursor = db.con.cursor(dictionary=True)

    for stadt in staedte:
        stationen = cfg.stationen[stadt]
        query = f"""SELECT 
                    station, 
                    betdate, 
                    p.paramName, 
                    value
                FROM 
                    {table_name} w
                INNER JOIN 
                    wp_wetterturnier_param p ON w.paramID = p.paramID
                WHERE 
                    station IN ({','.join(map(str, stationen))})
                    AND betdate IN ({','.join(map(str, tage))})
                    AND w.paramID IN ({','.join(map(str, elemente))})
                GROUP BY 
                    betdate, p.paramName, station
                ORDER BY 
                    betdate ASC, p.sort ASC, station ASC
                """
        cursor.execute(query)
        results = cursor.fetchall()  # List of dicts

        # Create nested dict: betdate → paramName → [values]
        nested = {}
        for row in results:
            betdate = row['betdate']
            param   = row['paramName']
            station = row['station']
            value = row['value']
            if value is not None:
                value /= 10  # Convert to correct unit
                nested.setdefault(betdate, {}).setdefault(param, []).append(value)
        
        obs_data[cfg.id_zu_kuerzel[stadt]] = nested # Store nested dict for the city
    
    return obs_data
    
def get_forecast_data(staedte, tage, elemente, users):
    """Lädt Forecast-Daten aus der Datenbank für die angegebenen Städte, Daten, Elemente und Benutzer."""
    forecast_data = {}
    table_name = "wp_wetterturnier_bets"
    
    cursor = db.con.cursor(dictionary=True)

    for stadt in staedte:
        query = f"""SELECT
                    betdate,
                    p.paramName,
                    u.user_login,
                    value
                FROM
                    {table_name} w
                INNER JOIN
                    wp_users u ON w.userID = u.ID
                INNER JOIN
                    wp_wetterturnier_param p ON w.paramID = p.paramID
                WHERE
                    w.cityID = {stadt}
                    AND betdate IN ({','.join(map(str, tage))})
                    AND w.paramID IN ({','.join(map(str, elemente))})
                    AND w.userID IN ({','.join(map(str, users))})
                GROUP BY
                    betdate, user_login, p.paramName
                ORDER BY
                    betdate ASC, user_login ASC, p.sort ASC
                """
        cursor.execute(query)
        results = cursor.fetchall()  # List of dicts

        # Create nested dict: betdate → userlogin → paramName → value
        nested = {}
        for row in results:
            betdate = row['betdate']
            user    = row['user_login']
            param   = row['paramName']
            value   = row['value']
            if value is not None:
                value /= 10
                nested.setdefault(betdate, {}).setdefault(user, {})[param] = value
        
        forecast_data[cfg.id_zu_kuerzel[stadt]] = nested # Store nested dict for the city
    
    return forecast_data


if __name__ == "__main__":
    print("Starte Verteilung der Beobachtungsdaten in die Forecast-Tabellen")
    print("---------------------------------------------------------------")
    
    # Kommandozeilenargumente parsen
    ps = ap()
    ps.add_argument("-v", "--verbose", action="store_true", help="Ausführliche Ausgabe")
    ps.add_argument("--von", type=str, help="Startdatum im Format JJJJ-MM-TT", default=datum_von)
    ps.add_argument("--bis", type=str, help="Enddatum im Format JJJJ-MM-TT", default=datum_bis)
    ps.add_argument("-p", "--params", type=str, help="Liste der Parameternamen, getrennt durch Komma", default=",".join(cfg.elemente_archiv_neu))
    ps.add_argument("-c", "--cities", type=str, help="Liste der Stadtnamen, getrennt durch Komma", default=",".join(cfg.stadtnamen))
    ps.add_argument("-u", "--users", type=str, help="Liste der Usernamen, getrennt durch Komma", default=",".join(cfg.auswertungsteilnehmer))
    ps = ps.parse_args()
    
    # Argumente extrahieren
    verbose = ps.verbose
    datum_von = ps.von
    datum_bis = ps.bis
    elemente_namen = ps.params.split(",")
    # Nur gültige Parameternamen behalten
    elemente_namen = [el for el in elemente_namen if el in cfg.elemente_archiv_neu]
    # Parameternamen in IDs umwandeln
    elemente = db.get_param_ids(elemente_namen).values()
    # Stadtnamen in IDs umwandeln
    staedte = [city_to_id(city, cfg) for city in ps.cities.split(",")]
    
    # Ausführliche Ausgabe, wenn gewünscht
    if verbose:
        print(f"Verarbeite Beobachtungsdaten von {datum_von} bis {datum_bis} für die Parameter: {elemente} und Städte: {staedte}")
    
    # Erhalte Liste der Wochenendtage im angegebenen Zeitraum
    tdate_von = date_2_index(datum_von)
    tdate_bis = date_2_index(datum_bis)
    wochenendtage = get_list_of_weekends(tdate_von, tdate_bis)
    
    # Beobachtungsdaten laden
    obs_data = get_obs_data(staedte, wochenendtage, elemente)
    
    # Benutzer-IDs für die Forecast-Daten
    user_logins = ps.users.split(",")
    users_dict = db.get_user_ids(user_logins)
    # UserID und Login tauschen für einfacheren Zugriff
    users_dict_swapped = {v: k for k, v in users_dict.items()}
    users = users_dict.values()
    
    # Forecast-Daten laden
    forecast_data = get_forecast_data(staedte, wochenendtage, elemente, users)

    # Daten in ein Dictionary kombinieren
    combined_data = {}
    for city in obs_data:
        combined_data[city] = {}
        for betdate in obs_data[city]:
            combined_data[city].setdefault(betdate, {})
            combined_data[city][betdate]['o'] = obs_data[city][betdate]
            combined_data[city][betdate]['f'] = {}
            for user in users:
                user_login = users_dict_swapped[user]
                if user_login in cfg.teilnehmerumbenennung:
                    user_login_actual = cfg.teilnehmerumbenennung[user_login]
                else:
                    user_login_actual = user_login
                try:
                    if betdate in forecast_data[city] and user_login_actual in forecast_data[city][betdate]:
                        combined_data[city][betdate]['f'][user_login] = forecast_data[city][betdate][user_login_actual]
                    else:
                        combined_data[city][betdate]['f'][user_login] = {el: None for el in elemente_namen}
                except KeyError:
                    combined_data[city][betdate]['f'][user_login] = {el: None for el in elemente_namen}

    #print(combined_data["BER"][20330])
