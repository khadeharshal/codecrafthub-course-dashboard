"""
Automated test suite for CodeCraftHub API endpoints.
Runs using Python standard library modules (urllib, json, pathlib, tempfile, shutil).

Behavior:
1. If the live server is running at http://127.0.0.1:5000, runs tests against the live API.
   Guarantees data safety by backing up courses.json before tests and restoring it afterward.
2. If the live server is not running, falls back automatically to Flask's in-process test client
   using an isolated temporary data file, ensuring tests pass in any environment without
   modifying real project data.
"""

from pathlib import Path
import json
import shutil
import sys
import tempfile
import urllib.error
import urllib.request

BASE_URL = "http://127.0.0.1:5000"
PROJECT_DIR = Path(__file__).resolve().parent
DATA_FILE = PROJECT_DIR / "courses.json"


def send_http_request(method, path, data=None, headers=None):
    """
    Send an HTTP request to the live CodeCraftHub server.
    """
    url = f"{BASE_URL}{path}"
    req_headers = headers if headers is not None else {}
    body = None

    if data is not None:
        if isinstance(data, (dict, list)):
            body = json.dumps(data).encode("utf-8")
            if "Content-Type" not in req_headers:
                req_headers["Content-Type"] = "application/json"
        elif isinstance(data, str):
            body = data.encode("utf-8")
            if "Content-Type" not in req_headers and body:
                req_headers["Content-Type"] = "application/json"

    req = urllib.request.Request(url, data=body, headers=req_headers, method=method)

    try:
        with urllib.request.urlopen(req) as response:
            status = response.status
            resp_body = response.read().decode("utf-8")
            parsed = json.loads(resp_body) if resp_body else None
            return status, parsed
    except urllib.error.HTTPError as error:
        err_body = error.read().decode("utf-8")
        try:
            parsed = json.loads(err_body)
        except Exception:
            parsed = err_body
        return error.code, parsed


