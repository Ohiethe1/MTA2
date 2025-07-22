import os
from flask import Flask, request, jsonify, g, Response
from flask_cors import CORS
from model import train_model
from db import init_db, add_user, check_user
import pytesseract
import cv2
from PIL import Image
import re
from db import init_exception_form_db, store_exception_form
from exception_codes import exception_codes
import sqlite3
import csv
import requests
import google.generativeai as genai

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

model = train_model()
init_db()

# Enable WAL mode for better SQLite concurrency
with sqlite3.connect('forms.db', timeout=10) as conn:
    conn.execute('PRAGMA journal_mode=WAL;')

# Utility: Google Gemini extraction
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    gemini_model = genai.GenerativeModel('gemini-1.5-flash')
else:
    gemini_model = None

def gemini_extract_file_details(file_path, prompt="Extract all relevant details from this document as structured JSON."):
    """
    Uses Google Gemini to extract details from a file (PDF or image).
    Returns Gemini's response text or None if not configured.
    """
    if not gemini_model:
        print("Gemini API key not set. Skipping Gemini extraction.")
        return None
    # Upload file to Gemini
    sample_file = genai.upload_file(path=file_path, display_name=os.path.basename(file_path))
    print(f"Uploaded file '{sample_file.display_name}' as: {sample_file.uri}")
    # Generate content using the uploaded document
    response = gemini_model.generate_content([sample_file, prompt])
    print("Gemini extraction response:", response.text)
    return response.text

# Remove pytesseract, cv2, PIL, and extract_text imports
# Remove extract_text function
# In upload_file, after saving the file, use only Gemini for extraction

# Utility to clean and map Gemini output

def clean_and_map_gemini_output(gemini_output):
    # Remove markdown code block markers and whitespace
    cleaned = re.sub(r"^```json|^```|```$", "", gemini_output.strip(), flags=re.MULTILINE).strip()
    import json
    try:
        data = json.loads(cleaned)
    except Exception as e:
        print("Error parsing cleaned Gemini output:", e)
        return {}, []

    key_map = {
        "Pass Number": "pass_number",
        "Title": "title",
        "Employee Name": "employee_name",
        "RDOS": "rdos",
        "Actual OT Date": "actual_ot_date",
        "DIV": "div",
        "Comments": "comments",
        "Supervisor Name": "supervisor_name",
        "Supervisor Pass No.": "supervisor_pass_no",
        "OTO": "oto",
        "OTO Amount Saved": "oto_amount_saved",
        "Entered in UTS": "entered_in_uts",
        "Regular Assignment": "regular_assignment",
        "Report station": "report",
        "Relief": "relief",
        "Today's Date": "todays_date",
        "Code": "code",
        "Line/Location": "line_location",
        "Run No.": "run_no",
        "Exception Time From HH": "exception_time_from_hh",
        "Exception Time From MM": "exception_time_from_mm",
        "Exception Time To HH": "exception_time_to_hh",
        "Exception Time To MM": "exception_time_to_mm",
        "Overtime HH": "overtime_hh",
        "Overtime MM": "overtime_mm",
        "Bonus HH": "bonus_hh",
        "Bonus MM": "bonus_mm",
        "Nite Diff HH": "nite_diff_hh",
        "Nite Diff MM": "nite_diff_mm",
        "TA Job No.": "ta_job_no"
    }

    # Split into form_data and rows if needed
    form_data = {}
    row = {}
    for k, v in data.items():
        mapped = key_map.get(k, None)
        if mapped:
            if mapped in [
                "code", "line_location", "run_no", "exception_time_from_hh", "exception_time_from_mm",
                "exception_time_to_hh", "exception_time_to_mm", "overtime_hh", "overtime_mm",
                "bonus_hh", "bonus_mm", "nite_diff_hh", "nite_diff_mm", "ta_job_no"
            ]:
                row[mapped] = v
            else:
                form_data[mapped] = v
    rows = [row] if row else []
    return form_data, rows

