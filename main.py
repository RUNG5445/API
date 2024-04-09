from flask import Flask, request, jsonify
from haversine import haversine
from datetime import datetime, date
import mysql.connector, pytz, requests, json, time, re
from flask_cors import CORS
app = Flask(__name__)
CORS(app)
values_list = []
db_config = {
    "user": "xxxxxxxxx",
    "password": "xxxxx",
    "host": "xxxxxxxxxx",
    "database": "xxxxxxxxxxx",
}
login_config = {
    "user": "xxxxxxxx",
    "password": "xxxxxxxxxxxxxx",
    "host": "xxxxxxxxxxx",
    "database": "xxxxxxxxx",
}
def get_db_config(user):
    return {
        "user": "xxxxxx",
        "password": "xxxxxxxxxxx",
        "host": "xxxxxxxxxx",
        "database": user,
    }
def parse_api_time(api_time_str):
    return datetime.strptime(api_time_str, "%a, %d %b %Y %H:%M:%S GMT")
def increment_node(previous_node):
    match = re.match(r"([a-zA-Z]+)(\d+)", previous_node)
    if match:
        non_numeric_part, numeric_part = match.groups()
        incremented_numeric_part = str(int(numeric_part) + 1)
        new_node = non_numeric_part + incremented_numeric_part
        return new_node
    return previous_node
def caldis(coord1, coord2):
    distance_km = haversine(coord1, coord2)
    return distance_km
def check_alert(nodename, temperature, humidity, speed, latitude, longitude, node_battery, gateway_battery):
    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()
        query = "SELECT * FROM Alert"
        cursor.execute(query)
        alert_data = cursor.fetchone()
        if not alert_data:
            return "No alert zone data found."
        alert_message = ""
        subject = f"Alert from {nodename}!! ("
        if len(alert_data) >= 8:
            if temperature > alert_data[0]:
                subject += " Temperature"
                alert_message += f"Temperature is {temperature}, which is above the alert zone of {alert_data[0]}.\n"
            if humidity > alert_data[1]:
                subject += ",Humidity"
                alert_message += f"Humidity is {humidity}, which is above the alert zone of {alert_data[1]}.\n"
            if speed > alert_data[2]:
                subject += ",Speed"
                alert_message += (
                    f"Speed is {speed}, which is above the alert zone of {alert_data[2]}.\n"
                )
            input_coord = (latitude, longitude)
            alert_coord = (
                alert_data[4],
                alert_data[3],
            )
            distance_km = caldis(input_coord, alert_coord)
            if distance_km < alert_data[5]:
                subject += ",Distance"
                alert_message += f"The distance between the points ({distance_km:.2f} kilometers) exceeds the alert radius ({alert_data[5]} kilometers). It is near the destination.\n"
            if len(alert_data) >= 10:
                if node_battery < alert_data[6]:
                    subject += ",Node Battery"
                    alert_message += f"Node Battery is {node_battery}, which is below the alert zone of {alert_data[6]}.\n"
                if gateway_battery < alert_data[7]:
                    subject += ",Gateway Battery"
                    alert_message += f"Gateway Battery is {gateway_battery}, which is below the alert zone of {alert_data[7]}.\n"
        if alert_message:
            subject += ")"
            index = subject.index("(")
            subject = subject[: index + 1] + subject[index + 2:]
            send_email(subject, alert_message)
            return alert_message
        else:
            return "All parameters are within the alert zone."
    except Exception as e:
        return "Error checking alert."
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
def send_email(subject, content):
    api_url = "http://127.0.0.1:5000/api/emails"
    response = requests.get(api_url)
    emails = response.json().get("Emails", []) if response.status_code == 200 else []
    for email in emails:
        payload = {
            "lib_version": "2.6.4",
            "user_id": "xxxxxxxxxxxx",
            "service_id": "xxxxxxxxxxxxxx",
            "template_id": "xxxxxxxxxxxxx",
            "template_params": {
                "to_email": email,
                "Subject": subject,
                "Content": content,
            },
        }
        headers = {
            "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "en-US,en",
            "Content-Type": "application/json",
            "Origin": "http://127.0.0.1:5500",
        }
        url = "https://api.emailjs.com/api/v1.0/email/send"
        send_response = requests.post(
            url, data=json.dumps(payload), headers=headers)
        if send_response.status_code == 200:
            print(f"Email sent successfully to {email}.")
        else:
            print(f"Failed to send email to {email}. Status code:", send_response.status_code)
        time.sleep(1)
