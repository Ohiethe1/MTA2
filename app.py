import os
from flask import Flask, request, jsonify, g, Response
from flask_cors import CORS
from model import train_model
from db import init_db, add_user, check_user
import re
from db import init_exception_form_db, store_exception_form
from exception_codes import exception_codes
import sqlite3
import csv
import requests
import google.generativeai as genai
import datetime
import pdfplumber
from PIL import Image
import io
import json
from typing import Dict, Any, List, Tuple

# Configuration flag for extraction mode
PURE_GEMINI_EXTRACTION = False  # Set to True to use pure extraction

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

model = train_model()
init_db()
init_exception_form_db()    
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
    sample_file = genai.upload_file(path=file_path, display_name=os.path.basename(file_path))
    print(f"Uploaded file '{sample_file.display_name}' as: {sample_file.uri}")
    response = gemini_model.generate_content([sample_file, prompt])
    print("Gemini extraction response:", response.text)
    return response.text

# Utility to clean and map Gemini output

def clean_and_map_gemini_output(gemini_output, form_type=None):
    cleaned = re.sub(r"^```json|^```|```$", "", gemini_output.strip(), flags=re.MULTILINE).strip()
    import json
    try:
        data = json.loads(cleaned)
        raw_gemini_json = json.dumps(data)  # Store the raw Gemini output
    except Exception as e:
        print("Error parsing cleaned Gemini output:", e)
        return {}, []
    
    # Check if this is a multi-form response (has 'entries' array)
    if isinstance(data, dict) and 'entries' in data and isinstance(data['entries'], list):
        print("Detected multi-form response with entries array")
        forms_data = []
        for i, entry in enumerate(data['entries']):
            print(f"Processing entry {i+1}: {entry}")
            form_data, rows = process_single_form(entry, form_type)
            # Create individual JSON for this form
            individual_json = {
                "form_type": data.get("form_type", "SUPERVISOR'S OVERTIME AUTHORIZATION"),
                "entry": entry
            }
            forms_data.append((form_data, rows, json.dumps(individual_json)))
        return forms_data, raw_gemini_json
    else:
        # Single form response
        print("Processing as single form")
        form_data, rows = process_single_form(data, form_type)
        return [(form_data, rows, raw_gemini_json)], raw_gemini_json

def process_gemini_extraction_hybrid(gemini_output: str, form_type: str = None) -> Tuple[Dict[str, Any], List[Dict[str, Any]], str]:
    """
    Hybrid approach: Store both mapped fields and raw Gemini JSON.
    Can switch between pure extraction and mapped extraction modes.
    """
    cleaned = re.sub(r"^```json|^```|```$", "", gemini_output.strip(), flags=re.MULTILINE).strip()
    
    try:
        raw_data = json.loads(cleaned)
        raw_gemini_json = json.dumps(raw_data, indent=2)
    except Exception as e:
        print("Error parsing cleaned Gemini output:", e)
        return {}, [], ""
    
    if PURE_GEMINI_EXTRACTION:
        # Pure extraction mode - store everything as-is
        return process_pure_extraction(raw_data, form_type, raw_gemini_json)
    else:
        # Mapped extraction mode - use existing logic
        return process_mapped_extraction(raw_data, form_type, raw_gemini_json)

def process_gemini_extraction_dual(gemini_output: str, form_type: str = None) -> Tuple[List[Tuple[Dict[str, Any], List[Dict[str, Any]], str]], str]:
    """
    Process forms in BOTH extraction modes simultaneously.
    Returns both pure and mapped versions of each form.
    """
    cleaned = re.sub(r"^```json|^```|```$", "", gemini_output.strip(), flags=re.MULTILINE).strip()
    
    try:
        raw_data = json.loads(cleaned)
        raw_gemini_json = json.dumps(raw_data, indent=2)
    except Exception as e:
        print("Error parsing cleaned Gemini output:", e)
        return [], ""
    
    all_forms = []
    
    # Process as pure extraction
    pure_forms = process_pure_extraction(raw_data, form_type, raw_gemini_json)
    if isinstance(pure_forms, tuple) and len(pure_forms) == 2:
        # Single form response
        all_forms.extend(pure_forms[0])
    else:
        # Multi-form response
        all_forms.extend(pure_forms)
    
    # Process as mapped extraction
    mapped_forms = process_mapped_extraction(raw_data, form_type, raw_gemini_json)
    if isinstance(mapped_forms, tuple) and len(mapped_forms) == 2:
        # Single form response
        all_forms.extend(mapped_forms[0])
    else:
        # Multi-form response
        all_forms.extend(mapped_forms)
    
    return all_forms, raw_gemini_json

def process_pure_extraction(data: Dict[str, Any], form_type: str, raw_gemini_json: str) -> Tuple[Dict[str, Any], List[Dict[str, Any]], str]:
    """
    Pure Gemini extraction - store everything without mapping.
    """
    # Check if this is a multi-form response
    if isinstance(data, dict) and 'entries' in data and isinstance(data['entries'], list):
        print("Detected multi-form response with entries array")
        forms_data = []
        for i, entry in enumerate(data['entries']):
            print(f"Processing entry {i+1}: {entry}")
            form_data, rows = extract_single_form_pure(entry, form_type)
            individual_json = {
                "form_type": data.get("form_type", "SUPERVISOR'S OVERTIME AUTHORIZATION"),
                "entry": entry
            }
            forms_data.append((form_data, rows, json.dumps(individual_json)))
        return forms_data, raw_gemini_json
    else:
        # Single form response
        print("Processing as single form")
        form_data, rows = extract_single_form_pure(data, form_type)
        return [(form_data, rows, raw_gemini_json)], raw_gemini_json

def extract_single_form_pure(data: Dict[str, Any], form_type: str) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
    """
    Extract a single form using pure Gemini output without field mapping.
    """
    # Store all top-level fields as-is
    form_data = {
        'form_type': form_type,
        'raw_extracted_data': json.dumps(data),  # Store complete raw data
        'extraction_mode': 'pure'
    }
    
    # Extract any obvious fields that we know about for basic functionality
    # but don't enforce strict mapping
    if 'employee_name' in data:
        form_data['employee_name'] = data['employee_name']
    
    # Flexible pass number extraction
    pass_number = get_flexible_field(data, [
        'pass_number', 'pass', 'PASS', 'pass_no', 'pass no', 'passnumber', 'pass number'
    ])
    if pass_number:
        form_data['pass_number'] = pass_number
    
    if 'title' in data:
        form_data['title'] = data['title']
    if 'comments' in data:
        form_data['comments'] = data['comments']
    
    # Handle rows/entries if they exist
    rows = []
    if 'rows' in data and isinstance(data['rows'], list):
        rows = data['rows']
    elif 'entries' in data and isinstance(data['entries'], list):
        rows = data['entries']
    
    return form_data, rows

def process_mapped_extraction(data: Dict[str, Any], form_type: str, raw_gemini_json: str) -> Tuple[Dict[str, Any], List[Dict[str, Any]], str]:
    """
    Use existing mapped extraction logic but also store raw JSON.
    """
    # Use existing logic but ensure raw JSON is stored
    if isinstance(data, dict) and 'entries' in data and isinstance(data['entries'], list):
        print("Detected multi-form response with entries array")
        forms_data = []
        for i, entry in enumerate(data['entries']):
            print(f"Processing entry {i+1}: {entry}")
            form_data, rows = process_single_form(entry, form_type)
            # Add raw JSON to form data
            form_data['raw_extracted_data'] = json.dumps(entry)
            form_data['extraction_mode'] = 'mapped'
            individual_json = {
                "form_type": data.get("form_type", "SUPERVISOR'S OVERTIME AUTHORIZATION"),
                "entry": entry
            }
            forms_data.append((form_data, rows, json.dumps(individual_json)))
        return forms_data, raw_gemini_json
    else:
        # Single form response
        print("Processing as single form")
        form_data, rows = process_single_form(data, form_type)
        # Add raw JSON to form data
        form_data['raw_extracted_data'] = json.dumps(data)
        form_data['extraction_mode'] = 'mapped'
        return [(form_data, rows, raw_gemini_json)], raw_gemini_json

