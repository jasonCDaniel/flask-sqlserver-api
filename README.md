# flask-sqlserver-api

This project is a **Flask-based REST API** designed to manage workflows, steps, and device logging. It provides endpoints for workflow execution, validation, and GPS/device data logging.

All sensitive company-specific details (e.g., IP addresses, database names, usernames/passwords) have been **masked or replaced with placeholders** so this project can be safely shared as part of your GitHub portfolio.

---

## Features

- Retrieve workflows and workflow steps from a SQL Server database.
- Start new jobs and log job step progress.
- Retrieve dropdown list values dynamically from database views.
- Execute stored procedures for workflow actions and conditions.
- Log device GPS location, battery level, Wi-Fi strength, and storage data.
- Configurable logging interval fetched from the database.

---

## Tech Stack

- **Python** (Flask, Flask-CORS)
- **SQL Server** (via pyodbc)
- REST API (JSON-based communication)

---

## Endpoints

### Health Check

- `GET /test` → Test database connection.

### Workflows

- `GET /workflows` → Retrieve list of workflows.
- `POST /workflow/start` → Start a workflow job.
- `GET /workflow/<workflow_id>/step/<step_id>` → Get step details.
- `GET /workflow/<workflow_id>/step/<step_id>/dropdown` → Get dropdown list data.
- `POST /workflow/<workflow_id>/step/<step_id>/actions` → Execute actions procedure.
- `POST /workflow/<workflow_id>/step/<step_id>/conditions` → Execute conditions procedure.
- `POST /workflow/step/log` → Log workflow step details.

### Device Logging

- `POST /log_location` → Log GPS coordinates and device vitals.
- `GET /get_logging_interval` → Retrieve location logging interval.

---

## Database Connection (Placeholder)

Update your connection string in `flaskAPP.py`:

```python
conn = pyodbc.connect(
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=<your_sql_server>;"
    "DATABASE=<your_database>;"
    "UID=<your_username>;"
    "PWD=<your_password>;"
)
```

---

## Getting Started

### 1. Clone Repository

```bash
git clone https://github.com/<your-username>/<your-repo-name>.git
cd <your-repo-name>
```

### 2. Set Up Virtual Environment

```bash
python -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the App

```bash
python flaskAPP.py
```

App runs by default at `http://0.0.0.0:5090`.

---

## Example Request

```bash
curl -X POST http://localhost:5090/workflow/start \
  -H "Content-Type: application/json" \
  -d '{"WorkflowID": 1}'
```

**Response:**

```json
{
  "JOB_ID": 1234
}
```

---

## Roadmap / Future Improvements

- Add authentication and role-based access control.
- Improve error handling and logging.
- Add Docker support for containerized deployment.
- CI/CD integration for automated testing and deployment.

---

## License

This project is open-source under the MIT License.

---

## Notes

- All IP addresses, company names, and credentials have been replaced with placeholders.
- Replace `<your_sql_server>`, `<your_database>`, `<your_username>`, and `<your_password>` with your own values when deploying.
