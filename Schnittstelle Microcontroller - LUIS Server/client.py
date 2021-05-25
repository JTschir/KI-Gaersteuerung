import requests
import time
from datetime import datetime


def get_sensor_value():
    response = requests.get("http://127.0.0.1:5000/sensor/")
    response_json = response.json()
    sensor_value = response_json['value']
    return sensor_value

def set_actor_value(actor_value):
    requests.post("http://127.0.0.1:5000/actor/", json={"actor_value": 15})

if __name__ == '__main__':
    set_actor_value(15.1)
    for i in range(10):
        value = get_sensor_value()
        now = datetime.now()
        print(f"{now} \ncurrent sensor value is {value}\n")
        time.sleep(1)
