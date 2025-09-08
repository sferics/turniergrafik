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
import os
import re
import yaml
import numpy as np
import matplotlib.pyplot as plt
from collections import defaultdict
from scipy.stats import binned_statistic_2d
from decimal import Decimal, localcontext, ROUND_HALF_EVEN


db = dbr.db()

# ------------------- YAML laden -------------------#
def _load_yaml_data(filepaths=['tabelle_obs_for.yml']):
    config_data = {}
    for filepath in filepaths:
        with open(filepath, 'r', encoding='utf-8') as f: data = yaml.safe_load(f)
        if data:
            config_data.update(data)
        return config_data

# ------------------ gewünschte Genauigkeit -------------#

DEC_QUANT = Decimal('0.001') 

# ------------------- Hilfsfunktionen -------------------#
def to_value(raw_value):
    """Konvertiert raw_value (z.B. int oder str) zu einem gerundeten float.
       Intern wird Decimal für korrektes Runden benutzt; Rückgabe ist float.
    """
    if raw_value is None:
        return None
    with localcontext() as ctx:
        ctx.prec = 12
        ctx.rounding = ROUND_HALF_EVEN
        d = Decimal(str(raw_value)) / Decimal('10')
        d = d.quantize(DEC_QUANT, rounding=ROUND_HALF_EVEN)
    return float(d)

def get_interval(value, ranges):
    """Gibt (Index, Range-Text) zurück, in dem der Wert liegt, oder (None, None)."""
    for i, r in enumerate(ranges):
        a = r[0]
        b = r[1]
        if i == len(ranges)-1:  # Einzelwert
            if a <= value <= b:
                return i, f"[{a}, {b}]"
        else:
            if a <= value < b:
                return i, f"[{a}, {b}]"
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
            raw_value = row['value']
            if raw_value is not None:
                v = to_value(raw_value)   
                nested.setdefault(betdate, {}).setdefault(param, []).append(v)
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
            raw_value = row['value']
            if raw_value is not None:
                v = to_value(raw_value)
                # Wichtig: nach User verschachteln
                nested.setdefault(betdate, {}).setdefault(user, {})[param] = v
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
    tdate_von = date_2_index(datum_von)
    tdate_bis = date_2_index(datum_bis)
    wochenendtage = get_list_of_weekends(tdate_von, tdate_bis)

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
            print(f"Skipping {param} due to missing ranges.")
            continue

    counts = defaultdict(int)
    obs_missing = []
    for_missing = []
    users_set = set()

    for city in combined_data:
            for betdate, data in combined_data[city].items():
                obs_vals_list = data["o"].get(param, [])
                if not obs_vals_list:
                    continue
                obs_max = pl.Series(obs_vals_list).max()
                obs_idx, _ = get_interval(obs_max, obs_ranges_def)
                if obs_idx is None:
                    obs_missing.append(obs_max)
                    continue
                obs_range_key = tuple(obs_ranges_def[obs_idx])
                for user, fvals in data["f"].items():
                    users_set.add(user)
                    fcast_val = fvals.get(param)
                    #print(np.min(fcast_val))
                    if fcast_val is None:
                        continue
                    f_idx, _ = get_interval(fcast_val, for_ranges_def)
                    if f_idx is None:
                        for_missing.append(fcast_val)
                        continue
                    for_range_key = tuple(for_ranges_def[f_idx])

                    counts[(param, obs_range_key, for_range_key)] += 1
    print(f"{param} Obs outside ranges:", obs_missing)
    print(f"{param} For outside ranges:", for_missing)

            

# ------------------- DataFrame bauen -------------------
rows = []
si = param_to_si_map.get(param, "")
for obs_r in obs_ranges_def:
    obs_label = get_max_label(obs_r)
    for for_r in for_ranges_def:
        for_label = get_max_label(for_r)
        rows.append({
              "Obs": f"{obs_label} {si}" if si else obs_label,
               "For": f"{for_label} {si}" if si else for_label,
               "Count": counts.get((param, tuple(obs_r), tuple(for_r)), 0)
        })
df_dist = pl.DataFrame(rows)
if df_dist["Obs"].dtype == pl.List:
    df_dist = df_dist.with_columns(
        pl.col("Obs").arr.get(0).alias("Obs")
    )
    
df_pivot = df_dist.pivot(
            values="Count",
            index="Obs",
            on="For",
            aggregate_function="sum"
        )
