import os
from flask import Flask, request, jsonify, g
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

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

model = train_model()
init_db()

def extract_text(image_path):
    image = cv2.imread(image_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)
    text = pytesseract.image_to_string(thresh)
    lines = [line.strip() for line in text.split("\n") if line.strip()]
    return lines

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

    lines = extract_text(filepath)
    print("--- OCR Lines ---")
    for i, line in enumerate(lines):
        print(f"{i}: {line}")
    print("--- END OCR Lines ---")
    results = [{"field": model.predict([line])[0], "value": line} for line in lines]
    print("Extraction results:", results)

    return jsonify({"results": results})

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
    conn = sqlite3.connect('forms.db')
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
    conn.close()
    return jsonify({
        'total_overtime': f"{total_overtime_hh:02d}:{total_overtime_mm:02d}",
        'total_job_numbers': total_job_numbers
    })

@app.route('/api/dashboard', methods=['GET'])
def get_dashboard_data():
    conn = sqlite3.connect('forms.db')
    c = conn.cursor()
    # Get all forms
    c.execute('SELECT * FROM exception_forms')
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

    # Most relevant position (using code_description)
    from collections import Counter
    positions = [desc for desc, _, _, _, _ in rows if desc]
    most_position, most_position_count = ('N/A', 0)
    if positions:
        most_position, most_position_count = Counter(positions).most_common(1)[0]

    # Most relevant location
    locations = [loc for _, _, _, _, loc in rows if loc]
    most_location, most_location_count = ('N/A', 0)
    if locations:
        most_location, most_location_count = Counter(locations).most_common(1)[0]

    # Forms table
    c.execute('SELECT id, pass_number, title, employee_name, actual_ot_date, div, comments FROM exception_forms')
    forms_table = [
        {
            "id": row[0],
            "pass_number": row[1],
            "title": row[2],
            "employee_name": row[3],
            "actual_ot_date": row[4],
            "div": row[5],
            "comments": row[6]
        }
        for row in c.fetchall()
    ]

    conn.close()
    return jsonify({
        "total_forms": total_forms,
        "total_overtime": f"{total_overtime_hh}h {total_overtime_mm}m",
        "total_job_numbers": len(job_numbers),
        "unique_job_numbers": len(unique_job_numbers),
        "most_relevant_position": {"position": most_position, "count": most_position_count},
        "most_relevant_location": {"location": most_location, "count": most_location_count},
        "forms": forms_table
    })

@app.route('/api/form/<int:form_id>', methods=['GET'])
def get_form_details(form_id):
    import sqlite3
    conn = sqlite3.connect('forms.db')
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
    conn.close()
    return jsonify({'form': form_data, 'rows': form_rows})

def parse_exception_form(ocr_lines):
    # This is a simplified parser. You may need to adjust regexes for your OCR output.
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
        'entered_in_uts': ''
    }
    rows = []

    # Example: parse header fields
    for line in ocr_lines:
        if "Pass Number" in line:
            form_data['pass_number'] = line.split()[-1]
        elif "Title" in line:
            form_data['title'] = line.split()[-1]
        elif "Employee Name" in line:
            form_data['employee_name'] = line.split(":")[-1].strip()
        # ...repeat for other fields

    # Improved: parse table rows more robustly
    for line in ocr_lines:
        # Skip lines that are too short or don't have enough numbers
        parts = re.split(r'\s+', line.strip())
        if len(parts) < 8:
            continue
        # Try to find a code at the start (2-4 digits or digits+letter)
        if not re.match(r'^[0-9]{2,4}[A-Z]?$', parts[0]):
            continue
        # Try to pad missing columns with empty strings
        while len(parts) < 14:
            parts.append('')
        code = parts[0]
        code_description = exception_codes.get(code, "")
        row = {
            'code': code,
            'code_description': code_description,
            'line_location': parts[1],
            'run_no': parts[2],
            'exception_time_from_hh': parts[3],
            'exception_time_from_mm': parts[4],
            'exception_time_to_hh': parts[5],
            'exception_time_to_mm': parts[6],
            'overtime_hh': parts[7],
            'overtime_mm': parts[8],
            'bonus_hh': parts[9],
            'bonus_mm': parts[10],
            'nite_diff_hh': parts[11],
            'nite_diff_mm': parts[12],
            'ta_job_no': parts[13]
        }
        rows.append(row)
    return form_data, rows

# Example usage after OCR:
ocr_lines = [
    # ...lines from your OCR output...
]
init_exception_form_db()
form_data, rows = parse_exception_form(ocr_lines)
store_exception_form(form_data, rows)

def init_audit_db():
    conn = sqlite3.connect('forms.db')
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
    conn.close()

def log_audit(username, action, target_type, target_id, details=""):
    conn = sqlite3.connect('forms.db')
    c = conn.cursor()
    c.execute('''
        INSERT INTO audit_trail (username, action, target_type, target_id, details)
        VALUES (?, ?, ?, ?, ?)
    ''', (username, action, target_type, target_id, details))
    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_audit_db()
    app.run(port=8000, debug=True)
