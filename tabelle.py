import matplotlib.pyplot as plt
import os
import time         # für die Laufzeit später
# ------------------------------
# Datei einlesen und Werte extrahieren
# ------------------------------

# Dateipfad zur Textdatei mit den Modellwerten

dateipfade = [
    '2025-08-18_SatSun_Wien_dd12_MSwr-MOS-Mix_MSwr-EZ-MOS_MSwr-GFS-MOS_DWD-MOS-Mix_DWD-MOS-Mix-test_DWD-EZ-MOS_DWD-ICON-MOS_MOS-Mix_weeks.txt',
    '2025-08-18_SatSun_Wien_dd12_MSwr-MOS-Mix_MSwr-EZ-MOS_MSwr-GFS-MOS_DWD-MOS-Mix_DWD-MOS-Mix-test_DWD-EZ-MOS_DWD-ICON-MOS_MOS-Mix_years.txt'  # weitere Dateien hier einfügen
]

modelle = ['DWD-EZ-MOS', 'MSwr-EZ-MOS']

# Funktion zum Einlesen der Werte für ein bestimmtes Modell
def lade_modell_werte(dateipfad, modell_prefix):
    with open(dateipfad, 'r', encoding='utf-8') as f:     
        # Öffnet die Datei im Lesemodus ("r") und mit UTF-8 Zeichenkodierung

        daten = f.readline().strip().split()  
        # Liest die erste Zeile (= enthält die Datumsangaben), 
        # entfernt Leerzeichen und teilt die Werte in eine Liste

        for zeile in f:   # Jede weitere Zeile durchgehen
            zeile = zeile.strip()
            if zeile.startswith(modell_prefix):  
                # Nur die Zeilen nehmen, die mit dem Modellnamen anfangen, z.B. "DWD-EZ-MOS"

                werte_teile = zeile[len(modell_prefix):].strip().split()
                # Modellname vorne abschneiden, Rest in Zahlenwerte zerlegen

                if len(werte_teile) != len(daten):
                    raise ValueError(f"Anzahl der Werte ({len(werte_teile)}) stimmt nicht mit Anzahl der Daten ({len(daten)}) überein")
                # Sicherheitsprüfung: Anzahl der Werte = Anzahl der Datumsangaben

                return {datum: float(wert) for datum, wert in zip(daten, werte_teile)}, daten
                # Rückgabe als Wörterbuch (in Python Dictionary): 
                # 1) Ein Wörterbuch: jedem Datum wird der entsprechende Zahlenwert zugeordnet
                # 2) Die komplette Liste der Daten
                

# ------------------------------
# Alle Dateien durchgehen
# ------------------------------
for dateipfad in dateipfade:
    print(f"\n=== Datei: {dateipfad} ===\n")
    
    # Werte für alle Modelle speichern
    werte_modelle = {}
    alle_daten = None
    for modell in modelle:
        werte, daten = lade_modell_werte(dateipfad, modell)
        werte_modelle[modell] = werte
        if alle_daten is None:
            alle_daten = daten  # einmalig die Datums-Liste speichern


# ------------------------------
# Summen berechnen
# ------------------------------
gesamt_summen = {modell: sum(werte.values()) for modell, werte in werte_modelle.items()}
for modell, summe in gesamt_summen.items():
    print(f"Gesamtsumme {modell}: {summe:.2f}")


# ------------------------------
# Differenzen und Quotienten (zwischen den beiden Modellen)
# ------------------------------
differenzen = {datum: werte_modelle[modelle[0]][datum] - werte_modelle[modelle[1]][datum] for datum in alle_daten}
quotienten = {datum: werte_modelle[modelle[0]][datum] / werte_modelle[modelle[1]][datum] for datum in alle_daten}


# ------------------------------
# Tabelle in der Konsole anzeigen
# ------------------------------

# Kopfzeile (Spaltenüberschriften) für die Ausgabe in der Konsole definieren
# f"" bedeutet "formatierter Text", damit wir Spaltenbreiten einstellen können
header = f"{'Datum':<12} {'DWD-EZ-MOS':>12} {'Summe MSwr':>12} {'Differenz':>12} {'Quotient':>12}"

# Kopfzeile in der Konsole ausgeben
print(header)

# Eine Linie (----) unter der Kopfzeile, damit es wie eine Tabelle aussieht
print('-' * len(header))


# ------------------------------
# Einzelne Tageswerte in die Tabelle schreiben (Konsole)
# ------------------------------

