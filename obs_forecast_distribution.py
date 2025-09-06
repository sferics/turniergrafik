import numpy as np
import polars as pl
from collections import defaultdict
from datetime import date
from argparse import ArgumentParser as ap
from global_functions import date_2_index, city_to_id, get_list_of_weekends
import db_read as dbr
import config_loader as cfg
import yaml
from itertools import product
from scipy.stats import gaussian_kde
import os
import re
import yaml
import numpy as np
import polars as pl
import matplotlib.pyplot as plt
from collections import defaultdict
from scipy.stats import gaussian_kde


db = dbr.db()

# ------------------- YAML laden -------------------
def _load_yaml_data(filepaths=['tabelle_obs_for.yml']):
    config_data = {}
    for filepath in filepaths:
        with open(filepath, 'r', encoding='utf-8') as f: data = yaml.safe_load(f)
        if data:
            config_data.update(data)
            return config_data

# ------------------- Hilfsfunktionen -------------------
def get_interval(value, ranges):
    """Gibt (Index, Range-Text) zurück, in dem der Wert liegt, oder (None, None)."""
    for i, r in enumerate(ranges):
        if len(r) == 1:  # Einzelwert
            if value == r[0]:
                return i, str(r[0])
        elif r[0] <= value <= r[1]:  # Intervall
            return i, f"[{r[0]}, {r[1]}]"
    return None, None

intervals_cfg = _load_yaml_data(filepaths=['tabelle_obs_for.yml'])['Intervalle']
    
def get_obs_data(staedte, tage, elemente):
    obs_data = {}
    table_name = "wp_wetterturnier_obs"
    cursor = db.con.cursor(dictionary=True)
    for stadt in staedte:
        stationen = cfg.stationen[stadt]
        query = f"""
            SELECT station, betdate, p.paramName, value
            FROM {table_name} w
            INNER JOIN wp_wetterturnier_param p ON w.paramID = p.paramID
            WHERE station IN ({','.join(map(str, stationen))})
              AND betdate IN ({','.join(map(str, tage))})
              AND w.paramID IN ({','.join(map(str, elemente))})
            GROUP BY betdate, p.paramName, station
            ORDER BY betdate ASC, p.sort ASC, station ASC
        """
        cursor.execute(query)
        results = cursor.fetchall()
        nested = {}
        for row in results:
            betdate = row['betdate']
            param = row['paramName']
            value = row['value']
            if value is not None:
                value /= 10
                nested.setdefault(betdate, {}).setdefault(param, []).append(value)
        obs_data[cfg.id_zu_kuerzel[stadt]] = nested
    return obs_data   

                
def get_forecast_data(staedte, tage, elemente, users):
    forecast_data = {}
    table_name = "wp_wetterturnier_bets"
    cursor = db.con.cursor(dictionary=True)
    for stadt in staedte:
        query = f"""
            SELECT betdate, p.paramName, u.user_login, value
            FROM {table_name} w
            INNER JOIN wp_users u ON w.userID = u.ID
            INNER JOIN wp_wetterturnier_param p ON w.paramID = p.paramID
            WHERE w.cityID = {stadt}
              AND betdate IN ({','.join(map(str, tage))})
              AND w.paramID IN ({','.join(map(str, elemente))})
              AND w.userID IN ({','.join(map(str, users))})
            GROUP BY betdate, user_login, p.paramName
            ORDER BY betdate ASC, user_login ASC, p.sort ASC
        """
        cursor.execute(query)
        results = cursor.fetchall()
        nested = {}
        for row in results:
            betdate = row['betdate']
            user = row['user_login']
            param = row['paramName']
            value = row['value']
            if value is not None:
                value /= 10
                nested.setdefault(betdate, {}).setdefault(user, {})[param] = value
        forecast_data[cfg.id_zu_kuerzel[stadt]] = nested
    return forecast_data   


def get_max_label(r):
    return str(r[1]) if len(r) > 1 else str(r[0])