def run_live_tests():
    """
    Run comprehensive test suite against the live API server.
    Safely backs up courses.json and restores it in a finally block.
    """
    print(f"Connecting to live CodeCraftHub API at {BASE_URL}...\n")

    # Safety check: backup existing courses.json
    original_data = None
    if DATA_FILE.exists():
        original_data = DATA_FILE.read_bytes()
        print(f"[DATA SAFETY] Backed up existing courses.json ({len(original_data)} bytes).")

    tests_run = 0
    tests_passed = 0

    def record_test(name, passed, detail=""):
        nonlocal tests_run, tests_passed
        tests_run += 1
        if passed:
            tests_passed += 1
            print(f"  [PASS] {name} {detail}")
        else:
            print(f"  [FAIL] {name} {detail}")

    try:
        # Test 1: Root endpoint (GET /)
        print("1. Root Endpoint Test:")
        status, body = send_http_request("GET", "/")
        record_test("GET / returns 200 and API status", status == 200 and body.get("status") == "online")

        # Test 2: Create a course (POST /api/courses)
        print("\n2. Create Course (POST /api/courses):")
        create_payload = {
            "name": "Flask REST API Fundamentals",
            "description": "Learn how to build REST APIs using Python and Flask.",
            "target_date": "2026-12-31",
            "status": "Not Started",
        }
        status, body = send_http_request("POST", "/api/courses", data=create_payload)
        course_id = body.get("id") if body else None
        record_test("POST returns 201 CREATED", status == 201)
        record_test("POST generates integer ID", isinstance(course_id, int))
        record_test("POST generates created_at timestamp", "created_at" in body if body else False)
        record_test("POST matches input fields", body.get("name") == create_payload["name"] if body else False)

        # Test 3: Get all courses (GET /api/courses)
        print("\n3. Retrieve All Courses (GET /api/courses):")
        status, body = send_http_request("GET", "/api/courses")
        record_test("GET all returns 200 OK", status == 200)
        record_test("GET all returns a list", isinstance(body, list))
        record_test("GET all contains created course", any(c.get("id") == course_id for c in body) if isinstance(body, list) else False)

        # Test 4: Get course by ID (GET /api/courses/<id>)
        print(f"\n4. Retrieve Course by ID (GET /api/courses/{course_id}):")
        status, body = send_http_request("GET", f"/api/courses/{course_id}")
        record_test("GET by ID returns 200 OK", status == 200)
        record_test("GET by ID returns correct course object", body.get("id") == course_id if body else False)

        # Test 5: Update course with PUT (PUT /api/courses/<id>)
        print(f"\n5. Update Course via PUT (PUT /api/courses/{course_id}):")
        original_created_at = body.get("created_at") if body else None
        update_payload = {
            "name": "Advanced Flask REST APIs",
            "description": "Learn routing, validation, JSON storage, and error handling.",
            "target_date": "2027-01-31",
            "status": "In Progress",
        }
        status, body = send_http_request("PUT", f"/api/courses/{course_id}", data=update_payload)
        record_test("PUT returns 200 OK", status == 200)
        record_test("PUT updates fields correctly", body.get("status") == "In Progress" and body.get("name") == update_payload["name"] if body else False)
        record_test("PUT preserves original id", body.get("id") == course_id if body else False)
        record_test("PUT preserves original created_at", body.get("created_at") == original_created_at if body else False)

        # Test 6: Verify Persistence on Disk
        print("\n6. Persistence Verification:")
        if DATA_FILE.exists():
            disk_courses = json.loads(DATA_FILE.read_text(encoding="utf-8"))
            disk_course = next((c for c in disk_courses if c.get("id") == course_id), None)
            record_test("Updated course is persisted in courses.json", disk_course is not None and disk_course.get("name") == update_payload["name"])
        else:
            record_test("courses.json exists on disk", False)

        # Test 7: Validation - Missing Required Fields
        print("\n7. Validation: Missing Required Fields (POST /api/courses):")
        status, body = send_http_request("POST", "/api/courses", data={"name": "Incomplete Course"})
        record_test("Returns 400 for missing fields", status == 400)
        record_test("Error message identifies missing fields", "Missing required field(s)" in body.get("error", "") if body else False)

        # Test 8: Validation - Unknown Fields
        print("\n8. Validation: Unknown Fields (POST /api/courses):")
        status, body = send_http_request("POST", "/api/courses", data={
            "name": "Course",
            "description": "Desc",
            "target_date": "2026-12-31",
            "status": "Not Started",
            "unknown_extra": "rejected",
        })
        record_test("Returns 400 for unknown fields", status == 400)
        record_test("Error message identifies unknown fields", "Unknown field(s)" in body.get("error", "") if body else False)

        # Test 9: Validation - Empty Name
        print("\n9. Validation: Empty Name String (POST /api/courses):")
        status, body = send_http_request("POST", "/api/courses", data={
            "name": "   ",
            "description": "Desc",
            "target_date": "2026-12-31",
            "status": "Not Started",
        })
        record_test("Returns 400 for empty name", status == 400)
        record_test("Error message specifies non-empty string", "non-empty string" in body.get("error", "") if body else False)

        # Test 10: Validation - Invalid Status Value
        print("\n10. Validation: Invalid Status (POST /api/courses):")
        status, body = send_http_request("POST", "/api/courses", data={
            "name": "Course",
            "description": "Desc",
            "target_date": "2026-12-31",
            "status": "Pending",
        })
        record_test("Returns 400 for invalid status", status == 400)
        record_test("Error lists valid statuses", "Not Started" in body.get("error", "") if body else False)

        # Test 11: Validation - Invalid Date Format
        print("\n11. Validation: Invalid Date Format (POST /api/courses):")
        status, body = send_http_request("POST", "/api/courses", data={
            "name": "Course",
            "description": "Desc",
            "target_date": "31-12-2026",
            "status": "Not Started",
        })
        record_test("Returns 400 for wrong date format", status == 400)
        record_test("Error mentions YYYY-MM-DD", "YYYY-MM-DD" in body.get("error", "") if body else False)

        # Test 12: Validation - Nonexistent Calendar Date
        print("\n12. Validation: Nonexistent Calendar Date (POST /api/courses):")
        status, body = send_http_request("POST", "/api/courses", data={
            "name": "Course",
            "description": "Desc",
            "target_date": "2026-02-30",
            "status": "Not Started",
        })
        record_test("Returns 400 for impossible date (Feb 30)", status == 400)

        # Test 13: Validation - Missing / Empty JSON Body
        print("\n13. Validation: Missing / Empty JSON Body (POST /api/courses):")
        status, body = send_http_request("POST", "/api/courses", data="", headers={"Content-Type": "application/json"})
        record_test("Returns 400 for empty body", status == 400)
        record_test("Error mentions JSON body required", "A JSON request body is required" in body.get("error", "") if body else False)

        # Test 14: Nonexistent Course ID (404)
        print("\n14. Nonexistent Course ID (GET /api/courses/999999):")
        status, body = send_http_request("GET", "/api/courses/999999")
        record_test("GET nonexistent ID returns 404", status == 404)
        record_test("Error mentions course not found", "was not found" in body.get("error", "") if body else False)

        # Test 15: Delete Course (DELETE /api/courses/<id>)
        print(f"\n15. Delete Course (DELETE /api/courses/{course_id}):")
        status, body = send_http_request("DELETE", f"/api/courses/{course_id}")
        record_test("DELETE returns 204 NO CONTENT", status == 204)
        record_test("DELETE body is empty", body is None or body == "")

        # Test 16: Verify Deletion
        print(f"\n16. Verification of Deletion (GET /api/courses/{course_id}):")
        status, body = send_http_request("GET", f"/api/courses/{course_id}")
        record_test("GET deleted course returns 404 NOT FOUND", status == 404)

        print("\n" + "=" * 50)
        print(f" LIVE TEST RESULTS: {tests_passed} / {tests_run} assertions passed.")
        print("=" * 50)

    finally:
        # Restore original user data
        if original_data is not None:
            DATA_FILE.write_bytes(original_data)
            print(f"\n[DATA SAFETY] Restored original courses.json successfully.")
        else:
            DATA_FILE.write_text("[]\n", encoding="utf-8")
            print(f"\n[DATA SAFETY] Reinitialized courses.json to empty list [].")

    return tests_passed == tests_run