# ! API Endpoint 1: Insert Data
@app.route("/api/data", methods=["POST"])
def insert_data():
    user = request.json.get("user")
    if not user:
        return jsonify({"error": "User not provided in query parameters"}), 400
    db_config = get_db_config(user)
    current_time = datetime.now(pytz.timezone("Asia/Bangkok"))
    current_timestamp = datetime.now(pytz.timezone("Asia/Bangkok")).timestamp()
    api_url_latest = "http://127.0.0.1:5000/api/latest?user=" + user
    api_url_delay = "http://127.0.0.1:5000/api/emails?user=" + user
    delay_response = requests.get(api_url_delay)
    if delay_response.status_code != 200:
        return "Failed to fetch delay from API", 500
    datetime_str = "Mon, 21 Feb 2022 15:30:00 UTC"
    delay_data = delay_response.json()
    delay = delay_data.get("Delay", 10)
    response = requests.get(api_url_latest)
    if response.status_code != 200:
        return "Failed to fetch latest data from API", 500
    latest_time_str =""
    latest_data = response.json()
    if latest_data is not None:
        latest_time_str = latest_data.get("Time")
        latest_time_obj = datetime.strptime(latest_time_str, "%a, %d %b %Y %H:%M:%S %Z")
    else:
        latest_time_obj = datetime.strptime(datetime_str, "%a, %d %b %Y %H:%M:%S %Z")
    latest_timestamp = int(latest_time_obj.timestamp()) - 25200
    time_difference = current_timestamp - latest_timestamp
    if request.method == "POST":
        data = request.get_json()
        if all(key in data for key in ("nodename", "temperature", "humidity")):
            nodename = data.get("nodename", "")
            if nodename == "":
                latest_data = fetch_latest_data()
                previousnode = latest_data[1] if latest_data else ""
                nodename = increment_node(previousnode)
            temperature = data.get("temperature", None)
            humidity = data.get("humidity", None)
            latitude = data.get("latitude", None)
            longitude = data.get("longitude", None)
            speed = data.get("speed", None)
            ebatlvl = data.get("ebatlvl", None)
            gbatlvl = data.get("gbatlvl", None)
            if speed is not None and speed < 5:
                speed = 0
            try:
                connection = mysql.connector.connect(**db_config)
                if connection.is_connected():
                    data_to_insert = {
                        "Time": current_time.strftime("%Y-%m-%d %H:%M:%S"),
                        "Nodename": nodename,
                        "Temperature": temperature,
                        "Humidity": humidity,
                        "Latitude": latitude,
                        "Longitude": longitude,
                        "Speed": speed,
                        "ebatlvl": ebatlvl,
                        "gbatlvl": gbatlvl,
                    }
                    cursor = connection.cursor()
                    query = """
                        INSERT INTO Data (Time, Nodename, Temperature, Humidity, Latitude, Longitude, Speed, `Node Battery`, `Gateway Battery`)
                        VALUES (%(Time)s, %(Nodename)s, %(Temperature)s, %(Humidity)s, %(Latitude)s, %(Longitude)s, %(Speed)s, %(ebatlvl)s, %(gbatlvl)s)
                    """
                    cursor.execute(query, data_to_insert)
                    connection.commit()
                    if speed is None:
                        speed = 0
                    if time_difference < delay:
                        check_alert(nodename, temperature, humidity, speed, latitude, longitude, ebatlvl, gbatlvl)
                    return "Data inserted successfully"
            except Exception as e:
                return "Error inserting data into database", 500
            finally:
                if connection.is_connected():
                    connection.close()
        else:
            return "Invalid data", 400
    else:
        return "Only POST requests are supported", 405
