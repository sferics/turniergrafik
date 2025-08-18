#!/usr/bin/env python3
# -*- coding: utf-8 -*-

##########################################################################################
## Programmiert von André Petersen (mail@andrepetersen.de) im Auftrag von Meteo Service ##
## Idee: Klaus Knüpffer ### Unterstützung bei der Programmierstruktur: Diederik Haalman ##
##########################################################################################

# Dieser Teil des Turnier-Grafik-Programmes wurde zum grossen Teil von André
# Petersen programmiert und aus Kompatibilitaetsgrunden von Felix Korthals
# angepasst.

# zur grafischen Darstellung
import matplotlib
# kein Xserver
matplotlib.use('Agg')
import matplotlib.pyplot as plt
# damit kann das Logo einfach auf dem Plot dargest. werden:
from matplotlib.cbook import get_sample_data

import locale
from datetime import date
from datetime import timedelta
from datetime import datetime as dt

# einfachere Berechnungen und Umgang mit Fehlwerten
import numpy as np

# Ermöglicht das Wechseln der Ordner
import os

### Konfiguration

# Variablen aus config.py mit cfg.variable aufrufbar
import config as cfg

from turniergrafik import index_2_date, kuerzel_zu_id

#TODO move to turniergrafik.py and re-use, remove from here
def stadtname(stadt):
    """
    Liefert den Namen der Stadt, die in der Konfiguration
    hinterlegt ist, zurück.
    
    :param stadt: entweder eine Stadt-ID (int) oder ein 3-stelliges Kürzel
    
    :return: Name der Stadt (String)
    """
    # Wenn die Stadt eine ID ist, wird der Name direkt aus cfg.stadtnamen geholt
    if type(stadt) == int:
        return cfg.stadtnamen[stadt]
    # Wenn die Stadt ein 3-stelliges Kürzel ist, wird die ID aus kuerzel_zu_id geholt
    elif len(stadt) == 3:
        return cfg.stadtnamen[kuerzel_zu_id[stadt] - 1 ]
    # Wenn die Stadt ein String ist, wird die ID aus stadt_zu_id geholt
    return cfg.stadtnamen[ cfg.stadt_zu_id[stadt] - 1 ]


#TODO cfg.xxx lieber als Argumente von erstelleGrafik() (sonst 'verschleiert')
def gibDateinamen(laufindex = 0, cfg=cfg):
    """
    Erstellt den Dateinamen für die zu speichernde Grafik.
    
    :param laufindex: Laufindex, der an den Dateinamen angehängt wird
    :param cfg: Konfiguration, die die Einstellungen enthält
    
    :return: Dateiname der Grafik (String)
    """
    #FIXME kann weg, wenn kein multi implementiert
    auswertungsstaedte = cfg.auswertungsstaedte
    stadtnamen = cfg.stadtnamen
    auswertungstage = cfg.auswertungstage
    auswertungselemente = cfg.auswertungselemente
    auswertungsteilnehmer = cfg.auswertungsteilnehmer
    elemente_archiv = cfg.elemente_archiv

    ### Erstelle Dateinamen für Plot
    now = dt.now()
    
    # Wenn alle Städte ausgewertet werden, wird "allCities" verwendet
    if auswertungsstaedte == stadtnamen:
        stadtinfo = "allCities"
    # Wenn nur bestimmt Städte ausgewertet werden, dann werden diese
    # in einem String zusammengefasst
    else:
        stadtinfo = ""
        for stadt in cfg.auswertungsstaedte:
            stadtinfo += stadtname(stadt)
    
    # Info über die ausgewerteten Tage (Sa, So oder beide)
    taginfo = ""
    tage_uebersetzung_kurz = {"Sa" : "Sat", "So" : "Sun"}
    for tag in auswertungstage:
        taginfo += tage_uebersetzung_kurz[tag]

    # Wenn alle Elemente ausgewertet werden, wird "allElements" verwendet
    if auswertungselemente == elemente_archiv:
        elementinfo = "allElements"
    # Wenn nur bsestimmte Elemente ausgewertet werden, dann werden diese
    # in einem String mit Bindestrichen getrennt zusammengefasst
    else:
        elementinfo = ""
        for element in auswertungselemente:
            elementinfo += element+"-"
        # Löschen des letzten Bindestrichs
        elementinfo = elementinfo[:-1]
    
    # Info über das Datum, an dem die Grafik erstellt wurde
    zeitinfo = now.strftime("%Y-%m-%d")
    
    # Die Teilnehmer werden in einem String durch Unterstriche getrennt
    teilnehmer = ""
    for i in auswertungsteilnehmer:
        teilnehmer += (i + "_")
    
    # Entferne den letzten Unterstrich aus dem Teilnehmer-String
    teilnehmer = teilnehmer[:-1]
    # Speichere den Dateinamen der Grafik im Format:
    file_name = f"{zeitinfo}_{taginfo}_{stadtinfo}_{elementinfo}_{teilnehmer}.png"
    print( "Dateiname der Grafik: ", file_name )
    # Gib den Dateinamen zurück, der für die Grafik verwendet wird
    return file_name