def process_single_form(data, form_type=None):

    # Normalize keys for mapping
    def normalize_key(k):
        # Handle special cases first
        if k == "RC#":
            return "rc"
        if k == "REPORT LOC.":
            return "report_loc"
        if k == "S/M":
            return "sm"
        
        # General normalization
        normalized = k.lower().replace(" ", "_").replace(".", "").replace("#", "").replace("/", "_").replace("'", "").replace("-", "_")
        return normalized

    # Full slot list for supervisor overtime form and exception claim (hourly) form
    all_fields = [
        # Supervisor/Overtime fields
        "reg_assignment", "reg", "pass_number", "title", "rc_number", "employee_name", "report_loc", "date", "rdos", "date_of_overtime",
        "job_number", "overtime_location", "report_time", "relief_time", "overtime_hours",
        "reason_rdo", "reason_absentee_coverage", "reason_no_lunch", "reason_early_report", "reason_late_clear", "reason_save_as_oto", "reason_capital_support_go", "reason_other",
        "acct_number", "amount",
        "superintendent_authorization_signature", "superintendent_authorization_pass", "superintendent_authorization_date", "entered_into_uts",
        # Exception claim (hourly) fields
        "regular_assignment", "report", "relief", "todays_date", "title", "employee_name", "rdos", "actual_ot_date", "div", "pass_number",
        "exception_code", "line_location", "run_no", "exception_time_from_hh", "exception_time_from_mm", "exception_time_to_hh", "exception_time_to_mm",
        "overtime_hh", "overtime_mm", "ta_job_no", "comments", "oto", "oto_amount_saved_hh", "oto_amount_saved_mm", "entered_in_uts_yes", "entered_in_uts_no", "supervisor_name", "supervisor_pass_no"
    ]
    # Map normalized Gemini keys to our slots
    key_map = {
        # Supervisor/Overtime fields (expanded variants for all possible Gemini outputs)
        "reg": "reg",
        "reg.": "reg",
        "reg_assignment": "regular_assignment",
        "assignment": "pass_number",
        "pass": "pass_number",
        "PASS": "pass_number",  # Direct mapping for original key
        "rc": "rc_number",
        "rc.": "rc_number",
        "rc#": "rc_number",
        "rc_#": "rc_number",
        "rc number": "rc_number",
        "rc ": "rc_number",  # Handle RC with space
        "RC#": "rc_number",  # Direct mapping for original key
        "employee_name": "employee_name",
        "employee name": "employee_name",
        "EMPLOYEE NAME": "employee_name",  # Direct mapping for original key
        "job": "job_number",
        "job.": "job_number",
        "job#": "job_number",
        "job_#": "job_number",
        "job number": "job_number",
        "JOB #": "job_number",  # Direct mapping for original key
        "overtime_location": "overtime_location",
        "overtime location": "overtime_location",
        "OVERTIME LOCATION": "overtime_location",  # Direct mapping for original key
        "report_loc": "report_loc",
        "report_loc.": "report_loc",
        "report_loc..": "report_loc",  # Handle double periods
        "report location": "report_loc",
        "REPORT LOC.": "report_loc",  # Direct mapping for original key
        "report_time": "report_time",
        "report time": "report_time",
        "REPORT TIME": "report_time",  # Direct mapping for original key
        "relief_time": "relief_time",
        "relief time": "relief_time",
        "RELIEF TIME": "relief_time",  # Direct mapping for original key
        "overtime_hours": "overtime_hours",
        "overtime hours": "overtime_hours",
        "OVERTIME HOURS": "overtime_hours",  # Direct mapping for original key
        "date": "todays_date",
        "date_of_overtime": "date_of_overtime",
        "date of overtime": "date_of_overtime",
        "rdo's": "rdos",
        "rdos": "rdos",
        "sm": "rdos",  # Handle S/M field
        "S/M": "rdos",  # Direct mapping for original key
        "reason_for_overtime": "reason_for_overtime",
        "reason for overtime": "reason_for_overtime",
        "REASON FOR OVERTIME": "reason_for_overtime",  # Direct mapping for original key
        "comments": "comments",
        "COMMENTS": "comments",  # Direct mapping for original key
        "acct": "acct_number",
        "acct.": "acct_number",
        "acct#": "acct_number",
        "acct_#": "acct_number",
        "acct number": "acct_number",
        "ACCT #": "acct_number",  # Direct mapping for original key
        "amount": "amount",
        "supervisors_signature": "superintendent_authorization_signature",
        "supervisor's_signature": "superintendent_authorization_signature",
        "superintendent_authorization_signature": "superintendent_authorization_signature",
        "superintendent's_authorization_-_signature": "superintendent_authorization_signature",
        "superintendent_authorization_pass": "superintendent_authorization_pass",
        "superintendent's_authorization_-_pass": "superintendent_authorization_pass",
        "superintendent_authorization_date": "superintendent_authorization_date",
        "superintendent's_authorization_-_date": "superintendent_authorization_date",
        "entered_into_uts": "entered_into_uts",
        # Additional mappings for specific Gemini output formats
        "reg_assignment": "regular_assignment",
        "report_loc": "report_loc",
        "report loc": "report_loc",
        "report location": "report_loc",
        "overtime_location": "overtime_location",
        "overtime location": "overtime_location",
        "report_time": "report_time",
        "report time": "report_time",
        "relief_time": "relief_time",
        "relief time": "relief_time",
        "overtime_hours": "overtime_hours",
        "overtime hours": "overtime_hours",
        "rdo's": "rdos",
        "rdos": "rdos",
        "reason_for_overtime": "reason_for_overtime",
        "reason for overtime": "reason_for_overtime",
        "acct": "acct_number",
        "acct#": "acct_number",
        "acct number": "acct_number",
        "superintendent's_authorization": "superintendent_authorization",
        # Exception claim (hourly) fields
        "regular_assignment": "regular_assignment",
        "report": "report",
        "relief": "relief",
        "todays_date": "todays_date",
        "today's_date": "todays_date",
        "pass_number": "pass_number",
        "title": "title",
        "TITLE": "title",  # Direct mapping for original key
        "employee_name": "employee_name",
        "rdos": "rdos",
        "actual_ot_date": "actual_ot_date",
        "div": "div",
        "code": "exception_code",
        "line_location": "line_location",
        "run_no": "run_no",
        "exception_time_from_hh": "exception_time_from_hh",
        "exception_time_from_mm": "exception_time_from_mm",
        "exception_time_to_hh": "exception_time_to_hh",
        "exception_time_to_mm": "exception_time_to_mm",
        "overtime_hh": "overtime_hh",
        "overtime_mm": "overtime_mm",
        "ta_job_no": "ta_job_no",
        "comments": "comments",
        "oto": "oto",
        "oto_amount_saved_hh": "oto_amount_saved_hh",
        "oto_amount_saved_mm": "oto_amount_saved_mm",
        "entered_in_uts_yes": "entered_in_uts_yes",
        "entered_in_uts_no": "entered_in_uts_no",
        "supv_name": "supervisor_name",
        "supervisor_name": "supervisor_name",
        "pass_no": "supervisor_pass_no",
        "supervisor_pass_no": "supervisor_pass_no",
        "job_": "job_number",
        "rc_": "rc_number",
        "acct_": "acct_number",
        "report_time": "report_time",
        "relief_time": "relief_time",
        "overtime_hours": "overtime_hours",
        "superintendent_s_authorization___pass": "superintendent_authorization_pass",
        "superintendent_s_authorization___date": "superintendent_authorization_date",
        "superintendent_s_authorization___signature": "superintendent_authorization_signature",
        "entered_into_uts": "entered_into_uts"
    }
    # Robust time/location field variants
    key_map.update({
        "report_time": "report_time",
        "report time": "report_time",
        "report-time": "report_time",
        "report.time": "report_time",
        "reporttime": "report_time",
        "relief_time": "relief_time",
        "relief time": "relief_time",
        "relief-time": "relief_time",
        "relief.time": "relief_time",
        "relieftime": "relief_time",
        "report_loc": "report_loc",
        "report loc": "report_loc",
        "report-loc": "report_loc",
        "report.loc": "report_loc",
        "reportloc": "report_loc",
        "overtime_location": "overtime_location",
        "overtime location": "overtime_location",
        "overtime-location": "overtime_location",
        "overtime.location": "overtime_location",
        "overtimelocation": "overtime_location",
    })
    # Checkbox mapping
    checkbox_map = {
        "rdo": "reason_rdo",
        "absentee_coverage": "reason_absentee_coverage",
        "no_lunch": "reason_no_lunch",
        "early_report": "reason_early_report",
        "late_clear": "reason_late_clear",
        "save_as_oto": "reason_save_as_oto",
        "capital_support_go": "reason_capital_support_go",
        "other": "reason_other"
    }
    form_data = {field: False if field.startswith('reason_') else '' for field in all_fields}
    row = {}
    # Flatten nested dicts if needed
    def flatten(d, parent_key=""):
        items = []
        for k, v in d.items():
            new_key = f"{parent_key}_{k}" if parent_key else k
            if isinstance(v, dict):
                # Special handling for supervisor nested fields
                if parent_key.lower().startswith("superintendent's_authorization") or k.lower().startswith("superintendent's_authorization"):
                    # Map nested keys directly to their backend fields
                    for subk, subv in v.items():
                        subkey_norm = normalize_key(f"superintendent's_authorization_-_{subk}")
                        items.append((subkey_norm, subv))
                elif k.lower() == "superintendent's_authorization":
                    # Handle the nested superintendent authorization object
                    for subk, subv in v.items():
                        subkey_norm = normalize_key(f"superintendent's_authorization_-_{subk}")
                        items.append((subkey_norm, subv))
                else:
                    items.extend(flatten(v, new_key).items())
            else:
                items.append((new_key, v))
        return dict(items)
    flat_data = flatten(data)
    print("FLATTENED GEMINI DATA:", flat_data)
    # Map fields
    for k, v in flat_data.items():
        norm_k = normalize_key(k)
        print(f"Mapping: '{k}' -> '{norm_k}' = '{v}'")
        # Handle reason_for_overtime as string or list
        if norm_k == "reason_for_overtime":
            if isinstance(v, str):
                v = [v]
            for reason in v:
                reason_norm = normalize_key(reason)
                if reason_norm in checkbox_map:
                    form_data[checkbox_map[reason_norm]] = True
        # Custom logic for ambiguous keys
        elif norm_k == "pass":
            if "superintendent_authorization" in k.lower():
                form_data["superintendent_authorization_pass"] = v
            else:
                form_data["pass_number"] = v
        elif norm_k == "date":
            if "superintendent_authorization" in k.lower():
                form_data["superintendent_authorization_date"] = v
            elif "date_of_overtime" in k.lower():
                form_data["date_of_overtime"] = v
            elif form_type == 'supervisor':
                form_data["todays_date"] = v
            # else: do not map 'date' for hourly forms
        elif norm_k == "job":
            form_data["job_number"] = v
        elif norm_k == "rc":
            form_data["rc_number"] = v
        elif norm_k == "report_loc":
            form_data["report_loc"] = v
        elif norm_k == "reg_assignment":
            form_data["regular_assignment"] = v
        elif norm_k == "overtime_location":
            form_data["overtime_location"] = v
        elif norm_k == "report_time":
            form_data["report_time"] = v
        elif norm_k == "relief_time":
            form_data["relief_time"] = v
        elif norm_k == "overtime_hours":
            form_data["overtime_hours"] = v
        elif norm_k == "rdos":
            form_data["rdos"] = v
        elif norm_k == "sm":
            form_data["rdos"] = v
        elif norm_k == "acct":
            form_data["acct_number"] = v
        elif norm_k == "superintendents_authorization":
            # Handle combined superintendent authorization field (e.g., "713026 07/06/25")
            if isinstance(v, str) and ' ' in v:
                parts = v.split(' ', 1)  # Split on first space
                if len(parts) == 2:
                    form_data["superintendent_authorization_pass"] = parts[0]
                    form_data["superintendent_authorization_date"] = parts[1]
                else:
                    form_data["superintendent_authorization_pass"] = v
            else:
                form_data["superintendent_authorization_pass"] = v
        elif norm_k in key_map:
            form_data[key_map[norm_k]] = v
        elif norm_k in checkbox_map:
            form_data[checkbox_map[norm_k]] = bool(v)
        elif norm_k.startswith("reason_for_overtime_"):
            # e.g. reason_for_overtime_rdo: True
            reason = norm_k.replace("reason_for_overtime_", "")
            if reason in checkbox_map:
                form_data[checkbox_map[reason]] = bool(v)
        else:
            print(f"Unmapped Gemini key: {k} -> {v}")
    # Clean the form data to handle None values and lists
    for key, value in form_data.items():
        if value is None:
            form_data[key] = ''
        elif isinstance(value, list):
            form_data[key] = ', '.join(str(item) for item in value if item is not None)
        elif isinstance(value, bool):
            form_data[key] = 1 if value else 0
        elif key.startswith('reason_') and isinstance(value, str):
            # Convert string boolean values to integers for reason fields
            form_data[key] = 1 if value.lower() in ['true', '1', 'yes', 'on'] else 0
        else:
            form_data[key] = str(value) if value is not None else ''
    print("FINAL FORM DATA (mapped):", form_data)
    # Log dashboard-relevant fields
    dashboard_fields = ['overtime_hours', 'job_number', 'title', 'report_loc', 'overtime_location']
    for field in dashboard_fields:
        print(f"DASHBOARD FIELD {field}: {form_data.get(field)}")

    # --- PATCH: Ensure dashboard-relevant mapped fields are always set using flexible lookup from original Gemini data ---
    dashboard_fields = {
        'overtime_hours': [
            'overtime_hours', 'overtime', 'hours', 'ot_hours', 'ot', 'total_overtime', 'overtime total', 'ot total', 'ot time', 'total ot', 'total_ot', 'ot time (hh:mm)', 'overtime (hh:mm)'
        ],
        'job_number': [
            'job_number', 'job no', 'job_no', 'job', 'job#', 'job number', 'ta_job_no', 'ta job no', 'jobnum', 'jobnumber', 'job id', 'jobid'
        ],
        'title': [
            'title', 'position', 'job_title', 'role', 'job title', 'employee_title', 'employee title'
        ],
        'report_loc': [
            'report_loc', 'report location', 'location', 'reportloc', 'report', 'loc', 'report station', 'station', 'reporting location'
        ],
        'overtime_location': [
            'overtime_location', 'overtime location', 'overtimelocation', 'ot_location', 'otloc', 'location', 'ot location', 'ot station', 'overtime station'
        ]
    }
    for field, variants in dashboard_fields.items():
        if not form_data.get(field):
            value = get_flexible_field(data, variants)
            if value:
                form_data[field] = value
    # Log the final values for dashboard fields
    print("DASHBOARD FIELD VALUES:")
    for field in dashboard_fields:
        print(f"  {field}: {form_data.get(field)}")

    # For exception claim (hourly) forms, build a row if relevant fields are present
    row_fields = [
        "exception_code", "line_location", "run_no",
        "exception_time_from_hh", "exception_time_from_mm",
        "exception_time_to_hh", "exception_time_to_mm",
        "overtime_hh", "overtime_mm",
        "bonus_hh", "bonus_mm",
        "nite_diff_hh", "nite_diff_mm",
        "ta_job_no"
    ]
    row = {field: form_data.get(field, '') for field in row_fields}
    # Add a row if ANY of the key fields are present (not just code/location/run_no)
    if any(str(v).strip() for v in row.values()):
        rows = [row]
    else:
        rows = []
    return form_data, rows

