# Gemini Extraction Modes

This document explains the **dual extraction approach** implemented in the MTA Forms application.

## Overview

The application now supports **dual extraction** where each uploaded form is stored in **both extraction modes simultaneously**:

1. **Pure Extraction** - Stores all Gemini output without field mapping
2. **Mapped Extraction (BETA)** - Maps Gemini output to predefined database fields

**Key Feature**: Every form you upload creates **TWO database entries** - one for each extraction mode, allowing you to compare and switch between approaches seamlessly.

## Extraction Modes

### Mapped Extraction Mode
- **Purpose**: Production-ready extraction with structured data
- **Behavior**: Maps Gemini JSON output to predefined database schema fields
- **Benefits**:
  - Structured, predictable database schema
  - Easy to query and filter specific fields
  - Better performance for database operations
  - Type safety and validation
  - Consistent field names across the application
- **Drawbacks**:
  - Complex mapping logic (200+ lines of key mapping)
  - Brittle - new Gemini output formats can break mappings
  - May miss unexpected fields that Gemini extracts
  - Requires maintenance when forms change

### Pure Extraction Mode
- **Purpose**: Exploration and capturing all possible data
- **Behavior**: Stores complete Gemini output without field mapping
- **Benefits**:
  - Captures everything Gemini finds
  - No mapping maintenance needed
  - More flexible for different form variations
  - Future-proof for new field types
  - Simpler backend logic
- **Drawbacks**:
  - Unstructured data storage
  - Harder to query specific fields efficiently
  - More complex UI logic to handle unknown fields
  - Potential data inconsistency

## Dual Extraction Implementation

The application implements a **dual extraction approach** that stores forms in both modes simultaneously:

### Backend Changes
1. **Dual Processing Function**: `process_gemini_extraction_dual()` - Creates both pure and mapped versions
2. **Processing Functions**:
   - `process_pure_extraction()` - Pure extraction logic
   - `process_mapped_extraction()` - Mapped extraction logic
   - `extract_single_form_pure()` - Single form pure extraction
3. **Upload Handler**: Modified to use dual processing for all uploads

3. **Database Schema Updates**:
   - `raw_extracted_data` - Stores complete raw Gemini output
   - `extraction_mode` - Tracks which mode was used
   - `raw_gemini_json` - Existing field for backward compatibility

4. **API Endpoint**: `/api/extraction-mode` for getting/setting mode

### Frontend Changes
1. **Extraction Mode Toggle**: Button in Dashboard header to switch between viewing modes
2. **Mode Indicator**: Visual indicator showing current viewing mode
3. **Dual Storage Indicator**: Shows "(Forms stored in both modes)" to indicate dual storage
4. **Real-time Updates**: Dashboard reloads when switching between viewing modes
5. **Enhanced Export**: Export button respects current filters and extraction mode

## Usage

### How Dual Extraction Works

When you upload a form, the system automatically creates **TWO database entries**:

1. **Pure Extraction Entry** (`extraction_mode = 'pure'`)
   - Stores complete raw Gemini JSON in `raw_extracted_data`
   - Preserves all original field names and values
   - No field mapping or transformation

2. **Mapped Extraction Entry** (`extraction_mode = 'mapped'`)
   - Maps Gemini fields to database schema
   - Stores structured data in individual columns
   - Includes both mapped fields and raw JSON backup

### Switching Viewing Modes

The dashboard allows you to switch between viewing the data in different modes:

1. **Via UI**: Click the extraction mode button in the Dashboard header
2. **Via API**: 
   ```bash
   # Get current viewing mode
   curl http://localhost:8000/api/extraction-mode
   
   # Switch to pure mode view
   curl -X POST http://localhost:8000/api/extraction-mode \
     -H "Content-Type: application/json" \
     -d '{"mode": "pure"}'
   
   # Switch to mapped mode view
   curl -X POST http://localhost:8000/api/extraction-mode \
     -H "Content-Type: application/json" \
     -d '{"mode": "mapped"}'
   ```

### Export Functionality

The system includes enhanced export capabilities that work with dual extraction:

#### Export Features
- **Filtered Exports**: Export only data from current extraction mode
- **Raw Data Inclusion**: Complete Gemini JSON data included in exports
- **Excel Compatibility**: Properly formatted CSV files for Excel
- **Dynamic Filenames**: Filenames reflect current filters

#### Export Scenarios
```bash
# Export all data
GET /api/forms/export

# Export only pure extraction data
GET /api/forms/export?extraction_mode=pure

# Export only mapped extraction data  
GET /api/forms/export?extraction_mode=mapped

# Export hourly forms only
GET /api/forms/export?form_type=hourly

# Export hourly pure extraction only
GET /api/forms/export?form_type=hourly&extraction_mode=pure
```

#### Generated Filenames
- `exception_forms.csv` - All data
- `exception_forms_pure.csv` - Pure extraction only
- `exception_forms_mapped.csv` - Mapped extraction only
- `exception_forms_hourly.csv` - Hourly forms only
- `exception_forms_hourly_pure.csv` - Hourly pure extraction only

### Recommended Usage Patterns

#### For Production (Mapped Mode)
```python
PURE_GEMINI_EXTRACTION = False  # Use mapped extraction
```
- Better performance and reliability
- Structured data for reporting and filtering
- Consistent user experience

#### For Exploration (Pure Mode)
```python
PURE_GEMINI_EXTRACTION = True  # Use pure extraction
```
- When testing new form types
- When exploring what Gemini can extract
- When you want to capture everything

