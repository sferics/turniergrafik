import matplotlib.pyplot as plt
import os

dateipfad = '2025-08-16_SatSun_allCities_allElements_MSwr-MOS-Mix_MSwr-EZ-MOS_MSwr-GFS-MOS_DWD-MOS-Mix_DWD-MOS-Mix-test_DWD-EZ-MOS_DWD-ICON-MOS_MOS-Mix_weeks.txt'
# geht für weeks und years
def lade_modell_werte(dateipfad, modell_prefix):
    with open(dateipfad, 'r', encoding='utf-8') as f:
        daten = f.readline().strip().split()  # erste Zeile = Datumsangaben
        for zeile in f:
            zeile = zeile.strip()
            if zeile.startswith(modell_prefix):
                werte_teile = zeile[len(modell_prefix):].strip().split()
                if len(werte_teile) != len(daten):
                    raise ValueError(f"Anzahl der Werte ({len(werte_teile)}) stimmt nicht mit Anzahl der Daten ({len(daten)}) überein")
                return {datum: float(wert) for datum, wert in zip(daten, werte_teile)}, daten

# Werte laden
werte_dwd, alle_daten = lade_modell_werte(dateipfad, 'DWD-EZ-MOS')
werte_mswr, _ = lade_modell_werte(dateipfad, 'MSwr-EZ-MOS')

# Summen berechnen
gesamt_summe_dwd = sum(werte_dwd.values())
gesamt_summe_mswr = sum(werte_mswr.values())

print("Gesamtsumme DWD-EZ-MOS:", sum(werte_dwd.values()))
print("Gesamtsumme MSwr-EZ-MOS:", sum(werte_mswr.values()))


# Differenzen und Quotienten
differenzen = {datum: werte_dwd[datum] - werte_mswr[datum] for datum in alle_daten}
quotienten = {datum: werte_dwd[datum] / werte_mswr[datum] for datum in alle_daten}



# --- Tabelle in Konsole ausgeben ---
header = f"{'Datum':<12} {'DWD-EZ-MOS':>12} {'Summe MSwr':>12} {'Differenz':>12} {'Quotient':>12}"
print(header)
print('-' * len(header))
for datum in alle_daten:
    jahr, monat, tag = datum[:4], datum[4:6], datum[6:8]
    datum_formatiert = f"{tag}.{monat}.{jahr}"
    print(f"{datum_formatiert:<12} "
          f"{werte_dwd[datum]:>12.2f} "
          f"{werte_mswr[datum]:>12.2f} "
          f"{differenzen[datum]:>12.2f} "
          f"{quotienten[datum]:>12.3f}")

# Gesamtsumme in Konsole ausgeben
print('-' * len(header))
print(f"{'Gesamt':<12} "
      f"{gesamt_summe_dwd:>12.2f} "
      f"{gesamt_summe_mswr:>12.2f} "
      f"{'':>12} "
      f"{'':>12}")

# --- Daten für PNG-Tabelle vorbereiten ---
tabellen_daten = []
for datum in alle_daten:
    jahr, monat, tag = datum[:4], datum[4:6], datum[6:8]
    datum_formatiert = f"{tag}.{monat}.{jahr}"
    tabellen_daten.append([
        datum_formatiert,
        f"{werte_dwd[datum]:>10.2f}",
        f"{werte_mswr[datum]:>10.2f}",
        f"{differenzen[datum]:>10.2f}",
        f"{quotienten[datum]:>10.3f}"
    ])

# Gesamtsumme als letzte Zeile hinzufügen
tabellen_daten.append([
    "Gesamt",
    f"{gesamt_summe_dwd:>10.2f}",
    f"{gesamt_summe_mswr:>10.2f}",
    "",
    ""
])

# --- Spaltenüberschriften ---
spalten = ["Datum", "DWD-EZ-MOS", "MSwr-EZ-MOS", "Differenz", "Quotient"]

# --- Abmessungen automatisch anpassen ---
fig, ax = plt.subplots(figsize=(12, max(len(tabellen_daten)*0.5, 2)))
ax.axis('off')

# --- Tabelle erstellen ---
tabelle = ax.table(cellText=tabellen_daten,
                   colLabels=spalten,
                   cellLoc='center',
                   loc='center',
                   colColours=['#f2f2f2']*len(spalten))  # helle Kopfzeilenfarbe

# --- Schriftgröße und Spaltenbreite anpassen ---
tabelle.auto_set_font_size(False)
tabelle.set_fontsize(10)
tabelle.auto_set_column_width(col=list(range(len(spalten))))

# --- Speichern ---
plt.savefig("tabelle_mosse.png", dpi=300, bbox_inches='tight')
plt.close()
print("Tabelle als 'tabelle_mosse.png' gespeichert.")