# Wir gehen nacheinander jedes Datum in der Liste "alle_daten" durch
for datum in alle_daten:
    # Ein Datum wie "20250816" wird in Jahr, Monat, Tag zerlegt
    jahr, monat, tag = datum[:4], datum[4:6], datum[6:8]

    # Datum hübsch formatieren -> aus "20250816" wird "16.08.2025"
    datum_formatiert = f"{tag}.{monat}.{jahr}"   

    # Für jedes Datum die Werte von beiden Modellen ausgeben:
    # - DWD-Modell
    # - MSwr-Modell
    # - die Differenz
    # - den Quotienten
    # Alles schön in Spalten ausgerichtet
    print(f"{datum_formatiert:<12} "
          f"{werte_dwd[datum]:>12.2f} "
          f"{werte_mswr[datum]:>12.2f} "
          f"{differenzen[datum]:>12.2f} "
          f"{quotienten[datum]:>12.3f}")


# ------------------------------
# Gesamtsummen in der Konsole ausgeben
# ------------------------------

# Trennlinie wie vorher
print('-' * len(header))

# Letzte Zeile mit den Summen beider Modelle
# In den Spalten "Differenz" und "Quotient" bleibt es leer
print(f"{'Gesamt':<12} "
      f"{gesamt_summe_dwd:>12.2f} "
      f"{gesamt_summe_mswr:>12.2f} "
      f"{'':>12} "
      f"{'':>12}")


# ------------------------------
# Daten für PNG-Tabelle vorbereiten
# ------------------------------

# Hier bauen wir die Tabelle Zeile für Zeile als "Liste von Listen" auf
tabellen_daten = []

# Wieder durch alle Tage gehen
for datum in alle_daten:
    jahr, monat, tag = datum[:4], datum[4:6], datum[6:8]
    datum_formatiert = f"{tag}.{monat}.{jahr}"
    tabellen_daten.append([
        datum_formatiert,
        f"{werte_dwd[datum]:>10.2f}",   # Wert vom DWD-Modell
        f"{werte_mswr[datum]:>10.2f}",  # Wert vom MSwr-Modell
        f"{differenzen[datum]:>10.2f}", # Differenz
        f"{quotienten[datum]:>10.3f}"   # Quotient
    ])

# Am Ende die Gesamtsummen als eigene Zeile hinzufügen
tabellen_daten.append([
    "Gesamt",
    f"{gesamt_summe_dwd:>10.2f}",
    f"{gesamt_summe_mswr:>10.2f}",
    "",   # leer lassen
    ""    # leer lassen
])

# Überschriften für die Spalten
spalten = ["Datum", "DWD-EZ-MOS", "MSwr-EZ-MOS", "Differenz", "Quotient"]


# ------------------------------
# Tabelle als Bild (PNG) speichern
# ------------------------------


# Ein "Figure" (fig) und eine "Axes" (ax) erzeugen.
# - fig ist das gesamte Bild (Leinwand).
# - ax ist ein einzelner Zeichenbereich (quasi ein Kästchen auf der Leinwand).
fig, ax = plt.subplots(figsize=(12, max(len(tabellen_daten)*0.5, 2)))

# Die Achsen (Skalen, Zahlen am Rand) werden hier ausgeschaltet,
# weil wir keine Kurve oder Punkte zeichnen wollen, sondern nur eine Tabelle.
ax.axis('off')

# Jetzt kommt die Tabelle:
# Wir hängen die Tabelle an den Achsenbereich (ax) an.
# Warum an "ax"?  
# → Weil in Matplotlib alles in sogenannte "Axes" hineingezeichnet wird.
# Eine Figur (fig) kann mehrere Achsenbereiche (ax) enthalten.
# Tabellen, Diagramme, Plots – all das "lebt" in einem ax.
# Ohne Angabe von ax wüsste Matplotlib nicht, *wohin* es die Tabelle zeichnen soll -> eine Fehlermeldung folgt dann im Terminal.
tabelle = ax.table(cellText=tabellen_daten,   # Tabelleninhalt (Zellen)
                   colLabels=spalten,         # Spaltenüberschriften
                   cellLoc='center',          # Text in den Zellen zentrieren
                   loc='center',              # Tabelle in der Mitte der Achse platzieren
                   colColours=['#f2f2f2']*len(spalten))  # Kopfzeile grau einfärben


# Tabelle als Bild speichern
plt.savefig("tabelle_mosse.png", dpi=300, bbox_inches='tight')

# plt.close() macht das aktuelle Bild "zu".
# Warum? 
#   Wenn man viele Plots oder Tabellen erstellt, bleiben diese intern im Speicher.
#   Ohne close() würde Matplotlib alle Bilder "offen halten".
#   Das braucht unnötig Speicher und kann Programme verlangsamen.
# Mit plt.close() sagt man: "Fertig! Dieses Bild ist gespeichert, 
#   jetzt kann Matplotlib es aus dem Speicher löschen.
plt.close()

# Kontrollausgabe für den Nutzer:
print("Tabelle als 'tabelle_mosse.png' gespeichert.")


# Info für den Nutzer in der Konsole
print("Tabelle als 'tabelle_mosse.png' gespeichert.")  