#### For Development (Hybrid)
- Start with pure mode to see what Gemini extracts
- Switch to mapped mode for production
- Use the toggle button to experiment

## Data Storage

### Mapped Mode Storage
```json
{
  "employee_name": "John Doe",
  "pass_number": "12345678",
  "title": "Operator",
  "raw_extracted_data": "{\"employee_name\": \"John Doe\", \"unexpected_field\": \"value\"}",
  "extraction_mode": "mapped"
}
```

### Pure Mode Storage
```json
{
  "form_type": "hourly",
  "raw_extracted_data": "{\"employee_name\": \"John Doe\", \"unexpected_field\": \"value\"}",
  "extraction_mode": "pure",
  "employee_name": "John Doe"
}
```

## Migration Strategy

### From Existing System
1. **Backward Compatible**: Existing data continues to work
2. **Gradual Migration**: New forms use hybrid approach
3. **Raw Data Preservation**: All Gemini output is preserved

### To Pure Mode
1. Set `PURE_GEMINI_EXTRACTION = True`
2. Upload new forms
3. Review extracted data
4. Decide on field mapping strategy

### To Mapped Mode
1. Set `PURE_GEMINI_EXTRACTION = False`
2. Upload new forms
3. Verify field mapping works correctly
4. Use structured queries and filters

## Testing

Run the test script to see the difference:
```bash
python3 test_extraction_modes.py
```

This will show:
- How the same Gemini output is processed differently
- Field capture comparison
- Pros and cons of each approach

## Best Practices

1. **Start with Pure Mode**: When testing new form types
2. **Use Mapped Mode for Production**: Better performance and reliability
3. **Preserve Raw Data**: Always store complete Gemini output
4. **Monitor Field Mapping**: Watch for unmapped fields in logs
5. **Regular Testing**: Test both modes with new form variations

## Troubleshooting

### Common Issues

1. **Unmapped Fields**: Check logs for "Unmapped Gemini key" messages
2. **Missing Data**: Verify extraction mode is set correctly
3. **UI Issues**: Ensure frontend is reloaded after mode changes
4. **Database Errors**: Check that new columns exist in database

### Debug Commands

```bash
# Check current extraction mode
curl http://localhost:8000/api/extraction-mode

# View raw Gemini output in database
sqlite3 forms.db "SELECT raw_extracted_data FROM exception_forms LIMIT 1;"

# Check extraction mode distribution
sqlite3 forms.db "SELECT extraction_mode, COUNT(*) FROM exception_forms GROUP BY extraction_mode;"
```

## Dashboard Statistics with Pure Extraction

### How Dashboard Highlights Work

The dashboard statistics are now **extraction-mode aware** and work seamlessly with both pure and mapped extraction:

#### Pure Extraction Mode
- **Statistics Source**: Parses `raw_extracted_data` JSON to calculate metrics
- **Field Detection**: Intelligently searches for fields in raw Gemini output
- **Flexible Mapping**: Handles various field name variations (e.g., `overtime_hours`, `overtime`, `hours`)
- **Complete Data**: Captures statistics from all extracted fields, including unexpected ones

#### Mapped Extraction Mode  
- **Statistics Source**: Uses structured database fields
- **Fast Performance**: Direct database queries for statistics
- **Predictable Results**: Consistent field mapping and calculations

#### Filtered Mode (New Implementation)
- **Mode-Specific Statistics**: Shows only data from the current extraction mode
- **Clear Separation**: Pure mode shows only pure extraction data, mapped mode shows only mapped data
- **Accurate Comparisons**: Easy to compare statistics between extraction approaches
- **Better Decision Making**: Helps decide which fields to map based on pure extraction results

### Dashboard Statistics Supported

All dashboard highlights work with **filtered extraction mode**:

1. **Total Forms**: Count of forms from current extraction mode only
2. **Total Overtime**: Calculated from current mode's overtime fields only
3. **Total Job Numbers**: Extracted from current mode's job number fields only
4. **Most Relevant Position**: Determined from current mode's title/position fields only
5. **Most Relevant Location**: Found in current mode's location-related fields only
6. **Most Common Reason** (Supervisor): Parsed from current mode's reason data only

### Filtered Statistics Examples

**Mapped Mode Statistics:**
- Only includes forms with `extraction_mode = 'mapped'`
- Uses structured database fields for calculations
- Fast, reliable statistics for production reporting

**Pure Mode Statistics:**
- Only includes forms with `extraction_mode = 'pure'`
- Parses raw Gemini JSON for calculations
- Shows complete data capture including unexpected fields

### Visual Indicators

- **Extraction Mode Badge**: Shows current mode (Purple for Pure, Green for Mapped) with "(Statistics filtered)" indicator
- **Extraction Mode Button**: Shows current mode and allows switching
- **Mode-Aware Statistics**: All cards reflect only data from the current extraction approach
- **Real-time Updates**: Statistics update automatically when switching modes

### Performance Considerations

- **Pure Mode**: Slower for large datasets due to JSON parsing
- **Mapped Mode**: Faster performance with direct database queries
- **Caching**: Consider implementing result caching for pure mode statistics

## Future Enhancements

1. **Smart Field Detection**: Automatically detect new fields
2. **Dynamic Schema**: Auto-create database columns for new fields
3. **Field Mapping UI**: Visual field mapping interface
4. **Extraction Analytics**: Track extraction success rates
5. **Multi-Mode Support**: Support for different modes per form type
6. **Statistics Caching**: Cache pure extraction statistics for better performance
7. **Advanced Field Mapping**: Machine learning-based field detection 