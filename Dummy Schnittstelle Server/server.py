from flask import Flask, request, jsonify

app = Flask(__name__)


@app.route('/sensor/', methods=['GET'])
def send_from_sensor():
    sensor_data = {
        'value': 10,
    }
    return jsonify(sensor_data)


@app.route('/actor/', methods=['POST'])
def receive_for_actor():
    actor_value = request.json["actor_value"]
    print(f"received new actor value {actor_value}")
    return 'OK'


if __name__ == '__main__':
    app.run(debug=True)