# ------------------- Hauptprogramm -------------------
if __name__ == "__main__":
    # DB-Verbindung
    db = dbr.db()
    # Kommandozeilenargumente
    ps = ap()
    ps.add_argument("--von", type=str, default=cfg.datum_neue_elemente)
    ps.add_argument("--bis", type=str, default=cfg.endtermin)
    ps.add_argument("-p", "--params", type=str, default=",".join(cfg.elemente_archiv_neu))
    ps.add_argument("-c", "--cities", type=str, default=",".join(cfg.stadtnamen))
    ps.add_argument("-u", "--users", type=str, default=",".join(cfg.auswertungsteilnehmer))
    ps.add_argument("-v", "--verbose", action="store_true")
    ps = ps.parse_args()
    datum_von = ps.von
    datum_bis = ps.bis

    elemente_namen = [el for el in ps.params.split(",") if el in cfg.elemente_archiv_neu]
    elemente = db.get_param_ids(elemente_namen).values()
    staedte = [city_to_id(city, cfg) for city in ps.cities.split(",")]
    user_logins = ps.users.split(",")
    users_dict = db.get_user_ids(user_logins)
    users_dict_swapped = {v: k for k, v in users_dict.items()}
    users = users_dict.values()

    # Load data
    obs_data = get_obs_data(staedte, wochenendtage, elemente)
    forecast_data = get_forecast_data(staedte, wochenendtage, elemente, users)




# ------------------- Daten kombinieren -------------------
combined_data = {}
for city in obs_data:
    combined_data[city] = {}
    for betdate in obs_data[city]:
        combined_data[city].setdefault(betdate, {})
        combined_data[city][betdate]['o'] = obs_data[city][betdate]
        combined_data[city][betdate]['f'] = {}
        for user in users:
            user_login = users_dict_swapped[user]
            user_login_actual = cfg.teilnehmerumbenennung.get(user_login, user_login)
            try:
                combined_data[city][betdate]['f'][user_login] = forecast_data[city][betdate].get( user_login_actual, {el: None for el in elemente_namen} )
            except KeyError: combined_data[city][betdate]['f'][user_login] = {el: None for el in elemente_namen}

config_cfg = _load_yaml_data(filepaths=['cfg.yml'])
elemente_namen_cfg = config_cfg["elemente"]["elemente_archiv_neu"]
elemente_einheiten_cfg = config_cfg["elemente"]["elemente_einheiten_neu"]
param_to_si_map = {name: unit for name, unit in zip(elemente_namen_cfg, elemente_einheiten_cfg)}
cities_to_use = list(combined_data.keys())
            

for param in elemente_namen:
    obs_ranges_def = intervals_cfg["obs"].get(param, [])
    for_ranges_def = intervals_cfg["for"].get(param, [])

    if not obs_ranges_def or not for_ranges_def:
            print(f"Skipping {param_to_plot} due to missing ranges.")
            continue

    counts = defaultdict(int)
    obs_missing = []
    for_missing = []
    users_set = set()

    for city in combined_data:
            for betdate, data in combined_data[city].items():
                obs_vals_list = data["o"].get(param_to_plot, [])
                if not obs_vals_list:
                    continue
                obs_max = np.max(obs_vals_list)
                print(np.max(obs_max))
                obs_idx, _ = get_interval(obs_max, obs_ranges_def)
                if obs_idx is None:
                    obs_missing.append(obs_max)
                    continue
                obs_range_key = tuple(obs_ranges_def[obs_idx])
                for user, fvals in data["f"].items():
                    users_set.add(user)
                    fcast_val = fvals.get(param_to_plot)
                    #print(np.min(fcast_val))
                    if fcast_val is None:
                        continue
                    f_idx, _ = get_interval(fcast_val, for_ranges_def)
                    if f_idx is None:
                        for_missing.append(fcast_val)
                        continue
                    for_range_key = tuple(for_ranges_def[f_idx])

                    counts[(param_to_plot, obs_range_key, for_range_key)] += 1
    print(f"{param_to_plot} Obs outside ranges:", obs_missing)
    print(f"{param_to_plot} For outside ranges:", for_missing)

            

# ------------------- DataFrame bauen -------------------



# DataFrame aus rows
df = pl.DataFrame(rows)

