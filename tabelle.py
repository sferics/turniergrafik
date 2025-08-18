import matplotlib.pyplot as plt
import os
import time         # für die Laufzeit später

start = time.time()
#-------------------------------
# Funktion, die Dateien mit * findet
#-------------------------------

def finde_dateien(muster):
    #   Bestimme den ordner, in dem gesucht werden soll
    #   os.path.dirname gibt den Pad zum Ordner zurück. 
    #   Dann muss man den nicht mehr implementieren.
    #   Wenn kein Ordner im Muster steht, wird "." benutzt, also der aktuelle Ordner
    ordner = os.path.dirname(muster) or "."
    #   Nimm nur "2025-08-18:*_Wien_*.txt"
    name_muster = os.path.basename(muster)
    #    Zerlege das Muster an jedem Sternchen "*"
    #    Beispiel: "2025-08-18_*_Wien_*.txt" -> ["2025-08-18_", "_Wien_", ".txt"]
    #    Alles zwischen den Sternchen wird "egal" – nur die festen Teile werden überprüft
    teile = name_muster.split("*")
    #    Leere Liste vorbereiten, um alle passenden Dateien zu speichern
    dateien = []
    #    Gehe alle Dateien im Ordner durch
    for fname in os.listdir(ordner):
        #    Prüfe nur Textdateien
        if fname.endswith(".txt"):      # Wenn Endung ".txt"

            #    Startposition für die Suche im Dateinamen
            pos = 0
            #    Flag, das merkt, ob alle Teile passen
            ok = True

            #  Prüfe, ob alle festen Teile des Musters in der richtigen Reihenfolge im Dateinamen vorkommen
            for teil in teile:
                #  Suche das Teil ab der Position pos
                idx = fname.find(teil, pos)
                #  Wenn das Teil nicht gefunden wird -> Datei passt nicht
                if idx == -1:
                    ok = False
                    break
                #  Wenn gefunden -> Position weiter nach hinten setzen, um Reihenfolge zu beachten
                pos = idx + len(teil)

            #   Wenn alle Teile gefunden wurden -> Datei merken
            if ok:
                dateien.append(os.path.join(ordner, fname))

    #  Gib am Ende die Liste aller passenden Dateien zurück
    return dateien
# ------------------------------
# Liste der Muster-Dateien und Modelle
# ------------------------------
# Dateipfade angeben. Es sind mehrere, aber durch "*" werden alle anderen txt Dateien mit gelistet. Das funktioniert wie im Terminal.
dateipfade = [
    '2025-08-18_*_Wien_dd12_MSwr-MOS-Mix_MSwr-EZ-MOS_MSwr-GFS-MOS_DWD-MOS-Mix_DWD-MOS-Mix-test_DWD-EZ-MOS_DWD-ICON-MOS_MOS-Mix_*.txt',
    # weitere Dateien hier
]

# Beide zu betrachtenden Modelle werden als Liste definiert.
modelle = ['DWD-EZ-MOS', 'MSwr-EZ-MOS']

# ------------------------------
# Funktion zum Einlesen der Werte für ein Modell
# ------------------------------
def lade_modell_werte(dateipfad, modell_prefix):
    #  Öffne die Datei, die unter "dateipfad" angegeben ist, zum Lesen
    #    'utf-8' sorgt dafür, dass Umlaute und Sonderzeichen korrekt gelesen werden.
    #    Bei Linux ist es utf8.
    #    "with" sorgt dafür, dass die Datei am Ende automatisch geschlossen wird
    with open(dateipfad, 'r', encoding='utf-8') as f:
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
# Alle Muster-Dateien durchgehen
# ------------------------------
# Gehe alle Muster in den Dateipfaden durch, die wir durchsuchen wollen
for muster in dateipfade:
    # Finde alle Dateien, die zu diesem Muster passen
    gefundene_dateien = finde_dateien(muster)

    # Wenn keine Datei gefunden wurde, gib eine Meldung aus 
    # und gehe zum nächsten Muster
    if not gefundene_dateien:
        print(f"Keine Dateien gefunden für Muster: {muster}")
        continue  # überspringt den Rest dieser Schleife 
        # und geht zum nächsten Muster
    # Gehe jede gefundene Datei einzeln durch
    for dateipfad in gefundene_dateien:
        print(f"\n=== Datei: {dateipfad} ===\n")

        # Hier speichern wir später die Werte aller Modelle 
        # für diese Datei in ein Wörterbuch.
        werte_modelle = {}
        alle_daten = None  # einmalig die Liste der Datumsangaben speichern

        # Gehe alle Modelle durch
        for modell in modelle:
            # Lade die Werte für dieses Modell aus der Datei
            werte, daten = lade_modell_werte(dateipfad, modell)
            # Speichere die Werte in einem Dictionary, das nach Modellnamen sortiert ist
            werte_modelle[modell] = werte
            # Speichere einmalig die Datums-Liste

            if alle_daten is None:
                alle_daten = daten

        # Berechne die Summe aller Werte für jedes Modell
        gesamt_summen = {modell: sum(werte.values()) for modell, werte in werte_modelle.items()}
        # Drucke die Gesamtsummen in die Konsole
        for modell, summe in gesamt_summen.items():
            print(f"Gesamtsumme {modell}: {summe:.2f}")
                
        

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
