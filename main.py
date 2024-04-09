from flask import Flask, jsonify, request
from flask_cors import CORS
import requests
import json

url = "http://rung.ddns.net:8050"
app = Flask(__name__)
CORS(app)


@app.route("/api/show", methods=["GET"])
def api_show():
    urlshow = url + "/api/show"
    user = request.args.get('user')
    
    try:
        response = requests.get(urlshow,params={'user': user})
        response.raise_for_status()

        data = response.json()

        return jsonify(data)
    except requests.exceptions.RequestException as e:
        print(f"Error making the request: {e}")
        return jsonify({"error": "Failed to get API response"}), 500


@app.route("/api/node", methods=["GET"])
def api_node():
    urlnode = url + "/api/node"
    user = request.args.get('user')
    
    try:
        response = requests.get(urlnode,params={'user': user})
        response.raise_for_status()

        data = response.json()

        return jsonify(data)
    except requests.exceptions.RequestException as e:
        print(f"Error making the request: {e}")
        return jsonify({"error": "Failed to get API response"}), 500


@app.route("/api/show/today", methods=["GET"])
def api_today():
    urlapitoday = url + "/api/show/today"

    user = request.args.get('user')
    try:
        response = requests.get(urlapitoday,params={'user': user})
        response.raise_for_status()

        data = response.json()

        return jsonify(data)
    except requests.exceptions.RequestException as e:
        print(f"Error making the request: {e}")
        return jsonify({"error": "Failed to get API response"}), 500


@app.route("/api/activate", methods=["GET"])
def activate():
    user = request.args.get('user')
    try:
        nodename = request.args.get("nodename")
        urlact = url + "/api/activate?nodename=" + nodename
        response = requests.get(urlact,params={'user': user})
        response.raise_for_status()

        return response.text
    except requests.exceptions.RequestException as e:
        print(f"Error making the request: {e}")
        return jsonify({"error": "Failed to get API response"}), 500


@app.route("/api/date", methods=["POST"])
def fetch_data():
    try:
        urldate = url + "/api/date"
        user = request.json.get("user")
        start = request.json.get("start")
        end = request.json.get("end")
        print(f"Received POST data - Start Datetime: {start}, End Datetime: {end}")
        payload = {"start": start, "end": end,"user":user}

        headers = {"Content-Type": "application/json"}

        response = requests.post(urldate, json=payload, headers=headers)

        data = response.json()
        return jsonify(data)

    except requests.exceptions.RequestException as e:
        print(f"Error making the request: {e}")
        return jsonify({"error": "Failed to get API response"}), 500


@app.route("/api/alert/changecon", methods=["POST"])
def change_con():
    try:
        data = request.json
        user = request.json.get("user")
        print(data)
        urlcon = url + "/api/alert/changecon"
        print(urlcon)
        temperature = data.get("Temperature")
        humidity = data.get("Humidity")
        speed = data.get("Speed")
        longitude = data.get("Longitude")
        latitude = data.get("Latitude")
        radius = data.get("Radius")
        nbat = data.get("NBattery")
        gbat = data.get("GBattery")
        payload = {
            "Temperature": temperature,
            "Humidity": humidity,
            "Speed": speed,
            "Longitude": longitude,
            "Latitude": latitude,
            "Radius": radius,
            "NBattery": nbat,
            "GBattery": gbat,
            "user":user
        }
        print(payload)
        headers = {"Content-Type": "application/json"}

        requests.post(urlcon, json=payload, headers=headers)

        return jsonify(data)

    except requests.exceptions.RequestException as e:
        print(f"Error making the request: {e}")
        return jsonify({"error": "Failed to get API response"}), 500


@app.route("/api/alert/con", methods=["GET"])
def con():
    user = request.args.get('user')
    try:
        urlcon = url + "/api/alert/con"
        response = requests.get(urlcon,params={'user': user})
        response.raise_for_status()

        data = response.json()

        return jsonify(data)
    except requests.exceptions.RequestException as e:
        print(f"Error making the request: {e}")
        return jsonify({"error": "Failed to get API response"}), 500


