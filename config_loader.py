#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import yaml

def _load_yaml_data(filepath='cfg.yml'):
    """Liest die YAML-Konfigurationsdatei und gibt sie als Dictionary zurück."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        raise FileNotFoundError(f"Fehler: Die Konfigurationsdatei '{filepath}' wurde nicht gefunden.")
    except yaml.YAMLError as e:
        raise yaml.YAMLError(f"Fehler beim Parsen der YAML-Datei: {e}")

try:
    # Lade die gesamte Konfiguration aus der YAML-Datei
    _config_data = _load_yaml_data()

    # Gehe durch jede Sektion (z.B. 'database', 'auswertung') in der YAML-Datei
    # und füge alle darin enthaltenen Schlüssel-Wert-Paare als globale Variablen
    # zu diesem Modul hinzu.
    for section_name, section_content in _config_data.items():
        if isinstance(section_content, dict):
            globals().update(section_content)

    # ############################################################################
    # # Erstelle die abgeleiteten Variablen, die in der originalen config.py
    # # dynamisch erzeugt wurden.
    # ############################################################################
    
    # Stelle sicher, dass die Basisvariablen existieren, bevor sie verwendet werden
    if 'stadt_zu_id' in globals():
        id_zu_stadt = {v: k for k, v in stadt_zu_id.items()}
    
    if 'id_zu_kuerzel' in globals():
        kuerzel_zu_id = {v: k for k, v in id_zu_kuerzel.items()}

    if 'mos_namen_starttermine' in globals():
        mos_teilnehmer = list(mos_namen_starttermine.keys())

except Exception as e:
    # Fängt alle potenziellen Fehler beim Laden ab
    print(f"KRITISCHER FEHLER: Die Konfiguration konnte nicht geladen werden. Details: {e}")
    exit()