# TODO API Endpoint 2: Fetch Latest Data  
@app.route("/api/latest")
def fetch_latest_data():
    try:
        user = request.args.get('user')
        if not user:
            return jsonify({"error": "User not provided in query parameters"}), 400
        db_config = get_db_config(user)
        connection = mysql.connector.connect(**db_config)
        if connection.is_connected():
            cursor = connection.cursor(dictionary=True)
            query = """
            SELECT * FROM Data
            ORDER BY Time DESC
            LIMIT 1
            """
            cursor.execute(query)
            latest_data = cursor.fetchone()
            json_data = jsonify(latest_data)
            return json_data, 200
    except Exception as e:
        error_message = {"error": str(e)}
        return jsonify(error_message), 500
    finally:
        if "connection" in locals() and connection.is_connected():
            connection.close()
# TODO API Endpoint 3: Fetches and displays the current configuration
@app.route("/api/showconfig")
def show_config():
    try:
        user = request.args.get('user')
        if not user:
            return jsonify({"error": "User not provided in query parameters"}), 400
        db_config = get_db_config(user)
        connection = mysql.connector.connect(**db_config)
        if connection.is_connected():
            cursor = connection.cursor(dictionary=True)
            query = """
            SELECT * FROM Configuration
            """
            cursor.execute(query)
            rows = cursor.fetchall()
            return jsonify(rows[0])
    except Exception as e:
        return jsonify({"error": "An error occurred"}), 500
    finally:
        if "connection" in locals() and connection.is_connected():
            connection.close()
# TODO API Endpoint 4: Sends new configuration settings.
@app.route("/api/sendconfig", methods=["POST"])
def send_config():
    try:
        user = request.json.get("user")
        if not user:
            return jsonify({"error": "User not provided in query parameters"}), 400
        db_config = get_db_config(user)
        connection = mysql.connector.connect(**db_config)
        if connection.is_connected():
            syncword = request.json.get("syncword")
            tx_power = request.json.get("txPower")
            freq = request.json.get("freq")
            interval = request.json.get("interval")
            cursor = connection.cursor()
            query = """
                UPDATE Configuration
                SET
                    Syncword = %s,
                    Tx_power = %s,
                    Frequency = %s,
                    Tx_interval = %s
                WHERE id = 1;
            """
            cursor.execute(query, (syncword, tx_power, freq, interval))
            connection.commit()
            return jsonify({"message": "Data inserted successfully"})
    finally:
        if "connection" in locals() and connection.is_connected():
            connection.close()
# TODO API Endpoint 5: Fetches data recorded today.
@app.route("/api/show/today")
def show_values_today():
    try:
        user = request.args.get('user')
        if not user:
            return jsonify({"error": "User not provided in query parameters"}), 400
        db_config = get_db_config(user)
        connection = mysql.connector.connect(**db_config)
        if connection.is_connected():
            cursor = connection.cursor(dictionary=True)
            today = date.today()
            query = """
            SELECT * FROM Data
            WHERE DATE_FORMAT(Time, '%a, %d %b %Y') = %s
            """
            cursor.execute(query, (today.strftime("%a, %d %b %Y"),))
            rows = cursor.fetchall()
            return jsonify(rows)
    except Exception as e:
        return jsonify({"error": "An error occurred"}), 500
    finally:
        if "connection" in locals() and connection.is_connected():
            connection.close()
# TODO API Endpoint 6: Fetches all recorded data.
@app.route("/api/show")
def show_values():
    try:
        user = request.args.get('user')
        if not user:
            return jsonify({"error": "User not provided in query parameters"}), 400
        db_config = get_db_config(user)
        connection = mysql.connector.connect(**db_config)
        if connection.is_connected():
            cursor = connection.cursor(dictionary=True)
            query = """
            SELECT * FROM Data ORDER BY Time DESC LIMIT 160
            """
            cursor.execute(query)
            rows = cursor.fetchall()
            return jsonify(rows)
    except Exception as e:
        return jsonify({"error": "An error occurred"}), 500
    finally:
        if "connection" in locals() and connection.is_connected():
            connection.close()
