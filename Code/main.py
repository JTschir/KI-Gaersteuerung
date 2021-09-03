import numpy as np
import time
import threading
from datetime import datetime

import sql_austausch as db
import communication_for_values as com
from store import ConfigStore
from app import run_server
import control as ctrl


configs = ConfigStore()



def program_thread():
    phase = 1
    flow_sum = 0
    flow_mass_sum = 0
    extract_s = np.array([])
    extract_seeming = 0
    extract_true = 0
    extract_6h_future = 0
    temp = 0
    timestamp_old = 0
    timestamp_old_ml = 0
    fermentation_nr = (db.read("Suddetails", "Max(SudID)"))[0][0]+1         # add 1 to highest value of SudID in DB
    configs.fermentation_nr = fermentation_nr
                    
    #   -----   WAIT FOR USER START -----
    try:
        while True:
            while not configs.run_program:
                time.sleep(0.5)

            # PRE START
            #   ----- VALUES FROM USER INPUT -----
            print("Program started with:")
            tank_vol = configs.tank_vol
            print("tank_vol:", configs.tank_vol)
            wort_vol = configs.wort_vol
            print("wort_vol:", configs.wort_vol)
            sw = configs.sw
            print("sw:", configs.sw)
            delta_goal = configs.delta_goal
            print("delta_goal:", configs.delta_goal)
            set_temperature = configs.set_temperature
            print("set_temperature:", configs.set_temperature)
            set_pressure = configs.set_pressure
            print("set_pressure:", configs.set_pressure)
            db.insert_suddetails(fermentation_nr, configs.sw, configs.tank_vol, configs.wort_vol, configs.delta_goal)
            #   -----   INDIVIDUAL CONSTANTS AT START   -----
            #start_date = datetime.now()
            #start_timestamp = datetime.timestamp(start_date)
            start_timestamp = 1630345314
            specific_weigth = (sw*4/1000)+1                     
            wort_mass = (wort_vol*1000)*specific_weigth                 # [kg],  (notice conversions: m^3 -> liter)
            rest_volume = (tank_vol - wort_vol)                         # [m^3]
            extract_mass_start = (sw * wort_mass) / 100                 # [kg]

            
            com.set_temperature(set_temperature)
            com.set_pressure(set_pressure)
            ################################################################################
            ###                         ITERATE WHILE ACTIVE                             ###
            ################################################################################
            while configs.run_program:
                
                now = datetime.now()
                timestamp = round(datetime.timestamp(now))

                ########################################################################
                ###                 EVERY 30 SECONDS                                 ###
                ########################################################################    
    
                if timestamp >= timestamp_old+30:
                    #   -------------------------------------------
                    #           READ ALL SENSOR VALUES          
                    #   -------------------------------------------
                    
                    duration_days = round((timestamp - start_timestamp)*(1/86400),4)
                    press = com.read_pressure_flow()[0]
                    flow = com.read_pressure_flow()[1]
                    temp = com.read_temperature(temp)
                    db.insert_input(fermentation_nr, timestamp, flow, press, temp)
                    print ("\n\n\nread data"
                           "\nduration[days]:", duration_days,
                           "\nflow [SLPM]:", flow,
                           "\npressure [bar]:", press,
                           "\ntemperature [°C]:", temp)
                    
                    #   -----------------------------------------------------------------
                    #                       CONVERSIONS       
                    #   -----------------------------------------------------------------
                    conversions = ctrl.conversions(flow, flow_sum, press, temp)
                    flow_30s = conversions[1]
                    flow_sum = conversions[2]
                    pressure = conversions[3]
                    temperature = conversions[4]
                     
                    flow_for_calc = flow_30s                      # [SL/30]
                    pressure_for_calc = pressure                  # [bar]
                    temperature_for_calc = temperature            # [°C]
                    
                    #   -----------------------------------------------------------------
                    #                       CALCULATION OF EXTRACT         
                    #   -----------------------------------------------------------------                     
                    calculations = ctrl.calc_extract(pressure_for_calc, temperature_for_calc,
                                                    flow_for_calc, flow_mass_sum,
                                                    wort_vol, rest_volume, extract_mass_start, sw, extract_s)
                    flow_mass_sum = calculations[0]
                    extract_true = np.round(calculations[1],2)
                    extract_s = np.round(calculations[2],2)
                    extract_seeming = np.round(calculations[3],2)
                    extract_delta05 = np.round(calculations[4],2)
                    extract_delta6 = np.round(calculations[5],2)
                    extract_delta24 = np.round(calculations[6],2)
                    
                    ########################################################################
                    ###                 EVERY 30 MINUTES                                 ###
                    ########################################################################
                    if timestamp >= timestamp_old_ml+3600:
                        print("\n\n\nstart ml")
                        #   -------------------------------------------------------------------
                        #                   MODEL 1: CHECK FERMENTATION PHASE
                        #   -------------------------------------------------------------------
                        phase = ctrl.find_phase(duration_days, extract_delta6)
                        if phase == 2:
                            
                            #   -------------------------------------------------------------------
                            #                   CONTROL WITH MODEL 2
                            #   -------------------------------------------------------------------
                            
                            parameters = ctrl.adjust_parameter(delta_goal,
                                                                pressure_for_calc, temperature_for_calc,
                                                                extract_seeming, extract_delta6)
                            set_temperature = parameters[0]
                            set_pressure = parameters[1]
                            extract_6h_future = parameters[2]
                            print("\nml:",
                                  "\nset_temperature:", set_temperature,
                                  "\nset_pressurure:", set_pressure,
                                  "\nextract_seeming_in_6h [bar]:", extract_6h_future,
                                  "\nextract_delta24_in_6h [bar]:", (extract_seeming - extract_6h_future)*4,)
                            db.insert_ml_berechnungen(fermentation_nr, duration_days, phase, extract_6h_future)
                            
                            
                        timestamp_old_ml = timestamp
                    
                    configs.flow_dash = flow_30s*2
                    configs.temperature_dash = temperature
                    configs.pressure_dash = pressure
                    configs.extract_s_dash = extract_seeming
                    configs.extract_delta24_dash = extract_delta6*4
                    configs.set_temperature_dash = set_temperature
                    configs.set_pressure_dash = set_pressure
                    configs.phase_dash = phase

                    db.insert_neue_daten(fermentation_nr, duration_days, flow_30s, flow_sum,
                                pressure, temperature, set_pressure, set_temperature,
                                phase, extract_true, extract_seeming,
                                extract_delta05, extract_delta6, extract_delta24)
                    
                    
                    print ("\n\n\nconverted data \n duration[days]:", duration_days,
                           "\nflow [l/30s]:", flow_30s,
<<<<<<< HEAD
                           "\nflow_sum [l]:", flow_mass_sum,
                           "\nflow mass sum [kg]:", flow_mass_sum,
=======
                           "\nflow_sum [l]:", flow_sum,
>>>>>>> cd53b511999ebe806fa6d7131a15c6fd0c4236f4
                           "\npressure [bar]:", pressure,
                           "\ntemperature [°C]:", temperature,
                           "\nphase:", phase,
                           "\nextract_seeming_now [bar]:", extract_seeming,
                           "\nextract_delta24_now", extract_delta24,
                           "\nset_temperature [°C]:", set_temperature,
                           "\nset_pressure [bar]", set_pressure)

                    timestamp_old = timestamp
                
    
                  
            print("Program stopped")
    except KeyboardInterrupt:
        print("exit")


thread = threading.Thread(target=program_thread)
thread.start()

run_server(configs)