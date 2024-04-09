
# Flask API for Data Management and Monitoring

This Flask application serves as an API for managing and monitoring data from sensor nodes. It provides endpoints for inserting sensor data, fetching latest data, configuring settings, managing alerts, and more.

## Prerequisites

- Python 3.x
- Flask
- Flask-CORS
- Haversine
- MySQL Connector
- Pytz
- Requests

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/RUNG5445/Dashboard.git
   ```

2. Install dependencies:

   ```bash
   pip install flask flask-cors haversine mysql-connector-python pytz requests
   ```

3. Configure MySQL:
   
   Update the `db_config` and `login_config` dictionaries in the code with your MySQL credentials.

4. Run the Flask application:

   ```bash
   python app.py
   ```

## Endpoints

### 1. Insert Data

- **URL:** `/api/data`
- **Method:** `POST`
- **Description:** Inserts sensor data into the database.
- **Parameters:** `nodename`, `temperature`, `humidity`, `latitude`, `longitude`, `speed`, `ebatlvl`, `gbatlvl`.

### 2. Fetch Latest Data

- **URL:** `/api/latest`
- **Method:** `GET`
- **Description:** Fetches the latest recorded sensor data.

### 3. Show Configuration

- **URL:** `/api/showconfig`
- **Method:** `GET`
- **Description:** Fetches and displays the current configuration settings.

### 4. Send Configuration

- **URL:** `/api/sendconfig`
- **Method:** `POST`
- **Description:** Sends new configuration settings.

### 5. Show Data Recorded Today

- **URL:** `/api/show/today`
- **Method:** `GET`
- **Description:** Fetches data recorded today.

### 6. Show All Recorded Data

- **URL:** `/api/show`
- **Method:** `GET`
- **Description:** Fetches all recorded data.

### 7. Activate/Deactivate Node

- **URL:** `/api/activate`
- **Method:** `GET`
- **Description:** Activates or deactivates a specific node.

### 8. Fetch Active Node Names

- **URL:** `/api/node`
- **Method:** `GET`
- **Description:** Fetches active node names.

### 9. Fetch Data Within Custom Date Range

- **URL:** `/api/date`
- **Method:** `POST`
- **Description:** Fetches data within a custom date range.

### 10. Change Alert Conditions

- **URL:** `/api/alert/changecon`
- **Method:** `POST`
- **Description:** Changes alert conditions.

### 11. Fetch Current Alert Conditions

- **URL:** `/api/alert/con`
- **Method:** `GET`
- **Description:** Fetches current alert conditions.

### 12. Add Email Address for Alerts

- **URL:** `/api/addemail`
- **Method:** `POST`
- **Description:** Adds an email address for alerts.

### 13. Delete Email Address for Alerts

- **URL:** `/api/deleteemail`
- **Method:** `POST`
- **Description:** Deletes an email address for alerts.

### 14. Fetch Configured Email Addresses and Delay

- **URL:** `/api/emails`
- **Method:** `GET`
- **Description:** Fetches configured email addresses and delay.

## Authors

- [Rungrueng Janrueng](https://github.com/RUNG5445)

## License

This project is licensed under the [MIT License](LICENSE).