# TODO API Endpoint 7: Activates or deactivates a specific node.
@app.route("/api/activate", methods=["GET"])
def activate():
    try:
        nodename = request.args.get("nodename")
        user = request.args.get('user')
        if not user:
            return jsonify({"error": "User not provided in query parameters"}), 400
        db_config = get_db_config(user)
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()
        if nodename:
            cursor.execute(
                f"SELECT * FROM Node WHERE nodename = %s", (nodename,))
            node = cursor.fetchone()
            if node:
                new_status = not node[2]
                cursor.execute(
                    f"UPDATE Node SET status = %s WHERE nodename = %s",
                    (new_status, nodename),
                )
                connection.commit()
                return f"{nodename} has been {'activated' if new_status else 'deactivated'}."
            else:
                return f"{nodename} not found."
        else:
            return "Nodename not provided."
    except Exception as e:
        return False
    finally:
        if "connection" in locals() and connection.is_connected():
            connection.close()
# TODO API Endpoint 8: Fetches active node names.
@app.route("/api/node", methods=["GET"])
def node():
    try:
        user = request.args.get('user')
        if not user:
            return jsonify({"error": "User not provided in query parameters"}), 400
        db_config = get_db_config(user)
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()
        query = "SELECT nodename FROM Node WHERE status = 1"
        cursor.execute(query)
        results = cursor.fetchall()
        nodenames = [result[0] for result in results]
        return jsonify({"nodenames": nodenames})
    except Exception as e:
        return "Error fetching true statuses."
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
# TODO API Endpoint 9: Fetches data within a custom date range.
@app.route("/api/date", methods=["POST"])
def fetch_custom_data():
    try:
        user = request.json.get("user")
        if not user:
            return jsonify({"error": "User not provided in query parameters"}), 400
        db_config = get_db_config(user)
        start = request.json.get("start")
        end = request.json.get("end")
        print(f"Received POST data - Start Datetime: {start}, End Datetime: {end}")
        connection = mysql.connector.connect(**db_config)
        if connection.is_connected():
            cursor = connection.cursor(dictionary=True)
            query = f"""
            SELECT * FROM Data
            WHERE Time BETWEEN '{start}' AND '{end}'
            """
            cursor.execute(query)
            data = cursor.fetchall()
            return jsonify(data)
    finally:
        if "connection" in locals() and connection.is_connected():
            connection.close()
# TODO API Endpoint 10: Changes alert conditions.
@app.route("/api/alert/changecon", methods=["POST"])
def change_con():
    try:
        user = request.json.get("user")
        if not user:
            return jsonify({"error": "User not provided in query parameters"}), 400
        db_config = get_db_config(user)
        data = request.json
        temperature = data.get("Temperature")
        humidity = data.get("Humidity")
        speed = data.get("Speed")
        longitude = data.get("Longitude")
        latitude = data.get("Latitude")
        radius = data.get("Radius")
        nbat = data.get("NBattery")
        gbat = data.get("GBattery")
        connection = mysql.connector.connect(**db_config)
        if connection.is_connected():
            cursor = connection.cursor(dictionary=True)
            cursor.execute("DELETE FROM Alert")
            insert_query = "INSERT INTO Alert (Temperature, Humidity, Speed, Longitude, Latitude, Radius,  `Node Battery`, `Gateway Battery`) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
            cursor.execute(insert_query, (temperature, humidity,speed, longitude, latitude, radius, nbat, gbat))
            connection.commit()
            return "Data processed successfully"
    except Exception as e:
        return f"Error processing data: {str(e)}"
    finally:
        if connection and connection.is_connected():
            connection.close()
