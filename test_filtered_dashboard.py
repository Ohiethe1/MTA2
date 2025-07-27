#!/usr/bin/env python3
"""
Test script to demonstrate how dashboard statistics are filtered by extraction mode.
This shows how statistics change when filtering by pure vs mapped extraction.
"""

import json
import sys
import os

# Mock data for testing
SAMPLE_DATA = [
    {
        "id": 1,
        "form_type": "hourly",
        "extraction_mode": "pure",
        "raw_extracted_data": json.dumps({
            "employee_name": "John Doe",
            "pass_number": "12345678",
            "title": "Operator",
            "rows": [
                {
                    "line_location": "Line 1",
                    "overtime_hh": "4",
                    "overtime_mm": "15",
                    "ta_job_no": "TA123"
                }
            ]
        })
    },
    {
        "id": 2,
        "form_type": "supervisor",
        "extraction_mode": "pure",
        "raw_extracted_data": json.dumps({
            "employee_name": "Jane Smith",
            "pass_number": "87654321",
            "title": "Supervisor",
            "job_number": "JOB789",
            "overtime_hours": "6:30",
            "report_loc": "Station A",
            "reason_for_overtime": ["RDO"]
        })
    },
    {
        "id": 3,
        "form_type": "hourly",
        "extraction_mode": "mapped",
        "employee_name": "Bob Wilson",
        "pass_number": "11111111",
        "title": "Conductor",
        "overtime_hh": "3",
        "overtime_mm": "45",
        "ta_job_no": "TA789"
    },
    {
        "id": 4,
        "form_type": "supervisor",
        "extraction_mode": "mapped",
        "employee_name": "Alice Johnson",
        "pass_number": "22222222",
        "title": "Supervisor",
        "job_number": "JOB101",
        "overtime_hours": "4:15",
        "report_loc": "Station C",
        "reason_rdo": 1
    }
]