def speicherGeplotteteWerte(ascii_datei_terminliste,
                            ascii_datei_spielernamen_punkteverlust,
                            plotname,
                            dateiname_plot):
    """
    Speichert die geplotteten Werte in einer ASCII-Datei.
    
    :param ascii_datei_terminliste: Liste der Termine (Datum) für die X-Achse
    :param ascii_datei_spielernamen_punkteverlust: Dictionary, das die
        Spieler und ihre Punkteverluste enthält
    :param plotname: Name des Plots (linker_plot oder rechter_plot)
    :param dateiname_plot: Dateiname der Grafik, die gespeichert wird
    
    :return: None
    """
    plotname_zu_zeitspannenbeschreibung = {"linker_plot" : "years",
                                           "rechter_plot" : "weeks"}

    # Entferne die Dateiendung des Plots und füge .txt an
    #FIXME schwer lesbar -> ugly..
    dateiname_txt_file = ('.').join(dateiname_plot.split('.')[:-1]) + "_" \
        + plotname_zu_zeitspannenbeschreibung[plotname] + ".txt"
    
    # Erstelle eine ASCII-Datei, in der die geplotteten Werte stehen
    with open(dateiname_txt_file, 'w') as f:
        # Schreibe die Kopfzeile mit den Terminen
        kopfzeile = " "*22
        # Kopfzeile: "Spielername" + " Termin1" + " Termin2" + ...
        for termin in ascii_datei_terminliste:
            kopfzeile += " "+str(termin)
        # Füge die Kopfzeile in die Datei ein
        f.write(kopfzeile+"\n")
        
        # Schreibe die Spieler und ihre Punkteverluste
        for spielername, punkteverluste \
                in ascii_datei_spielernamen_punkteverlust.items():
            # Spielername linksbündig mit 22 Zeichen
            zeile = spielername.ljust(22)
            
            # Füge die Punkteverluste für jeden Termin hinzu
            for punkteverlust in punkteverluste:
                zeile += " "+str(round(punkteverlust,3)).ljust(8)
            
            # Füge die Zeile in die Datei ein
            f.write(zeile+"\n")

