# flask-sqlserver-api

This project is a **Flask-based REST API** designed to execute business workflows based on rules stored in SQL Server. 

---

## Features

- Retrieves a list of current business workflows that can be executed.
- Starts a workflow on the db, which returns a JOB_ID of the workflow.
- Once the workflow has been generated, the workflowSteps table can be queried for each step.
- Dropdowns can be retrieved, conditions can be checked and actions can be executed for each specific workflow step.
- Once the workflow step is completed, it is logged, before continuing to the next workflow step id (returned by the conditions procedure linked to the current workflow step).

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

---

## Roadmap / Future Improvements

- Add authentication and role-based access control.
- Improve error handling and logging.
- Add Docker support for containerized deployment.
- CI/CD integration for automated testing and deployment.

---
