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
import matplotlib.pyplot as plt
from scipy.stats import binned_statistic_2d
from decimal import Decimal, localcontext, ROUND_HALF_EVEN
import openpyxl
from openpyxl.styles import PatternFill


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
    if raw_value is None:
        return None
    with localcontext() as ctx:
        ctx.prec = 12
        ctx.rounding = ROUND_HALF_EVEN
        d = Decimal(str(raw_value)) / Decimal('10')
        d = d.quantize(DEC_QUANT, rounding=ROUND_HALF_EVEN)
    return float(d)

def get_interval(value, ranges):
    for i, r in enumerate(ranges):
        a, b = r
        if a <= value <= b:
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
            betdate, param, raw_value = row['betdate'], row['paramName'], row['value']
            if raw_value is not None:
                nested.setdefault(betdate, {}).setdefault(param, []).append(to_value(raw_value))
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
            betdate, user, param, raw_value = row['betdate'], row['user_login'], row['paramName'], row['value']
            if raw_value is not None:
                nested.setdefault(betdate, {}).setdefault(user, {})[param] = to_value(raw_value)
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

    config_cfg = _load_yaml_data(filepaths=['cfg.yml'])
    param_to_si_map = {name: unit for name, unit in zip(
        config_cfg["elemente"]["elemente_archiv_neu"],
        config_cfg["elemente"]["elemente_einheiten_neu"]
    )}




# ------------------- Daten kombinieren -------------------
combined_data = {}
for city in obs_data:
    combined_data[city] = {}
    for betdate in obs_data[city]:
            combined_data[city][betdate] = {
                'o': obs_data[city][betdate],
                'f': {}
            }
        for user in users:
            user_login = users_dict_swapped[user]
            user_login_actual = cfg.teilnehmerumbenennung.get(user_login, user_login)
            try:
                combined_data[city][betdate]['f'][user_login] = forecast_data[city][betdate].get( user_login_actual, {el: None for el in elemente_namen} )
            except KeyError: combined_data[city][betdate]['f'][user_login] = {el: None for el in elemente_namen}

# ---------------------------- Verarbeitung und Export -----------------------------------#
outdir = "distribution_outputs"
os.makedirs(outdir, exist_ok=True)
cities_to_use = list(combined_data.keys())
            