# Pivot-Tabelle erstellen
df_pivot = df.pivot(
    values="Count",
    index=["Datum", "Obs_Range"],
    on="For_Range",  # neue Polars-Version: 'on' statt 'columns'
    aggregate_function="sum"
)

# Hilfsfunktion: Untergrenze eines Intervalls extrahieren
def lower_bound(r):
    if r.startswith("["):
        return float(r[1:-1].split(",")[0])
    else:
        return float(r)

# Obs-Ranges in Untergrenzen umwandeln für Sortierung
obs_lbs = [lower_bound(r) for r in df_pivot["Obs_Range"].to_list()]
df_pivot = df_pivot.with_columns(pl.Series("_obs_lb", obs_lbs))

# Nach Datum und Obs-Untergrenze sortieren, Hilfsspalte löschen
df_pivot = df_pivot.sort(["Datum", "_obs_lb"]).drop("_obs_lb")

# Spalten (For_Ranges) nach Untergrenze sortieren
sorted_columns = sorted(df_pivot.columns[2:], key=lower_bound)
df_pivot = df_pivot.select(["Datum", "Obs_Range"] + sorted_columns)

# Excel speichern
df_pivot.write_excel("df_polars_unsorted.xlsx")
print("Pivot-Tabelle erfolgreich als Excel gespeichert: df_polars_unsorted.xlsx")


# ------------------- Nur Vorhersagen -------------------
df_for = df.pivot(
    values="Count",
    index=["Datum"],
    on="For_Range",
    aggregate_function="sum"
)

# Spalten nach Untergrenze sortieren
sorted_for_cols = sorted(df_for.columns[1:], key=lower_bound)
df_for = df_for.select(["Datum"] + sorted_for_cols)

# Excel speichern
df_for.write_excel("df_polars_forecast.xlsx")
print("Vorhersagen erfolgreich als Excel gespeichert: df_polars_forecast.xlsx")

# ------------------- Nur Beobachtungen -------------------
df_obs = df.pivot(
    values="Count",
    index=["Datum"],
    on="Obs_Range",
    aggregate_function="sum"
)

# Spalten nach Untergrenze sortieren
sorted_obs_cols = sorted(df_obs.columns[1:], key=lower_bound)
df_obs = df_obs.select(["Datum"] + sorted_obs_cols)

# Excel speichern
df_obs.write_excel("df_polars_observation.xlsx")
print("Beobachtungen erfolgreich als Excel gespeichert: df_polars_observation.xlsx")


# ------------------- Scatter-Daten -------------------
obs_vals = []
fcast_vals = []

for city in combined_data:
    for param in elemente_namen:
        for betdate, data in combined_data[city].items():
            obs_list = data["o"].get(param, [])
            if not obs_list:
                continue
            obs_mean = np.mean(obs_list)

            for user, fvals in data["f"].items():
                fcast_val = fvals.get(param)
                if fcast_val is None:
                    continue
                obs_vals.append(obs_mean)
                fcast_vals.append(fcast_val)

# ------------------- Punktdichte berechnen -------------------
xy = np.vstack([obs_vals, fcast_vals])
z = gaussian_kde(xy)(xy)

# ------------------- Plot -------------------
plt.figure(figsize=(8,6))
scatter = plt.scatter(obs_vals, fcast_vals, c=z, s=20, cmap='viridis', alpha=0.7)

# 1:1 Linie
min_val = min(min(obs_vals), min(fcast_vals))
max_val = max(max(obs_vals), max(fcast_vals))
plt.plot([min_val, max_val], [min_val, max_val], 'k--', label="Beobachtung = Vorhersage")

plt.xlabel("Beobachtung (Observation_Mean)")
plt.ylabel("Vorhersage (Forecast_Mean)")
plt.title(f"Verteilungsfunktion: Beobachtungen vs Vorhersagen von {cfg.auswertungsstaedte}")
plt.legend()
plt.grid(True)
plt.colorbar(scatter, label='Dichte der Punkte')
plt.tight_layout()
plt.savefig("distribution_obs_vs_forecast_density.png", dpi=300)
plt.show()













