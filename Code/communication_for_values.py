
import requests

#   ----------------------------------------------------------------------------------
#                                       TEMPERATURE                            
#   ----------------------------------------------------------------------------------

def set_temperature(settemp):
    targ = "gaertank1"
    newTemp = settemp
    newKp = 300000
    newKi = 500
    newKd = 0
    newWinSize = 100
    newMinTime = 5

    requests.post("http://brewio.uni-hannover.de/brewapi/setpid/",
                  json={"password":"brewio123", "device":targ, "newTemp":newTemp, "newKp":newKp, "newKi":newKi, "newKd":newKd,
                        "newWinSize": newWinSize, "newMinTime": newMinTime})
    
# !!!!!!!!!!!! noch nicht schlön !!!!!!!!!!!!!!!!!
API_KEY = "eyJrIjoiWG8ycW1PUjJteWdsSnVjSm92YVFHcDFSOURuN3NqTUQiLCJuIjoibWxfY29udHJvbCIsImlkIjoxfQ=="
API_ROOT = "http://brewio.uni-hannover.de"
headers = { "Authorization": f"Bearer {API_KEY}" }
sql_query = 'SELECT%20distinct("temperature")%20FROM%20"brew"%20WHERE%20("name"%20%3D%20%27gaertank1%27)%20AND%20time%20>%3D%20now()%20-%201m%20GROUP%20BY%20time(1m)%20fill(null)&epoch=ms'

def read_temperature(temp):
    try:
        result = requests.get(f"{API_ROOT}/api/datasources/proxy/1/query?db=brewio&q={sql_query}", headers=headers).json()
        return result["results"][0]["series"][0]["values"][-1][1]
    except:
        return temp

#   -------------------------------------------------------------------------------------
#                                       PRESSURE & FLOW
#   -------------------------------------------------------------------------------------

def set_pressure(setpressure):
    requests.get("http://130.75.58.189/setpressure?pressure="+str(setpressure))


def read_pressure_flow():
    values = requests.get("http://130.75.58.189/measurement")
    values_dict = values.json()
    # values_dict = json.loads(values_json)
    pressure_dict=values_dict['pressure']
    pressure =pressure_dict['bar']
    if pressure < 0:
        pressure = 0
    airflow_dict = values_dict['airflow']
    airflow = airflow_dict['flow']
    if airflow < 0.005:
        airflow = 0
    return [pressure, airflow]


