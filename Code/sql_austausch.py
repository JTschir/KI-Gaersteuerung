import sqlite3

###########################################################################################################################
###                                                                                                                     ###
###                                     Funktionen zum Schreiben in KI-Gaersteuerung.db                                 ###
###                                                                                                                     ###
###########################################################################################################################


def insert_suddetails(sud_nr, tank_volumen, wuerze_volumen, SW, ziel_delta):
    
    # ----- 1. Verbindung zur Datenbank herstellen -----
    verbindung = sqlite3.connect("KI-Gaersteuerung.db")
    # ----- 2. Cursor-Objekt -----
    cursor = verbindung.cursor()
    # ----- 3. SQL-Query übergeben -----
    details = (sud_nr, tank_volumen, wuerze_volumen, SW, ziel_delta)
    cursor.execute("""
                   INSERT INTO Suddetails 
                   VALUES (?,?,?,?,?)
                    """, details
                    )   
    # ----- 4. commit: Anweisung ausführen (Beim Auslesen nicht notwendig, weil keine Änderung) -----
    verbindung.commit()
    # ----- 5. Schließen der Datenbankverbindung -----
    verbindung.close()
    
    
def insert_input(sud_nr, timestamp, flow, pressure, temperature):
    
    # ----- 1. Verbindung zur Datenbank herstellen -----
    verbindung = sqlite3.connect("KI-Gaersteuerung.db")
    # ----- 2. Cursor-Objekt -----
    cursor = verbindung.cursor()
    # ----- 3. SQL-Query übergeben -----
    in_val = (sud_nr, timestamp, flow, pressure, temperature)
    cursor.execute("""
                    INSERT INTO Input 
                    VALUES (?,?,?,?,?)
                    """, in_val
                    )   
    # ----- 4. commit: Anweisung ausführen (Beim Auslesen nicht notwendig, weil keine Änderung) -----
    verbindung.commit()
    # ----- 5. Schließen der Datenbankverbindung -----
    verbindung.close()
    
    
def insert_neue_daten(sud_nr, time_days, flow_30s, flow_sum, 
                      pressure, temperature, pressure_set, temperature_set,
                      phase, extraktgehalt_wahr, extraktgehalt_scheinbar,
                      d05, d6, d24):
    
    # ----- 1. Verbindung zur Datenbank herstellen -----
    verbindung = sqlite3.connect("KI-Gaersteuerung.db")
    # ----- 2. Cursor-Objekt -----
    cursor = verbindung.cursor()
    # ----- 3. SQL-Query übergeben -----
    data_neu = (sud_nr, time_days, flow_30s, flow_sum, 
                pressure, temperature, pressure_set, temperature_set, 
                phase, extraktgehalt_wahr, extraktgehalt_scheinbar,
                d05, d6, d24)
        
    cursor.execute("""
                   INSERT INTO Neue_Daten
                   VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)
                   """, data_neu
                   )    
    # ----- 4. commit: Anweisung ausführen (Beim Auslesen nicht notwendig, weil keine Änderung) -----
    verbindung.commit()
    # ----- 5. Schließen der Datenbankverbindung -----
    verbindung.close()
    
    
def insert_ml_berechnungen(sud_nr, time_days, phase, extraktgehalt_6h_s):
    
    # ----- 1. Verbindung zur Datenbank herstellen -----
    verbindung = sqlite3.connect("KI-Gaersteuerung.db")
    # ----- 2. Cursor-Objekt -----
    cursor = verbindung.cursor()
    # ----- 3. SQL-Query übergeben -----
    berechnungen = (sud_nr, time_days, phase, extraktgehalt_6h_s)
    cursor.execute("""
                   INSERT INTO ML_Berechnungen
                   VALUES (?,?,?,?)
                   """, berechnungen
                    )   
    # ----- 4. commit: Anweisung ausführen (Beim Auslesen nicht notwendig, weil keine Änderung) -----
    verbindung.commit()
    # ----- 5. Schließen der Datenbankverbindung -----
    verbindung.close()

###########################################################################################################################
###                                                                                                                     ###
###                                     Funktionen zum Lesen aus KI-Gaersteuerung.db                                    ###
###                                                                                                                     ###
###########################################################################################################################

def read(tabellenname, spaltenname="*", bedingung=None):
    # ----- 1. Verbindung zur Datenbank herstellen -----
    verbindung = sqlite3.connect("KI-Gaersteuerung.db")            
    # ----- 2. Cursor-Objekt -----
    cursor = verbindung.cursor()
    # ----- 3. SQL-Query übergeben -----
    if bedingung != None:
        anweisung = "SELECT " + spaltenname + " FROM " + tabellenname + bedingung 
    else:
        anweisung = "SELECT " + spaltenname + " FROM " + tabellenname
    cursor.execute(anweisung)
    inhalt = cursor.fetchall()
    # ----- 4. Schließen der Datenbankverbindung -----
    verbindung.close()
    
    return inhalt
