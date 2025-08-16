from flask import Flask, jsonify, request
from flask_cors import CORS
import pyodbc

app = Flask(__name__)

CORS(app, resources={r"/*": {"origins": "http://0.0.0.0:5095"}})

# Database connection function
def get_db_connection():
    conn = pyodbc.connect(
        "DRIVER={ODBC Driver 17 for SQL Server};"
        "SERVER=<server_name>;"
        "DATABASE=<database_name>;"
        "UID=<username>;"
        "PWD=<password>;"
    )
    return conn

# Endpoint to get all workflows
@app.route('/workflows', methods=['GET'])
def get_workflows():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT ID, WorkflowName, Description, CreationDate FROM tbl_Workflows WHERE HiddenFlag = 0")
    workflows = cursor.fetchall()
    result = [
        {
            "ID": row[0], 
            "WorkflowName": row[1], 
            "Description": row[2], 
            "CreationDate": row[3].strftime('%Y-%m-%d')
        }
        for row in workflows
    ]
    conn.close()
    return jsonify(result)

# Endpoint to start a new job
@app.route('/workflow/start', methods=['POST'])
def start_workflow():
    try:
        print("Headers:", request.headers)
        print("Body:", request.data)
        # Check Content-Type
        if request.content_type != 'application/json':
            return jsonify({"error": "Content-Type must be application/json"}), 415

        # Extract WorkflowID from the request body
        data = request.get_json()
        if not data:
            return jsonify({"error": "Request body must be JSON"}), 400
        
        workflow_id = data.get('WorkflowID')
        if not workflow_id:
            return jsonify({"error": "WorkflowID is required"}), 400

        # Execute the stored procedure
        conn = get_db_connection()
        cursor = conn.cursor()
        proc_query = """
        EXEC USP_JOB_START @WORKFLOW_ID=?
        """
        cursor.execute(proc_query, (workflow_id,))
        job_id_row = cursor.fetchone()
        conn.commit()
        conn.close()

        # Return the JOB_ID
        if job_id_row:
            return jsonify({"JOB_ID": job_id_row[0]}), 201
        else:
            return jsonify({"error": "Failed to start job"}), 500

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Endpoint to get details for a specific step in a workflow
@app.route('/workflow/<int:workflow_id>/step/<int:step_id>', methods=['GET'])
def get_workflow_step(workflow_id, step_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Fetch the step details for the specific StepID
        cursor.execute(
            """
            SELECT StepID, VariableName, Question, HelpText, InputType, Retrieve, HintText, Actions, Conditions
            FROM tbl_WorkFlowSteps
            WHERE WorkflowID = ? AND StepID = ?
            """,
            (workflow_id, step_id)
        )
        step = cursor.fetchone()
        conn.close()

        # Return the step details if found
        if step:
            result = {
                "StepID": step[0],
                "VariableName": step[1],
                "Question": step[2],
                "HelpText": step[3],
                "InputType": step[4],
                "Retrieve": step[5], 
                "HintText": step[6], 
                "Actions": step[7],  
                "Conditions": step[8]
            }
            return jsonify(result)
        else:
            return jsonify({"error": "Step not found"}), 404
    except Exception as e:
        conn.close()
        return jsonify({"error": str(e)}), 500

### 1. Endpoint to Retrieve Dropdown Data
@app.route('/workflow/<int:workflow_id>/step/<int:step_id>/dropdown', methods=['GET'])
def get_dropdown_data(workflow_id, step_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Retrieve the 'Retrieve' column value for the given step
        cursor.execute(
            "SELECT Retrieve FROM tbl_WorkFlowSteps WHERE WorkflowID = ? AND StepID = ?",
            (workflow_id, step_id)
        )
        row = cursor.fetchone()
        if not row or not row[0]:
            return jsonify({"error": "No dropdown view specified for this step"}), 400

        # Query the dropdown list view
        dropdown_view = row[0]
        cursor.execute(f"SELECT * FROM {dropdown_view}")
        dropdown_data = [row[0] for row in cursor.fetchall()]  # Fetch only the first column
        conn.close()

        return jsonify({"DropdownData": dropdown_data})
    except Exception as e:
        conn.close()
        return jsonify({"error": str(e)}), 500


### 2. Endpoint to Execute Actions Procedure
@app.route('/workflow/<int:workflow_id>/step/<int:step_id>/actions', methods=['POST'])
def execute_actions(workflow_id, step_id):
    data = request.get_json()
    if not data or "JOB_ID" not in data or "UserInput" not in data:
        return jsonify({"error": "Missing JOB_ID or UserInput in the request body"}), 400

    job_id = data["JOB_ID"]
    user_input = data["UserInput"]

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Retrieve the 'Actions' procedure name for the given step
        cursor.execute(
            "SELECT Actions FROM tbl_WorkFlowSteps WHERE WorkflowID = ? AND StepID = ?",
            (workflow_id, step_id)
        )
        row = cursor.fetchone()
        if not row or not row[0]:
            return jsonify({"error": "No actions procedure specified for this step"}), 400

        actions_proc = row[0]

        # Execute the procedure
        cursor.execute(f"EXEC {actions_proc} @JOB_ID = ?, @STEP_ID = ?, @USER_INPUT = ?", job_id, step_id, user_input)
        result = cursor.fetchone()
        # Commit transaction to finalize any insert
        conn.commit()

        if result and result[0].startswith("ERROR:"):
            return jsonify({"error": result[0][6:]}), 400  # Extract and return error message

        return jsonify({"Result": result[0]}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()


### 3. Endpoint to Execute Conditions Procedure
@app.route('/workflow/<int:workflow_id>/step/<int:step_id>/conditions', methods=['POST'])
def execute_conditions(workflow_id, step_id):
    data = request.get_json()
    if not data or "JOB_ID" not in data or "UserInput" not in data or "STEP_ID" not in data:
        return jsonify({"error": "Missing JOB_ID, STEP_ID or UserInput in the request body"}), 400

    job_id = data["JOB_ID"]
    user_input = data["UserInput"]

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Retrieve the 'Conditions' procedure name for the given step
        cursor.execute(
            "SELECT Conditions FROM tbl_WorkFlowSteps WHERE WorkflowID = ? AND StepID = ?",
            (workflow_id, step_id)
        )
        row = cursor.fetchone()
        # Commit transaction to finalize any insert
        # conn.commit()

        if not row or not row[0]:
            return jsonify({"error": "No conditions procedure specified for this step"}), 400

        conditions_proc = row[0]

        # Execute the procedure
        cursor.execute(f"EXEC {conditions_proc} @JOB_ID = ?, @STEP_ID = ?, @USER_INPUT = ?", job_id, step_id, user_input)
        result = cursor.fetchone()

        if result and str(result[0]).startswith("ERROR:"):
            return jsonify({"error": result[0][6:]}), 400  # Extract and return error message

        return jsonify({"Result": result[0]}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()


### This will log all the data relating to the workflow step before going to the next step
@app.route('/workflow/step/log', methods=['POST'])
def log_job_step():
    data = request.get_json()

    # Validate input data
    required_fields = ["JOB_ID", "STEP_ID", "USER_INPUT", "VariableName", "ActionsOutput", "ConditionsOutput"]
    if not all(field in data for field in required_fields):
        return jsonify({"error": "Missing one or more required fields."}), 400

    job_id = data["JOB_ID"]
    step_id = data["STEP_ID"]
    user_input = data["USER_INPUT"]
    variable_name = data["VariableName"]
    actions_output = data["ActionsOutput"]
    conditions_output = data["ConditionsOutput"]

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Execute the stored procedure
        cursor.execute(
            "EXEC dbo.USP_JOB_STEP @JOB_ID = ?, @STEP_ID = ?, @USER_INPUT = ?, @VariableName = ?, @ActionsOutput = ?, @ConditionsOutput = ?",
            job_id, step_id, user_input, variable_name, actions_output, conditions_output
        )
        
        # Fetch the response from the procedure
        response = cursor.fetchone()
        
        # Commit transaction to finalize the insert
        conn.commit()

        if response and response[0].startswith("ERROR:"):
            return jsonify({"error": response[0][6:]}), 400  # Extract and return error message

        return jsonify({"response": response[0]}), 200
    except pyodbc.Error as e:
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()



### Endpoint for testing connection
@app.route('/test', methods=['GET'])
def test_connection():
    try:
        conn = get_db_connection()
        conn.close()
        return jsonify({"status": "success", "message": "Database connection is working."})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})



### Main
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5090, debug=True)


