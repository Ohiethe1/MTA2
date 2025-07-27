import sqlite3
import json
from app import process_single_form

def migrate_mapped_fields(db_path='forms.db'):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('SELECT id, raw_gemini_json, form_type FROM exception_forms')
    forms = c.fetchall()
    updated = 0
    for form_id, raw_gemini_json, form_type in forms:
        if not raw_gemini_json:
            continue
        try:
            data = json.loads(raw_gemini_json)
        except Exception as e:
            print(f"Skipping form {form_id}: could not parse raw_gemini_json: {e}")
            continue
        form_data, _ = process_single_form(data, form_type)
        # Only update dashboard-relevant fields
        fields = ['overtime_hours', 'job_number', 'title', 'report_loc', 'overtime_location']
        updates = {field: form_data.get(field, '') for field in fields}
        set_clause = ', '.join([f'{field} = ?' for field in updates])
        values = list(updates.values()) + [form_id]
        c.execute(f'UPDATE exception_forms SET {set_clause} WHERE id = ?', values)
        updated += 1
        print(f"Updated form {form_id}: {updates}")
    conn.commit()
    conn.close()
    print(f"Migration complete. Updated {updated} forms.")

if __name__ == '__main__':
    migrate_mapped_fields() 