def erstelleGrafik(langfrist_player_date_points, kurzfrist_player_date_points, cfg=cfg):

    teilnehmerlinien_dickgedruckt = cfg.teilnehmerlinien_dickgedruckt
    sprache = cfg.sprache
    skalenfaktor = cfg.skalenfaktor
    auswertungstage = cfg.auswertungstage
    auswertungselemente = cfg.auswertungselemente
    auswertungsstaedte = cfg.auswertungsstaedte
    beschriftungen = cfg.beschriftungen
    legende_spaltenanzahl = cfg.grafik_spaltenanzahl
    linieneigenschaften = cfg.linieneigenschaften
    marker = cfg.marker
    marker_groesse = cfg.marker_groesse
    liniendicke = cfg.liniendicke

    """
    Erstellt eine Grafik, die die langfristigen und kurzfristigen
    Punkteverluste der Spieler anzeigt.
    Die langfristigen Punkteverluste sind die Punkteverluste, die
    über einen längeren Zeitraum (z.B. Jahre) gesammelt werden.
    Die kurzfristigen Punkteverluste sind die Punkteverluste, die
    über einen kürzeren Zeitraum (z.B. Wochen) gesammelt werden.
    Die Daten für die langfristigen Punkteverluste sind in
    langfrist_player_date_points gespeichert, die Daten für die
    kurzfristigen Punkteverluste in kurzfrist_player_date_points.
    Die Daten für langfrist_player_date_points und kurzfrist_player_date_points
    sind Listen von Tupeln, die jeweils den Spielernamen und eine Liste
    von Tupeln enthalten, die das Datum und den Punkteverlust
    enthalten. Also:
    langfrist_player_date_points hat den Typen:
    [(string Player, [(datetime Date, float LostPoints)])]
    kurzfrist_player_date_points hat den Typen:
    [(string Player, [(datetime Date, float LostPoints)])]
    
    Die Grafik wird in der Konfiguration angegebenen Sprache erstellt.
    Die Achsenbeschriftungen, Titel und Legende werden entsprechend
    der Sprache angepasst.
    
    :param langfrist_player_date_points: Langfristige Punkteverluste
        der Spieler (Liste von Tupeln) 
        [(string Player, [(datetime Date, float LostPoints)])]
    :param kurzfrist_player_date_points: Kurzfristige Punkteverluste
        der Spieler (Liste von Tupeln)
        [(string Player, [(datetime Date, float LostPoints)])]
    :param cfg: Konfiguration, die die Einstellungen enthält
    :type cfg: config.Config
    :raises ValueError: Wenn die Konfiguration ungültig ist

    :return: None
    """
    # Setze die Locale für die Datums- und Zeitformatierung
    locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
        # Erstelle eine neue Figur mit den angegebenen Abmessungen
    fig = plt.figure(figsize=(11.69,8.27))
        
        # Erstelle ein GridSpec-Objekt für die Anordnung der Subplots
    gs = matplotlib.gridspec.GridSpec(1, 2, width_ratios=[7, 4])
        # Setze den Abstand zwischen den Subplots
    gs.update(wspace=0.12)
        
        # Erstelle die Subplots für den linken und rechten Plot
        # TODO ugly..
        plots = {"linker_plot" : plt.subplot(gs[0]),
                 "rechter_plot" : plt.subplot(gs[1])}
        
        # TODO REFAKTORISIEREN!
        # Initialisiere Variablen für die Speicherung der Daten
        ascii_datei_terminliste = {"linker_plot": [], "rechter_plot": []}
        # Dictionary, das die Spieler und ihre Punkteverluste enthält
        ascii_datei_spielernamen_punkteverlust = {"linker_plot": {},
                                                  "rechter_plot": {}}
        # Initialisiere Variablen für die X-Achse
        x_beginn_zeitstempel = {"linker_plot": 0, "rechter_plot": 0}
        # X-Achse Ende Zeitstempel
        x_ende_zeitstempel = {"linker_plot": 0, "rechter_plot": 0}
        # X-Achse für die Plots
        x = {"linker_plot": [], "rechter_plot": []}
        # Terminliste für die X-Achse
        xlabel_terminliste = {"linker_plot": [], "rechter_plot": []}
        
        # Y-Achse Min- und Max-Werte für die Plots
        ymin = {}
        ymax = {}

        # behandelt linken und rechten Plot (items) #TODO ugly..
        for plotname, plot in plots.items():
            erster_teilnehmer = True
            erster_turniertag = True
            xlabel_terminliste[plotname] = []

            ymin[plotname] = 1000.0
            ymax[plotname] = -1000.0

            # teilnehmer Typ: (NameString),
            # turniertag_punkteverlust Typ: [(Turniertag, Punkteverlust)]
            # langfrist_player_date_points und kurzfrist_player_date_points Typ:
            # [(string Player, [(datetime Date, float LostPoints)])]
            #TODO flachere Hierarchie?

            #print( "LANGFRIST:\n", langfrist_player_date_points )
            #print( "KURZFRIST:\n", kurzfrist_player_date_points )

            #print(langfrist_player_date_points)
            
            # Durchgehen der Teilnehmer und deren Punkteverluste
            for teilnehmer, turniertag_punkteverlust \
                in langfrist_player_date_points \
                if plotname == "linker_plot" else kurzfrist_player_date_points:
                
                if teilnehmer not in cfg.auswertungsteilnehmer:
                    # Wenn der Teilnehmer nicht ausgewertet wird, überspringe ihn
                    continue

                punkteverluste_plot = []
                
                x[plotname] = []
                i = 7

                # durchgehen von [(Datum, Punkteverlust)]
                for turniertag, punkteverlust in turniertag_punkteverlust:

                    # Index des Turniertages in ein Date-Obj. unwandeln
                    turniertag = index_2_date(turniertag)
                    
                    # Wenn der linke Plot ausgewertet wird, wird der
                    # entsprechende Zeitstempel in der X-Achse gespeichert
                    if plotname == "linker_plot":
                        x[plotname].append(turniertag)
                        x_ende_zeitstempel[plotname] = turniertag
                    # Beim rechten Plot wird der Zeitstempel in der X-Achse
                    # in der Form 1/7 (1 Woche) gespeichert
                    else:
                        x[plotname].append(1/i)
                        x_ende_zeitstempel[plotname] = 1/i
                    
                    # Zur Liste der Punkteverluste wird der aktuelle
                    # Punkteverlust hinzugefügt
                    punkteverluste_plot.append(punkteverlust)
                    
                    # Die Min- und Max-Werte für die Y-Achse werden aktualisiert
                    ymin[plotname] = np.nanmin([ymin[plotname], punkteverlust])
                    ymax[plotname] = np.nanmax([ymax[plotname], punkteverlust])
                    
                    # Wenn der erste Turniertag ist, wird der Zeitstempel
                    # für den Beginn des Turniertages gespeichert
                    if erster_turniertag:
                        x_beginn_zeitstempel[plotname]  = turniertag
                        erster_turniertag = False

                    # Zeitstempel fuer ersten Teilnehmer schreiben (da folgende
                    # identisch)
                    if erster_teilnehmer:
                        if plotname == "linker_plot":
                            xlabel_terminliste[plotname] \
                            .append(turniertag.strftime("%d%b%y"))
                        else:
                            xlabel_terminliste[plotname] \
                            .append(turniertag.strftime("%d%b%y"))
                        ascii_datei_terminliste[plotname] \
                            .append(turniertag.strftime("%Y%m%d"))

                    i+=4
                
                # Wenn der erste Teilnehmer verarbeitet wurde, wird
                # erster_teilnehmer auf False gesetzt, damit die
                # Zeitstempel für die X-Achse nicht mehrfach geschrieben werden
                erster_teilnehmer = False
                
                label_name = teilnehmer
                
                # Soll der Teilnehmer dickgedruckt dargestellt werden?
                if teilnehmer in teilnehmerlinien_dickgedruckt:
                    spielerliniendicke = liniendicke[plotname]["dick"]
                else:
                    spielerliniendicke = liniendicke[plotname]["normal"]
                
                # Speichere die Punkteverluste des Teilnehmers für die ASCII-Datei
                # und für die geplotteten Werte in einem Dictionary
                ascii_datei_spielernamen_punkteverlust[plotname][label_name] \
                    = punkteverluste_plot
                
                # Spezialfall, dass im linken Plot genug Daten für den neuesten
                # Zeitpunkt vorhanden sind, aber nicht für ältere Zeitpunkte
                # in dem Fall soll beim linken Plot beim aktuellsten Zeitpunkt ein
                # waagerechter Strich angezeigt werden, um die Performance zu dem
                # Zeitpunkt anzuzeigen normalerweise würde diese Daten nicht
                # angezeigt werden, da für einen Strich logischerweise die Daten
                # zu zwei Zeitpunkten notwendig wären
                if plotname == "linker_plot" and \
                        punkteverluste_plot.count(np.nan) \
                        == len(punkteverluste_plot) - 1:

                    # Warum zweimal der Plot Befehl?
                    # Der erste sorgt dafür, dass in der Legende der Strich für
                    # das Modell angezeigt wird und nicht der Marker, der zweite
                    # plottet den Marker (nicht sehr schön, aber funktioniert
                    # problemlos)
                    plot.plot(x[plotname],
                              punkteverluste_plot,
                              label = label_name,
                              color = linieneigenschaften[label_name][0],
                              linestyle = linieneigenschaften[label_name][1],
                              linewidth = spielerliniendicke)
                    
                    plot.plot(x[plotname][-1],
                              punkteverluste_plot[-1],
                              color = linieneigenschaften[label_name][0],
                              marker = marker,
                              markersize = marker_groesse,
                              linewidth = spielerliniendicke)

                # Speziallfall nicht zutreffend
                else: 
                    plot.plot(x[plotname],
                              punkteverluste_plot,
                              label=label_name,
                              color=linieneigenschaften[label_name][0],
                              linestyle = linieneigenschaften[label_name][1],
                              linewidth = spielerliniendicke)
        
        # Setze die X-Achsen-Beschriftungen für die Plots
        box = plot.get_position()
        
        # Setze die Position des linken Plots
        plot.set_position([box.x0, box.y0 + box.height*0.08, box.width,
                          box.height*0.78])
        # Definiere die Limits für die X-Achsen des linken Plots
        plots["linker_plot"].set_xlim(
            x_beginn_zeitstempel["linker_plot"],
            x_ende_zeitstempel["linker_plot"])
        
        # Setze die Y-Achsen-Beschriftungen für den linken Plot
        plots["linker_plot"].set_ylabel(
            beschriftungen[sprache]["achse_links"],
            multialignment='center',
            fontsize = 'large',
            fontweight='bold')
        
        # set yscale to asinh function
        #plots["linker_plot"].set_yscale('asinh')
        #plots["rechter_plot"].set_yscale('asinh')
        
        power = lambda x, y=10e10 : x**y

        def inverse_power(x, y=10e10):
            """
            Inverse Funktion für die Potenzfunktion, die für die Y-Achse
            verwendet wird. Diese Funktion ermöglicht es, die Y-Achse
            logarithmisch zu skalieren, ohne dass negative Werte
            Probleme verursachen.
            
            :param x: Eingabewerte (Array oder Liste)
            :param y: Exponent (Standardwert ist 10e10)
            
            :return: Array mit den inversen Potenzwerten
            """
            res = []
            for i in x:
                if i < 0:
                    res.append(-(-i)**(1/y))
                else:
                    res.append(i**(1/y))
            return np.array(res)
        
        # Setze die Y-Achsen-Skalierung für den linken Plot
        plots["linker_plot"].set_yscale('function', functions=(inverse_power, power))
        #plots["rechter_plot"].set_yscale('function', functions=(inverse_power_6, power_6))
        
        # Für den rechten Plot nutze 1/7 und das Ende des Zeitstempels
        # als Begrenzung der X-Achse
        plots["rechter_plot"].set_xlim(1/7, x_ende_zeitstempel["rechter_plot"])
        # Setze die Labels für die Y-Achse des rechten Plots auf die rechte Seite
        plots["rechter_plot"].yaxis.set_label_position("right")
        # Setze die Beschriftungen des rechten Plots (Y-Achse)
        plots["rechter_plot"].set_ylabel(
            beschriftungen[sprache]["achse_rechts"],
            fontsize = 'large',
            fontweight='bold')

        """
        if abs(ymax["linker_plot"] - ymax["rechter_plot"])\
               + abs(ymin["linker_plot"] - ymin["rechter_plot"])\
               < skalenfaktor * (ymax["linker_plot"] - ymin["linker_plot"]):

            plots["linker_plot"].set_ylim(
                min(ymin["linker_plot"], ymin["rechter_plot"]),
                max(ymax["linker_plot"], ymax["rechter_plot"]))

            plots["rechter_plot"].set_ylim(
                min(ymin["linker_plot"],ymin["rechter_plot"]),
                max(ymax["linker_plot"],ymax["rechter_plot"]))
        """
        
        # Setze die X-Achsen Ticks (Markierungen) für die Plots
        for plotname, plot in plots.items():
            plot.set_xticks(x[plotname])
            plot.set_xticklabels(xlabel_terminliste[plotname],
                                 rotation=45, ha="right")
            # Plotte ein Grid (Gitter) für die X-Achse
            plot.grid()
        
        # Setze die Legende für den linken Plot
        plots["linker_plot"].legend(
            loc = 'upper center',
            bbox_to_anchor = (0.8, 1.29),
            fancybox = True,
            shadow = True,
            ncol = legende_spaltenanzahl,
            fontsize = 'medium')
        
        # Definiere den Titel für die Grafik
        plt.figtext(.33, .96, beschriftungen[sprache]["titel"],
                    fontsize=18, fontweight='bold')
        # Setze den Titel für den linken Plot
        plt.figtext(.27, .77, beschriftungen[sprache]["titel_links"],
                    fontsize=18, fontweight='bold')
        # Setze den Titel für den rechten Plot
        plt.figtext(.74, .77, beschriftungen[sprache]["titel_rechts"],
                    fontsize=18, fontweight='bold')

        ### COPYRIGHT LOGO ###
        # Versuche das Meteo Service Logo oben rechts in der Grafik
        # darzustellen. Wenn die Logo-Datei nicht gefunden wird,
        # wird eine Fehlermeldung ausgegeben.
        try:
            # FIXME
            # Die Datei logo.png muss im selben Verzeichnis liegen wie
            # dieses Skript, damit das Logo angezeigt wird.
            im = plt.imread(get_sample_data(os.getcwd()+'/logo.png'))
            #im = plt.imread(get_sample_data('logo.png'))
            # Füge das Logo in die Grafik ein
            # Die Position des Logos wird in der oberen rechten Ecke
            # der Grafik festgelegt
            newax = fig.add_axes([0.74, 0.94, 0.25, 0.05], anchor='NE', zorder=-1)
            # Zeige das Logo an
            newax.imshow(im)
            # Setze die Achsen des Logos auf "off", damit keine Achsen
            # angezeigt werden
            newax.axis('off')
        except:
            # Wenn die Logo-Datei nicht gefunden wird, wird eine Fehlermeldung
            # ausgegeben und das Logo wird nicht angezeigt.
            pass
            print("Damit das Meteo Service Logo oben rechts in der Grafik "\
                  "erscheint, muss das Logo (logo.png standardmäßig) im selben "\
                  "Verzeichnis liegen")

        ### Generiere Informationen über den Plot, die unten hineingeschrieben
        ### werden
        # Wenn die Sprache Englisch ist, werden die Tage in Englisch übersetzt
        if sprache == "en":
            tage_uebersetzung = {"Sa": "Saturday", "So": "Sunday", "all": "both"}
        # Wenn die Sprache Deutsch ist, werden die Tage in Deutsch übersetzt
        else:
            tage_uebersetzung = {"Sa": "Samstag", "So": "Sonntag", "all": "beide"}

        # Wenn nur ein Tag ausgewertet wird, wird der Tag in der
        # entsprechenden Sprache ausgegeben
        if len(auswertungstage) == 2:
            auswertungstage_plot = tage_uebersetzung["all"]
        # Wenn nur ein Tag ausgewertet wird, wird nur dieser Tag
        # auch in der entsprechenden Sprache ausgegeben
        else:
            auswertungstage_plot = ""
            for tag in auswertungstage:
                auswertungstage_plot += tage_uebersetzung[tag]+", "
            if auswertungstage_plot.endswith(", "):
                auswertungstage_plot = auswertungstage_plot[:-2]

        # Wenn alle Städte ausgewertet werden, wird "all(e)" verwendet
        if len(auswertungsstaedte) == len(cfg.stadtnamen):
            staedte_plot = "all"
            if sprache == "de":
                staedte_plot += "e"
        # Wenn nur bestimmte Städte ausgewertet werden, dann werden diese
        # in einem String mit Kommas getrennt zusammengefasst
        else:
            staedte_plot = ""
            for stadt in auswertungsstaedte:
                staedte_plot += stadtname(stadt)+", "
            if staedte_plot.endswith(", "):
                staedte_plot = staedte_plot[:-2]

        elemente_plot = ""
        
        # Wenn alle Elemente ausgewertet werden, wird "all(e)" verwendet
        if len(auswertungselemente) == len(cfg.elemente_archiv):
            elemente_plot = "all"
            if sprache == "de":
                elemente_plot += "e"
        # Wenn nur bestimmte Elemente ausgewertet werden, dann werden diese
        # in einem String mit Kommas getrennt zusammengefasst
        else:
            for element in auswertungselemente:
                elemente_plot += element+", "
            if elemente_plot.endswith(", "):
                elemente_plot = elemente_plot[:-2]
        
        # Wenn nur ein Element ausgewertet wird, wird kein "s" oder "e" angehängt
        # (für die Pluralform)
        if len(auswertungselemente) == 1:
            s = ""
        else:
            if sprache == "en":
                s = "s"
            else:
                s = "e"
        
        # Füge die Informationen über den Plot unten in die Grafik ein
        if sprache == "en":
            # Wenn die Sprache Englisch ist, wird "Averaged over" verwendet
            plt.figtext(.01,.01,
                        f"Averaged over – Days: {auswertungstage_plot} – Cities: {staedte_plot} – Element{s}: {elemente_plot}",
                        fontsize=11)
        else:
            # Wenn die Sprache Deutsch ist, wird "Gemittelt über" verwendet
            plt.figtext(.01,.01,
                        f"Gemittelt über – Tage: {auswertungstage_plot} – Städte: {staedte_plot} – Element{s}: {elemente_plot}",
                        fontsize=11)

        ### Speichervorgang ###
        dateiname_plot = gibDateinamen(cfg=cfg)

        # Speicherung ASCII-Datei, in der die geplotteten Werte stehen
        for plotname in ["linker_plot", "rechter_plot"]:
            # Speichere die geplotteten Werte in einer ASCII-Datei
            speicherGeplotteteWerte(
                ascii_datei_terminliste[plotname],
                ascii_datei_spielernamen_punkteverlust[plotname],
                plotname,
                dateiname_plot)
        
        # Setze den Abstand zwischen den Subplots
        plt.subplots_adjust(left=0.08, right=0.97, top=0.76, bottom=0.13)

        # Speicherung Plot
        plt.savefig(dateiname_plot, transparent = False)
        
        # Schließe die Grafik, um Speicher freizugeben
        plt.clf()
        #plt.gcf().clear()
        # Lösche die Achsen und schließe die Grafik
        plt.cla()
        plt.close()