@app.route("/api/addemail", methods=["POST"])
def insert_email():
    try:
        data = request.json
        print(data)
        urlcon = url + "/api/addemail"
        print(urlcon)
        user = request.json.get("user", None)
        email = request.json.get("email", None)
        delay = request.json.get("delay", None)
        payload = {
            "email": email,
            "delay": delay,
            "user":user
        }
        print(payload)
        headers = {"Content-Type": "application/json"}

        requests.post(urlcon, json=payload, headers=headers)

        return jsonify(data)

    except requests.exceptions.RequestException as e:
        print(f"Error making the request: {e}")
        return jsonify({"error": "Failed to get API response"}), 500


@app.route("/api/deleteemail", methods=["POST"])
def delete_email():
    urldel = url + "/api/deleteemail"
    try:
        user = request.json.get("user")
        email = request.json.get("email")
        payload = {"email": email,"user":user}
        print(payload)
        headers = {"Content-Type": "application/json"}

        response = requests.post(urldel, json=payload, headers=headers)

        data = response.json()
        return jsonify(data)

    except requests.exceptions.RequestException as e:
        print(f"Error making the request: {e}")
        return jsonify({"error": "Failed to get API response"}), 500


@app.route("/api/emails", methods=["GET"])
def get_emails():
    user = request.args.get('user')
    try:
        urlget = url + "/api/emails"
        response = requests.get(urlget,params={'user': user})
        response.raise_for_status()

        data = response.json()

        return jsonify(data)
    except requests.exceptions.RequestException as e:
        print(f"Error making the request: {e}")
        return jsonify({"error": "Failed to get API response"}), 500


@app.route("/api/sendconfig", methods=["POST"])
def sendconfig():
    urldel = url + "/api/sendconfig"
    try:
        payload = {
            "syncword": int(request.json.get("syncword")),
            "txPower": request.json.get("txPower"),
            "freq": request.json.get("freq"),
            "interval": request.json.get("interval"),
            "user": request.json.get("user"),
        }
        print(payload)
        headers = {"Content-Type": "application/json"}

        requests.post(urldel, json=payload, headers=headers)

        return payload

    except requests.exceptions.RequestException as e:
        print(f"Error making the request: {e}")
        return jsonify({"error": "Failed to get API response"}), 500


@app.route("/api/latest", methods=["GET"])
def latest():
    user = request.args.get('user')
    try:
        urllatest = url + "/api/latest"
        response = requests.get(urllatest,params={'user': user})
        response.raise_for_status()

        data = response.json()

        return jsonify(data)
    except requests.exceptions.RequestException as e:
        print(f"Error making the request: {e}")
        return jsonify({"error": "Failed to get API response"}), 500


@app.route("/api/showconfig", methods=["GET"])
def showconfig():
    user = request.args.get('user')
    try:
        urlshowcon = url + "/api/showconfig"
        response = requests.get(urlshowcon,params={'user': user})
        response.raise_for_status()

        data = response.json()

        return jsonify(data)
    except requests.exceptions.RequestException as e:
        print(f"Error making the request: {e}")
        return jsonify({"error": "Failed to get API response"}), 500
    
@app.route('/add_user', methods=['GET'])
def add_user():
    username = request.args.get('username')
    password = request.args.get('password')
    table = request.args.get('table')
    try:
        add_user = url + "/add_user"
        response = requests.get(add_user,params={'username': username,"password":password,"table":table})
        response.raise_for_status()

        data = response.json()

        return jsonify(data)
    except requests.exceptions.RequestException as e:
        print(f"Error making the request: {e}")
        return jsonify({"error": "Failed to get API response"}), 500


@app.route("/login", methods=["POST"])
def login():
    login_url = url + "/login"  # Assuming 'url' is defined somewhere
    try:
        payload = {
            "username": request.json.get("username"),
            "password": request.json.get("password"),
        }
        print(payload)
        headers = {"Content-Type": "application/json"}

        response = requests.post(login_url, json=payload, headers=headers)

        if response.status_code == 200:
            return jsonify(response.json()), 200
        else:  # Specify the condition for the elif statement
            return jsonify(response.json()), 404
        
    except requests.exceptions.RequestException as e:
        print(f"Error making the request: {e}")
        return jsonify({"error": "Failed to get API response"}), 500


@app.route('/api/user', methods=['GET'])
def user():
    try:
        userr = url + "/api/user"
        response = requests.get(userr)
        response.raise_for_status()

        data = response.json()

        print(jsonify(data))

        return jsonify(data)
    
    except requests.exceptions.RequestException as e:
        print(f"Error making the request: {e}")
        return jsonify({"error": "Failed to get API response"}), 500


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