def calculate_filtered_stats(forms, form_type=None, extraction_mode_filter=None):
    """Calculate dashboard statistics filtered by extraction mode"""
    import json
    from collections import Counter
    
    def safe_int(val):
        try:
            return int(val)
        except Exception:
            return 0
    
    total_forms = 0
    total_minutes = 0
    job_numbers = []
    positions = []
    locations = []
    reason_counts = {field: 0 for field in [
        'reason_rdo', 'reason_absentee_coverage', 'reason_no_lunch', 
        'reason_early_report', 'reason_late_clear', 'reason_save_as_oto', 
        'reason_capital_support_go', 'reason_other'
    ]}
    
    for form in forms:
        extraction_mode = form.get('extraction_mode', 'mapped')
        raw_data = form.get('raw_extracted_data')
        
        # Filter by extraction mode if specified
        if extraction_mode_filter and extraction_mode != extraction_mode_filter:
            continue
        
        total_forms += 1
        
        if extraction_mode == 'pure' and raw_data:
            try:
                raw_json = json.loads(raw_data)
                
                # Extract overtime information
                if form.get('form_type') == 'supervisor':
                    overtime_hours = raw_json.get('overtime_hours') or raw_json.get('overtime') or raw_json.get('hours')
                    if overtime_hours and overtime_hours != 'N/A':
                        try:
                            if ':' in str(overtime_hours):
                                hours, minutes = str(overtime_hours).split(':')
                                total_minutes += int(hours) * 60 + int(minutes)
                            else:
                                total_minutes += int(overtime_hours) * 60
                        except:
                            pass
                elif form.get('form_type') == 'hourly':
                    rows = raw_json.get('rows', [])
                    for row in rows:
                        if isinstance(row, dict):
                            hh = safe_int(row.get('overtime_hh', 0))
                            mm = safe_int(row.get('overtime_mm', 0))
                            total_minutes += hh * 60 + mm
                
                # Extract job numbers
                if form.get('form_type') == 'supervisor':
                    job_num = raw_json.get('job_number') or raw_json.get('job') or raw_json.get('job_no')
                    if job_num and job_num != 'N/A':
                        job_numbers.append(str(job_num))
                elif form.get('form_type') == 'hourly':
                    rows = raw_json.get('rows', [])
                    for row in rows:
                        if isinstance(row, dict):
                            ta_job = row.get('ta_job_no') or row.get('job_no')
                            if ta_job and ta_job != 'N/A':
                                job_numbers.append(str(ta_job))
                
                # Extract positions/titles
                title = raw_json.get('title') or raw_json.get('position')
                if title and title != 'N/A':
                    positions.append(title)
                elif form.get('form_type') == 'supervisor':
                    positions.append('Supervisor')
                
                # Extract locations
                if form.get('form_type') == 'supervisor':
                    report_loc = raw_json.get('report_loc') or raw_json.get('report_location')
                    overtime_loc = raw_json.get('overtime_location') or raw_json.get('location')
                    if report_loc and report_loc != 'N/A':
                        locations.append(report_loc)
                    if overtime_loc and overtime_loc != 'N/A':
                        locations.append(overtime_loc)
                elif form.get('form_type') == 'hourly':
                    rows = raw_json.get('rows', [])
                    for row in rows:
                        if isinstance(row, dict):
                            line_loc = row.get('line_location') or row.get('location')
                            if line_loc and line_loc != 'N/A':
                                locations.append(line_loc)
                
                # Extract reason counts for supervisor forms
                if form.get('form_type') == 'supervisor':
                    reasons = raw_json.get('reason_for_overtime', [])
                    if isinstance(reasons, list):
                        for reason in reasons:
                            reason_lower = str(reason).lower()
                            if 'rdo' in reason_lower:
                                reason_counts['reason_rdo'] += 1
                            elif 'early' in reason_lower and 'report' in reason_lower:
                                reason_counts['reason_early_report'] += 1
                
            except json.JSONDecodeError:
                pass
        
        # Use mapped fields as fallback
        if extraction_mode == 'mapped' or not raw_data:
            if form.get('form_type') == 'supervisor':
                overtime_hours = form.get('overtime_hours')
                if overtime_hours and overtime_hours != 'N/A':
                    try:
                        if ':' in str(overtime_hours):
                            hours, minutes = str(overtime_hours).split(':')
                            total_minutes += int(hours) * 60 + int(minutes)
                        else:
                            total_minutes += int(overtime_hours) * 60
                    except:
                        pass
                
                job_num = form.get('job_number')
                if job_num and job_num != 'N/A':
                    job_numbers.append(str(job_num))
                
                title = form.get('title')
                if title and title != 'N/A':
                    positions.append(title)
                else:
                    positions.append('Supervisor')
                
                report_loc = form.get('report_loc')
                overtime_loc = form.get('overtime_location')
                if report_loc and report_loc != 'N/A':
                    locations.append(report_loc)
                if overtime_loc and overtime_loc != 'N/A':
                    locations.append(overtime_loc)
                
                for field in reason_counts.keys():
                    if form.get(field):
                        reason_counts[field] += 1
    
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
    if form_type == 'supervisor' and any(reason_counts.values()):
        most_common_reason_field = max(reason_counts, key=lambda k: reason_counts[k])
        reason_label_map = {
            'reason_rdo': 'RDO',
            'reason_early_report': 'Early Report'
        }
        most_common_reason = {
            'reason': reason_label_map.get(most_common_reason_field, most_common_reason_field),
            'count': reason_counts[most_common_reason_field]
        }
    
    return {
        "total_forms": total_forms,
        "total_overtime": f"{total_overtime_hh}h {total_overtime_mm}m",
        "total_job_numbers": len(job_numbers),
        "unique_job_numbers": len(unique_job_numbers),
        "most_relevant_position": {"position": most_position, "count": most_position_count},
        "most_relevant_location": {"location": most_location, "count": most_location_count},
        "most_common_reason": most_common_reason
    }

