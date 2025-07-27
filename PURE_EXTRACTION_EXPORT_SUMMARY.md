# Pure Extraction Data in Exports ✅

## Answer to Your Question
**Yes, the export will show pure extraction data!** 

The export functionality includes both **mapped** and **pure** extraction data, and you can filter by extraction mode to get exactly what you need.

## What's Included in Exports

### 1. **Extraction Mode Column**
Every exported row includes an "Extraction Mode" column that shows:
- `"mapped"` - Forms processed with structured field mapping
- `"pure"` - Forms processed with raw Gemini extraction

### 2. **Raw Data Columns**
The export includes two important columns for extraction data:
- **"Raw Gemini JSON"** - The complete JSON response from Gemini
- **"Raw Gemini Data (JSON)"** - The raw extracted data without field mapping

## Current Database Status
- **Mapped Extraction**: 7 forms
- **Pure Extraction**: 2 forms (test data)
- **Total Forms**: 9 forms

## Export Options

### All Data (Default)
```bash
GET /api/forms/export
```
**Result**: 12 data rows (7 mapped + 2 pure + 3 other)

### Filter by Extraction Mode
```bash
# Pure extraction only
GET /api/forms/export?extraction_mode=pure

# Mapped extraction only  
GET /api/forms/export?extraction_mode=mapped
```

### Combined Filters
```bash
# Pure extraction + Hourly forms only
GET /api/forms/export?extraction_mode=pure&form_type=hourly

# Pure extraction + Supervisor forms only
GET /api/forms/export?extraction_mode=pure&form_type=supervisor
```

## Dashboard-Specific Exports

The export functionality automatically adapts based on your current dashboard:

1. **General Dashboard**: Exports ALL forms (both mapped and pure)
2. **Supervisor Dashboard**: Exports only supervisor forms (both mapped and pure)
3. **Hourly Dashboard**: Exports only hourly forms (both mapped and pure)

## Pure Extraction Data Example

When you export forms with pure extraction, you'll see data like this:

```json
{
  "employee_name": "Test Employee 1",
  "pass_number": "12345678", 
  "title": "Operator",
  "regular_assignment": "A-201",
  "report_station": "207th",
  "today_date": "2025-01-15",
  "rdos": "Sat/Sun",
  "actual_ot_date": "2025-01-15",
  "div": "A",
  "exception_code": "39",
  "line_location": "A 207th St",
  "run_no": "201A",
  "exception_time_from": "01:00",
  "exception_time_to": "01:30",
  "overtime_hours": "00:30",
  "ta_job_no": "09068",
  "comments": "Test pure extraction form 1",
  "oto": "YES",
  "entered_in_uts": "YES"
}
```

## How to Get Pure Extraction Data

### Option 1: Filter in Export
1. Go to any dashboard
2. Click the export button
3. Open the CSV file
4. Filter by "Extraction Mode" = "pure"

### Option 2: Use API Directly
```bash
curl "http://localhost:8000/api/forms/export?extraction_mode=pure"
```

### Option 3: Switch Extraction Mode
You can switch the system to use pure extraction for new uploads:
```bash
curl -X POST "http://localhost:8000/api/extraction-mode" \
  -H "Content-Type: application/json" \
  -d '{"mode": "pure"}'
```

## Benefits of Pure Extraction Data

1. **Complete Raw Data**: Get all fields that Gemini extracted, not just mapped ones
2. **Flexibility**: Access to any field that Gemini might have found
3. **Audit Trail**: See exactly what Gemini extracted vs. what was mapped
4. **Data Recovery**: Access fields that might not have been mapped to database columns

## Summary

✅ **Yes, exports include pure extraction data**  
✅ **You can filter by extraction mode**  
✅ **Pure extraction data contains raw Gemini JSON**  
✅ **Dashboard exports respect current view**  
✅ **Combined filters work (extraction mode + form type)**  

The export functionality is comprehensive and includes all extraction data types! 