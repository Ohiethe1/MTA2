import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
// import { useAuth } from '../contexts/AuthContext';

interface FormData {
  id: string;
  fileName: string;
  uploadDate: string;
  status: 'pending' | 'processed' | 'error';
  extractedData?: any;
  // Add all the Exception Claim Form fields
  passNumber?: string;
  title?: string;
  employeeName?: string;
  rdos?: string;
  actualOTDate?: string;
  div?: string;
  exceptionCode?: string;
  location?: string;
  runNo?: string;
  exceptionTimeFromHH?: string;
  exceptionTimeFromMM?: string;
  exceptionTimeToHH?: string;
  exceptionTimeToMM?: string;
  overtimeHH?: string;
  overtimeMM?: string;
  bonusHH?: string;
  bonusMM?: string;
  niteDiffHH?: string;
  niteDiffMM?: string;
  taJobNo?: string;
  oto?: string;
  otoAmountSaved?: string;
  enteredInUTS?: string;
  comments?: string;
  supervisorName?: string;
  supervisorPassNo?: string;
  regular_assignment?: string;
  report?: string;
  relief?: string;
  todays_date?: string;
  report_loc?: string;
}

interface DashboardProps {
  filterType?: 'hourly' | 'supervisor';
  heading?: string;
}

interface FilterState {
  search: string;
  status: string;
  dateFrom: string;
  dateTo: string;
  employeeName: string;
  passNumber: string;
  title: string;
  location: string;
  jobNumber: string;
  formType: string;
}