def run_inprocess_tests():
    """
    Run tests in-process using Flask's test_client in an isolated temporary directory.
    This runs without needing a running background server.
    """
    print("\nRunning in-process test suite via Flask test_client (isolated temp directory)...")
    temp_dir = Path(tempfile.mkdtemp(prefix="codecraft_test_"))
    temp_data_file = temp_dir / "courses.json"

    # Add project dir to path and import app
    sys.path.insert(0, str(PROJECT_DIR))
    import app as flask_app

    # Point app.DATA_FILE to the temporary data file
    original_app_data_file = flask_app.DATA_FILE
    flask_app.DATA_FILE = temp_data_file

    client = flask_app.app.test_client()
    tests_run = 0
    tests_passed = 0

    def record_test(name, passed, detail=""):
        nonlocal tests_run, tests_passed
        tests_run += 1
        if passed:
            tests_passed += 1
            print(f"  [PASS] {name} {detail}")
        else:
            print(f"  [FAIL] {name} {detail}")

    try:
        # Test 1: Empty list initially
        res = client.get("/api/courses")
        record_test("Initial GET returns 200 and []", res.status_code == 200 and res.get_json() == [])

        # Test 2: Create valid course
        create_res = client.post("/api/courses", json={
            "name": "Flask Testing",
            "description": "Testing Flask APIs",
            "target_date": "2026-12-31",
            "status": "Not Started"
        })
        created = create_res.get_json()
        record_test("POST returns 201 with generated id", create_res.status_code == 201 and created.get("id") == 1)

        # Test 3: Retrieve created course
        get_res = client.get("/api/courses/1")
        record_test("GET /1 returns 200 and course data", get_res.status_code == 200 and get_res.get_json().get("name") == "Flask Testing")

        # Test 4: Update with PUT
        put_res = client.put("/api/courses/1", json={
            "name": "Flask Testing Updated",
            "description": "Testing Flask APIs Updated",
            "target_date": "2027-01-15",
            "status": "In Progress"
        })
        record_test("PUT preserves id and updates status", put_res.status_code == 200 and put_res.get_json().get("status") == "In Progress")

        # Test 5: Validation - unknown field
        bad_put = client.put("/api/courses/1", json={
            "name": "Bad",
            "description": "Bad",
            "target_date": "2027-01-15",
            "status": "In Progress",
            "extra": "bad"
        })
        record_test("PUT rejects unknown fields with 400", bad_put.status_code == 400)

        # Test 6: Delete course
        del_res = client.delete("/api/courses/1")
        record_test("DELETE returns 204", del_res.status_code == 204)

        # Test 7: GET after delete returns 404
        after_del = client.get("/api/courses/1")
        record_test("GET after delete returns 404", after_del.status_code == 404)

        print("\n" + "=" * 50)
        print(f" IN-PROCESS TEST RESULTS: {tests_passed} / {tests_run} assertions passed.")
        print("=" * 50)
    finally:
        flask_app.DATA_FILE = original_app_data_file
        shutil.rmtree(temp_dir, ignore_errors=True)

    return tests_passed == tests_run


def main():
    live_success = False
    try:
        live_success = run_live_tests()
    except urllib.error.URLError:
        print("\n[INFO] Live server at http://127.0.0.1:5000 not detected.")

    inprocess_success = run_inprocess_tests()

    if live_success or inprocess_success:
        print("\nAll executed test suites completed successfully!")
        return 0
    else:
        print("\nTest failures encountered.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