def is_blank_or_crossed_out(image_path):
    # Simple blank/crossed-out detection: check if almost all pixels are white or if very little text is extracted
    # You can improve this with OCR or more advanced image analysis
    try:
        from PIL import Image
        img = Image.open(image_path).convert('L')
        # Threshold: count non-white pixels
        nonwhite = sum(1 for p in img.getdata() if p < 240)
        if nonwhite < 1000:  # Tune this threshold as needed
            return True
    except Exception as e:
        print(f"Error in blank/crossed-out detection: {e}")
    return False

# Flexible field lookup for raw JSON

def get_flexible_field(data, possible_keys):
    """
    Search for a value in a dict by a list of possible field names (case-insensitive, with normalization).
    Handles flat dicts only. For nested dicts, extend as needed.
    """
    def normalize(s):
        return s.lower().replace(' ', '').replace('_', '').replace('-', '')
    norm_data = {normalize(k): v for k, v in data.items()}
    for key in possible_keys:
        norm_key = normalize(key)
        if norm_key in norm_data:
            return norm_data[norm_key]
    return None

# --- PATCH: Set file_name using flexible lookup for both mapped and pure extraction modes ---
def get_flexible_file_name(form_data, raw_json=None, fallback=None):
    file_name = form_data.get('pass_number')
    if not file_name and raw_json:
        file_name = (
            raw_json.get('pass_number') or
            raw_json.get('file_name') or
            raw_json.get('filename') or
            raw_json.get('name')
        )
    if not file_name and fallback:
        file_name = fallback
    return str(file_name) if file_name else 'N/A'