const Dashboard: React.FC<DashboardProps> = ({ filterType, heading }) => {
  const [dashboard, setDashboard] = useState<any>(null);
  const [selectedFormDetails, setSelectedFormDetails] = useState<any>(null);
  const [detailsLoading, setDetailsLoading] = useState(false);
  const [detailsError, setDetailsError] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [isEditing, setIsEditing] = useState(false);
  const [editForm, setEditForm] = useState<any>(null);
  const [editRows, setEditRows] = useState<any[]>([]);
  const [saveLoading, setSaveLoading] = useState(false);
  const [saveError, setSaveError] = useState('');
  const [filters, setFilters] = useState<FilterState>({
    search: '',
    status: '',
    dateFrom: '',
    dateTo: '',
    employeeName: '',
    passNumber: '',
    title: '',
    location: '',
    jobNumber: '',
    formType: ''
  });
  const [showFilters, setShowFilters] = useState(false);
  const [isEditingRawJson, setIsEditingRawJson] = useState(false);
  const [rawJsonEdit, setRawJsonEdit] = useState('');
  const [showEditModal, setShowEditModal] = useState(false);
  const [extractionMode, setExtractionMode] = useState<'pure' | 'mapped'>('mapped');
  const [showExtractionModeModal, setShowExtractionModeModal] = useState(false);
  // const { user } = useAuth ? useAuth() : { user: null };

  useEffect(() => {
    setLoading(true);
    setError('');
    
    // Load extraction mode first
    fetch('http://localhost:8000/api/extraction-mode')
      .then(res => res.json())
      .then(data => {
        setExtractionMode(data.mode);
        
        // Then load dashboard data with extraction mode filter
        let url = 'http://localhost:8000/api/dashboard';
        const params = new URLSearchParams();
        
        if (filterType === 'hourly') {
          params.append('form_type', 'hourly');
        } else if (filterType === 'supervisor') {
          params.append('form_type', 'supervisor');
        }
        
        // Add extraction mode filter to show only data from current mode
        params.append('extraction_mode', data.mode);
        
        if (params.toString()) {
          url += '?' + params.toString();
        }
        
        return fetch(url);
      })
      .then(res => res.json())
      .then(data => {
        setDashboard(data);
        setLoading(false);
      })
      .catch(err => {
        setError('Failed to load dashboard data.');
        setLoading(false);
      });
  }, [filterType, extractionMode]);

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'processed':
        return 'bg-green-100 text-green-800';
      case 'pending':
        return 'bg-yellow-100 text-yellow-800';
      case 'error':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  // Helper to format date
  const formatDate = (dateString: string) => {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    return date.toLocaleString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  // Helper to prettify field names
  const prettyField = (key: string) => {
    const map: Record<string, string> = {
      pass_number: 'Pass Number',
      title: 'Title',
      employee_name: 'Employee Name',
      rdos: 'RDOS',
      actual_ot_date: 'Actual OT Date',
      div: 'DIV',
      comments: 'Comments',
      supervisor_name: 'Supervisor Name',
      supervisor_pass_no: 'Supervisor Pass No.',
      oto: 'OTO',
      oto_amount_saved: 'OTO Amount Saved',
      entered_in_uts: 'Entered in UTS',
      id: 'Form ID',
    };
    return map[key] || key.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase());
  };

  // Helper to format upload date
  const formatUploadDate = (dateString: string) => {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    if (isNaN(date.getTime())) return 'N/A';
    return date.toLocaleString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  // Helper to format time with colon
  const formatTime = (timeString: string) => {
    if (!timeString) return 'N/A';
    // Remove any non-digit characters and ensure it's 4 digits
    const cleanTime = timeString.toString().replace(/\D/g, '');
    if (cleanTime.length === 4) {
      return `${cleanTime.slice(0, 2)}:${cleanTime.slice(2)}`;
    }
    return timeString; // Return original if not 4 digits
  };

  const handleViewForm = (form: FormData) => {
    // setSelectedForm(form); // This state is removed
    // setShowModal(true); // This state is removed
  };

  const closeModal = () => {
    // setShowModal(false); // This state is removed
    // setSelectedForm(null); // This state is removed
  };

  const handleViewDetails = async (formId: number) => {
    console.log('handleViewDetails called with formId:', formId, 'extractionMode:', extractionMode);
    setDetailsLoading(true);
    setDetailsError('');
    setSelectedFormDetails(null);
    try {
      const response = await fetch(`http://localhost:8000/api/form/${formId}?extraction_mode=${extractionMode}`);
      const data = await response.json();
      console.log('Response status:', response.status, 'Data:', data);
      if (response.ok) {
        console.log('Setting selectedFormDetails with data:', data);
        setSelectedFormDetails(data);
      } else if (response.status === 404 && extractionMode === 'pure') {
        console.log('404 for pure mode, trying fallback to mapped');
        // For pure extraction mode, if form not found, try to get the mapped version to show raw data
        const fallbackResponse = await fetch(`http://localhost:8000/api/form/${formId}?extraction_mode=mapped`);
        const fallbackData = await fallbackResponse.json();
        console.log('Fallback response status:', fallbackResponse.status, 'Fallback data:', fallbackData);
                  if (fallbackResponse.ok) {
            if (fallbackData.form.raw_extracted_data) {
              console.log('Setting fallback data with raw_extracted_data');
              // Show the mapped form but indicate it's showing raw data from mapped version
              setSelectedFormDetails({
                ...fallbackData,
                isFallbackToMapped: true
              });
            } else {
              console.log('No raw_extracted_data available');
              // Set the form details so the modal opens, but with an error message
              setSelectedFormDetails({
                ...fallbackData,
                isFallbackToMapped: true,
                noRawDataAvailable: true
              });
            }
          } else {
            console.log('Fallback also failed');
            setDetailsError('No pure extraction data available for this form. This form was processed before dual extraction was implemented.');
          }
      } else {
        console.log('Other error:', data.error);
        setDetailsError(data.error || 'Failed to load form details.');
      }
    } catch (err) {
      console.log('Network error:', err);
      setDetailsError('Network or server error.');
    }
    setDetailsLoading(false);
  };
  const closeDetailsModal = () => {
    setSelectedFormDetails(null);
    setDetailsError('');
  };

  const handleEdit = () => {
    setEditForm({ ...selectedFormDetails.form });
    setEditRows(selectedFormDetails.rows.map((row: any) => ({ ...row })));
    setShowEditModal(true);
  };

  const handleEditFormChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setEditForm((prev: any) => ({ ...prev, [name]: value }));
  };

  // Update handleEditRowChange to accept (idx, field, value)
  const handleEditRowChange = (idx: number, field: string, value: string) => {
    setEditRows((prev) => prev.map((row, i) => i === idx ? { ...row, [field]: value } : row));
  };

  const handleSaveEdit = async () => {
    setSaveLoading(true);
    setSaveError('');
    try {
      const response = await fetch(`http://localhost:8000/api/form/${editForm.id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ form: editForm, rows: editRows }),
      });
      const data = await response.json();
      if (response.ok) {
        // Re-fetch the latest form details from the backend
        const detailsRes = await fetch(`http://localhost:8000/api/form/${editForm.id}?extraction_mode=${extractionMode}`);
        const detailsData = await detailsRes.json();
        setSelectedFormDetails(detailsData);
        setShowEditModal(false);
        // Re-fetch dashboard data to update the table
        let url = 'http://localhost:8000/api/dashboard';
        if (filterType === 'hourly') {
          url += '?form_type=hourly';
        } else if (filterType === 'supervisor') {
          url += '?form_type=supervisor';
        }
        fetch(url)
          .then(res => res.json())
          .then(data => {
            setDashboard(data);
          });
      } else {
        setSaveError(data.error || 'Failed to save changes.');
      }
    } catch (err) {
      setSaveError('Network or server error.');
    }
    setSaveLoading(false);
  };

  const handleCancelEdit = () => {
    setShowEditModal(false);
    setSaveError('');
  };

  const handleEditRawJson = () => {
    if (selectedFormDetails?.form?.raw_gemini_json) {
      try {
        const parsed = JSON.parse(selectedFormDetails.form.raw_gemini_json);
        setRawJsonEdit(JSON.stringify(parsed, null, 2));
        setIsEditingRawJson(true);
      } catch {
        setRawJsonEdit(selectedFormDetails.form.raw_gemini_json);
        setIsEditingRawJson(true);
      }
    }
  };

  const handleSaveRawJson = async () => {
    try {
      // Validate JSON
      JSON.parse(rawJsonEdit);
      
      setSaveLoading(true);
      setSaveError('');
      
      const response = await fetch(`http://localhost:8000/api/form/${selectedFormDetails.form.id}?extraction_mode=${extractionMode}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          form: { ...selectedFormDetails.form, raw_gemini_json: rawJsonEdit },
          rows: selectedFormDetails.rows 
        }),
      });
      
      const data = await response.json();
      if (response.ok) {
        // Re-fetch the latest form details
        const detailsRes = await fetch(`http://localhost:8000/api/form/${selectedFormDetails.form.id}`);
        const detailsData = await detailsRes.json();
        setSelectedFormDetails(detailsData);
        setIsEditingRawJson(false);
        
        // Re-fetch dashboard data to update the table
        let url = 'http://localhost:8000/api/dashboard';
        if (filterType === 'hourly') {
          url += '?form_type=hourly';
        } else if (filterType === 'supervisor') {
          url += '?form_type=supervisor';
        }
        fetch(url)
          .then(res => res.json())
          .then(data => {
            setDashboard(data);
          });
      } else {
        setSaveError(data.error || 'Failed to save raw JSON.');
      }
    } catch (err) {
      setSaveError('Invalid JSON format.');
    }
    setSaveLoading(false);
  };

  const handleCancelRawJson = () => {
    setIsEditingRawJson(false);
    setSaveError('');
  };

  const handleToggleExtractionMode = async () => {
    const newMode = extractionMode === 'pure' ? 'mapped' : 'pure';
    try {
      const response = await fetch('http://localhost:8000/api/extraction-mode', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ mode: newMode }),
      });
      const data = await response.json();
      if (response.ok) {
        setExtractionMode(newMode);
        setShowExtractionModeModal(false);
        // Trigger useEffect to reload dashboard data with new extraction mode filter
        setLoading(true);
      } else {
        alert(data.error || 'Failed to change extraction mode.');
      }
    } catch (err) {
      alert('Network or server error.');
    }
  };

  // Filter forms based on search and filters
  const getFilteredForms = () => {
    let filteredForms: any[] = dashboard?.forms || [];
    
    // First filter by form type
    if (filterType === 'hourly') {
      filteredForms = filteredForms.filter((form: any) => !form.form_type || form.form_type === 'hourly');
    } else if (filterType === 'supervisor') {
      filteredForms = filteredForms.filter((form: any) => form.form_type === 'supervisor');
    }
    // For general dashboard (no filterType), show all forms (both hourly and supervisor)

    // Apply search filter
    if (filters.search) {
      const searchTerm = filters.search.toLowerCase();
      filteredForms = filteredForms.filter((form: any) => {
        const searchableFields = [
          form.pass_number,
          form.employee_name,
          form.title,
          form.status,
          form.comments,
          form.fileName,
          form.regular_assignment,
          form.report_loc,
          form.overtime_location,
          form.job_number,
          form.ta_job_no
        ].filter(Boolean).join(' ').toLowerCase();
        
        return searchableFields.includes(searchTerm);
      });
    }

    // Apply individual filters
    if (filters.status) {
      filteredForms = filteredForms.filter((form: any) => form.status === filters.status);
    }

    if (filters.employeeName) {
      filteredForms = filteredForms.filter((form: any) => 
        form.employee_name?.toLowerCase().includes(filters.employeeName.toLowerCase())
      );
    }

    if (filters.passNumber) {
      filteredForms = filteredForms.filter((form: any) => 
        form.pass_number?.toLowerCase().includes(filters.passNumber.toLowerCase())
      );
    }

    if (filters.title) {
      filteredForms = filteredForms.filter((form: any) => 
        form.title?.toLowerCase().includes(filters.title.toLowerCase())
      );
    }

    if (filters.location) {
      filteredForms = filteredForms.filter((form: any) => {
        const locationFields = [
          form.report_loc,
          form.overtime_location,
          form.regular_assignment
        ].filter(Boolean).join(' ').toLowerCase();
        return locationFields.includes(filters.location.toLowerCase());
      });
    }

    if (filters.jobNumber) {
      filteredForms = filteredForms.filter((form: any) => {
        const jobFields = [
          form.job_number,
          form.ta_job_no
        ].filter(Boolean).join(' ').toLowerCase();
        return jobFields.includes(filters.jobNumber.toLowerCase());
      });
    }

    // Apply date range filter
    if (filters.dateFrom || filters.dateTo) {
      filteredForms = filteredForms.filter((form: any) => {
        const uploadDate = new Date(form.upload_date);
        if (filters.dateFrom && uploadDate < new Date(filters.dateFrom)) return false;
        if (filters.dateTo && uploadDate > new Date(filters.dateTo)) return false;
        return true;
      });
    }

    // Apply form type filter (only for general dashboard)
    if (!filterType && filters.formType) {
      if (filters.formType === 'hourly') {
        filteredForms = filteredForms.filter((form: any) => !form.form_type || form.form_type === 'hourly');
      } else if (filters.formType === 'supervisor') {
        filteredForms = filteredForms.filter((form: any) => form.form_type === 'supervisor');
      }
    }

    return filteredForms;
  };

  const filteredForms = getFilteredForms();

  // Use backend summary stats for cards
  const totalForms = filteredForms.length;
  const totalOvertime = dashboard?.total_overtime ?? '0h 0m';
  const totalJobNumbers = dashboard?.total_job_numbers ?? 0;
  const uniqueJobNumbers = dashboard?.unique_job_numbers ?? 0;
  const mostRelevantJob = dashboard?.most_relevant_position ?? { position: 'N/A', count: 0 };
  const mostRelevantLocation = dashboard?.most_relevant_location ?? { location: 'N/A', count: 0 };

  // Filter forms by search and type
  // let filteredForms = dashboard?.forms || [];
  // if (filterType === 'supervisor') {
  //   filteredForms = [];
  // }

  const handleExport = () => {
    // Build export URL with current filters
    let exportUrl = 'http://localhost:8000/api/forms/export';
    const params = new URLSearchParams();
    
    if (filterType) {
      params.append('form_type', filterType);
    }
    
    // Add extraction mode filter
    params.append('extraction_mode', extractionMode);
    
    if (params.toString()) {
      exportUrl += '?' + params.toString();
    }
    
    window.open(exportUrl, '_blank');
  };

  const handleDeleteForm = async (formId: number) => {
    if (!window.confirm('Are you sure you want to delete this form?')) return;
    try {
      const response = await fetch(`http://localhost:8000/api/form/${formId}`, {
        method: 'DELETE',
      });
      const data = await response.json();
      if (response.ok) {
        setDashboard((prev: any) => ({
          ...prev,
          forms: prev.forms.filter((f: any) => f.id !== formId),
        }));
      } else {
        alert(data.error || 'Failed to delete form.');
      }
    } catch (err) {
      alert('Network or server error.');
    }
  };

  const handleFilterChange = (key: keyof FilterState, value: string) => {
    setFilters(prev => ({ ...prev, [key]: value }));
  };

  const clearAllFilters = () => {
    setFilters({
      search: '',
      status: '',
      dateFrom: '',
      dateTo: '',
      employeeName: '',
      passNumber: '',
      title: '',
      location: '',
      jobNumber: '',
      formType: ''
    });
  };

  const hasActiveFilters = () => {
    return Object.values(filters).some(value => value !== '');
  };

  // Helper to get form type label
  const getFormTypeLabel = (form: any) => {
    if (form.form_type === 'supervisor') {
      return 'Supervisor';
    } else {
      return 'Hourly';
    }
  };

  // Helper to get form type color
  const getFormTypeColor = (form: any) => {
    if (form.form_type === 'supervisor') {
      return 'bg-purple-100 text-purple-800';
    } else {
      return 'bg-blue-100 text-blue-800';
    }
  };

  // Remove getFilteredProcessedForms and use filteredForms for table only
  // The summary cards use backend stats directly
  const hasStats = filteredForms.length > 0;

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }
  if (error) {
    return <div className="text-center text-red-600 mt-8">{error}</div>;
  }
  if (!dashboard) {
    return <div className="text-center text-gray-600 mt-8">No dashboard data available.</div>;
  }

  return (
    <div className="max-w-7xl mx-auto">
      <div className="mb-8">
        <div className="flex items-center justify-between">
          <h1
            className="text-3xl font-bold text-gray-900"
            style={filterType === 'supervisor' ? { wordSpacing: '0.12em' } : {}}
          >
            {filterType === 'hourly'
              ? 'Exception Claim Dashboard'
              : filterType === 'supervisor'
                ? 'Overtime Authorization Forms Dashboard (Supervisors)'
                : heading || 'MTA Forms Dashboard'}
          </h1>
          <div className={`flex items-center space-x-2 px-3 py-2 rounded-lg ${
            extractionMode === 'pure' 
              ? 'bg-purple-100 text-purple-800' 
              : 'bg-green-100 text-green-800'
          }`}>
            <svg className="w-4 h-4" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
            </svg>
            <span className="text-sm font-medium">
              {extractionMode === 'pure' ? 'Pure' : 'Mapped'} Extraction Mode
              {extractionMode === 'mapped' && (
                <span className="ml-1 px-1 py-0.5 bg-yellow-500 text-white text-xs rounded-full font-bold">BETA</span>
              )}
            </span>
            <span className="text-xs opacity-75">(Forms stored in both modes)</span>
          </div>
        </div>
      </div>

      {/* Tracker Section */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5 gap-6 mb-8">
        {/* General Dashboard Cards */}
        {!filterType && (
          <>
            <div className="bg-white p-6 rounded-xl shadow-lg border border-gray-200 hover:shadow-xl transition-shadow">
              <div className="flex items-start space-x-4">
                <div className="flex-shrink-0">
                  <div className="w-12 h-12 bg-blue-100 rounded-xl flex items-center justify-center">
                    <svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                    </svg>
                  </div>
                </div>
                <div className="flex-1 min-w-0">
                  <div className="text-sm font-medium text-gray-500 uppercase tracking-wide mb-1">Total Forms</div>
                  <div className="text-2xl font-bold text-gray-900">{totalForms}</div>
                </div>
              </div>
            </div>
            <div className="bg-white p-6 rounded-xl shadow-lg border border-gray-200 hover:shadow-xl transition-shadow">
              <div className="flex items-start space-x-4">
                <div className="flex-shrink-0">
                  <div className="w-12 h-12 bg-green-100 rounded-xl flex items-center justify-center">
                    <svg className="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                  </div>
                </div>
                <div className="flex-1 min-w-0">
                  <div className="text-sm font-medium text-gray-500 uppercase tracking-wide mb-1">Total Overtime</div>
                  <div className="text-2xl font-bold text-gray-900">{totalOvertime}</div>
                </div>
              </div>
            </div>
            <div className="bg-white p-6 rounded-xl shadow-lg border border-gray-200 hover:shadow-xl transition-shadow">
              <div className="flex items-start space-x-4">
                <div className="flex-shrink-0">
                  <div className="w-12 h-12 bg-purple-100 rounded-xl flex items-center justify-center">
                    <svg className="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 20l4-16m2 16l4-16M6 9h14M4 15h14" />
                    </svg>
                  </div>
                </div>
                <div className="flex-1 min-w-0">
                  <div className="text-sm font-medium text-gray-500 uppercase tracking-wide mb-1">Total Job Numbers</div>
                  <div className="text-2xl font-bold text-gray-900">{totalJobNumbers}</div>
                  <div className="text-xs text-gray-400 font-medium mt-1">
                    {uniqueJobNumbers} unique
                  </div>
                </div>
              </div>
            </div>
            <div className="bg-white p-6 rounded-xl shadow-lg border border-gray-200 hover:shadow-xl transition-shadow">
              <div className="flex items-start space-x-4">
                <div className="flex-shrink-0">
                  <div className="w-12 h-12 bg-orange-100 rounded-xl flex items-center justify-center">
                    <svg className="w-6 h-6 text-orange-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                    </svg>
                  </div>
                </div>
                <div className="flex-1 min-w-0">
                  <div className="text-sm font-medium text-gray-500 uppercase tracking-wide mb-1">Most Relevant Position</div>
                  <div className="text-lg font-bold text-gray-900 truncate">
                    {mostRelevantJob.position}
                  </div>
                  <div className="text-xs text-gray-400 font-medium mt-1">
                    {mostRelevantJob.count} forms
                  </div>
                </div>
              </div>
            </div>
            <div className="bg-white p-6 rounded-xl shadow-lg border border-gray-200 hover:shadow-xl transition-shadow">
              <div className="flex items-start space-x-4">
                <div className="flex-shrink-0">
                  <div className="w-12 h-12 bg-red-100 rounded-xl flex items-center justify-center">
                    <svg className="w-6 h-6 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                    </svg>
                  </div>
                </div>
                <div className="flex-1 min-w-0">
                  <div className="text-sm font-medium text-gray-500 uppercase tracking-wide mb-1">Most Relevant Line/Location</div>
                  <div className="text-lg font-bold text-gray-900 truncate">
                    {mostRelevantLocation.location}
                  </div>
                  <div className="text-xs text-gray-500 font-medium mt-1">
                    {(() => {
                      if (!filterType && mostRelevantLocation.form_type) {
                        return mostRelevantLocation.form_type === 'supervisor' ? '(supervisor)' : '(hourly employees)';
                      }
                      return '';
                    })()}
                  </div>
                  <div className="text-xs text-gray-400 font-medium mt-1">
                    {mostRelevantLocation.count} forms
                  </div>
                </div>
              </div>
            </div>
          </>
        )}
        {/* Hourly Employees Dashboard Cards */}
        {filterType === 'hourly' && (
          <>
            <div className="bg-white p-6 rounded-xl shadow-lg border border-gray-200 hover:shadow-xl transition-shadow">
              <div className="flex items-start space-x-4">
                <div className="flex-shrink-0">
                  <div className="w-12 h-12 bg-blue-100 rounded-xl flex items-center justify-center">
                    <svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                    </svg>
                  </div>
                </div>
                <div className="flex-1 min-w-0">
                  <div className="text-sm font-medium text-gray-500 uppercase tracking-wide mb-1">Total Forms</div>
                  <div className="text-2xl font-bold text-gray-900">{totalForms}</div>
                </div>
              </div>
            </div>
            <div className="bg-white p-6 rounded-xl shadow-lg border border-gray-200 hover:shadow-xl transition-shadow">
              <div className="flex items-start space-x-4">
                <div className="flex-shrink-0">
                  <div className="w-12 h-12 bg-green-100 rounded-xl flex items-center justify-center">
                    <svg className="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                  </div>
                </div>
                <div className="flex-1 min-w-0">
                  <div className="text-sm font-medium text-gray-500 uppercase tracking-wide mb-1">Total Overtime</div>
                  <div className="text-2xl font-bold text-gray-900">{totalOvertime}</div>
                </div>
              </div>
            </div>
            <div className="bg-white p-6 rounded-xl shadow-lg border border-gray-200 hover:shadow-xl transition-shadow">
              <div className="flex items-start space-x-4">
                <div className="flex-shrink-0">
                  <div className="w-12 h-12 bg-purple-100 rounded-xl flex items-center justify-center">
                    <svg className="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 20l4-16m2 16l4-16M6 9h14M4 15h14" />
                    </svg>
                  </div>
                </div>
                <div className="flex-1 min-w-0">
                  <div className="text-sm font-medium text-gray-500 uppercase tracking-wide mb-1">Total Job Numbers</div>
                  <div className="text-2xl font-bold text-gray-900">{totalJobNumbers}</div>
                  <div className="text-xs text-gray-400 font-medium mt-1">
                    {uniqueJobNumbers} unique
                  </div>
                </div>
              </div>
            </div>
            <div className="bg-white p-6 rounded-xl shadow-lg border border-gray-200 hover:shadow-xl transition-shadow">
              <div className="flex items-start space-x-4">
                <div className="flex-shrink-0">
                  <div className="w-12 h-12 bg-orange-100 rounded-xl flex items-center justify-center">
                    <svg className="w-6 h-6 text-orange-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                    </svg>
                  </div>
                </div>
                <div className="flex-1 min-w-0">
                  <div className="text-sm font-medium text-gray-500 uppercase tracking-wide mb-1">Most Relevant Position</div>
                  <div className="text-lg font-bold text-gray-900 truncate">
                    {mostRelevantJob.position}
                  </div>
                  <div className="text-xs text-gray-400 font-medium mt-1">
                    {mostRelevantJob.count} forms
                  </div>
                </div>
              </div>
            </div>
            <div className="bg-white p-6 rounded-xl shadow-lg border border-gray-200 hover:shadow-xl transition-shadow">
              <div className="flex items-start space-x-4">
                <div className="flex-shrink-0">
                  <div className="w-12 h-12 bg-red-100 rounded-xl flex items-center justify-center">
                    <svg className="w-6 h-6 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                    </svg>
                  </div>
                </div>
                <div className="flex-1 min-w-0">
                  <div className="text-sm font-medium text-gray-500 uppercase tracking-wide mb-1">Most Relevant Line/Location</div>
                  <div className="text-lg font-bold text-gray-900 truncate">
                    {mostRelevantLocation.location}
                  </div>
                  <div className="text-xs text-gray-400 font-medium mt-1">
                    {mostRelevantLocation.count} forms
                  </div>
                </div>
              </div>
            </div>
          </>
        )}
        {/* Supervisor Dashboard Cards */}
        {filterType === 'supervisor' && (
          <>
            <div className="bg-white p-6 rounded-xl shadow-lg border border-gray-200 hover:shadow-xl transition-shadow">
              <div className="flex items-start space-x-4">
                <div className="flex-shrink-0">
                  <div className="w-12 h-12 bg-blue-100 rounded-xl flex items-center justify-center">
                    <svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                    </svg>
                  </div>
                </div>
                <div className="flex-1 min-w-0">
                  <div className="text-sm font-medium text-gray-500 uppercase tracking-wide mb-1">Total Forms</div>
                  <div className="text-2xl font-bold text-gray-900">{totalForms}</div>
                </div>
              </div>
            </div>
            <div className="bg-white p-6 rounded-xl shadow-lg border border-gray-200 hover:shadow-xl transition-shadow">
              <div className="flex items-start space-x-4">
                <div className="flex-shrink-0">
                  <div className="w-12 h-12 bg-green-100 rounded-xl flex items-center justify-center">
                    <svg className="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                  </div>
                </div>
                <div className="flex-1 min-w-0">
                  <div className="text-sm font-medium text-gray-500 uppercase tracking-wide mb-1">Total Overtime</div>
                  <div className="text-2xl font-bold text-gray-900">{totalOvertime}</div>
                </div>
              </div>
            </div>
            {/* Only show Most Common Reason for Overtime if supervisor dashboard */}
            <div className="bg-white p-6 rounded-xl shadow-lg border border-gray-200 hover:shadow-xl transition-shadow">
              <div className="flex items-start space-x-4">
                <div className="flex-shrink-0">
                  <div className="w-12 h-12 bg-yellow-100 rounded-xl flex items-center justify-center">
                    <svg className="w-6 h-6 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 17v-2a4 4 0 014-4h2a4 4 0 014 4v2" />
                      <circle cx="12" cy="7" r="4" />
                    </svg>
                  </div>
                </div>
                <div className="flex-1 min-w-0">
                  <div className="text-sm font-medium text-gray-500 uppercase tracking-wide mb-1">Most Common Reason</div>
                  <div className="text-lg font-bold text-gray-900 truncate">
                    {dashboard?.most_common_reason?.reason || 'N/A'}
                  </div>
                  <div className="text-xs text-gray-400 font-medium mt-1">
                    {dashboard?.most_common_reason?.count || 0} forms
                  </div>
                </div>
              </div>
            </div>
            {/* Most Relevant Line/Location for supervisor forms only */}
            <div className="bg-white p-6 rounded-xl shadow-lg border border-gray-200 hover:shadow-xl transition-shadow">
              <div className="flex items-start space-x-4">
                <div className="flex-shrink-0">
                  <div className="w-12 h-12 bg-red-100 rounded-xl flex items-center justify-center">
                    <svg className="w-6 h-6 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                    </svg>
                  </div>
                </div>
                <div className="flex-1 min-w-0">
                  <div className="text-sm font-medium text-gray-500 uppercase tracking-wide mb-1">Most Relevant Line/Location</div>
                  <div className="text-lg font-bold text-gray-900 truncate">
                    {mostRelevantLocation.location}
                  </div>
                  <div className="text-xs text-gray-400 font-medium mt-1">
                    {mostRelevantLocation.count} forms
                  </div>
                </div>
              </div>
            </div>
          </>
        )}
      </div>

      {/* Uploaded Forms Table */}
      <div className="bg-white rounded-xl shadow-lg overflow-hidden border border-gray-200 mt-8">
        <div className="px-8 py-6 border-b border-gray-200 bg-gray-50 flex flex-col md:flex-row md:items-center md:justify-between gap-4">
          <h2 className="text-2xl font-bold text-gray-800">Uploaded Forms ({filteredForms.length})</h2>
          <div className="flex gap-2 items-center">
            {/* Search Input */}
            <div className="relative">
              <input
                type="text"
                placeholder="Search by Pass Number, Name, Title, Status, Line/Location, Comments..."
                value={filters.search}
                onChange={e => handleFilterChange('search', e.target.value)}
                className="border rounded px-3 py-2 text-sm w-64 pr-8"
              />
              {filters.search && (
                <button
                  onClick={() => handleFilterChange('search', '')}
                  className="absolute right-2 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
                >
                  ×
                </button>
              )}
            </div>
            
            {/* Filter Toggle Button */}
            <button
              onClick={() => setShowFilters(!showFilters)}
              className={`px-3 py-2 rounded-lg font-semibold text-sm transition-colors ${
                showFilters 
                  ? 'bg-blue-600 text-white hover:bg-blue-700' 
                  : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
              }`}
            >
              <svg className="w-4 h-4 inline-block mr-1" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.207A1 1 0 013 6.5V4z" />
              </svg>
              Filters {hasActiveFilters() && <span className="ml-1 bg-red-500 text-white text-xs rounded-full px-1.5 py-0.5">●</span>}
            </button>
            
                    <button
          onClick={() => setShowExtractionModeModal(true)}
          className={`px-3 py-1.5 rounded-lg font-semibold text-sm transition-colors ${
            extractionMode === 'pure'
              ? 'bg-purple-600 text-white hover:bg-purple-700'
              : 'bg-green-600 text-white hover:bg-green-700'
          }`}
          title={`Current mode: ${extractionMode === 'pure' ? 'Pure Gemini extraction' : 'Mapped field extraction (Beta)'}`}
        >
          <svg className="w-4 h-4 inline-block mr-2 -mt-1" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
          </svg>
          {extractionMode === 'pure' ? 'Pure Extraction' : 'Mapped Extraction'}
          {extractionMode === 'mapped' && (
            <span className="ml-1 px-1.5 py-0.5 bg-yellow-500 text-white text-xs rounded-full font-bold">BETA</span>
          )}
        </button>
            
            <button
              onClick={handleExport}
              className="bg-gradient-to-r from-blue-500 to-blue-700 text-white px-3 py-1.5 rounded-lg font-semibold shadow hover:from-blue-600 hover:to-blue-800 transition-colors relative group text-sm"
              title="Download a CSV of all forms in the system"
            >
              <svg className="w-4 h-4 inline-block mr-2 -mt-1" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" d="M4 16v2a2 2 0 002 2h12a2 2 0 002-2v-2M7 10l5 5m0 0l5-5m-5 5V4" /></svg>
              Export All Forms (CSV)
              <span className="absolute left-1/2 -bottom-7 -translate-x-1/2 bg-gray-800 text-xs text-white rounded px-2 py-1 opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none z-10">Exports all forms, not just filtered results</span>
            </button>
          </div>
        </div>
        
        {/* Advanced Filters Panel */}
        {showFilters && (
          <div className="px-8 py-6 border-b border-gray-200 bg-gray-50">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              {/* Form Type Filter (only show in general dashboard) */}
              {!filterType && (
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Form Type</label>
                  <select
                    value={filters.formType}
                    onChange={e => handleFilterChange('formType', e.target.value)}
                    className="w-full border rounded px-3 py-2 text-sm"
                  >
                    <option value="">All Form Types</option>
                    <option value="hourly">Hourly</option>
                    <option value="supervisor">Supervisor</option>
                  </select>
                </div>
              )}

              {/* Status Filter */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Status</label>
                <select
                  value={filters.status}
                  onChange={e => handleFilterChange('status', e.target.value)}
                  className="w-full border rounded px-3 py-2 text-sm"
                >
                  <option value="">All Statuses</option>
                  <option value="pending">Pending</option>
                  <option value="processed">Processed</option>
                  <option value="error">Error</option>
                </select>
              </div>

              {/* Employee Name Filter */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Employee Name</label>
                <input
                  type="text"
                  placeholder="Enter employee name..."
                  value={filters.employeeName}
                  onChange={e => handleFilterChange('employeeName', e.target.value)}
                  className="w-full border rounded px-3 py-2 text-sm"
                />
              </div>

              {/* Pass Number Filter */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Pass Number</label>
                <input
                  type="text"
                  placeholder="Enter pass number..."
                  value={filters.passNumber}
                  onChange={e => handleFilterChange('passNumber', e.target.value)}
                  className="w-full border rounded px-3 py-2 text-sm"
                />
              </div>

              {/* Title Filter */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Title</label>
                <input
                  type="text"
                  placeholder="Enter title..."
                  value={filters.title}
                  onChange={e => handleFilterChange('title', e.target.value)}
                  className="w-full border rounded px-3 py-2 text-sm"
                />
              </div>

              {/* Location Filter */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Location/Line</label>
                <input
                  type="text"
                  placeholder="Enter location or line..."
                  value={filters.location}
                  onChange={e => handleFilterChange('location', e.target.value)}
                  className="w-full border rounded px-3 py-2 text-sm"
                />
              </div>

              {/* Job Number Filter */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Job Number</label>
                <input
                  type="text"
                  placeholder="Enter job number..."
                  value={filters.jobNumber}
                  onChange={e => handleFilterChange('jobNumber', e.target.value)}
                  className="w-full border rounded px-3 py-2 text-sm"
                />
              </div>

              {/* Date From Filter */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Date From</label>
                <input
                  type="date"
                  value={filters.dateFrom}
                  onChange={e => handleFilterChange('dateFrom', e.target.value)}
                  className="w-full border rounded px-3 py-2 text-sm"
                />
              </div>

              {/* Date To Filter */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Date To</label>
                <input
                  type="date"
                  value={filters.dateTo}
                  onChange={e => handleFilterChange('dateTo', e.target.value)}
                  className="w-full border rounded px-3 py-2 text-sm"
                />
              </div>
            </div>

            {/* Filter Actions */}
            <div className="flex justify-end gap-2 mt-4 pt-4 border-t border-gray-200">
              <button
                onClick={clearAllFilters}
                className="px-4 py-2 text-sm font-medium text-gray-600 bg-gray-200 rounded-lg hover:bg-gray-300 transition-colors"
              >
                Clear All Filters
              </button>
              <button
                onClick={() => setShowFilters(false)}
                className="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-700 transition-colors"
              >
                Apply Filters
              </button>
            </div>
          </div>
        )}
        
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-white border-b border-gray-200">
              <tr>
                <th className="px-8 py-4 text-left text-sm font-bold text-gray-700 uppercase tracking-wider">File Name</th>
                <th className="px-8 py-4 text-left text-sm font-bold text-gray-700 uppercase tracking-wider">Upload Date</th>
                <th className="px-8 py-4 text-left text-sm font-bold text-gray-700 uppercase tracking-wider">Form Type</th>
                <th className="px-8 py-4 text-left text-sm font-bold text-gray-700 uppercase tracking-wider">Status</th>
                <th className="px-8 py-4 text-left text-sm font-bold text-gray-700 uppercase tracking-wider">Actions</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {filteredForms.map((form: any) => (
                <tr key={form.id} className="hover:bg-gray-50 transition-colors">
                  <td className="px-8 py-4 whitespace-nowrap">
                    <div className="text-sm font-semibold text-gray-900">{form.fileName || form.pass_number || 'N/A'}</div>
                  </td>
                  <td className="px-8 py-4 whitespace-nowrap">
                    <div className="text-sm text-gray-600">{formatUploadDate(form.upload_date)}</div>
                  </td>
                  <td className="px-8 py-4 whitespace-nowrap">
                    <span className={`inline-flex px-3 py-1 text-xs font-bold rounded-full ${getFormTypeColor(form)}`}>
                      {getFormTypeLabel(form)}
                    </span>
                  </td>
                  <td className="px-8 py-4 whitespace-nowrap">
                    <span className={`inline-flex px-3 py-1 text-xs font-bold rounded-full ${getStatusColor(form.status)}`}>
                      {form.status || 'N/A'}
                    </span>
                  </td>
                  <td className="px-8 py-4 whitespace-nowrap text-sm font-medium">
                    <button className="text-blue-600 hover:text-blue-900 font-semibold transition-colors mr-4" onClick={() => handleViewDetails(form.id)}>View Details</button>
                    <button className="text-red-600 hover:text-red-900 font-semibold transition-colors" onClick={() => handleDeleteForm(form.id)}>Delete</button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Details Modal */}
      {console.log('Rendering modal, selectedFormDetails:', selectedFormDetails)}
      {selectedFormDetails && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-xl shadow-xl max-w-4xl w-full max-h-[90vh] overflow-y-auto">
            <div className="px-6 py-4 border-b border-gray-200 flex justify-between items-center">
              <h3 className="text-xl font-semibold text-gray-800">
                Form Details {selectedFormDetails?.form?.form_type && (
                  <span className={`ml-2 px-2 py-1 text-sm rounded-full ${selectedFormDetails.form.form_type === 'supervisor' ? 'bg-purple-100 text-purple-800' : 'bg-blue-100 text-blue-800'}`}>
                    {selectedFormDetails.form.form_type === 'supervisor' ? 'Supervisor' : 'Hourly'}
                  </span>
                )}
              </h3>
              <button
                onClick={closeDetailsModal}
                className="text-gray-400 hover:text-gray-600 text-2xl font-bold"
              >
                ×
              </button>
            </div>
            <div className="p-6">
              {detailsLoading ? (
                <div>Loading...</div>
              ) : detailsError ? (
                <div className="text-red-600">{detailsError}</div>
              ) : (
                <>

                  {/* Hourly Exception Form Details (View Mode) */}
                  {(filterType === 'hourly' || (!filterType && selectedFormDetails.form.form_type !== 'supervisor')) && !isEditing && selectedFormDetails && selectedFormDetails.form && (
                    <div className="mb-4">
                      <div className="flex justify-between items-center mb-4">
                        <h4 className="font-semibold text-gray-800 text-lg border-b pb-2">Hourly Exception Claim Form Info</h4>
                        <button
                          onClick={handleEdit}
                          className="bg-blue-600 text-white px-4 py-2 rounded-lg font-medium hover:bg-blue-700 transition-colors shadow-sm"
                        >
                          Edit Form
                        </button>
                      </div>
                      <div className="grid grid-cols-2 md:grid-cols-3 gap-4 mb-2">
                        <div><span className="font-medium">Regular Assignment:</span> {selectedFormDetails.form.regular_assignment || 'N/A'}</div>
                        <div><span className="font-medium">Report:</span> {selectedFormDetails.form.report || 'N/A'}</div>
                        <div><span className="font-medium">Relief:</span> {selectedFormDetails.form.relief || 'N/A'}</div>
                        <div><span className="font-medium">Today's Date:</span> {selectedFormDetails.form.todays_date || 'N/A'}</div>
                        <div><span className="font-medium">Pass Number:</span> {selectedFormDetails.form.pass_number || 'N/A'}</div>
                        <div><span className="font-medium">Title:</span> {selectedFormDetails.form.title || 'N/A'}</div>
                        <div><span className="font-medium">Employee Name:</span> {selectedFormDetails.form.employee_name || 'N/A'}</div>
                        <div><span className="font-medium">RDOS:</span> {selectedFormDetails.form.rdos || 'N/A'}</div>
                        <div><span className="font-medium">Actual OT Date:</span> {selectedFormDetails.form.actual_ot_date || 'N/A'}</div>
                        <div><span className="font-medium">DIV:</span> {selectedFormDetails.form.div || 'N/A'}</div>
                      </div>
                      <div className="mb-2">
                        <span className="font-medium">Comments:</span>
                        <div className="bg-gray-100 rounded p-2 text-gray-700 min-h-[2rem]">{selectedFormDetails.form.comments || 'N/A'}</div>
                      </div>
                      
                      {/* Overtime Time Details */}
                      {selectedFormDetails.rows && selectedFormDetails.rows.length > 0 && (
                        <div className="mt-4">
                          <h5 className="font-semibold text-gray-800 text-md border-b pb-2 mb-3">Overtime Time Details</h5>
                          {selectedFormDetails.rows.map((row: any, index: number) => (
                            <div key={index} className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-3">
                              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                                <div><span className="font-medium">Line/Location:</span> {row.line_location || 'N/A'}</div>
                                <div><span className="font-medium">Run No.:</span> {row.run_no || 'N/A'}</div>
                                <div><span className="font-medium">Exception Time From:</span> {row.exception_time_from_hh || '0'}:{row.exception_time_from_mm || '00'}</div>
                                <div><span className="font-medium">Exception Time To:</span> {row.exception_time_to_hh || '0'}:{row.exception_time_to_mm || '00'}</div>
                                <div><span className="font-medium">Overtime:</span> {row.overtime_hh || '0'}h {row.overtime_mm || '0'}m</div>
                                <div><span className="font-medium">Bonus:</span> {row.bonus_hh || '0'}h {row.bonus_mm || '0'}m</div>
                                <div><span className="font-medium">Nite Diff:</span> {row.nite_diff_hh || '0'}h {row.nite_diff_mm || '0'}m</div>
                                <div><span className="font-medium">TA Job No.:</span> {row.ta_job_no || 'N/A'}</div>
                              </div>
                            </div>
                          ))}
                        </div>
                      )}
                      

                    </div>
                  )}
                  {/* Pure Extraction Mode - Show Raw Data */}
                  {console.log('Pure extraction section, extractionMode:', extractionMode, 'raw_extracted_data:', selectedFormDetails?.form?.raw_extracted_data)}
                  {extractionMode === 'pure' && (
                    <div className="mb-6">
                      {selectedFormDetails.form.raw_extracted_data ? (
                        <>
                          {selectedFormDetails.isFallbackToMapped && (
                            <div className="mb-4 p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
                              <p className="text-yellow-800 text-sm">
                                <strong>Note:</strong> This form was processed before dual extraction was implemented. 
                                Showing raw data from the mapped extraction version.
                              </p>
                            </div>
                          )}
                          <div className="flex justify-between items-center mb-4">
                            <h4 className="font-semibold text-gray-800 text-lg border-b pb-2">Raw Gemini Extraction Data</h4>
                            <button
                              onClick={handleEditRawJson}
                              className="bg-purple-600 text-white px-4 py-2 rounded-lg font-medium hover:bg-purple-700 transition-colors shadow-sm"
                            >
                              Edit Raw JSON
                            </button>
                          </div>
                          <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
                            <pre className="text-sm text-gray-800 whitespace-pre-wrap overflow-x-auto">
                              {(() => {
                                try {
                                  const parsed = JSON.parse(selectedFormDetails.form.raw_extracted_data);
                                  return JSON.stringify(parsed, null, 2);
                                } catch {
                                  return selectedFormDetails.form.raw_extracted_data;
                                }
                              })()}
                            </pre>
                          </div>
                        </>
                      ) : selectedFormDetails.noRawDataAvailable ? (
                        <div className="p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
                          <p className="text-yellow-800 text-sm">
                            <strong>No raw extraction data available.</strong> This form was processed before dual extraction was implemented. 
                            Upload a new form to see both pure and mapped extraction data.
                          </p>
                          <p className="text-yellow-700 text-sm mt-2">
                            <strong>Showing mapped extraction data below:</strong>
                          </p>
                        </div>
                      ) : (
                        <div className="p-4 bg-gray-50 border border-gray-200 rounded-lg">
                          <p className="text-gray-600 text-sm">
                            <strong>No raw extraction data available.</strong> This form was processed before dual extraction was implemented. 
                            Upload a new form to see both pure and mapped extraction data.
                          </p>
                        </div>
                      )}
                    </div>
                  )}

                  {/* If no fields extracted */}
                  {!(selectedFormDetails.form.regular_assignment || selectedFormDetails.form.report || selectedFormDetails.form.relief || selectedFormDetails.form.todays_date || selectedFormDetails.form.pass_number || selectedFormDetails.form.employee_name || selectedFormDetails.form.title || selectedFormDetails.form.rdos || selectedFormDetails.form.actual_ot_date || selectedFormDetails.form.div || selectedFormDetails.form.supervisor_name || selectedFormDetails.form.supervisor_pass_no || selectedFormDetails.form.oto || selectedFormDetails.form.oto_amount_saved || selectedFormDetails.form.entered_in_uts || selectedFormDetails.form.comments) && extractionMode === 'mapped' && (
                    <div className="text-gray-500 mb-4">No details were extracted from this form.</div>
                  )}


                  {(filterType === 'supervisor' || (!filterType && selectedFormDetails.form.form_type === 'supervisor')) && selectedFormDetails && selectedFormDetails.form && (
                    <div className="mb-6">
                      {/* Supervisor Form Details (View Mode) */}
                      <div className="mb-6">
                        <div className="flex justify-between items-center mb-4">
                          <h4 className="font-semibold text-gray-800 text-lg border-b pb-2">Supervisor Overtime Authorization Details</h4>
                          <button
                            onClick={handleEdit}
                            className="bg-blue-600 text-white px-4 py-2 rounded-lg font-medium hover:bg-blue-700 transition-colors shadow-sm"
                          >
                            Edit Form
                          </button>
                        </div>
                        
                        {/* View Mode */}
                        <div>
                          <div className="grid grid-cols-2 md:grid-cols-3 gap-4 mb-4">
                            <div><span className="font-medium">Regular Assignment:</span> {selectedFormDetails.form.reg || selectedFormDetails.form.regular_assignment || 'N/A'}</div>
                            <div><span className="font-medium">Pass Number:</span> {selectedFormDetails.form.pass_number || 'N/A'}</div>
                            <div><span className="font-medium">Title:</span> {selectedFormDetails.form.title || 'N/A'}</div>
                            <div><span className="font-medium">Employee Name:</span> {selectedFormDetails.form.employee_name || 'N/A'}</div>
                            <div><span className="font-medium">Job Number:</span> {selectedFormDetails.form.job_number || 'N/A'}</div>
                            <div><span className="font-medium">RC Number:</span> {selectedFormDetails.form.rc_number || 'N/A'}</div>
                            <div><span className="font-medium">Report Location:</span> {selectedFormDetails.form.report_loc || 'N/A'}</div>
                            <div><span className="font-medium">Overtime Location:</span> {selectedFormDetails.form.overtime_location || 'N/A'}</div>
                            <div><span className="font-medium">Report Time:</span> {formatTime(selectedFormDetails.form.report_time)}</div>
                            <div><span className="font-medium">Relief Time:</span> {formatTime(selectedFormDetails.form.relief_time)}</div>
                            <div><span className="font-medium">Date of Overtime:</span> {selectedFormDetails.form.date_of_overtime || 'N/A'}</div>
                            <div><span className="font-medium">Overtime Hours:</span> {selectedFormDetails.form.overtime_hours || 'N/A'}</div>
                            <div><span className="font-medium">Account Number:</span> {selectedFormDetails.form.acct_number || 'N/A'}</div>
                            <div><span className="font-medium">Entered into UTS:</span> {selectedFormDetails.form.entered_into_uts || 'N/A'}</div>
                            <div><span className="font-medium">RDOS:</span> {selectedFormDetails.form.rdos || 'N/A'}</div>
                            <div><span className="font-medium">Today's Date:</span> {selectedFormDetails.form.todays_date || 'N/A'}</div>
                          </div>
                          
                          {/* Reason for Overtime - View Mode */}
                          <div className="mb-4">
                            <span className="font-medium">Reason for Overtime:</span>
                            <div className="mt-2 grid grid-cols-2 md:grid-cols-4 gap-2">
                              <div className={`px-3 py-2 rounded-lg text-sm ${selectedFormDetails.form.reason_rdo == 1 ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-600'}`}>
                                RDO {selectedFormDetails.form.reason_rdo == 1 ? '✓' : '✗'}
                              </div>
                              <div className={`px-3 py-2 rounded-lg text-sm ${selectedFormDetails.form.reason_absentee_coverage == 1 ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-600'}`}>
                                Absentee Coverage {selectedFormDetails.form.reason_absentee_coverage == 1 ? '✓' : '✗'}
                              </div>
                              <div className={`px-3 py-2 rounded-lg text-sm ${selectedFormDetails.form.reason_no_lunch == 1 ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-600'}`}>
                                No Lunch {selectedFormDetails.form.reason_no_lunch == 1 ? '✓' : '✗'}
                              </div>
                              <div className={`px-3 py-2 rounded-lg text-sm ${selectedFormDetails.form.reason_early_report == 1 ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-600'}`}>
                                Early Report {selectedFormDetails.form.reason_early_report == 1 ? '✓' : '✗'}
                              </div>
                              <div className={`px-3 py-2 rounded-lg text-sm ${selectedFormDetails.form.reason_late_clear == 1 ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-600'}`}>
                                Late Clear {selectedFormDetails.form.reason_late_clear == 1 ? '✓' : '✗'}
                              </div>
                              <div className={`px-3 py-2 rounded-lg text-sm ${selectedFormDetails.form.reason_save_as_oto == 1 ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-600'}`}>
                                Save as OTO {selectedFormDetails.form.reason_save_as_oto == 1 ? '✓' : '✗'}
                              </div>
                              <div className={`px-3 py-2 rounded-lg text-sm ${selectedFormDetails.form.reason_capital_support_go == 1 ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-600'}`}>
                                Capital Support/GO {selectedFormDetails.form.reason_capital_support_go == 1 ? '✓' : '✗'}
                              </div>
                              <div className={`px-3 py-2 rounded-lg text-sm ${selectedFormDetails.form.reason_other == 1 ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-600'}`}>
                                Other {selectedFormDetails.form.reason_other == 1 ? '✓' : '✗'}
                              </div>
                            </div>
                          </div>
                          
                          <div className="mb-4">
                            <span className="font-medium">Comments:</span>
                            <div className="bg-gray-100 rounded p-2 text-gray-700 min-h-[2rem] mt-1">{selectedFormDetails.form.comments || 'N/A'}</div>
                          </div>
                        </div>
                      </div>
                    </div>
                  )}
                </>
              )}
            </div>
            <div className="px-6 py-4 border-t border-gray-200 flex justify-end gap-2">
              <button
                onClick={closeDetailsModal}
                className="bg-gray-600 text-white px-6 py-2 rounded-lg font-semibold hover:bg-gray-700 transition-colors"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Edit Modal */}
      {showEditModal && editForm && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-xl shadow-xl max-w-6xl w-full max-h-[90vh] overflow-y-auto">
            <div className="px-6 py-4 border-b border-gray-200 flex justify-between items-center">
              <h3 className="text-xl font-semibold text-gray-800">
                {filterType === 'hourly' ? 'Edit Hourly Exception Form' : 'Edit Supervisor Overtime Form'}
              </h3>
              <button
                onClick={handleCancelEdit}
                className="text-gray-400 hover:text-gray-600 text-2xl font-bold"
              >
                ×
              </button>
            </div>
            <div className="p-6">
              {(filterType === 'hourly' || (!filterType && editForm.form_type !== 'supervisor')) && (
                <div className="space-y-6">
                  {/* Hourly Form Edit Fields */}
                  <div>
                    <h4 className="font-semibold text-gray-800 text-lg border-b pb-2 mb-4">Hourly Exception Claim Form Info</h4>
                    <div className="grid grid-cols-2 md:grid-cols-3 gap-4 mb-4">
                      <div><span className="font-medium">Regular Assignment:</span> <input name="regular_assignment" value={editForm.regular_assignment || ''} onChange={handleEditFormChange} className="border rounded p-2 w-full" /></div>
                      <div><span className="font-medium">Report:</span> <input name="report" value={editForm.report || ''} onChange={handleEditFormChange} className="border rounded p-2 w-full" /></div>
                      <div><span className="font-medium">Relief:</span> <input name="relief" value={editForm.relief || ''} onChange={handleEditFormChange} className="border rounded p-2 w-full" /></div>
                      <div><span className="font-medium">Today's Date:</span> <input name="todays_date" value={editForm.todays_date || ''} onChange={handleEditFormChange} className="border rounded p-2 w-full" /></div>
                      <div><span className="font-medium">Pass Number:</span> <input name="pass_number" value={editForm.pass_number || ''} onChange={handleEditFormChange} className="border rounded p-2 w-full" /></div>
                      <div><span className="font-medium">Title:</span> <input name="title" value={editForm.title || ''} onChange={handleEditFormChange} className="border rounded p-2 w-full" /></div>
                      <div><span className="font-medium">Employee Name:</span> <input name="employee_name" value={editForm.employee_name || ''} onChange={handleEditFormChange} className="border rounded p-2 w-full" /></div>
                      <div><span className="font-medium">RDOS:</span> <input name="rdos" value={editForm.rdos || ''} onChange={handleEditFormChange} className="border rounded p-2 w-full" /></div>
                      <div><span className="font-medium">Actual OT Date:</span> <input name="actual_ot_date" value={editForm.actual_ot_date || ''} onChange={handleEditFormChange} className="border rounded p-2 w-full" /></div>
                      <div><span className="font-medium">DIV:</span> <input name="div" value={editForm.div || ''} onChange={handleEditFormChange} className="border rounded p-2 w-full" /></div>
                    </div>
                    <div className="mb-4">
                      <span className="font-medium">Comments:</span>
                      <textarea name="comments" value={editForm.comments || ''} onChange={handleEditFormChange} className="border rounded p-2 w-full mt-1" rows={3} />
                    </div>
                  </div>

                  {/* Hourly Overtime Time Details Edit */}
                  {editRows && editRows.length > 0 && (
                    <div>
                      <h5 className="font-semibold text-gray-800 text-md border-b pb-2 mb-4">Overtime Time Details</h5>
                      {editRows.map((row: any, index: number) => (
                        <div key={index} className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 mb-4">
                          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                            <div>
                              <span className="font-medium">Line/Location:</span>
                              <input 
                                value={row.line_location || ''} 
                                onChange={(e) => handleEditRowChange(index, 'line_location', e.target.value)}
                                className="border rounded p-2 w-full mt-1" 
                              />
                            </div>
                            <div>
                              <span className="font-medium">Run No.:</span>
                              <input 
                                value={row.run_no || ''} 
                                onChange={(e) => handleEditRowChange(index, 'run_no', e.target.value)}
                                className="border rounded p-2 w-full mt-1" 
                              />
                            </div>
                            <div>
                              <span className="font-medium">Exception Time From:</span>
                              <div className="flex gap-1 mt-1">
                                <input 
                                  value={row.exception_time_from_hh || ''} 
                                  onChange={(e) => handleEditRowChange(index, 'exception_time_from_hh', e.target.value)}
                                  className="border rounded p-2 w-16 text-center" 
                                  placeholder="HH"
                                />
                                <span className="self-center">:</span>
                                <input 
                                  value={row.exception_time_from_mm || ''} 
                                  onChange={(e) => handleEditRowChange(index, 'exception_time_from_mm', e.target.value)}
                                  className="border rounded p-2 w-16 text-center" 
                                  placeholder="MM"
                                />
                              </div>
                            </div>
                            <div>
                              <span className="font-medium">Exception Time To:</span>
                              <div className="flex gap-1 mt-1">
                                <input 
                                  value={row.exception_time_to_hh || ''} 
                                  onChange={(e) => handleEditRowChange(index, 'exception_time_to_hh', e.target.value)}
                                  className="border rounded p-2 w-16 text-center" 
                                  placeholder="HH"
                                />
                                <span className="self-center">:</span>
                                <input 
                                  value={row.exception_time_to_mm || ''} 
                                  onChange={(e) => handleEditRowChange(index, 'exception_time_to_mm', e.target.value)}
                                  className="border rounded p-2 w-16 text-center" 
                                  placeholder="MM"
                                />
                              </div>
                            </div>
                            <div>
                              <span className="font-medium">Overtime:</span>
                              <div className="flex gap-1 mt-1">
                                <input 
                                  value={row.overtime_hh || ''} 
                                  onChange={(e) => handleEditRowChange(index, 'overtime_hh', e.target.value)}
                                  className="border rounded p-2 w-16 text-center" 
                                  placeholder="HH"
                                />
                                <span className="self-center">h</span>
                                <input 
                                  value={row.overtime_mm || ''} 
                                  onChange={(e) => handleEditRowChange(index, 'overtime_mm', e.target.value)}
                                  className="border rounded p-2 w-16 text-center" 
                                  placeholder="MM"
                                />
                                <span className="self-center">m</span>
                              </div>
                            </div>
                            <div>
                              <span className="font-medium">Bonus:</span>
                              <div className="flex gap-1 mt-1">
                                <input 
                                  value={row.bonus_hh || ''} 
                                  onChange={(e) => handleEditRowChange(index, 'bonus_hh', e.target.value)}
                                  className="border rounded p-2 w-16 text-center" 
                                  placeholder="HH"
                                />
                                <span className="self-center">h</span>
                                <input 
                                  value={row.bonus_mm || ''} 
                                  onChange={(e) => handleEditRowChange(index, 'bonus_mm', e.target.value)}
                                  className="border rounded p-2 w-16 text-center" 
                                  placeholder="MM"
                                />
                                <span className="self-center">m</span>
                              </div>
                            </div>
                            <div>
                              <span className="font-medium">Nite Diff:</span>
                              <div className="flex gap-1 mt-1">
                                <input 
                                  value={row.nite_diff_hh || ''} 
                                  onChange={(e) => handleEditRowChange(index, 'nite_diff_hh', e.target.value)}
                                  className="border rounded p-2 w-16 text-center" 
                                  placeholder="HH"
                                />
                                <span className="self-center">h</span>
                                <input 
                                  value={row.nite_diff_mm || ''} 
                                  onChange={(e) => handleEditRowChange(index, 'nite_diff_mm', e.target.value)}
                                  className="border rounded p-2 w-16 text-center" 
                                  placeholder="MM"
                                />
                                <span className="self-center">m</span>
                              </div>
                            </div>
                            <div>
                              <span className="font-medium">TA Job No.:</span>
                              <input 
                                value={row.ta_job_no || ''} 
                                onChange={(e) => handleEditRowChange(index, 'ta_job_no', e.target.value)}
                                className="border rounded p-2 w-full mt-1" 
                              />
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              )}

              {(filterType === 'supervisor' || (!filterType && editForm.form_type === 'supervisor')) && (
                <div className="space-y-6">
                  {/* Supervisor Form Edit Fields */}
                  <div>
                    <h4 className="font-semibold text-gray-800 text-lg border-b pb-2 mb-4">Supervisor Overtime Authorization Details</h4>
                    <div className="grid grid-cols-2 md:grid-cols-3 gap-4 mb-4">
                      <div><span className="font-medium">Regular Assignment:</span> <input name="reg" value={editForm.reg || editForm.regular_assignment || ''} onChange={handleEditFormChange} className="border rounded p-2 w-full" /></div>
                      <div><span className="font-medium">Pass Number:</span> <input name="pass_number" value={editForm.pass_number || ''} onChange={handleEditFormChange} className="border rounded p-2 w-full" /></div>
                      <div><span className="font-medium">Title:</span> <input name="title" value={editForm.title || ''} onChange={handleEditFormChange} className="border rounded p-2 w-full" /></div>
                      <div><span className="font-medium">Employee Name:</span> <input name="employee_name" value={editForm.employee_name || ''} onChange={handleEditFormChange} className="border rounded p-2 w-full" /></div>
                      <div><span className="font-medium">Job Number:</span> <input name="job_number" value={editForm.job_number || ''} onChange={handleEditFormChange} className="border rounded p-2 w-full" /></div>
                      <div><span className="font-medium">RC Number:</span> <input name="rc_number" value={editForm.rc_number || ''} onChange={handleEditFormChange} className="border rounded p-2 w-full" /></div>
                      <div><span className="font-medium">Report Location:</span> <input name="report_loc" value={editForm.report_loc || ''} onChange={handleEditFormChange} className="border rounded p-2 w-full" /></div>
                      <div><span className="font-medium">Overtime Location:</span> <input name="overtime_location" value={editForm.overtime_location || ''} onChange={handleEditFormChange} className="border rounded p-2 w-full" /></div>
                      <div><span className="font-medium">Report Time:</span> <input name="report_time" value={editForm.report_time || ''} onChange={handleEditFormChange} className="border rounded p-2 w-full" placeholder="HHMM (e.g., 0430)" /></div>
                      <div><span className="font-medium">Relief Time:</span> <input name="relief_time" value={editForm.relief_time || ''} onChange={handleEditFormChange} className="border rounded p-2 w-full" placeholder="HHMM (e.g., 1415)" /></div>
                      <div><span className="font-medium">Date of Overtime:</span> <input name="date_of_overtime" value={editForm.date_of_overtime || ''} onChange={handleEditFormChange} className="border rounded p-2 w-full" /></div>
                      <div><span className="font-medium">Overtime Hours:</span> <input name="overtime_hours" value={editForm.overtime_hours || ''} onChange={handleEditFormChange} className="border rounded p-2 w-full" /></div>
                      <div><span className="font-medium">Account Number:</span> <input name="acct_number" value={editForm.acct_number || ''} onChange={handleEditFormChange} className="border rounded p-2 w-full" /></div>
                      <div><span className="font-medium">Entered into UTS:</span> <input name="entered_into_uts" value={editForm.entered_into_uts || ''} onChange={handleEditFormChange} className="border rounded p-2 w-full" /></div>
                      <div><span className="font-medium">RDOS:</span> <input name="rdos" value={editForm.rdos || ''} onChange={handleEditFormChange} className="border rounded p-2 w-full" /></div>
                      <div><span className="font-medium">Today's Date:</span> <input name="todays_date" value={editForm.todays_date || ''} onChange={handleEditFormChange} className="border rounded p-2 w-full" /></div>
                    </div>
                    
                    {/* Reason for Overtime - Edit Mode */}
                    <div className="mb-4">
                      <span className="font-medium">Reason for Overtime:</span>
                      <div className="mt-2 grid grid-cols-2 md:grid-cols-4 gap-2">
                        <label className="flex items-center space-x-2">
                          <input type="checkbox" checked={editForm.reason_rdo == 1} onChange={(e) => setEditForm({...editForm, reason_rdo: e.target.checked ? 1 : 0})} className="rounded" />
                          <span className="text-sm">RDO</span>
                        </label>
                        <label className="flex items-center space-x-2">
                          <input type="checkbox" checked={editForm.reason_absentee_coverage == 1} onChange={(e) => setEditForm({...editForm, reason_absentee_coverage: e.target.checked ? 1 : 0})} className="rounded" />
                          <span className="text-sm">Absentee Coverage</span>
                        </label>
                        <label className="flex items-center space-x-2">
                          <input type="checkbox" checked={editForm.reason_no_lunch == 1} onChange={(e) => setEditForm({...editForm, reason_no_lunch: e.target.checked ? 1 : 0})} className="rounded" />
                          <span className="text-sm">No Lunch</span>
                        </label>
                        <label className="flex items-center space-x-2">
                          <input type="checkbox" checked={editForm.reason_early_report == 1} onChange={(e) => setEditForm({...editForm, reason_early_report: e.target.checked ? 1 : 0})} className="rounded" />
                          <span className="text-sm">Early Report</span>
                        </label>
                        <label className="flex items-center space-x-2">
                          <input type="checkbox" checked={editForm.reason_late_clear == 1} onChange={(e) => setEditForm({...editForm, reason_late_clear: e.target.checked ? 1 : 0})} className="rounded" />
                          <span className="text-sm">Late Clear</span>
                        </label>
                        <label className="flex items-center space-x-2">
                          <input type="checkbox" checked={editForm.reason_save_as_oto == 1} onChange={(e) => setEditForm({...editForm, reason_save_as_oto: e.target.checked ? 1 : 0})} className="rounded" />
                          <span className="text-sm">Save as OTO</span>
                        </label>
                        <label className="flex items-center space-x-2">
                          <input type="checkbox" checked={editForm.reason_capital_support_go == 1} onChange={(e) => setEditForm({...editForm, reason_capital_support_go: e.target.checked ? 1 : 0})} className="rounded" />
                          <span className="text-sm">Capital Support/GO</span>
                        </label>
                        <label className="flex items-center space-x-2">
                          <input type="checkbox" checked={editForm.reason_other == 1} onChange={(e) => setEditForm({...editForm, reason_other: e.target.checked ? 1 : 0})} className="rounded" />
                          <span className="text-sm">Other</span>
                        </label>
                      </div>
                    </div>
                    
                    <div className="mb-4">
                      <span className="font-medium">Comments:</span>
                      <textarea name="comments" value={editForm.comments || ''} onChange={handleEditFormChange} className="border rounded p-2 w-full mt-1" rows={3} />
                    </div>
                  </div>
                </div>
              )}

              {/* Edit Action Buttons */}
              {saveError && (
                <div className="text-red-600 text-sm mb-4">{saveError}</div>
              )}
              <div className="flex gap-3 pt-6 border-t border-gray-200">
                <button
                  onClick={handleSaveEdit}
                  className="bg-green-600 text-white px-6 py-2 rounded-lg font-medium hover:bg-green-700 transition-colors disabled:opacity-50 shadow-sm"
                  disabled={saveLoading}
                >
                  {saveLoading ? 'Saving...' : 'Save Changes'}
                </button>
                <button
                  onClick={handleCancelEdit}
                  className="bg-gray-500 text-white px-6 py-2 rounded-lg font-medium hover:bg-gray-600 transition-colors shadow-sm"
                >
                  Cancel
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Extraction Mode Modal */}
      {showExtractionModeModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-xl shadow-xl max-w-md w-full">
            <div className="px-6 py-4 border-b border-gray-200">
              <h3 className="text-xl font-semibold text-gray-800">Extraction Mode</h3>
            </div>
            <div className="p-6">
              <div className="mb-6">
                <h4 className="font-semibold text-gray-800 mb-3">Current Mode: {extractionMode === 'pure' ? 'Pure Extraction' : 'Mapped Extraction'}</h4>
                
                <div className="space-y-4">
                  <div className={`p-4 rounded-lg border-2 ${extractionMode === 'pure' ? 'border-purple-300 bg-purple-50' : 'border-gray-200 bg-gray-50'}`}>
                    <h5 className="font-medium text-gray-800 mb-2">Pure Extraction</h5>
                    <p className="text-sm text-gray-600">
                      Extracts all fields from Gemini without mapping to predefined database fields. 
                      Captures everything Gemini finds but may be harder to query and filter.
                    </p>
                  </div>
                  
                  <div className={`p-4 rounded-lg border-2 ${extractionMode === 'mapped' ? 'border-green-300 bg-green-50' : 'border-gray-200 bg-gray-50'}`}>
                    <h5 className="font-medium text-gray-800 mb-2 flex items-center">
                      Mapped Extraction
                      <span className="ml-2 px-1.5 py-0.5 bg-yellow-500 text-white text-xs rounded-full font-bold">BETA</span>
                    </h5>
                    <p className="text-sm text-gray-600">
                      Maps Gemini output to predefined database fields. 
                      Better for querying and filtering but may miss unexpected fields.
                      <span className="block mt-1 text-yellow-600 font-medium">⚠️ Experimental - field mapping may not be perfect</span>
                    </p>
                  </div>
                </div>
              </div>
              
              <div className="flex gap-3">
                <button
                  onClick={handleToggleExtractionMode}
                  className={`flex-1 px-4 py-2 rounded-lg font-medium transition-colors ${
                    extractionMode === 'pure' 
                      ? 'bg-green-600 text-white hover:bg-green-700' 
                      : 'bg-purple-600 text-white hover:bg-purple-700'
                  }`}
                >
                  Switch to {extractionMode === 'pure' ? 'Mapped' : 'Pure'} Extraction
                  {extractionMode === 'pure' && (
                    <span className="ml-1 px-1 py-0.5 bg-yellow-500 text-white text-xs rounded-full font-bold">BETA</span>
                  )}
                </button>
                <button
                  onClick={() => setShowExtractionModeModal(false)}
                  className="px-4 py-2 text-gray-600 bg-gray-200 rounded-lg font-medium hover:bg-gray-300 transition-colors"
                >
                  Cancel
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Dashboard; 