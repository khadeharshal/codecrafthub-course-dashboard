# CodeCraftHub - Learning Management System REST API

CodeCraftHub is a lightweight, personalized learning management system built with Python and Flask. It provides a complete REST API backend for managing learning courses — plus a responsive web dashboard (`index.html`) that connects to the API through a browser. Track courses, manage learning progress, and explore REST API principles without requiring a database setup.

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [Features](#features)
3. [Technologies Used](#technologies-used)
4. [Project Structure](#project-structure)
5. [Prerequisites](#prerequisites)
6. [Installation Instructions](#installation-instructions)
7. [Running the Application](#running-the-application)
8. [API Documentation](#api-documentation)
9. [Request and Response Examples](#request-and-response-examples)
10. [Course Fields and Validation](#course-fields-and-validation)
11. [Important PUT Behavior](#important-put-behavior)
12. [Testing Instructions (Windows PowerShell)](#testing-instructions-windows-powershell)
13. [File Storage and Recovery](#file-storage-and-recovery)
14. [Troubleshooting](#troubleshooting)
15. [Frontend Dashboard](#frontend-dashboard)
16. [Conclusion](#conclusion)

---

## Project Overview

CodeCraftHub provides a simple and educational REST API backend where learners can track their technical learning goals. Designed as a foundational project for RESTful API concepts, it manages course resources using standard HTTP verbs (`GET`, `POST`, `PUT`, `DELETE`) and stores records in a local JSON text file (`courses.json`).

The project intentionally avoids the overhead of database systems and authentication mechanisms, allowing developers to focus on request routing, payload validation, status code semantics, and JSON data persistence.

---

## Features

- **Full CRUD Support**: Create, Read (all or by ID), Update, and Delete courses.
- **Web Dashboard**: A standalone `index.html` dashboard with real-time API status, metric cards, course table, search/filter/sort, add/edit form, toast notifications, and delete confirmation modal.
- **Local JSON File Persistence**: Course records are saved in `courses.json` in the project directory.
- **Safe File Writes**: Write operations use temporary files, buffer flushing, and atomic file replacement (`os.replace`) to prevent file corruption.
- **Automatic Initialization**: Creates `courses.json` with an empty list (`[]`) if the file does not exist when starting the server or reading data.
- **Defensive Request Validation**:
  - Rejects empty bodies and non-JSON content types with HTTP 400.
  - Requires all necessary fields and rejects unexpected unknown fields.
  - Validates that course names are non-empty strings.
  - Enforces `YYYY-MM-DD` formatting and verifies real calendar dates.
  - Limits course status to `"Not Started"`, `"In Progress"`, or `"Completed"`.
- **Standard HTTP Status Codes**:
  - `201 CREATED`: Course created successfully.
  - `200 OK`: Successful retrieval or update.
  - `204 NO CONTENT`: Successful deletion with an empty response body.
  - `400 BAD REQUEST`: Invalid JSON, missing required fields, or validation failures.
  - `404 NOT FOUND`: Requested course ID does not exist.
  - `500 INTERNAL SERVER ERROR`: File system read or write failure.

---

## Technologies Used

- **Python (3.8+)**: Core programming language.
- **Flask (>= 2.0.0)**: Micro web framework for routing, request parsing, and JSON responses.
- **REST API**: Architectural pattern using standard HTTP methods for resource operations.
- **JSON**: Data exchange format for request bodies, responses, and file storage.
- **HTML5 / CSS3 / Vanilla JavaScript**: Frontend dashboard (`index.html`) with no external frameworks.
- **Windows PowerShell / curl.exe**: Command-line tools for executing and testing API endpoints.

---

## Project Structure

```text
CodeCraftHub/
├── app.py              # Main Flask application with API routes, validation, and storage logic
├── index.html          # Frontend dashboard (HTML5 + CSS3 + Vanilla JS) — open with Live Server
├── courses.json        # Local JSON text file storing course records
├── requirements.txt    # Python package dependencies (Flask)
├── test_api.py         # Automated test script verifying API endpoints and validation
└── README.md           # Project documentation and setup guide
```

### File Details
- **`app.py`**: The application entry point. Implements route handlers, data validation routines, and the storage helpers `load_courses()` and `save_courses()`. Also includes CORS headers so the dashboard can communicate with the API from a browser.
- **`index.html`**: Standalone web dashboard. Opens in any browser via VS Code Live Server (port 5500). Communicates with the Flask API at `http://localhost:5000/api/courses`.
- **`courses.json`**: Data storage file storing a JSON array of course objects. Automatically created with `[]` if missing when the application starts or reads courses.
- **`requirements.txt`**: Lists project dependencies (`Flask>=2.0.0`).
- **`test_api.py`**: Helper test script using Python's standard `urllib` library to test all endpoints against the running server.
- **`README.md`**: Complete reference documentation.

---

## Prerequisites

Before setting up the project, make sure Python and pip are installed.

### 1. Check Python Installation
Open PowerShell and run:
```powershell
python --version
```
*Python 3.8 or higher is recommended.*

### 2. Check Pip Installation
```powershell
python -m pip --version
```

---

## Installation Instructions

1. Open Windows PowerShell and navigate to the project directory:
   ```powershell
   cd CodeCraftHub
   ```

2. Install the required dependencies using pip:
   ```powershell
   python -m pip install -r requirements.txt
   ```

*(Optional)* You may create and activate a Python virtual environment before installing:
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

---

## Running the Application

1. Start the Flask application:
   ```powershell
   python app.py
   ```

2. When the application starts, you should see output similar to:
   ```text
    * Serving Flask app 'app'
    * Debug mode: on
    * Running on http://127.0.0.1:5000
   Press CTRL+C to quit
   ```

3. Open your web browser:
   - Visit `http://127.0.0.1:5000` to view API status and available endpoints.
   - Visit `http://127.0.0.1:5000/api/courses` to view the list of courses in JSON format.

---

## API Documentation

### Core Course Endpoints
| HTTP Method | Endpoint | Description | Expected Status |
|---|---|---|---|
| `POST` | `/api/courses` | Create and add a new course | `201 CREATED` |
| `GET` | `/api/courses` | Retrieve all courses as a JSON list | `200 OK` |
| `GET` | `/api/courses/<int:course_id>` | Retrieve a single course by integer ID | `200 OK` or `404 NOT FOUND` |
| `PUT` | `/api/courses/<int:course_id>` | Replace an existing course (all 4 editable fields required) | `200 OK` or `404 NOT FOUND` |
| `DELETE` | `/api/courses/<int:course_id>` | Delete a course by integer ID | `204 NO CONTENT` or `404 NOT FOUND` |

### Utility Endpoint
| HTTP Method | Endpoint | Description | Expected Status |
|---|---|---|---|
| `GET` | `/` | Root endpoint displaying API status and available routes | `200 OK` |

---

## Request and Response Examples

> **Note**: In the examples below, values for `id` and `created_at` are automatically generated by the server; the specific values shown are illustrative.

### 1. Create a Course (`POST /api/courses`)
**Request Body**:
```json
{
  "name": "Flask REST API Fundamentals",
  "description": "Learn how to build REST APIs using Python and Flask.",
  "target_date": "2026-12-31",
  "status": "Not Started"
}
```
**Response Status**: `201 CREATED`  
**Response Body**:
```json
{
  "id": 1,
  "name": "Flask REST API Fundamentals",
  "description": "Learn how to build REST APIs using Python and Flask.",
  "target_date": "2026-12-31",
  "status": "Not Started",
  "created_at": "2026-10-28T18:46:29.391837+00:00"
}
```

---

### 2. Retrieve All Courses (`GET /api/courses`)
**Response Status**: `200 OK`  
**Response Body**:
```json
[
  {
    "id": 1,
    "name": "Flask REST API Fundamentals",
    "description": "Learn how to build REST APIs using Python and Flask.",
    "target_date": "2026-12-31",
    "status": "Not Started",
    "created_at": "2026-10-28T18:46:29.391837+00:00"
  }
]
```

---

### 3. Retrieve One Course (`GET /api/courses/1`)
**Response Status**: `200 OK`  
**Response Body**:
```json
{
  "id": 1,
  "name": "Flask REST API Fundamentals",
  "description": "Learn how to build REST APIs using Python and Flask.",
  "target_date": "2026-12-31",
  "status": "Not Started",
  "created_at": "2026-10-28T18:46:29.391837+00:00"
}
```

---

### 4. Update a Course (`PUT /api/courses/1`)
**Request Body**:
```json
{
  "name": "Advanced Flask REST APIs",
  "description": "Learn routing, validation, JSON storage, and REST API error handling with Flask.",
  "target_date": "2027-01-31",
  "status": "In Progress"
}
```
**Response Status**: `200 OK`  
**Response Body**:
```json
{
  "id": 1,
  "name": "Advanced Flask REST APIs",
  "description": "Learn routing, validation, JSON storage, and REST API error handling with Flask.",
  "target_date": "2027-01-31",
  "status": "In Progress",
  "created_at": "2026-10-28T18:46:29.391837+00:00"
}
```

---

### 5. Delete a Course (`DELETE /api/courses/1`)
**Response Status**: `204 NO CONTENT`  
**Response Body**: *(Empty)*

---

### 6. Error Responses
- **Validation Failure (`400 BAD REQUEST`)**:
  ```json
  {
    "error": "Missing required field(s): status."
  }
  ```
- **Course Not Found (`404 NOT FOUND`)**:
  ```json
  {
    "error": "Course with ID 999999 was not found."
  }
  ```
- **Invalid JSON Body (`400 BAD REQUEST`)**:
  ```json
  {
    "error": "The request body contains invalid JSON."
  }
  ```
- **Missing Request Body (`400 BAD REQUEST`)**:
  ```json
  {
    "error": "A JSON request body is required."
  }
  ```

---

## Course Fields and Validation

Each course in `courses.json` has six fields:

| Field Name | Type | Controlled By | Rules & Validation |
|---|---|---|---|
| `id` | Integer | Server | Auto-generated starting at `1`. Automatically increments based on the highest existing ID to prevent ID reuse. Cannot be supplied or edited by client. |
| `name` | String | Client | Required non-empty string. Whitespace-only strings are rejected. |
| `description` | String | Client | Required string providing details about the course. |
| `target_date` | String | Client | Required string in `YYYY-MM-DD` format. Must be a valid calendar date (e.g., `2026-02-30` is rejected). |
| `status` | String | Client | Required string. Must be exactly `"Not Started"`, `"In Progress"`, or `"Completed"`. |
| `created_at` | String | Server | Auto-generated ISO 8601 UTC timestamp. Preserved across updates. |

---

## Important PUT Behavior

When using `PUT /api/courses/<int:course_id>` to update a course:

1. **All four editable fields are required**: The request body must include `name`, `description`, `target_date`, and `status`. If any field is missing, the request is rejected with `400 BAD REQUEST`.
2. **Server-managed fields are preserved**: The original `id` and `created_at` values cannot be modified and are preserved by the server.
3. **No extra fields allowed**: Attempting to pass `id`, `created_at`, or any unrecognized field in the body returns an `Unknown field(s)` error (`400 BAD REQUEST`).
4. **Immediate persistence**: The updated course is safely saved to disk before `200 OK` is returned.

---

## Testing Instructions (Windows PowerShell)

In Windows PowerShell, standard `curl` is aliased to `Invoke-WebRequest`. To test the REST API correctly, always call **`curl.exe`**.

To prevent JSON quoting issues in PowerShell, construct your JSON payload with `ConvertTo-Json -Compress` and pass the variable to `curl.exe -d`.

### Step 1: Find Existing Course IDs
Before retrieving, updating, or deleting by ID, inspect the current course list to find an existing ID:
```powershell
curl.exe -i http://127.0.0.1:5000/api/courses
```

---

### Step 2: Create a Course (`POST`)
```powershell
$body = @{
    name = "Flask REST API Fundamentals"
    description = "Learn how to build REST APIs using Python and Flask."
    target_date = "2026-12-31"
    status = "Not Started"
} | ConvertTo-Json -Compress

curl.exe -i -X POST http://127.0.0.1:5000/api/courses -H "Content-Type: application/json" -d $body
```
*Expected Status: `HTTP/1.1 201 CREATED`*

---

### Step 3: Get All Courses (`GET`)
```powershell
curl.exe -i http://127.0.0.1:5000/api/courses
```
*Expected Status: `HTTP/1.1 200 OK`*

---

### Step 4: Get a Course by ID (`GET`)
Replace `$courseId` with an ID from your course list:
```powershell
$courseId = 1
curl.exe -i "http://127.0.0.1:5000/api/courses/$courseId"
```
*Expected Status: `HTTP/1.1 200 OK`*

---

### Step 5: Update a Course with PUT
Replace `$courseId` with an existing course ID. Ensure all four editable fields are included:
```powershell
$courseId = 1
$body = @{
    name = "Advanced Flask REST APIs"
    description = "Learn routing, validation, JSON storage, and REST API error handling with Flask."
    target_date = "2027-01-31"
    status = "In Progress"
} | ConvertTo-Json -Compress

curl.exe -i -X PUT "http://127.0.0.1:5000/api/courses/$courseId" -H "Content-Type: application/json" -d $body
```
*Expected Status: `HTTP/1.1 200 OK`*

---

### Step 6: Delete a Course (`DELETE`)
Replace `$courseId` with an existing course ID:
```powershell
$courseId = 1
curl.exe -i -X DELETE "http://127.0.0.1:5000/api/courses/$courseId"
```
*Expected Status: `HTTP/1.1 204 NO CONTENT` (empty response body)*

---

### Step 7: Testing Invalid Requests and Errors

#### A. Missing Required Fields
```powershell
$body = @{
    name = "Python Basics"
    description = "Learn Python"
    target_date = "2026-12-31"
} | ConvertTo-Json -Compress

curl.exe -i -X POST http://127.0.0.1:5000/api/courses -H "Content-Type: application/json" -d $body
```
*Expected Status: `HTTP/1.1 400 BAD REQUEST` (`Missing required field(s): status.`)*

#### B. Invalid Status Value
```powershell
$body = @{
    name = "Databases"
    description = "SQL basics"
    target_date = "2026-12-31"
    status = "Pending"
} | ConvertTo-Json -Compress

curl.exe -i -X POST http://127.0.0.1:5000/api/courses -H "Content-Type: application/json" -d $body
```
*Expected Status: `HTTP/1.1 400 BAD REQUEST` (`The status field must be one of...`)*

#### C. Invalid Date Format
```powershell
$body = @{
    name = "Web Architecture"
    description = "HTTP protocols"
    target_date = "31-12-2026"
    status = "Not Started"
} | ConvertTo-Json -Compress

curl.exe -i -X POST http://127.0.0.1:5000/api/courses -H "Content-Type: application/json" -d $body
```
*Expected Status: `HTTP/1.1 400 BAD REQUEST` (`The target_date field must be a valid date in YYYY-MM-DD format.`)*

#### D. Nonexistent Course ID
```powershell
curl.exe -i http://127.0.0.1:5000/api/courses/999999
```
*Expected Status: `HTTP/1.1 404 NOT FOUND` (`Course with ID 999999 was not found.`)*

#### E. Missing JSON Body
```powershell
curl.exe -i -X POST http://127.0.0.1:5000/api/courses -H "Content-Type: application/json" -d ""
```
*Expected Status: `HTTP/1.1 400 BAD REQUEST` (`A JSON request body is required.`)*

---

### Step 8: Automated Test Script
An automated test script [`test_api.py`](test_api.py) is included in the project. While the server is running, execute in a second terminal:
```powershell
python test_api.py
```
This script exercises all CRUD operations and validation rules end-to-end.

---

## File Storage and Recovery

### Automatic Initialization
- When the application starts (`python app.py`), `initialize_data_file()` checks if `courses.json` exists. If not, it creates it with an empty list (`[]`).
- If `courses.json` is deleted while the server is running, `load_courses()` automatically recreates `courses.json` with `[]` on the next read.

### Safe Recovery from Invalid JSON
If `courses.json` is edited manually with incorrect JSON syntax (for example, missing commas or unclosed brackets), the server raises a `StorageError` and returns `HTTP 500 INTERNAL SERVER ERROR` to protect data from being overwritten blindly.

To recover without losing your existing data:
1. **Make a backup copy** of `courses.json`:
   ```powershell
   Copy-Item courses.json courses_backup.json
   ```
2. Open `courses.json` in VS Code or any text editor and fix the syntax error (ensure it is a valid JSON list of objects).
3. If you want a fresh start and do not need previous course data, reset the file with:
   ```powershell
   Set-Content courses.json "[]"
   ```

---

## Troubleshooting

### 1. `ModuleNotFoundError: No module named 'flask'`
- **Cause**: Flask is not installed in the active Python environment.
- **Solution**: Run `python -m pip install -r requirements.txt`.

### 2. `Address already in use` (Port 5000 Conflict)
- **Cause**: Another process or an existing Flask server instance is occupying port 5000.
- **Solution**: Stop the existing instance by pressing `Ctrl + C` in its terminal, or run Flask on an alternate port:
  ```powershell
  python -m flask --app app run --port 5001
  ```

### 3. `Invoke-WebRequest: Cannot bind parameter 'Headers'`
- **Cause**: Windows PowerShell runs `Invoke-WebRequest` when typing `curl`.
- **Solution**: Explicitly type **`curl.exe`** instead of `curl`.

### 4. `400 BAD REQUEST: The request body contains invalid JSON`
- **Cause**: Double quotes were stripped by the PowerShell command-line parser when passing inline JSON strings.
- **Solution**: Construct the payload using `@ { ... } | ConvertTo-Json -Compress` and pass the variable to `curl.exe -d $body` as demonstrated in the testing instructions.

### 5. `404 NOT FOUND: Course with ID ... was not found`
- **Cause**: The specified ID does not exist in `courses.json` or was deleted.
- **Solution**: Call `curl.exe -i http://127.0.0.1:5000/api/courses` to inspect the available IDs.

---

## Frontend Dashboard

CodeCraftHub includes a fully functional web dashboard (`index.html`) that provides a visual interface for managing courses. It communicates directly with the Flask REST API using the browser's built-in `fetch` API.

### Dashboard Features

- **API Status Indicator**: Live badge in the header showing whether the Flask backend is reachable.
- **Metric Cards**: Real-time summary showing total courses, and counts by status (Not Started, In Progress, Completed).
- **Add / Edit Form**: Form to create new courses or edit existing ones. All four editable fields (`name`, `description`, `target_date`, `status`) are presented with inline validation feedback.
- **Search, Filter, and Sort**: Search by name or description; filter by status; sort by name, target date, or status.
- **Course Table**: Paginated table displaying all courses with color-coded status badges, and Edit / Delete action buttons per row.
- **Delete Confirmation Modal**: Prevents accidental deletions with a confirmation dialog before sending `DELETE`.
- **Toast Notifications**: Non-blocking success and error notifications for all API operations.

### How to Open the Dashboard

The dashboard requires the Flask backend to be running first. Open **two separate terminals**:

**Terminal 1 — Start the Flask API:**
```powershell
cd CodeCraftHub
python app.py
```
*Keep this terminal open. The API runs on `http://127.0.0.1:5000`.*

**Terminal 2 (or VS Code) — Open the Dashboard:**

**Option A — VS Code Live Server (recommended):**
1. Open the `CodeCraftHub` folder in VS Code.
2. Right-click `index.html` in the Explorer panel.
3. Select **"Open with Live Server"**.
4. The dashboard opens automatically in your browser at `http://127.0.0.1:5500/index.html`.

**Option B — Open directly in browser:**
- Double-click `index.html` in File Explorer, or drag it into your browser.
- Note: Some browsers may block `fetch` requests from `file://` URLs due to CORS policy. Use Live Server for reliable results.

### API Base URL Configuration

The dashboard connects to the Flask API using a constant defined near the top of the `<script>` section in `index.html`:

```javascript
const API_BASE_URL = 'http://localhost:5000/api/courses';
```

If your Flask server runs on a different port, update this value accordingly.

### CORS Support

The Flask backend (`app.py`) includes CORS headers on all responses so the dashboard can communicate with the API from a browser running on a different port (e.g., Live Server port 5500):

```
Access-Control-Allow-Origin: *
Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS
Access-Control-Allow-Headers: Content-Type
```

This is handled by the `@app.after_request` hook in `app.py`. No extra Flask extension is required.

### Dashboard Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| API Status badge shows **"Disconnected"** | Flask server is not running | Run `python app.py` in a separate terminal |
| Dashboard shows no courses | `courses.json` is empty or Flask is unreachable | Add a course using the form; verify the server is running |
| `fetch` errors in browser console | CORS blocked (opened via `file://`) | Use VS Code Live Server instead of double-clicking the file |
| Form shows validation error | Missing or invalid field value | Ensure date is `YYYY-MM-DD` and status is one of the three allowed values |

---

## Conclusion

The CodeCraftHub project demonstrates the core foundations of building RESTful services with Python and Flask:

- **Resource-Oriented Architecture**: Natural mapping of CRUD operations to standard HTTP verbs (`GET`, `POST`, `PUT`, `DELETE`).
- **HTTP Status Semantics**: Communicating request outcomes clearly with standard HTTP status codes (`200`, `201`, `204`, `400`, `404`, `500`).
- **Defensive Server-Side Validation**: Ensuring data consistency by checking data types, date formats, and allowed values.
- **Safe Persistence**: Implementing atomic file writes and error handling to ensure data reliability without database complexity.