@app.route('/upload/hourly', methods=['POST'])
def upload_hourly_file():
    return handle_upload(form_type='hourly')

@app.route('/upload/supervisor', methods=['POST'])
def upload_supervisor_file():
    return handle_upload(form_type='supervisor')

# Refactor the upload logic into a helper

def handle_upload(form_type):
    try:
        files = request.files.getlist('files')
        if not files:
            # fallback for single file upload (old clients)
            if 'file' in request.files:
                files = [request.files['file']]
            else:
                return jsonify({'error': 'No file(s) part in the request.'}), 400

        from db import store_exception_form, log_audit
        username = request.form.get('username') or request.args.get('username') or (request.json.get('username') if request.is_json else None)
        if not username:
            username = 'unknown'
        success = 0
        failed = 0
        for file in files:
            if file.filename == '':
                failed += 1
                continue
            try:
                # Save files in subfolders by form_type
                subfolder = form_type if form_type in ['hourly', 'supervisor'] else ''
                target_folder = os.path.join(UPLOAD_FOLDER, subfolder) if subfolder else UPLOAD_FOLDER
                os.makedirs(target_folder, exist_ok=True)
                filepath = os.path.join(target_folder, file.filename)
                file.save(filepath)

                # If supervisor and PDF, split each page into two halves and process each as a form
                if form_type == 'supervisor' and file.filename.lower().endswith('.pdf'):
                    with pdfplumber.open(filepath) as pdf:
                        for i, page in enumerate(pdf.pages):
                            img = page.to_image(resolution=300).original
                            width, height = img.size
                            # Top half
                            top_half = img.crop((0, 0, width, height // 2))
                            top_path = os.path.join(target_folder, f"{os.path.splitext(file.filename)[0]}_page{i+1}_top.png")
                            top_half.save(top_path)
                            # Bottom half
                            bottom_half = img.crop((0, height // 2, width, height))
                            bottom_path = os.path.join(target_folder, f"{os.path.splitext(file.filename)[0]}_page{i+1}_bottom.png")
                            bottom_half.save(bottom_path)
                            # Process each half
                            for img_path in [top_path, bottom_path]:
                                if is_blank_or_crossed_out(img_path):
                                    print(f"Skipped blank/crossed-out form: {img_path}")
                                    continue
                                # Use Gemini to extract details with dual approach (both pure and mapped)
                                gemini_output = gemini_extract_file_details(img_path)
                                print("--- Gemini Output ---")
                                print(gemini_output)
                                print("--- END Gemini Output ---")
                                forms_data, raw_gemini_json = process_gemini_extraction_dual(gemini_output, form_type=form_type) if gemini_output else ([], '')
                                
                                # Process each form from the response
                                for form_data, rows, individual_json in forms_data:
                                    # Use the individual_json for the raw_gemini_json
                                    form_data['raw_gemini_json'] = individual_json
                                    # --- PATCH: Set file_name using flexible lookup for both mapped and pure extraction modes ---
                                    form_data['file_name'] = get_flexible_file_name(form_data, raw_gemini_json, os.path.basename(img_path))
                                    if form_data:
                                        required_form_fields = [
                                            'pass_number', 'title', 'employee_name', 'rdos', 'actual_ot_date', 'div',
                                            'comments', 'supervisor_name', 'supervisor_pass_no', 'oto', 'oto_amount_saved',
                                            'entered_in_uts', 'regular_assignment', 'report', 'relief', 'todays_date', 'status', 'file_name'
                                        ]
                                        for key in required_form_fields:
                                            if key not in form_data:
                                                form_data[key] = 'N/A'
                                        form_data['status'] = 'processed'
                                    else:
                                        form_data = {key: '' for key in required_form_fields}
                                        form_data['file_name'] = os.path.basename(img_path)
                                        form_data['comments'] = f"Gemini extraction failed for {img_path}. Output: {gemini_output if gemini_output else 'None'}"
                                        form_data['status'] = 'error'
                                        if not rows:
                                            rows = []
                                    upload_date = datetime.datetime.now().isoformat()
                                    form_id = store_exception_form(form_data, rows, username, form_type=form_type, upload_date=upload_date)
                                    if not form_id:
                                        failed += 1
                                        continue
                                    log_audit(username, 'upload', 'form', form_id, f"Form uploaded: {form_data.get('pass_number', 'N/A')}")
                                    success += 1
                    continue  # Skip the rest of the loop for supervisor PDFs

                # Default: process as a single file (for hourly or non-PDF supervisor uploads)
                gemini_output = gemini_extract_file_details(filepath)
                print("--- Gemini Output ---")
                print(gemini_output)
                print("--- END Gemini Output ---")
                forms_data, raw_gemini_json = process_gemini_extraction_dual(gemini_output, form_type=form_type) if gemini_output else ([], '')
                
                # Process each form from the response
                for form_data, rows, individual_json in forms_data:
                    # Use the individual_json for the raw_gemini_json
                    form_data['raw_gemini_json'] = individual_json
                    # --- PATCH: Set file_name using flexible lookup for both mapped and pure extraction modes ---
                    form_data['file_name'] = get_flexible_file_name(form_data, raw_gemini_json, file.filename)
                    if form_data:
                        required_form_fields = [
                            'pass_number', 'title', 'employee_name', 'rdos', 'actual_ot_date', 'div',
                            'comments', 'supervisor_name', 'supervisor_pass_no', 'oto', 'oto_amount_saved',
                            'entered_in_uts', 'regular_assignment', 'report', 'relief', 'todays_date', 'status', 'file_name'
                        ]
                        for key in required_form_fields:
                            if key not in form_data:
                                form_data[key] = 'N/A'
                        form_data['status'] = 'processed'
                    else:
                        form_data = {key: '' for key in required_form_fields}
                        form_data['file_name'] = file.filename
                        form_data['comments'] = f"Gemini extraction failed for {file.filename}. Output: {gemini_output if gemini_output else 'None'}"
                        form_data['status'] = 'error'
                        if not rows:
                            rows = []
                    upload_date = datetime.datetime.now().isoformat()
                    form_id = store_exception_form(form_data, rows, username, form_type=form_type, upload_date=upload_date)
                    if not form_id:
                        failed += 1
                        continue
                    log_audit(username, 'upload', 'form', form_id, f"Form uploaded: {form_data.get('pass_number', 'N/A')}")
                    success += 1
            except Exception as e:
                print(f"Error processing file {file.filename}: {e}")
                failed += 1
        return jsonify({'message': 'Batch upload complete', 'success': success, 'failed': failed})
    except Exception as e:
        print(f"Error in handle_upload: {e}")
        return jsonify({'error': str(e)}), 500

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
        form_type = request.args.get('form_type')
        username = request.args.get('username')
        extraction_mode_filter = request.args.get('extraction_mode')  # Get extraction mode filter
        
        with sqlite3.connect('forms.db', timeout=10) as conn:
            c = conn.cursor()
            
            # Get forms for statistics calculation with extraction mode filter
            if form_type:
                if extraction_mode_filter == 'pure':
                    c.execute('SELECT id, pass_number, title, employee_name, rdos, actual_ot_date, div, comments, supervisor_name, supervisor_pass_no, oto, oto_amount_saved, entered_in_uts, regular_assignment, report, relief, todays_date, status, username, ocr_lines, form_type, upload_date, file_name, reg, superintendent_authorization_signature, superintendent_authorization_pass, superintendent_authorization_date, entered_into_uts, raw_gemini_json, overtime_hours, report_loc, overtime_location, report_time, relief_time, date_of_overtime, job_number, rc_number, acct_number, reason_rdo, reason_absentee_coverage, reason_no_lunch, reason_early_report, reason_late_clear, reason_save_as_oto, reason_capital_support_go, reason_other, amount, raw_extracted_data, extraction_mode FROM exception_forms WHERE status = "processed" AND form_type = ? AND extraction_mode = ?', (form_type, extraction_mode_filter))
                elif extraction_mode_filter == 'mapped':
                    c.execute('SELECT id, pass_number, title, employee_name, rdos, actual_ot_date, div, comments, supervisor_name, supervisor_pass_no, oto, oto_amount_saved, entered_in_uts, regular_assignment, report, relief, todays_date, status, username, ocr_lines, form_type, upload_date, file_name, reg, superintendent_authorization_signature, superintendent_authorization_pass, superintendent_authorization_date, entered_into_uts, raw_gemini_json, overtime_hours, report_loc, overtime_location, report_time, relief_time, date_of_overtime, job_number, rc_number, acct_number, reason_rdo, reason_absentee_coverage, reason_no_lunch, reason_early_report, reason_late_clear, reason_save_as_oto, reason_capital_support_go, reason_other, amount, raw_extracted_data, extraction_mode FROM exception_forms WHERE status = "processed" AND form_type = ? AND (extraction_mode = ? OR extraction_mode IS NULL)', (form_type, extraction_mode_filter))
                else:
                    c.execute('SELECT id, pass_number, title, employee_name, rdos, actual_ot_date, div, comments, supervisor_name, supervisor_pass_no, oto, oto_amount_saved, entered_in_uts, regular_assignment, report, relief, todays_date, status, username, ocr_lines, form_type, upload_date, file_name, reg, superintendent_authorization_signature, superintendent_authorization_pass, superintendent_authorization_date, entered_into_uts, raw_gemini_json, overtime_hours, report_loc, overtime_location, report_time, relief_time, date_of_overtime, job_number, rc_number, acct_number, reason_rdo, reason_absentee_coverage, reason_no_lunch, reason_early_report, reason_late_clear, reason_save_as_oto, reason_capital_support_go, reason_other, amount, raw_extracted_data, extraction_mode FROM exception_forms WHERE status = "processed" AND form_type = ?', (form_type,))
            else:
                if extraction_mode_filter == 'pure':
                    c.execute('SELECT id, pass_number, title, employee_name, rdos, actual_ot_date, div, comments, supervisor_name, supervisor_pass_no, oto, oto_amount_saved, entered_in_uts, regular_assignment, report, relief, todays_date, status, username, ocr_lines, form_type, upload_date, file_name, reg, superintendent_authorization_signature, superintendent_authorization_pass, superintendent_authorization_date, entered_into_uts, raw_gemini_json, overtime_hours, report_loc, overtime_location, report_time, relief_time, date_of_overtime, job_number, rc_number, acct_number, reason_rdo, reason_absentee_coverage, reason_no_lunch, reason_early_report, reason_late_clear, reason_save_as_oto, reason_capital_support_go, reason_other, amount, raw_extracted_data, extraction_mode FROM exception_forms WHERE status = "processed" AND extraction_mode = ?', (extraction_mode_filter,))
                elif extraction_mode_filter == 'mapped':
                    c.execute('SELECT id, pass_number, title, employee_name, rdos, actual_ot_date, div, comments, supervisor_name, supervisor_pass_no, oto, oto_amount_saved, entered_in_uts, regular_assignment, report, relief, todays_date, status, username, ocr_lines, form_type, upload_date, file_name, reg, superintendent_authorization_signature, superintendent_authorization_pass, superintendent_authorization_date, entered_into_uts, raw_gemini_json, overtime_hours, report_loc, overtime_location, report_time, relief_time, date_of_overtime, job_number, rc_number, acct_number, reason_rdo, reason_absentee_coverage, reason_no_lunch, reason_early_report, reason_late_clear, reason_save_as_oto, reason_capital_support_go, reason_other, amount, raw_extracted_data, extraction_mode FROM exception_forms WHERE status = "processed" AND (extraction_mode = ? OR extraction_mode IS NULL)', (extraction_mode_filter,))
                else:
                    c.execute('SELECT id, pass_number, title, employee_name, rdos, actual_ot_date, div, comments, supervisor_name, supervisor_pass_no, oto, oto_amount_saved, entered_in_uts, regular_assignment, report, relief, todays_date, status, username, ocr_lines, form_type, upload_date, file_name, reg, superintendent_authorization_signature, superintendent_authorization_pass, superintendent_authorization_date, entered_into_uts, raw_gemini_json, overtime_hours, report_loc, overtime_location, report_time, relief_time, date_of_overtime, job_number, rc_number, acct_number, reason_rdo, reason_absentee_coverage, reason_no_lunch, reason_early_report, reason_late_clear, reason_save_as_oto, reason_capital_support_go, reason_other, amount, raw_extracted_data, extraction_mode FROM exception_forms WHERE status = "processed"')
            
            forms = c.fetchall()
            
            # Calculate statistics using the new filtered function
            stats = calculate_dashboard_stats_with_raw_data(forms, form_type, extraction_mode_filter)
            
            # Get forms for the table display with extraction mode filter
            if form_type:
                if extraction_mode_filter == 'pure':
                    c.execute('SELECT id, pass_number, title, employee_name, actual_ot_date, div, comments, status, form_type, upload_date FROM exception_forms WHERE status = "processed" AND form_type = ? AND extraction_mode = ?', (form_type, extraction_mode_filter))
                elif extraction_mode_filter == 'mapped':
                    c.execute('SELECT id, pass_number, title, employee_name, actual_ot_date, div, comments, status, form_type, upload_date FROM exception_forms WHERE status = "processed" AND form_type = ? AND (extraction_mode = ? OR extraction_mode IS NULL)', (form_type, extraction_mode_filter))
                else:
                    c.execute('SELECT id, pass_number, title, employee_name, actual_ot_date, div, comments, status, form_type, upload_date FROM exception_forms WHERE status = "processed" AND form_type = ?', (form_type,))
            else:
                if extraction_mode_filter == 'pure':
                    c.execute('SELECT id, pass_number, title, employee_name, actual_ot_date, div, comments, status, form_type, upload_date FROM exception_forms WHERE status = "processed" AND extraction_mode = ?', (extraction_mode_filter,))
                elif extraction_mode_filter == 'mapped':
                    c.execute('SELECT id, pass_number, title, employee_name, actual_ot_date, div, comments, status, form_type, upload_date FROM exception_forms WHERE status = "processed" AND (extraction_mode = ? OR extraction_mode IS NULL)', (extraction_mode_filter,))
                else:
                    c.execute('SELECT id, pass_number, title, employee_name, actual_ot_date, div, comments, status, form_type, upload_date FROM exception_forms WHERE status = "processed"')
            
            forms_table = [
                {
                    "id": row[0],
                    "pass_number": row[1],
                    "title": row[2],
                    "employee_name": row[3],
                    "actual_ot_date": row[4],
                    "div": row[5],
                    "comments": row[6],
                    "status": row[7],
                    "form_type": row[8] if len(row) > 8 else '',
                    "upload_date": row[9] if len(row) > 9 else ''
                }
                for row in c.fetchall()
            ]
            
            conn.commit()
        
        result = {
            "total_forms": stats["total_forms"],
            "total_overtime": stats["total_overtime"],
            "total_job_numbers": stats["total_job_numbers"],
            "unique_job_numbers": stats["unique_job_numbers"],
            "most_relevant_position": stats["most_relevant_position"],
            "most_relevant_location": stats["most_relevant_location"],
            "most_common_reason": stats.get("most_common_reason"),
            "forms": forms_table
        }
        
        return jsonify(result)
        
    except Exception as e:
        print(f"Error in dashboard: {e}")
        return jsonify({"error": str(e)}), 500

def calculate_dashboard_stats_with_raw_data(forms, form_type=None, extraction_mode_filter=None):
    """
    Calculate dashboard statistics that works with both pure and mapped extraction modes.
    For pure extraction, it parses the raw_extracted_data JSON to extract statistics.
    Now uses flexible field lookup for raw JSON.
    """
    import json
    from collections import Counter
    
    def safe_int(val):
        try:
            return int(val)
        except Exception:
            return 0
    
    total_forms = len(forms)
    total_minutes = 0
    job_numbers = []
    positions = []
    locations = []
    reason_counts = {field: 0 for field in [
        'reason_rdo', 'reason_absentee_coverage', 'reason_no_lunch', 
        'reason_early_report', 'reason_late_clear', 'reason_save_as_oto', 
        'reason_capital_support_go', 'reason_other'
    ]}
    
    # Define the exact column order that matches our SELECT statement
    columns = ['id', 'pass_number', 'title', 'employee_name', 'rdos', 'actual_ot_date', 'div', 'comments', 'supervisor_name', 'supervisor_pass_no', 'oto', 'oto_amount_saved', 'entered_in_uts', 'regular_assignment', 'report', 'relief', 'todays_date', 'status', 'username', 'ocr_lines', 'form_type', 'upload_date', 'file_name', 'reg', 'superintendent_authorization_signature', 'superintendent_authorization_pass', 'superintendent_authorization_date', 'entered_into_uts', 'raw_gemini_json', 'overtime_hours', 'report_loc', 'overtime_location', 'report_time', 'relief_time', 'date_of_overtime', 'job_number', 'rc_number', 'acct_number', 'reason_rdo', 'reason_absentee_coverage', 'reason_no_lunch', 'reason_early_report', 'reason_late_clear', 'reason_save_as_oto', 'reason_capital_support_go', 'reason_other', 'amount', 'raw_extracted_data', 'extraction_mode']
    
    for form in forms:
        # Convert tuple to dictionary using column names
        if isinstance(form, tuple):
            form_dict = dict(zip(columns, form))
        else:
            form_dict = dict(form)
        
        print(f"\n--- Debug: Processing form ID {form_dict.get('id')} ---")
        print(f"Mapped fields: overtime_hours={form_dict.get('overtime_hours')}, job_number={form_dict.get('job_number')}, title={form_dict.get('title')}, report_loc={form_dict.get('report_loc')}, overtime_location={form_dict.get('overtime_location')}")
        print(f"Extraction mode: {form_dict.get('extraction_mode')}")
        print(f"Raw extracted data: {form_dict.get('raw_extracted_data')}")
        
        extraction_mode = form_dict.get('extraction_mode')
        raw_data = form_dict.get('raw_extracted_data')
        current_form_type = form_dict.get('form_type')
        
        # Filter by extraction mode if specified
        if extraction_mode_filter:
            if extraction_mode_filter == 'pure' and extraction_mode != 'pure':
                continue
            elif extraction_mode_filter == 'mapped' and extraction_mode not in [None, '', 'mapped']:
                continue
        
        # Use the current form's type for processing this specific form
        current_form_type_for_processing = current_form_type
        
        if extraction_mode == 'pure' and raw_data:
            try:
                raw_json = json.loads(raw_data)
                # --- Flexible Overtime Extraction ---
                if current_form_type_for_processing == 'supervisor':
                    overtime_hours = get_flexible_field(raw_json, [
                        'overtime_hours', 'overtime', 'hours', 'ot_hours', 'ot', 'total_overtime'
                    ])
                    if overtime_hours and overtime_hours != 'N/A':
                        try:
                            if '+' in str(overtime_hours):
                                parts = str(overtime_hours).split('+')
                                for part in parts:
                                    part = part.strip()
                                    if ':' in part:
                                        hours, minutes = part.split(':')
                                        total_minutes += int(hours) * 60 + int(minutes)
                                    else:
                                        total_minutes += int(part) * 60
                            elif ':' in str(overtime_hours):
                                hours, minutes = str(overtime_hours).split(':')
                                total_minutes += int(hours) * 60 + int(minutes)
                            else:
                                total_minutes += int(overtime_hours) * 60
                        except:
                            pass
                    
                    # --- Flexible Job Number Extraction (Supervisor) ---
                    job_num = get_flexible_field(raw_json, [
                        'job', 'job_number', 'job no', 'job_no', 'job#', 'job number', 'ta_job_no', 'ta job no', 'jobnum', 'jobnumber', 'job id', 'jobid'
                    ])
                    if job_num and job_num != 'N/A':
                        job_numbers.append(str(job_num))
                elif current_form_type_for_processing == 'hourly':
                    # Look for overtime in rows or direct fields
                    rows = raw_json.get('rows', [])
                    for row in rows:
                        if isinstance(row, dict):
                            # --- Flexible Overtime Extraction (Hourly Row) ---
                            hh = get_flexible_field(row, ['overtime_hh', 'ot_hh', 'hh'])
                            mm = get_flexible_field(row, ['overtime_mm', 'ot_mm', 'mm'])
                            print('Hourly row:', row)
                            print('Extracted overtime:', hh, mm)
                            try:
                                total_minutes += safe_int(hh) * 60 + safe_int(mm)
                            except:
                                pass
                            # --- Flexible Job Number Extraction (Hourly Row) ---
                            ta_job = get_flexible_field(row, [
                                'ta_job_no', 'job_no', 'jobnumber', 'jobnum'
                            ])
                            if ta_job and ta_job != 'N/A':
                                job_numbers.append(str(ta_job))
                            # --- Flexible Location Extraction (Hourly Row) ---
                            line_loc = get_flexible_field(row, [
                                'line_location', 'location', 'line', 'loc', 'line_loc'
                            ])
                            if line_loc and line_loc != 'N/A':
                                locations.append(line_loc)
                    # Also check for overtime, job number, and location at the top level (in case some forms store them there)
                    hh_top = get_flexible_field(raw_json, ['overtime_hh', 'ot_hh', 'hh'])
                    mm_top = get_flexible_field(raw_json, ['overtime_mm', 'ot_mm', 'mm'])
                    try:
                        total_minutes += safe_int(hh_top) * 60 + safe_int(mm_top)
                    except:
                        pass
                    # Also check for overtime_hours at the top level (e.g., "00:30")
                    overtime_hours_top = get_flexible_field(raw_json, [
                        'overtime_hours', 'overtime', 'hours', 'ot_hours', 'ot', 'total_overtime'
                    ])
                    if overtime_hours_top and overtime_hours_top != 'N/A':
                        try:
                            if '+' in str(overtime_hours_top):
                                parts = str(overtime_hours_top).split('+')
                                for part in parts:
                                    part = part.strip()
                                    if ':' in part:
                                        hours, minutes = part.split(':')
                                        total_minutes += int(hours) * 60 + int(minutes)
                                    else:
                                        total_minutes += int(part) * 60
                            elif ':' in str(overtime_hours_top):
                                hours, minutes = str(overtime_hours_top).split(':')
                                total_minutes += int(hours) * 60 + int(minutes)
                            else:
                                total_minutes += int(overtime_hours_top) * 60
                        except:
                            pass
                    # --- NEW: Also check for job number and location at the top level ---
                    ta_job_top = get_flexible_field(raw_json, [
                        'ta_job_no', 'job_no', 'jobnumber', 'jobnum', 'job number', 'TA Job No', 'TA Job Number'
                    ])
                    if ta_job_top and ta_job_top != 'N/A':
                        job_numbers.append(str(ta_job_top))
                    line_loc_top = get_flexible_field(raw_json, [
                        'line_location', 'location', 'line', 'loc', 'line_loc', 'report_station'
                    ])
                    if line_loc_top and line_loc_top != 'N/A':
                        locations.append(line_loc_top)
                # --- Flexible Position/Title Extraction ---
                if current_form_type_for_processing == 'supervisor':
                    positions.append('Supervisor')
                else:
                    title = get_flexible_field(raw_json, [
                        'title', 'position', 'job_title', 'role'
                    ])
                    if title and title != 'N/A':
                        positions.append(title)
                # --- Flexible Location Extraction ---
                if current_form_type_for_processing == 'supervisor':
                    report_loc = get_flexible_field(raw_json, [
                        'report_loc', 'report_location', 'location', 'reportloc', 'report', 'loc'
                    ])
                    overtime_loc = get_flexible_field(raw_json, [
                        'overtime_location', 'location', 'overtimelocation', 'ot_location', 'otloc'
                    ])
                    if report_loc and report_loc != 'N/A':
                        locations.append(report_loc)
                    if overtime_loc and overtime_loc != 'N/A':
                        locations.append(overtime_loc)
                elif current_form_type_for_processing == 'hourly':
                    rows = raw_json.get('rows', [])
                    for row in rows:
                        if isinstance(row, dict):
                            line_loc = get_flexible_field(row, [
                                'line_location', 'location', 'line', 'loc', 'line_loc'
                            ])
                            if line_loc and line_loc != 'N/A':
                                locations.append(line_loc)
                # --- Flexible Reason Extraction (Supervisor) ---
                if current_form_type_for_processing == 'supervisor':
                    reasons = get_flexible_field(raw_json, [
                        'reason_for_overtime', 'reason', 'overtime_reason', 'reasonovertime', 'reasonforot'
                    ])
                    if isinstance(reasons, str):
                        reasons = [reasons]
                    if isinstance(reasons, list):
                        for reason in reasons:
                            reason_lower = str(reason).lower()
                            if 'rdo' in reason_lower:
                                reason_counts['reason_rdo'] += 1
                            elif 'absentee' in reason_lower or 'coverage' in reason_lower:
                                reason_counts['reason_absentee_coverage'] += 1
                            elif 'lunch' in reason_lower:
                                reason_counts['reason_no_lunch'] += 1
                            elif 'early' in reason_lower and 'report' in reason_lower:
                                reason_counts['reason_early_report'] += 1
                            elif 'late' in reason_lower and 'clear' in reason_lower:
                                reason_counts['reason_late_clear'] += 1
                            elif 'oto' in reason_lower:
                                reason_counts['reason_save_as_oto'] += 1
                            elif 'capital' in reason_lower or 'support' in reason_lower:
                                reason_counts['reason_capital_support_go'] += 1
                            else:
                                reason_counts['reason_other'] += 1
            except json.JSONDecodeError:
                # Fall back to mapped fields if JSON parsing fails
                pass
        
        # Use mapped fields as fallback or for mapped extraction mode
        if extraction_mode == 'mapped' or not raw_data:
            # Overtime calculation
            overtime_hours = form_dict.get('overtime_hours')
            if (not overtime_hours or overtime_hours == 'N/A') and form_dict.get('raw_extracted_data'):
                try:
                    raw_json = json.loads(form_dict['raw_extracted_data'])
                    overtime_hours = get_flexible_field(raw_json, [
                        'overtime_hours', 'overtime', 'hours', 'ot_hours', 'ot', 'total_overtime'
                    ])
                    print(f"Fallback: Found overtime_hours in raw_extracted_data: {overtime_hours}")
                except Exception as e:
                    print(f"Error parsing raw_extracted_data for overtime_hours: {e}")
                    overtime_hours = None
            else:
                print(f"Using mapped overtime_hours: {overtime_hours}")
            
            # Process overtime hours for mapped extraction
            if overtime_hours and overtime_hours != 'N/A':
                try:
                    if '+' in str(overtime_hours):
                        parts = str(overtime_hours).split('+')
                        for part in parts:
                            part = part.strip()
                            if ':' in part:
                                hours, minutes = part.split(':')
                                total_minutes += int(hours) * 60 + int(minutes)
                            else:
                                total_minutes += int(part) * 60
                    elif ':' in str(overtime_hours):
                        hours, minutes = str(overtime_hours).split(':')
                        total_minutes += int(hours) * 60 + int(minutes)
                    else:
                        total_minutes += int(overtime_hours) * 60
                except:
                    pass
            
            # Job numbers (for supervisor forms)
            job_num = form_dict.get('job_number')
            if (not job_num or job_num == 'N/A') and form_dict.get('raw_extracted_data'):
                try:
                    raw_json = json.loads(form_dict['raw_extracted_data'])
                    job_num = get_flexible_field(raw_json, [
                        'job_number', 'job no', 'job_no', 'job', 'job#', 'job number', 'ta_job_no', 'ta job no', 'jobnum', 'jobnumber', 'job id', 'jobid'
                    ])
                    print(f"Fallback: Found job_number in raw_extracted_data: {job_num}")
                except Exception as e:
                    print(f"Error parsing raw_extracted_data for job_number: {e}")
                    job_num = None
            else:
                print(f"Using mapped job_number: {job_num}")
            
            # Add job number to statistics
            if job_num and job_num != 'N/A':
                job_numbers.append(str(job_num))
            
            # Positions
            title = form_dict.get('title')
            if (not title or title == 'N/A' or (isinstance(title, str) and title.isdigit())) and form_dict.get('raw_extracted_data'):
                try:
                    raw_json = json.loads(form_dict['raw_extracted_data'])
                    title = get_flexible_field(raw_json, [
                        'title', 'position', 'job_title', 'role'
                    ])
                    print(f"Fallback: Found title in raw_extracted_data: {title}")
                except Exception as e:
                    print(f"Error parsing raw_extracted_data for title: {e}")
                    title = None
            else:
                print(f"Using mapped title: {title}")
            
            # Add position to statistics
            if title and title != 'N/A':
                if current_form_type_for_processing == 'supervisor':
                    positions.append('Supervisor')
                else:
                    positions.append(title)
            
            # Locations (for supervisor forms)
            report_loc = form_dict.get('report_loc')
            overtime_loc = form_dict.get('overtime_location')
            if (not report_loc or report_loc == 'N/A') and form_dict.get('raw_extracted_data'):
                try:
                    raw_json = json.loads(form_dict['raw_extracted_data'])
                    report_loc = get_flexible_field(raw_json, [
                        'report_loc', 'report location', 'location', 'reportloc', 'report', 'loc', 'report station', 'station', 'reporting location'
                    ])
                    print(f"Fallback: Found report_loc in raw_extracted_data: {report_loc}")
                except Exception as e:
                    print(f"Error parsing raw_extracted_data for report_loc: {e}")
                    report_loc = None
            else:
                print(f"Using mapped report_loc: {report_loc}")
            if (not overtime_loc or overtime_loc == 'N/A') and form_dict.get('raw_extracted_data'):
                try:
                    raw_json = json.loads(form_dict['raw_extracted_data'])
                    overtime_loc = get_flexible_field(raw_json, [
                        'overtime_location', 'overtime location', 'overtimelocation', 'ot_location', 'otloc', 'location', 'ot location', 'ot station', 'overtime station'
                    ])
                    print(f"Fallback: Found overtime_location in raw_extracted_data: {overtime_loc}")
                except Exception as e:
                    print(f"Error parsing raw_extracted_data for overtime_location: {e}")
                    overtime_loc = None
            else:
                print(f"Using mapped overtime_location: {overtime_loc}")
            
            # Add locations to statistics
            if report_loc and report_loc != 'N/A':
                locations.append(report_loc)
            if overtime_loc and overtime_loc != 'N/A':
                locations.append(overtime_loc)
            
            # Reason counts for supervisor
            if current_form_type_for_processing == 'supervisor':
                for field in reason_counts.keys():
                    if form_dict.get(field):
                        reason_counts[field] += 1
            
            # For hourly forms, also check the rows table for additional data
            if current_form_type_for_processing == 'hourly':
                # Get rows for this form from the database
                with sqlite3.connect('forms.db', timeout=10) as conn:
                    c = conn.cursor()
                    c.execute('SELECT * FROM exception_form_rows WHERE form_id = ?', (form_dict.get('id'),))
                    rows = c.fetchall()
                    if rows:
                        row_columns = [desc[0] for desc in c.description]
                        for row in rows:
                            row_dict = dict(zip(row_columns, row))
                            # Process overtime from rows
                            hh = row_dict.get('overtime_hh')
                            mm = row_dict.get('overtime_mm')
                            if hh and mm:
                                try:
                                    total_minutes += safe_int(hh) * 60 + safe_int(mm)
                                except:
                                    pass
                            # Process job numbers from rows
                            ta_job = row_dict.get('ta_job_no')
                            if ta_job and ta_job != 'N/A':
                                job_numbers.append(str(ta_job))
                            # Process locations from rows
                            line_loc = row_dict.get('line_location')
                            if line_loc and line_loc != 'N/A':
                                locations.append(line_loc)
    
    # Calculate final statistics
    total_overtime_hh = total_minutes // 60
    total_overtime_mm = total_minutes % 60
    
    unique_job_numbers = set(job_numbers)
    
    most_position, most_position_count = ('N/A', 0)
    if positions:
        most_position, most_position_count = Counter(positions).most_common(1)[0]
    
    most_location, most_location_count = ('N/A', 0)
    if locations:
        most_location, most_location_count = Counter(locations).most_common(1)[0]
    
    most_common_reason = None
    if any(reason_counts.values()):
        most_common_reason_field = max(reason_counts, key=lambda k: reason_counts[k])
        reason_label_map = {
            'reason_rdo': 'RDO',
            'reason_absentee_coverage': 'Absentee Coverage',
            'reason_no_lunch': 'No Lunch',
            'reason_early_report': 'Early Report',
            'reason_late_clear': 'Late Clear',
            'reason_save_as_oto': 'Save as OTO',
            'reason_capital_support_go': 'Capital Support / GO',
            'reason_other': 'Other'
        }
        most_common_reason = {
            'reason': reason_label_map.get(most_common_reason_field, most_common_reason_field),
            'count': reason_counts[most_common_reason_field]
        }
    else:
        most_common_reason = {'reason': 'N/A', 'count': 0}
    
    return {
        "total_forms": total_forms,
        "total_overtime": f"{total_overtime_hh}h {total_overtime_mm}m",
        "total_job_numbers": len(job_numbers),
        "unique_job_numbers": len(unique_job_numbers),
        "most_relevant_position": {"position": most_position, "count": most_position_count},
        "most_relevant_location": {"location": most_location, "count": most_location_count},
        "most_common_reason": most_common_reason
    }

@app.route('/api/form/<int:form_id>', methods=['GET'])
def get_form_details(form_id):
    import sqlite3
    extraction_mode = request.args.get('extraction_mode', 'mapped')
    
    with sqlite3.connect('forms.db', timeout=10) as conn:
        c = conn.cursor()
        # Get form header with extraction mode filter
        if extraction_mode == 'pure':
            # For pure extraction, only return forms that have extraction_mode = 'pure'
            c.execute('SELECT * FROM exception_forms WHERE id = ? AND extraction_mode = ?', (form_id, extraction_mode))
        else:
            # For mapped extraction, return forms with extraction_mode = 'mapped' OR NULL (backward compatibility)
            c.execute('SELECT * FROM exception_forms WHERE id = ? AND (extraction_mode = ? OR extraction_mode IS NULL)', (form_id, extraction_mode))
        
        form_row = c.fetchone()
        if not form_row:
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
                status = ?,
                reg = ?,
                superintendent_authorization_signature = ?,
                superintendent_authorization_pass = ?,
                superintendent_authorization_date = ?,
                entered_into_uts = ?,
                overtime_hours = ?,
                report_loc = ?,
                overtime_location = ?,
                report_time = ?,
                relief_time = ?,
                date_of_overtime = ?,
                job_number = ?,
                rc_number = ?,
                acct_number = ?,
                amount = ?,
                reason_rdo = ?,
                reason_absentee_coverage = ?,
                reason_no_lunch = ?,
                reason_early_report = ?,
                reason_late_clear = ?,
                reason_save_as_oto = ?,
                reason_capital_support_go = ?,
                reason_other = ?
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
            form.get('reg', ''),
            form.get('superintendent_authorization_signature', ''),
            form.get('superintendent_authorization_pass', ''),
            form.get('superintendent_authorization_date', ''),
            form.get('entered_into_uts', ''),
            form.get('overtime_hours', ''),
            form.get('report_loc', ''),
            form.get('overtime_location', ''),
            form.get('report_time', ''),
            form.get('relief_time', ''),
            form.get('date_of_overtime', ''),
            form.get('job_number', ''),
            form.get('rc_number', ''),
            form.get('acct_number', ''),
            form.get('amount', ''),
            form.get('reason_rdo', False),
            form.get('reason_absentee_coverage', False),
            form.get('reason_no_lunch', False),
            form.get('reason_early_report', False),
            form.get('reason_late_clear', False),
            form.get('reason_save_as_oto', False),
            form.get('reason_capital_support_go', False),
            form.get('reason_other', False),
            form_id
        ))
        # PATCH: Update raw_gemini_json if present
        if 'raw_gemini_json' in form:
            print(f"Updating raw_gemini_json for form {form_id}: {form['raw_gemini_json'][:100]}...")
            c.execute('UPDATE exception_forms SET raw_gemini_json = ? WHERE id = ?', (form['raw_gemini_json'], form_id))
        # PATCH: Update raw_extracted_data if present
        if 'raw_extracted_data' in form:
            print(f"Updating raw_extracted_data for form {form_id}: {form['raw_extracted_data'][:100]}...")
            c.execute('UPDATE exception_forms SET raw_extracted_data = ? WHERE id = ?', (form['raw_extracted_data'], form_id))
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

@app.route('/api/extraction-mode', methods=['GET', 'POST'])
def extraction_mode():
    """Get or set the extraction mode (pure vs mapped)"""
    global PURE_GEMINI_EXTRACTION
    
    if request.method == 'POST':
        data = request.get_json()
        if data and 'mode' in data:
            PURE_GEMINI_EXTRACTION = data['mode'] == 'pure'
            return jsonify({
                'mode': 'pure' if PURE_GEMINI_EXTRACTION else 'mapped',
                'message': f'Extraction mode set to {"pure" if PURE_GEMINI_EXTRACTION else "mapped"}'
            })
        else:
            return jsonify({'error': 'Mode not specified'}), 400
    
    return jsonify({
        'mode': 'pure' if PURE_GEMINI_EXTRACTION else 'mapped',
        'description': {
            'pure': 'Extract all fields from Gemini without mapping to predefined fields',
            'mapped': 'Map Gemini output to predefined database fields'
        }
    })

@app.route('/api/forms/export', methods=['GET'])
def export_forms():
    import sqlite3
    import json
    
    # Get query parameters
    form_type = request.args.get('form_type')
    extraction_mode = request.args.get('extraction_mode')
    
    with sqlite3.connect('forms.db', timeout=10) as conn:
        c = conn.cursor()
        
        # Build query with filters
        query = "SELECT * FROM exception_forms WHERE 1=1"
        params = []
        
        if form_type:
            query += " AND form_type = ?"
            params.append(form_type)
        
        if extraction_mode:
            query += " AND extraction_mode = ?"
            params.append(extraction_mode)
        
        c.execute(query, params)
        rows = c.fetchall()
        
        # Get column names
        columns = [desc[0] for desc in c.description]
        
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
            'todays_date': "Today's Date",
            'form_type': 'Form Type',
            'extraction_mode': 'Extraction Mode',
            'raw_extracted_data': 'Raw Gemini Data (JSON)',
            'raw_gemini_json': 'Raw Gemini JSON',
            'upload_date': 'Upload Date'
        }
        
        headers = [header_map.get(col, col) for col in columns]
        
        conn.commit()
    
    def stream():
        yield ','.join(headers) + '\n'
        for row in rows:
            # Process each cell, handling JSON data specially
            processed_row = []
            for i, item in enumerate(row):
                if item is None:
                    processed_row.append('')
                elif columns[i] in ['raw_extracted_data', 'raw_gemini_json'] and item:
                    # Format JSON data for Excel readability
                    try:
                        parsed_json = json.loads(item)
                        formatted_json = json.dumps(parsed_json, indent=2)
                        # Escape quotes and newlines for CSV
                        formatted_json = formatted_json.replace('"', '""').replace('\n', ' ')
                        processed_row.append(f'"{formatted_json}"')
                    except:
                        escaped_item = str(item).replace('"', '""')
                        processed_row.append(f'"{escaped_item}"')
                else:
                    # Escape quotes for CSV
                    cell_value = str(item).replace('"', '""')
                    processed_row.append(f'"{cell_value}"')
            
            yield ','.join(processed_row) + '\n'
    
    # Generate filename based on filters
    filename_parts = ['exception_forms']
    if form_type:
        filename_parts.append(form_type)
    if extraction_mode:
        filename_parts.append(extraction_mode)
    filename = '_'.join(filename_parts) + '.csv'
    
    return Response(stream(), mimetype='text/csv', headers={
        'Content-Disposition': f'attachment; filename={filename}'
    })

if __name__ == "__main__":
    init_audit_db()
    init_exception_form_db()
    app.run(port=8000, debug=True)

    
