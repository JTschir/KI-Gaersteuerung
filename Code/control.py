import pickle
import communication_for_values as com
import math
import numpy as np
from sklearn.neural_network import MLPClassifier
from sklearn.neural_network import MLPRegressor


#   -----------------------------------------------------------------
#                       CONVERSIONS OF INOUT DATA       
#   -----------------------------------------------------------------
def conversions(flow, flow_sum, press, temp):
    #   -----   flow    -----
    real_flow = round(flow*0.06, 3)                                 # [SLPM]     conversion because of faulty senor values
    flow_30s = round(real_flow*0.5, 4)                              # [SL/30s]
    flow_sum += flow_30s                                        # [L]
    
    #   -----   pressure    -----
    # average of 5 last values
    pressure = round(press, 2)                                       # [bar]
    
    #   -----   temperature    -----
    # average of 5 last values
    temperature = round(temp, 2)                                      # [°C]
    
    return real_flow, flow_30s, flow_sum, pressure, temperature


#   -----------------------------------------------------------------
#                       CALCULATION OF EXTRACT         
#   -----------------------------------------------------------------

#   -----   CHEMICAL CONSTANTS FOR CALCULATIONS  -----
mol_mass = 44.01                                                        # Molare Masse von CO2 in [g/mol]
henry_const = 0.0338                                                    # Henry-Konstante für CO2 [mol/(l*bar)]
density = 1.98                                                          # density of CO2 at standard conditions

def calc_extract(pressure_for_calc, temperature_for_calc, flow_for_calc, flow_mass_sum,
                 wort_vol, rest_volume, extract_mass_start, sw, extract_s):
    
    pressure_for_calc = pressure_for_calc + 1.01325                 # [bar],    add value of atm-pressure
    temperature_kelvin = temperature_for_calc + 273.15              # [K]

    #   -----   CO2 flow mass   -----
    flow_mass = flow_for_calc * density * 0.001                     # [kg]
    flow_mass_sum += flow_mass                                      # [kg]

    #   -----   CO2 mass in beer    -----
    temp_compensation = math.exp(2400 * ((1/temperature_kelvin) - (1/298.15)))          # for Henry's law
    henry_coefficient = henry_const * temp_compensation                                 # [mol/(l*bar)], Henry coefficient for CO2 
    co2__concentration = henry_coefficient * pressure_for_calc                          # [mol/l], concentration of co2 in liquid
    co2_in_liquid_mass = mol_mass * wort_vol * co2__concentration                       # [kg]

    #   -----   CO2 mass in rest volume -----
    rest_mass = (pressure_for_calc * 100000 * rest_volume) / (188.9 * temperature_kelvin)   # [kg] (notice conversions: bar -> Pa)

    #   -----   total co2 mass till now  -----
    total_co2_mass = flow_mass_sum + co2_in_liquid_mass + rest_mass             # [kg]

    #   -----   extract  -----
    extract_mass_converted = total_co2_mass * 2.1605                            # [kg]
    degree_of_fermentation = extract_mass_converted / extract_mass_start
    extract_true = sw - (degree_of_fermentation * sw)                           # [°P]
    extract_seeming = (extract_true - (0.1808*sw))/0.8192                       # [°P]

    extract_s = np.append(extract_s, extract_seeming)

    #   -----   extract seeming delta   -----
    # 24 hours 
    if len(extract_s) > 17280:
        extract_delta24 = extract_s[-2880] - extract_s[-1]
    else:
        extract_delta24 = 0
    # 6 hours
    if len(extract_s) > 720:
        extract_delta6 = extract_s[-720] - extract_s[-1]
    else:
        extract_delta6 = 0
    # 30 minutes
    if len(extract_s) > 60:
        extract_delta05 = extract_s[-60] - extract_s[-1]
    else:
        extract_delta05 = 0


    return flow_mass_sum, extract_true, extract_s, extract_seeming, extract_delta05, extract_delta6 ,extract_delta24



#   -------------------------------------------------------------
#                   MODEL 1
#   -------------------------------------------------------------

def find_phase(duration_days, extract_delta6):
    
    classification_path = 'models/clf_model.sav'
    
    # input
    X = np.array([duration_days, extract_delta6]).reshape(1, -1)
    # load model
    model_phase = pickle.load(open(classification_path, 'rb'))
    # predict fermentation phase
    phase = model_phase.predict(X)
    
    return phase


#   -----------------------------------------------------------
#                   MODEL 2
#   -----------------------------------------------------------

def adjust_parameter(goal24, set_pressure, set_temperature,
                     extract, delta6):
    
    regression_path = 'models/reg_model.sav'
    done = False
    set_temperature_new = set_temperature
    set_pressure_new = set_pressure
    
    #   -----   load model for regression of fermentation process   -----
    model_extract = pickle.load(open(regression_path, 'rb'))

    while done == False and -2.1 < set_temperature_new-set_temperature < 2.1 and set_pressure_new <=1.1:
        
        #   -----   input   -----
        X = np.array([set_pressure_new, set_temperature_new, extract, delta6]).reshape(1, -1)
        #   -----   predict extract in 6h -----
        extract_6h = model_extract.predict(X)
        
        #   -----   change  set values depending on extract delta   ------ 
        delta6_future = extract_6h - extract
        check_delta = delta6_future*4
        control_parameter = goal24 - check_delta
        if -0.1 <= control_parameter <= 0.1:
            done = True
        elif control_parameter <= -0.4:
            set_temperature_new -= 1
            set_pressure_new += 0.2
        elif control_parameter <= -0.1:
            set_temperature_new -= 0.2
        elif control_parameter >= -0.1:
            set_temperature_new -= 0.2
            set_pressure_new = 0
    
    #   -----   CHECK BORDERS   -----
    if set_pressure <= 1:
        set_pressure = set_pressure_new
    else:
        set_pressure = 1
    
    if 4 <= set_temperature <= 14:
        set_temperature = set_temperature_new
    elif set_temperature <= 4:
        set_temperature = 4
    elif set_temperature >= 14:
        set_temperature = 14
        
    com.set_temperature(set_temperature)
    com.set_pressure(set_pressure)
    return set_temperature, set_pressure, extract_6h