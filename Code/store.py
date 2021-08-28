class ConfigStore:
    tank_vol = 0          # Volumen des Gärtanks[m^3]
    wort_vol = 0          # Volumen der Würze[m^3]
    sw = 0                 # Stammwürze [°P]
    delta_goal = 0          # Ziel-Extraktabbau pro 24 Stunden [°P]
    set_temperature = 0     # Solltemperatur für Angärphase [°C]
    set_pressure = 0        # Solldruck für Angärphase [bar]
    run_program = 0     # Process starten


    flow_dash = None
    extract_s_dash = None
    temperature_dash = None        # Temperatur
    pressure_dash = None           # Druck
    phase_dash = None
    extract_delta24_dash = None
    set_temperature_dash = None    # Solltemperatur
    set_pressure_dash = None       # Solldruck



    fermentation_nr = 36