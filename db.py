# === db.py ===
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

def init_db():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def add_user(username, password):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    try:
        hashed_pw = generate_password_hash(password, method='pbkdf2:sha256')
        c.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, hashed_pw))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def check_user(username, password):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('SELECT password FROM users WHERE username = ?', (username,))
    row = c.fetchone()
    conn.close()
    if row:
        return check_password_hash(row[0], password)
    return False

import sqlite3

def init_exception_form_db():
    conn = sqlite3.connect('forms.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS exception_forms (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pass_number TEXT,
            title TEXT,
            employee_name TEXT,
            rdos TEXT,
            actual_ot_date TEXT,
            div TEXT,
            comments TEXT,
            supervisor_name TEXT,
            supervisor_pass_no TEXT,
            oto TEXT,
            oto_amount_saved TEXT,
            entered_in_uts TEXT,
            regular_assignment TEXT,
            report TEXT,
            relief TEXT,
            todays_date TEXT,
            status TEXT DEFAULT 'processed',
            reg TEXT,
            superintendent_authorization_signature TEXT,
            superintendent_authorization_pass TEXT,
            superintendent_authorization_date TEXT,
            entered_into_uts TEXT
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS exception_form_rows (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            form_id INTEGER,
            code TEXT,
            code_description TEXT,
            line_location TEXT,
            run_no TEXT,
            exception_time_from_hh TEXT,
            exception_time_from_mm TEXT,
            exception_time_to_hh TEXT,
            exception_time_to_mm TEXT,
            overtime_hh TEXT,
            overtime_mm TEXT,
            bonus_hh TEXT,
            bonus_mm TEXT,
            nite_diff_hh TEXT,
            nite_diff_mm TEXT,
            ta_job_no TEXT,
            FOREIGN KEY(form_id) REFERENCES exception_forms(id)
        )
    ''')
    conn.commit()
    conn.close()

import re
from exception_codes import exception_codes

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

    # Example: parse table rows (very basic, you may need to improve this)
    table_start = False
    for line in ocr_lines:
        if re.match(r'\d{2,4}', line.strip().split()[0]):  # If line starts with a code
            table_start = True
        if table_start:
            parts = line.split()
            if len(parts) >= 10:  # crude check for a table row
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
                    'nite_diff_hh': parts[11] if len(parts) > 11 else '',
                    'nite_diff_mm': parts[12] if len(parts) > 12 else '',
                    'ta_job_no': parts[13] if len(parts) > 13 else ''
                }
                rows.append(row)
    return form_data, rows

# (Removed example usage block that called parse_exception_form and store_exception_form)

def store_exception_form(form_data, rows, username, form_type=None, upload_date=None):
    import sqlite3
    with sqlite3.connect('forms.db', timeout=10) as conn:
        c = conn.cursor()
        # Ensure upload_date and form_type columns exist
        c.execute("""
            CREATE TABLE IF NOT EXISTS exception_forms (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pass_number TEXT,
                title TEXT,
                employee_name TEXT,
                rdos TEXT,
                actual_ot_date TEXT,
                div TEXT,
                comments TEXT,
                supervisor_name TEXT,
                supervisor_pass_no TEXT,
                oto TEXT,
                oto_amount_saved TEXT,
                entered_in_uts TEXT,
                regular_assignment TEXT,
                report TEXT,
                relief TEXT,
                todays_date TEXT,
                status TEXT,
                username TEXT,
                ocr_lines TEXT,
                form_type TEXT,
                upload_date TEXT,
                file_name TEXT,
                reg TEXT,
                superintendent_authorization_signature TEXT,
                superintendent_authorization_pass TEXT,
                superintendent_authorization_date TEXT,
                entered_into_uts TEXT
            )
        """)
        # Insert form with form_type and upload_date
        c.execute('''
            INSERT INTO exception_forms (
                pass_number, title, employee_name, rdos, actual_ot_date, div, comments, supervisor_name, supervisor_pass_no, oto, oto_amount_saved, entered_in_uts, regular_assignment, report, relief, todays_date, status, username, ocr_lines, form_type, upload_date, file_name, reg, superintendent_authorization_signature, superintendent_authorization_pass, superintendent_authorization_date, entered_into_uts
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            form_data.get('pass_number', ''),
            form_data.get('title', ''),
            form_data.get('employee_name', ''),
            form_data.get('rdos', ''),
            form_data.get('actual_ot_date', ''),
            form_data.get('div', ''),
            form_data.get('comments', ''),
            form_data.get('supervisor_name', ''),
            form_data.get('supervisor_pass_no', ''),
            form_data.get('oto', ''),
            form_data.get('oto_amount_saved', ''),
            form_data.get('entered_in_uts', ''),
            form_data.get('regular_assignment', ''),
            form_data.get('report', ''),
            form_data.get('relief', ''),
            form_data.get('todays_date', ''),
            form_data.get('status', 'processed'),
            username,
            str(form_data.get('ocr_lines', '')),
            form_type or '',
            upload_date or '',
            form_data.get('file_name', ''),
            form_data.get('reg', ''),
            form_data.get('superintendent_authorization_signature', ''),
            form_data.get('superintendent_authorization_pass', ''),
            form_data.get('superintendent_authorization_date', ''),
            form_data.get('entered_into_uts', '')
        ))
        form_id = c.lastrowid
        # Insert rows if any
        row_fields = [
            'form_id', 'code', 'code_description', 'line_location', 'run_no',
            'exception_time_from_hh', 'exception_time_from_mm',
            'exception_time_to_hh', 'exception_time_to_mm',
            'overtime_hh', 'overtime_mm', 'bonus_hh', 'bonus_mm',
            'nite_diff_hh', 'nite_diff_mm', 'ta_job_no'
        ]
        for row in rows:
            insert_row_fields = [f for f in row_fields if f == 'form_id' or f in row]
            insert_row_values = [form_id if f == 'form_id' else row.get(f, '') for f in insert_row_fields]
            row_placeholders = ', '.join(['?'] * len(insert_row_fields))
            row_sql = f"INSERT INTO exception_form_rows ({', '.join(insert_row_fields)}) VALUES ({row_placeholders})"
            c.execute(row_sql, insert_row_values)
        conn.commit()
        return form_id

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