df_pivot = df_pivot.with_columns(
            pl.col("Obs").str.extract(r"([-+]?\d*\.?\d+)").cast(pl.Float64).alias("_obs_lb")
        ).sort("_obs_lb").drop("_obs_lb")
for_cols = [c for c in df_pivot.columns if c != "Obs"]

def extract_numeric_column(col_names):
    """Extrahiert erste Zahl aus jedem Spaltennamen und liefert sortierte Liste"""
    def parse_number(s):
        m = re.search(r"[-+]?\d*\.?\d+", s)
        return float(m.group()) if m else float("inf")
    return sorted(col_names, key=parse_number)

sorted_cols = extract_numeric_column(for_cols)

df_pivot = df_pivot.select(["Obs"] + sorted_cols)


outdir = "distribution_outputs"
os.makedirs(outdir, exist_ok=True)

cities_str = "_".join(re.sub(r'[\\/:"*?<>|\s]+', '_', c) for c in cities_to_use)
users_str = "_".join(sorted(users_set)) if users_set else "all_users"

outfile = os.path.join(outdir, f"distribution_{cities_str}_{param}_{users_str}.xlsx")
df_pivot.write_excel(outfile)
print(f"Distribution matrix saved: {outfile}")


# plotting
obs_vals = []
fcast_vals = []

for city in cities_to_use:
    for betdate, data in combined_data[city].items():
        obs_list = data["o"].get(param, [])
        if not obs_list:
            continue
        obs_mean = pl.Series(obs_list).mean()
        for user, fvals in data["f"].items():
            fcast_val = fvals.get(param)
            if fcast_val is None:
                continue
            obs_vals.append(obs_mean)
            fcast_vals.append(fcast_val)

    if len(obs_vals) < 2 or len(fcast_vals) < 2:
        print(f"Not enough data for parameter {param} to plot.")
    else:
        obs_vals_float = np.array(obs_vals)
        fcast_vals_float = np.array(fcast_vals)
    
        # ----------------- Heatmap (2D-Histogramm) -----------------
        # Anzahl Bins anpassen je nach Datengröße
        bins = 50
        heatmap, xedges, yedges = np.histogram2d(
            obs_vals_float, fcast_vals_float, bins=bins
        )
    
        # jedem Punkt die Häufigkeit im passenden Bin zuordnen
        x_idx = np.searchsorted(xedges, obs_vals_float) - 1
        y_idx = np.searchsorted(yedges, fcast_vals_float) - 1
        # in Bounds bleiben
        x_idx = np.clip(x_idx, 0, heatmap.shape[0]-1)
        y_idx = np.clip(y_idx, 0, heatmap.shape[1]-1)
        z = heatmap[x_idx, y_idx]
    
        # ----------------- Plot -----------------
        fig, ax = plt.subplots(figsize=(16, 10))
    scatter = ax.scatter(
        obs_vals_float, fcast_vals_float,
        c=z, s=20, cmap='jet', alpha=0.7
    )
    
    min_val = (obs_vals_float.min(), fcast_vals_float.min())
    max_val = (obs_vals_float.max(), fcast_vals_float.max())
    ax.plot([min_val[0], max_val[0]], [min_val[1], max_val[1]], 'k--', label="Observation = Forecast")
    
    # Achsenbeschriftungen inkl. Einheit
    x_label = f"Observation ({param})"
    y_label = f"Forecast ({param})"
    si_element = param_to_si_map.get(param, None)
    if si_element:
        x_label += f" [{si_element}]"
        y_label += f" [{si_element}]"
    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)
    ax.set_title(f"Scatterplot with absolute frequency for cities: {', '.join(cities_to_use)}")
    
    ax.grid(True)
    ax.legend()
    
    # Colorbar zeigt absolute Häufigkeit
    cbar = fig.colorbar(scatter, ax=ax, location='right')
    cbar.set_label('Absolute frequency (counts per bin)')
    
    plt.tight_layout(rect=[0, 0, 0.9, 1])
    
    plot_filename = os.path.join(outdir, f"scatter_absfreq_{cities_str}_{param}_{users_str}.png")
    plt.savefig(plot_filename, dpi=300)
    print(f"Scatterplot with absolute frequency saved for parameter {param}: {plot_filename}")
    plt.close(fig)



















