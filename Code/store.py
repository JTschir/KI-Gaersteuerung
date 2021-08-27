class ConfigStore:
    tank_vol = 0.2          # Volumen des Gärtanks[m^3]
    wort_vol = 0.1          # Volumen der Würze[m^3]
    sw = 12                 # Stammwürze [°P]
    delta_goal = 2          # Ziel-Extraktabbau pro 24 Stunden [°P]
    set_temperature = 8     # Solltemperatur für Angärphase [°C]
    set_pressure = 0        # Solldruck für Angärphase [bar]
    run_program = False     # Process starten


    flow_dash = None
    extract_s_dash = None
    temperature_dash = None        # Temperatur
    pressure_dash = None           # Druck
    phase_dash = 1.2
    extract_delta24_dash = 2.1
    set_temperature_dash = 8    # Solltemperatur
    set_pressure_dash = 0       # Solldruck



    fermentation_nr = 3