# TODO API Endpoint 11: Fetches current alert conditions.
@app.route("/api/alert/con", methods=["GET"])
def con():
    try:
        user = request.args.get('user')
        if not user:
            return jsonify({"error": "User not provided in query parameters"}), 400
        db_config = get_db_config(user)
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()
        query = "SELECT * FROM Alert"
        cursor.execute(query)
        results = cursor.fetchall()
        for row in results:
            data = {
                "Temperature": row[0],
                "Humidity": row[1],
                "Speed": row[2],
                "Longitude": row[3],
                "Latitude": row[4],
                "Radius": row[5],
                "Node Battery": row[6],
                "Gateway Battery": row[7],
            }
        return jsonify(data)
    except Exception as e:
        return "Error fetching data."
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
# TODO API Endpoint 12: Adds an email address for alerts.
@app.route("/api/addemail", methods=["POST"])
def insert_email():
    email = request.json.get("email", None)
    delay = request.json.get("delay", None)
    try:
        user = request.json.get("user")
        if not user:
            return jsonify({"error": "User not provided in query parameters"}), 400
        db_config = get_db_config(user)
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()
        query = "SELECT * FROM Email WHERE email = %s"
        cursor.execute(query, (email,))
        existing_email = cursor.fetchone()
        if email == "" and delay is not None:
            update_query = """
                UPDATE Email
                SET Delay = %s
                WHERE id = 1
                            """
            cursor.execute(update_query, (delay,))
            connection.commit()
            return jsonify({"message": "Changed delay."})
        if existing_email:
            return jsonify({"message": "Email already exists."}), 409
        insert_query = "INSERT INTO Email (email, Delay) VALUES (%s, %s)"
        cursor.execute(insert_query, (email, delay))
        connection.commit()
        update_query = """
            UPDATE Email
            SET Delay = %s
            WHERE id = 1
            """
        cursor.execute(update_query, (delay,))
        connection.commit()
        return jsonify({"message": "Email inserted successfully."}), 201
    except Exception as e:
        return jsonify({"message": "Error inserting email."}), 500
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
# TODO API Endpoint 13: Deletes an email address from alerts.
@app.route("/api/deleteemail", methods=["POST"])
def delete_email():
    email = request.json.get("email")
    if not email:
        return jsonify({"message": "Email is required."}), 400
    try:
        user = request.json.get("user")
        if not user:
            return jsonify({"error": "User not provided in query parameters"}), 400
        db_config = get_db_config(user)
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()
        query = "SELECT * FROM Email WHERE email = %s"
        cursor.execute(query, (email,))
        existing_email = cursor.fetchone()
        if not existing_email:
            return jsonify({"message": "Email does not exist."}), 404
        delete_query = "DELETE FROM Email WHERE email = %s"
        cursor.execute(delete_query, (email,))
        connection.commit()
        cursor.execute("SELECT COUNT(*) FROM Email")
        count = cursor.fetchone()[0]
        if count == 1:
            reset_auto_increment_query = "ALTER TABLE Email AUTO_INCREMENT = 2"
            cursor.execute(reset_auto_increment_query)
            connection.commit()
        return jsonify({"message": "Email deleted successfully."}), 200
    except Exception as e:
        return jsonify({"message": "Error deleting email."}), 500
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
# TODO API Endpoint 14: Fetches configured email addresses and delay.
@app.route("/api/emails", methods=["GET"])
def get_emails():
    try:
        user = request.args.get('user')
        if not user:
            return jsonify({"error": "User not provided in query parameters"}), 400
        db_config = get_db_config(user)
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()
        query = "SELECT email, delay FROM Email"
        cursor.execute(query)
        emails = [row[0] for row in cursor.fetchall()]
        query = "SELECT Delay FROM Email WHERE email = %s"
        cursor.execute(query, ("delay",))
        delay = cursor.fetchone()
        response = {"Delay": delay[0], "Emails": emails[1:]}
        return jsonify(response), 200
    except Exception as e:
        return jsonify({"message": "Error fetching emails."}), 500
    finally:
        if connection.is_connected():