@app.route("/upload", methods=["POST"])
def upload_file():
    print("Upload route called")
    print("Files received:", request.files)
    if "file" not in request.files:
        print("No file uploaded")
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]
    print(f"Received file: {file.filename}")
    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filepath)

    # Use Gemini to extract details
    gemini_output = gemini_extract_file_details(filepath)
    print("--- Gemini Output ---")
    print(gemini_output)
    print("--- END Gemini Output ---")

    form_data, rows = clean_and_map_gemini_output(gemini_output) if gemini_output else ({}, [])
    # If Gemini output was parsed, fill missing fields with 'N/A'
    if form_data:
        required_form_fields = [
            'pass_number', 'title', 'employee_name', 'rdos', 'actual_ot_date', 'div',
            'comments', 'supervisor_name', 'supervisor_pass_no', 'oto', 'oto_amount_saved',
            'entered_in_uts', 'regular_assignment', 'report', 'relief', 'todays_date', 'status'
        ]
        for key in required_form_fields:
            if key not in form_data:
                form_data[key] = 'N/A'
        # Always set status to 'processed' after upload
        form_data['status'] = 'processed'
        # For each row, fill missing fields with 'N/A'
        required_row_fields = [
            'code', 'code_description', 'line_location', 'run_no',
            'exception_time_from_hh', 'exception_time_from_mm',
            'exception_time_to_hh', 'exception_time_to_mm',
            'overtime_hh', 'overtime_mm', 'bonus_hh', 'bonus_mm',
            'nite_diff_hh', 'nite_diff_mm', 'ta_job_no'
        ]
        for row in rows:
            for key in required_row_fields:
                if key not in row:
                    row[key] = 'N/A'
    else:
        # fallback if Gemini output could not be parsed
        required_form_fields = [
            'pass_number', 'title', 'employee_name', 'rdos', 'actual_ot_date', 'div',
            'comments', 'supervisor_name', 'supervisor_pass_no', 'oto', 'oto_amount_saved',
            'entered_in_uts', 'regular_assignment', 'report', 'relief', 'todays_date', 'status'
        ]
        form_data = {key: '' for key in required_form_fields}
        form_data['comments'] = "Gemini output could not be parsed."
        form_data['status'] = 'processed'
        if not rows:
            rows = []

    # Ensure all required fields in each row
    required_row_fields = [
        'code', 'code_description', 'line_location', 'run_no',
        'exception_time_from_hh', 'exception_time_from_mm',
        'exception_time_to_hh', 'exception_time_to_mm',
        'overtime_hh', 'overtime_mm', 'bonus_hh', 'bonus_mm',
        'nite_diff_hh', 'nite_diff_mm', 'ta_job_no'
    ]
    for row in rows:
        for key in required_row_fields:
            if key not in row:
                row[key] = ''
    rows_fallback = [] # This variable is no longer used for the final rows list

    from db import store_exception_form
    username = request.form.get('username') or request.args.get('username') or request.json.get('username') if request.is_json else None
    if not username:
        username = 'unknown'
    store_exception_form(form_data, rows, username)
    from db import log_audit
    log_audit(username, 'upload', 'form', None, f"Form uploaded: {form_data.get('pass_number', 'N/A')}")

    return jsonify({
        "message": "Upload and save successful!",
        "form": form_data,
        "rows": rows,
        "status": "processed"
    })

# @app.route('/api/register', methods=['POST'])
# def register():
#     data = request.json
#     print("Register data received:", data)
#     if add_user(data['username'], data['password']):
#         print(f"User {data['username']} registered successfully")
#         return jsonify({"message": "User registered successfully"}), 201
#     print(f"User {data['username']} registration failed: already exists")
#     return jsonify({"error": "Username already exists"}), 409

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    print("Login data received:", data)
    if check_user(data['username'], data['password']):
        print("Login successful")
        # Dummy token and user info for now
        token = "dummy-token-123"
        user = {
            "id": data['username'],
            "name": data['username'],  # Replace with real name if available
            "bscId": data['username'],
            "role": "user"
        }
        return jsonify({
            "message": "Login successful!",
            "token": token,
            "user": user
        }), 200
    print("Login failed")
    return jsonify({"error": "Invalid credentials"}), 401