for param in elemente_namen:
    obs_ranges_def = intervals_cfg.get(param, [])
    for_ranges_def = intervals_cfg.get(param, [])

    if not obs_ranges_def or not for_ranges_def:
            print(f"Skipping {param} due to missing ranges.")
            continue
    si = param_to_si_map.get(param, "")
    for city, city_data in combined_data.items():
        users_set = {u for betdate, data in city_data.items() for u in data.get('f', {}).keys()}
        for user in users_set:
            counts = defaultdict(int)
            values_by_bin = defaultdict(list)
            obs_missing = []
            for_missing = []
    
            for betdate, data in combined_data[city].items():
                obs_vals_list = data["o"].get(param, [])
                valid_obs = [v for v in obs_vals_list if v is not None]
                if not obs_vals_list:
                    continue
                if not valid_obs:
                    continue
                obs_max = max(valid_obs)
                obs_idx, _ = get_interval(obs_max, obs_ranges_def)
                if obs_idx is None:
                    obs_missing.append((city, betdate, obs_max))
                    continue
                obs_range_key = tuple(obs_ranges_def[obs_idx])
                user_fvals = data['f'].get(user)
                if user_fvals is None:
                    for_missing.append((city, betdate, user, "no_forecast"))
                    continue
                fcast_val = user_fvals[param]
                f_idx, _ = get_interval(fcast_val, for_ranges_def)
                if f_idx is None:
                    for_missing.append(fcast_val)
                    continue
                for_range_key = tuple(for_ranges_def[f_idx])
    
                counts[(param, obs_range_key, for_range_key)] += 1
                values_by_bin[(obs_range_key, for_range_key)].append((obs_max, fcast_val))
                        
    print(f"{param} Obs outside ranges:", obs_missing)
    print(f"{param} For outside ranges:", for_missing)

            

        # ------------------- DataFrame bauen -------------------
        rows = [
            {"Obs": str(obs_r[1]),
             "For": str(for_r[1]),
             "Count": counts.get((tuple(obs_r), tuple(for_r)), 0)}
             for obs_r, for_r in product(obs_ranges_def, for_ranges_def)
            ]

        df_dist = pl.DataFrame(rows)

        df_pivot = df_dist.pivot(
            values="Count",
            index="Obs",
            on="For",
            aggregate_function="sum"
        )
        # --- Numerisch korrekt sortieren nach Obs ---
        df_pivot = df_pivot.with_columns(
            pl.col("Obs").str.extract(r"([-+]?\d*\.?\d+)").cast(pl.Float64).alias("_obs_sort")
        ).sort("_obs_sort").drop("_obs_sort")

        # Spalten numerisch sortieren (ohne Obs)
        for_cols = [c for c in df_pivot.columns if c != "Obs"]
        for_cols_sorted = sorted(for_cols, key=lambda x: float(re.findall(r"[-+]?\d*\.?\d+", x)[0]))
        df_pivot = df_pivot.select(["Obs"] + for_cols_sorted)
            
        # ------------------- Row_Sum berechnen -------------------
        df_pivot = df_pivot.with_columns(
            pl.sum_horizontal(for_cols_sorted).alias("Row_Sum")
        )

        # ------------------- Column_Sum (vertikal) -------------------
        col_sums = {c: df_pivot[c].sum() for c in for_cols_sorted}  # vertikale Summen
        col_sums["Obs"] = "Col_Sum"
        col_sums["Row_Sum"] = df_pivot["Row_Sum"].sum()  # Kreuzsumme unten rechts

        col_sums_df = pl.DataFrame([col_sums], schema=df_pivot.columns)
        df_pivot = df_pivot.vstack(col_sums_df)
            
            # --- Export ---
        outdir = os.path.join("distribution_outputs", "BER_neu")
        os.makedirs(outdir, exist_ok=True)
        city_str = re.sub(r'[\\/:"*?<>|\s]+', '_', city)
        user_str = re.sub(r'[\\/:"*?<>|\s]+', '_', user)
            
        outfile_xlsx = os.path.join(outdir, f"distribution_{city_str}_{param}_{user_str}.xlsx")
        # Erste Spalte umbenennen zu "Obs \ For"
        df_excel = df_pivot.rename({"Obs": "Obs \\ For"})
        df_excel.write_excel(outfile_xlsx, worksheet="Distribution")
        print(f"Saved Excel for {city}, user {user}: {outfile_xlsx}")

        # --- Farben mit openpyxl setzen ---
        wb = openpyxl.load_workbook(outfile_xlsx)
        ws = wb.active

        blue_fill = PatternFill(start_color="ADD8E6", end_color="ADD8E6", fill_type="solid")  # Hauptdiagonale
        orchid_fill = PatternFill(start_color="DA70D6", end_color="DA70D6", fill_type="solid")  # Kreuzsumme
        n_rows = len(df_pivot) - 1  # letzte Zeile = Col_Sum
        n_cols = len(for_cols_sorted)
        for i in range(n_rows):
            ws.cell(row=i+2, column=i+2).fill = blue_fill  # +2: Header-Zeile

        # Kreuzsumme markieren (letzte Zeile, letzte Spalte)
        ws.cell(row=n_rows+2, column=len(df_pivot.columns)).fill = orchid_fill

        wb.save(outfile_xlsx)

             # --- TXT-Export (Fortran-lesbar) ---
        txt_outfile = os.path.join(outdir, f"distribution_{city_str}_{param}_{user_str}.txt")
        # Spaltenbreiten bestimmen
        col_widths = {}
        for c in df_excel.columns:
            max_len = max([len(str(val)) for val in df_excel[c].to_list()] + [len(c)])
            col_widths[c] = max_len

        with open(txt_outfile, "w", encoding="utf-8") as f:
                # Header
            header = " ".join(f"{c:>{col_widths[c]}}" for c in df_excel.columns)
            f.write(header + "\n")
                
            # Zeilen
            for row in df_excel.rows():
                line = " ".join(f"{str(val):>{col_widths[df_excel.columns[i]]}}" for i, val in enumerate(row))
                f.write(line + "\n")

        print(f"Saved TXT for {city}, user {user}: {txt_outfile}")


# ------------------- ASCII-Tabelle bauen -------------------
        asc_outfile = os.path.join(outdir, f"distribution_{city}_{param}_{user}.asc")
        # Header mit Unterzeile
        headers = ["Kl", "MFc", "MOb", "#"]

        # Werte vorbereiten (erst sammeln, dann Spaltenbreiten bestimmen)
        rows = []

        # Werte pro Klasse
        for obs_r in obs_ranges_def:
            lower, upper = obs_r
            combined_vals = []
            for for_r in for_ranges_def:
                combined_vals.extend(values_by_bin.get((tuple(obs_r), tuple(for_r)), []))

            count = len(combined_vals)
            mean_fc = sum(v for (_, v) in combined_vals) / count if count else 0.0
            mean_obs = sum(o for (o, _) in combined_vals) / count if count else 0.0
            print(f"count ist {count}.")

            kl_val = f"{upper:.1f}"
            rows.append([kl_val, f"{mean_fc:.2f}", f"{mean_obs:.2f}", str(count)])

        col_widths = []
        for i, h enumerate(headers):
            max_val_len = max(len(r[i]) for h, w in zip(headers, col_widths)))
            col_widths.append(max(len(h), max_val_len))

        asc_lines = []
        # Header-Zeile rechtsbündig
        asc_lines.append(" ".join(f"{val:>{w}}" for h, w in zip(headers, col_widths)))
        # Trennstriche (genauso wie die Spaltenbreite)
        asc.append(" ".join("-" * w for w in col_widths))
        # Daten rechtsbündig
        for r in rows:
            asc_lines.append(" ".join(f"{val:>{w}}" for val, w in zip(r, col_widths)))
        # Datei schreiben
        with open(asc_outfile, "w", encodeing="utf-8") as f:
            f.write("\n".join(asc_lines))
        print(f"ASCII table saved: {asc_outfile}")

           


for param in elemente_namen:
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
        
        plot_filename = os.path.join(outdir, f"scatter_absfreq_{city_str}_{param}_{user_str}.png")
        plt.savefig(plot_filename, dpi=300)
        print(f"Scatterplot with absolute frequency saved for parameter {param}: {plot_filename}")
        plt.close(fig)



