def test_filtered_statistics():
    """Test dashboard statistics filtered by extraction mode"""
    print("=== FILTERED DASHBOARD STATISTICS ===")
    
    # Test all data (no filter)
    print("\n1. ALL DATA (No extraction mode filter):")
    stats_all = calculate_filtered_stats(SAMPLE_DATA)
    print(f"   Total Forms: {stats_all['total_forms']}")
    print(f"   Total Overtime: {stats_all['total_overtime']}")
    print(f"   Total Job Numbers: {stats_all['total_job_numbers']}")
    print(f"   Most Relevant Position: {stats_all['most_relevant_position']['position']} ({stats_all['most_relevant_position']['count']} forms)")
    print(f"   Most Relevant Location: {stats_all['most_relevant_location']['location']} ({stats_all['most_relevant_location']['count']} forms)")
    
    # Test pure extraction only
    print("\n2. PURE EXTRACTION ONLY:")
    stats_pure = calculate_filtered_stats(SAMPLE_DATA, extraction_mode_filter='pure')
    print(f"   Total Forms: {stats_pure['total_forms']}")
    print(f"   Total Overtime: {stats_pure['total_overtime']}")
    print(f"   Total Job Numbers: {stats_pure['total_job_numbers']}")
    print(f"   Most Relevant Position: {stats_pure['most_relevant_position']['position']} ({stats_pure['most_relevant_position']['count']} forms)")
    print(f"   Most Relevant Location: {stats_pure['most_relevant_location']['location']} ({stats_pure['most_relevant_location']['count']} forms)")
    
    # Test mapped extraction only
    print("\n3. MAPPED EXTRACTION ONLY:")
    stats_mapped = calculate_filtered_stats(SAMPLE_DATA, extraction_mode_filter='mapped')
    print(f"   Total Forms: {stats_mapped['total_forms']}")
    print(f"   Total Overtime: {stats_mapped['total_overtime']}")
    print(f"   Total Job Numbers: {stats_mapped['total_job_numbers']}")
    print(f"   Most Relevant Position: {stats_mapped['most_relevant_position']['position']} ({stats_mapped['most_relevant_position']['count']} forms)")
    print(f"   Most Relevant Location: {stats_mapped['most_relevant_location']['location']} ({stats_mapped['most_relevant_location']['count']} forms)")
    
    # Test supervisor forms only (pure extraction)
    print("\n4. SUPERVISOR FORMS - PURE EXTRACTION ONLY:")
    stats_supervisor_pure = calculate_filtered_stats(SAMPLE_DATA, form_type='supervisor', extraction_mode_filter='pure')
    print(f"   Total Forms: {stats_supervisor_pure['total_forms']}")
    print(f"   Total Overtime: {stats_supervisor_pure['total_overtime']}")
    print(f"   Most Common Reason: {stats_supervisor_pure['most_common_reason']['reason']} ({stats_supervisor_pure['most_common_reason']['count']} forms)")
    print(f"   Most Relevant Location: {stats_supervisor_pure['most_relevant_location']['location']} ({stats_supervisor_pure['most_relevant_location']['count']} forms)")

def demonstrate_benefits():
    """Demonstrate the benefits of filtered statistics"""
    print("\n=== BENEFITS OF FILTERED STATISTICS ===")
    
    print("✅ Mapped Mode Benefits:")
    print("   - See only structured, reliable data")
    print("   - Fast performance with direct database queries")
    print("   - Consistent field mapping and calculations")
    print("   - Predictable statistics for reporting")
    
    print("\n✅ Pure Mode Benefits:")
    print("   - See all data that Gemini extracted")
    print("   - Discover unexpected fields and patterns")
    print("   - Complete data capture without loss")
    print("   - Flexible field detection")
    
    print("\n✅ Filtered Mode Benefits:")
    print("   - Clear separation between extraction approaches")
    print("   - Accurate statistics for each mode")
    print("   - Easy comparison between pure and mapped results")
    print("   - Better decision making for field mapping")

if __name__ == "__main__":
    test_filtered_statistics()
    demonstrate_benefits()
    
    print("\n=== IMPLEMENTATION SUMMARY ===")
    print("The dashboard now filters statistics by extraction mode:")
    print("1. Mapped Mode: Shows only data from mapped extraction")
    print("2. Pure Mode: Shows only data from pure extraction")
    print("3. Visual indicators show which mode is active")
    print("4. Statistics update automatically when switching modes") 