@app.route('/api/stats', methods=['GET'])
def get_stats():
    with sqlite3.connect('forms.db', timeout=10) as conn:
        c = conn.cursor()
        # Sum overtime (convert HH:MM to minutes, then back to HH:MM)
        c.execute('SELECT overtime_hh, overtime_mm FROM exception_form_rows')
        total_minutes = 0
        for hh, mm in c.fetchall():
            try:
                total_minutes += int(hh or 0) * 60 + int(mm or 0)
            except Exception:
                continue
        total_overtime_hh = total_minutes // 60
        total_overtime_mm = total_minutes % 60
        # Count unique TA job numbers (non-empty)
        c.execute('SELECT COUNT(DISTINCT ta_job_no) FROM exception_form_rows WHERE ta_job_no != ""')
        total_job_numbers = c.fetchone()[0]
        conn.commit()
    return jsonify({
        'total_overtime': f"{total_overtime_hh:02d}:{total_overtime_mm:02d}",
        'total_job_numbers': total_job_numbers
    })

@app.route('/api/dashboard', methods=['GET'])
def get_dashboard_data():
    try:
        username = request.args.get('username')
        with sqlite3.connect('forms.db', timeout=10) as conn:
            c = conn.cursor()
            # Count all processed forms
            c.execute('SELECT * FROM exception_forms WHERE status = "processed"')
            forms = c.fetchall()
            total_forms = len(forms)

            # Get all rows for stats
            c.execute('SELECT code_description, overtime_hh, overtime_mm, ta_job_no, line_location FROM exception_form_rows')
            rows = c.fetchall()

            # Overtime
            total_minutes = sum(int(hh or 0) * 60 + int(mm or 0) for _, hh, mm, _, _ in rows)
            total_overtime_hh = total_minutes // 60
            total_overtime_mm = total_minutes % 60

            # Job numbers
            job_numbers = [ta_job_no for _, _, _, ta_job_no, _ in rows if ta_job_no]
            unique_job_numbers = set(job_numbers)

            # Most relevant position (using title)
            c.execute('SELECT title FROM exception_forms WHERE status = "processed"')
            titles = [row[0] for row in c.fetchall() if row[0] and row[0] != 'N/A']
            most_position, most_position_count = ('N/A', 0)
            if titles:
                from collections import Counter
                most_position, most_position_count = Counter(titles).most_common(1)[0]

            # Most relevant location
            locations = [loc for _, _, _, _, loc in rows if loc]
            most_location, most_location_count = ('N/A', 0)
            if locations:
                from collections import Counter
                most_location, most_location_count = Counter(locations).most_common(1)[0]

            # Forms table
            c.execute('SELECT id, pass_number, title, employee_name, actual_ot_date, div, comments, status FROM exception_forms')
            forms_table = [
                {
                    "id": row[0],
                    "pass_number": row[1],
                    "title": row[2],
                    "employee_name": row[3],
                    "actual_ot_date": row[4],
                    "div": row[5],
                    "comments": row[6],
                    "status": row[7]
                }
                for row in c.fetchall()
            ]
            conn.commit()
        return jsonify({
            "total_forms": total_forms,
            "total_overtime": f"{total_overtime_hh}h {total_overtime_mm}m",
            "total_job_numbers": len(job_numbers),
            "unique_job_numbers": len(unique_job_numbers),
            "most_relevant_position": {"position": most_position, "count": most_position_count},
            "most_relevant_location": {"location": most_location, "count": most_location_count},
            "forms": forms_table
        })
    except Exception as e:
        print(f"Error in dashboard: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/form/<int:form_id>', methods=['GET'])
def get_form_details(form_id):
    import sqlite3
    with sqlite3.connect('forms.db', timeout=10) as conn:
        c = conn.cursor()
        # Get form header
        c.execute('SELECT * FROM exception_forms WHERE id = ?', (form_id,))
        form_row = c.fetchone()
        if not form_row:
            conn.close()
            return jsonify({'error': 'Form not found'}), 404
        columns = [desc[0] for desc in c.description]
        form_data = dict(zip(columns, form_row))
        # Get all rows for this form
        c.execute('SELECT * FROM exception_form_rows WHERE form_id = ?', (form_id,))
        rows = c.fetchall()
        row_columns = [desc[0] for desc in c.description]
        form_rows = [dict(zip(row_columns, row)) for row in rows]
        conn.commit()
    return jsonify({'form': form_data, 'rows': form_rows})

@app.route('/api/form/<int:form_id>', methods=['PUT'])
def update_form(form_id):
    import sqlite3
    data = request.json
    form = data.get('form', {})
    rows = data.get('rows', [])
    username = data.get('username', 'unknown')  # For audit logging
    with sqlite3.connect('forms.db', timeout=10) as conn:
        c = conn.cursor()
        # Update form header
        c.execute('''
            UPDATE exception_forms SET
                pass_number = ?,
                title = ?,
                employee_name = ?,
                rdos = ?,
                actual_ot_date = ?,
                div = ?,
                comments = ?,
                supervisor_name = ?,
                supervisor_pass_no = ?,
                oto = ?,
                oto_amount_saved = ?,
                entered_in_uts = ?,
                regular_assignment = ?,
                report = ?,
                relief = ?,
                todays_date = ?,
                status = ?
            WHERE id = ?
        ''', (
            form.get('pass_number', ''),
            form.get('title', ''),
            form.get('employee_name', ''),
            form.get('rdos', ''),
            form.get('actual_ot_date', ''),
            form.get('div', ''),
            form.get('comments', ''),
            form.get('supervisor_name', ''),
            form.get('supervisor_pass_no', ''),
            form.get('oto', ''),
            form.get('oto_amount_saved', ''),
            form.get('entered_in_uts', ''),
            form.get('regular_assignment', ''),
            form.get('report', ''),
            form.get('relief', ''),
            form.get('todays_date', ''),
            form.get('status', ''),
            form_id
        ))
        # Delete old rows
        c.execute('DELETE FROM exception_form_rows WHERE form_id = ?', (form_id,))
        # Insert new rows
        for row in rows:
            c.execute('''
                INSERT INTO exception_form_rows (
                    form_id, code, code_description, line_location, run_no,
                    exception_time_from_hh, exception_time_from_mm,
                    exception_time_to_hh, exception_time_to_mm,
                    overtime_hh, overtime_mm, bonus_hh, bonus_mm,
                    nite_diff_hh, nite_diff_mm, ta_job_no
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                form_id,
                row.get('code', ''),
                row.get('code_description', ''),
                row.get('line_location', ''),
                row.get('run_no', ''),
                row.get('exception_time_from_hh', ''),
                row.get('exception_time_from_mm', ''),
                row.get('exception_time_to_hh', ''),
                row.get('exception_time_to_mm', ''),
                row.get('overtime_hh', ''),
                row.get('overtime_mm', ''),
                row.get('bonus_hh', ''),
                row.get('bonus_mm', ''),
                row.get('nite_diff_hh', ''),
                row.get('nite_diff_mm', ''),
                row.get('ta_job_no', '')
            ))
        conn.commit()
        # Audit log
        c.execute('''
            INSERT INTO audit_trail (username, action, target_type, target_id, details)
            VALUES (?, ?, ?, ?, ?)
        ''', (username, 'edit', 'form', form_id, 'Form and rows edited via API'))
        conn.commit()
    return jsonify({'message': 'Form updated successfully.'})

@app.route('/api/form/<int:form_id>', methods=['DELETE'])
def delete_form(form_id):
    try:
        with sqlite3.connect('forms.db', timeout=10) as conn:
            c = conn.cursor()
            c.execute('DELETE FROM exception_form_rows WHERE form_id = ?', (form_id,))
            c.execute('DELETE FROM exception_forms WHERE id = ?', (form_id,))
            from db import log_audit
            log_audit('system', 'delete', 'form', form_id, "Form deleted via API", conn=conn)
        return jsonify({'message': 'Form deleted successfully.'})
    except Exception as e:
        print(f"Error deleting form {form_id}: {e}")
        return jsonify({'error': str(e)}), 500

def parse_exception_form(ocr_lines):
    import re
    form_data = {
        'pass_number': '',
        'title': '',
        'employee_name': '',
        'rdos': '',
        'actual_ot_date': '',
        'div': '',
        'comments': '',
        'supervisor_name': '',
        'supervisor_pass_no': '',
        'oto': '',
        'oto_amount_saved': '',
        'entered_in_uts': '',
        'regular_assignment': '',
        'report': '',
        'relief': '',
        'todays_date': ''
    }
    rows = []
    # Pass 1: Look for header fields (unchanged)
    for line in ocr_lines:
        today_match = re.search(r"Today.?s Date[\s:]*([\d/]+)", line, re.IGNORECASE)
        if today_match:
            form_data['todays_date'] = today_match.group(1)
        reg_match = re.search(r"Regular Assignment[\s:]*([A-Za-z0-9\- ]+)", line, re.IGNORECASE)
        if reg_match:
            form_data['regular_assignment'] = reg_match.group(1).strip()
        report_match = re.search(r"Report[\s:]*([A-Za-z0-9\- ]+)", line, re.IGNORECASE)
        if report_match:
            form_data['report'] = report_match.group(1).strip()
        relief_match = re.search(r"Relief[\s:]*([A-Za-z0-9\- ]+)", line, re.IGNORECASE)
        if relief_match:
            form_data['relief'] = relief_match.group(1).strip()
        if 'Comments:' in line:
            form_data['comments'] = line.split('Comments:')[-1].strip()
        if 'Supv. Name' in line or 'Supervisor Name' in line:
            name_match = re.search(r"(Supv\. Name|Supervisor Name)[^A-Za-z]*([A-Za-z .]+)", line)
            if name_match:
                form_data['supervisor_name'] = name_match.group(2).strip()
        if 'Pass No.' in line and ('Supv.' in line or 'Supervisor' in line):
            passno_match = re.search(r"Pass No\.?[\s:]*([0-9]+)", line)
            if passno_match:
                form_data['supervisor_pass_no'] = passno_match.group(1)
        if 'OTO' in line and ('YES' in line or 'NO' in line):
            oto_match = re.search(r"OTO.*?(YES|NO)", line)
            if oto_match:
                form_data['oto'] = oto_match.group(1)
        if 'OTO AMOUNT SAVED' in line:
            amt_match = re.search(r"OTO AMOUNT SAVED[^0-9]*([0-9]+)", line)
            if amt_match:
                form_data['oto_amount_saved'] = amt_match.group(1)
        if 'Entered in UTS' in line:
            form_data['entered_in_uts'] = 'YES'
    # Pass 2: Improved extraction for main info line
    for line in ocr_lines:
        parts = line.split()
        # Look for a line that starts with a number and has at least 6 parts
        if len(parts) >= 6 and parts[0].isdigit():
            form_data['pass_number'] = parts[0]
            form_data['title'] = parts[1]
            # Find where the name ends (before rdos/date/div)
            # Assume rdos is the first part that looks like '5/5' or similar
            name_end = 2
            for i in range(2, len(parts)):
                if re.match(r'\d+/\d+', parts[i]):
                    break
                name_end = i + 1
            form_data['employee_name'] = ' '.join(parts[2:name_end])
            # rdos, actual_ot_date, div are the last three parts
            if len(parts) >= 3:
                form_data['rdos'] = parts[-3]
                form_data['actual_ot_date'] = parts[-2]
                form_data['div'] = parts[-1]
    # Pass 3: Table rows (unchanged)
    for line in ocr_lines:
        parts = line.split()
        if len(parts) >= 10 and re.match(r'\d{2,4}', parts[0]):
            row = {
                'code': parts[0],
                'code_description': exception_codes.get(parts[0], ''),
                'line_location': parts[1] if len(parts) > 1 else '',
                'run_no': parts[2] if len(parts) > 2 else '',
                'exception_time_from_hh': parts[3] if len(parts) > 3 else '',
                'exception_time_from_mm': parts[4] if len(parts) > 4 else '',
                'exception_time_to_hh': parts[5] if len(parts) > 5 else '',
                'exception_time_to_mm': parts[6] if len(parts) > 6 else '',
                'overtime_hh': parts[7] if len(parts) > 7 else '',
                'overtime_mm': parts[8] if len(parts) > 8 else '',
                'bonus_hh': parts[9] if len(parts) > 9 else '',
                'bonus_mm': parts[10] if len(parts) > 10 else '',
                'nite_diff_hh': parts[11] if len(parts) > 11 else '',
                'nite_diff_mm': parts[12] if len(parts) > 12 else '',
                'ta_job_no': parts[13] if len(parts) > 13 else ''
            }
            rows.append(row)
    print('--- Parsed Form Data ---')
    print(form_data)
    print('--- Parsed Rows ---')
    print(rows)
    return form_data, rows

# Example usage after OCR:
ocr_lines = [
    # ...lines from your OCR output...
]
init_exception_form_db()
form_data, rows = parse_exception_form(ocr_lines)
store_exception_form(form_data, rows)

def init_audit_db():
    with sqlite3.connect('forms.db', timeout=10) as conn:
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS audit_trail (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT,
                action TEXT,
                target_type TEXT,
                target_id INTEGER,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                details TEXT
            )
        ''')
        conn.commit()

def log_audit(username, action, target_type, target_id, details="", conn=None):
    close_conn = False
    if conn is None:
        conn = sqlite3.connect('forms.db', timeout=10)
        close_conn = True
    c = conn.cursor()
    c.execute('''
        INSERT INTO audit_trail (username, action, target_type, target_id, details)
        VALUES (?, ?, ?, ?, ?)
    ''', (username, action, target_type, target_id, details))
    if close_conn:
        conn.commit()
        conn.close()

@app.route('/api/audit-trail', methods=['GET'])
def get_audit_trail():
    with sqlite3.connect('forms.db', timeout=10) as conn:
        c = conn.cursor()
        c.execute('SELECT id, username, action, target_type, target_id, timestamp, details FROM audit_trail ORDER BY timestamp DESC')
        logs = [
            {
                "id": row[0],
                "user": row[1],
                "action": row[2],
                "target": f"{row[3]}:{row[4]}",
                "timestamp": row[5],
                "details": row[6]
            }
            for row in c.fetchall()
        ]
        conn.commit()
    return jsonify({"logs": logs})

@app.route('/api/forms/export', methods=['GET'])
def export_forms():
    import sqlite3
    with sqlite3.connect('forms.db', timeout=10) as conn:
        c = conn.cursor()
        # Get all columns except 'status'
        c.execute('PRAGMA table_info(exception_forms)')
        all_columns = [row[1] for row in c.fetchall() if row[1] != 'status']
        # Human-friendly headers
        header_map = {
            'id': 'Form ID',
            'pass_number': 'Pass Number',
            'title': 'Title',
            'employee_name': 'Employee Name',
            'rdos': 'RDOS',
            'actual_ot_date': 'Actual OT Date',
            'div': 'DIV',
            'comments': 'Comments',
            'supervisor_name': 'Supervisor Name',
            'supervisor_pass_no': 'Supervisor Pass No.',
            'oto': 'OTO',
            'oto_amount_saved': 'OTO Amount Saved',
            'entered_in_uts': 'Entered in UTS',
            'regular_assignment': 'Regular Assignment',
            'report': 'Report',
            'relief': 'Relief',
            'todays_date': "Today's Date"
        }
        headers = [header_map.get(col, col) for col in all_columns]
        sql = f"SELECT {', '.join(all_columns)} FROM exception_forms"
        c.execute(sql)
        rows = c.fetchall()
        conn.commit()
    def stream():
        yield ','.join(headers) + '\n'
        for row in rows:
            yield ','.join([str(item) if item is not None else '' for item in row]) + '\n'
    return Response(stream(), mimetype='text/csv', headers={
        'Content-Disposition': 'attachment; filename=exception_forms.csv'
    })

if __name__ == "__main__":
    init_audit_db()
    app.run(port=8000, debug=True)
