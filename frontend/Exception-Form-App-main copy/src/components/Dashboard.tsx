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
  const [search, setSearch] = useState('');
  // const { user } = useAuth ? useAuth() : { user: null };

  useEffect(() => {
    setLoading(true);
    setError('');
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
        setLoading(false);
      })
      .catch(err => {
        setError('Failed to load dashboard data.');
        setLoading(false);
      });
  }, [filterType]);

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

  const handleViewForm = (form: FormData) => {
    // setSelectedForm(form); // This state is removed
    // setShowModal(true); // This state is removed
  };

  const closeModal = () => {
    // setShowModal(false); // This state is removed
    // setSelectedForm(null); // This state is removed
  };

  const handleViewDetails = async (formId: number) => {
    setDetailsLoading(true);
    setDetailsError('');
    setSelectedFormDetails(null);
    try {
      const response = await fetch(`http://localhost:8000/api/form/${formId}`);
      const data = await response.json();
      if (response.ok) {
        setSelectedFormDetails(data);
      } else {
        setDetailsError(data.error || 'Failed to load form details.');
      }
    } catch (err) {
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
    setIsEditing(true);
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
        const detailsRes = await fetch(`http://localhost:8000/api/form/${editForm.id}`);
        const detailsData = await detailsRes.json();
        setSelectedFormDetails(detailsData);
        setIsEditing(false);
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
    setIsEditing(false);
    setSaveError('');
  };

  // Add explicit type for filteredForms
  let filteredForms: any[] = dashboard?.forms || [];
  // Show all forms if form_type is missing or 'hourly' for hourly dashboard
  if (filterType === 'hourly') {
    filteredForms = filteredForms.filter((form: any) => !form.form_type || form.form_type === 'hourly');
  } else if (filterType === 'supervisor') {
    filteredForms = filteredForms.filter((form: any) => form.form_type === 'supervisor');
  }

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
    window.open('http://localhost:8000/api/forms/export', '_blank');
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
                      if (!dashboard?.forms) return '';
                      const supervisorCount = dashboard.forms.filter((f: any) => f.form_type === 'supervisor').length;
                      const hourlyCount = dashboard.forms.filter((f: any) => !f.form_type || f.form_type === 'hourly').length;
                      return supervisorCount > hourlyCount ? '(supervisor)' : '(hourly employees)';
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
            <input
              type="text"
              placeholder="Search by Pass Number, Name, Title, Status, Line/Location, Comments..."
              value={search}
              onChange={e => setSearch(e.target.value)}
              className="border rounded px-3 py-2 text-sm w-64"
            />
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
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-white border-b border-gray-200">
              <tr>
                <th className="px-8 py-4 text-left text-sm font-bold text-gray-700 uppercase tracking-wider">File Name</th>
                <th className="px-8 py-4 text-left text-sm font-bold text-gray-700 uppercase tracking-wider">Upload Date</th>
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
      {selectedFormDetails && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-xl shadow-xl max-w-4xl w-full max-h-[90vh] overflow-y-auto">
            <div className="px-6 py-4 border-b border-gray-200 flex justify-between items-center">
              <h3 className="text-xl font-semibold text-gray-800">Form Details</h3>
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
                  {isEditing && filterType === 'hourly' && editForm && (
                    <div className="mb-4">
                      <h4 className="font-semibold text-gray-800 text-lg border-b pb-2 mb-2">Hourly Exception Claim Form Info</h4>
                      <div className="grid grid-cols-2 md:grid-cols-3 gap-4 mb-2">
                        <div><span className="font-medium">Regular Assignment:</span> <input name="regular_assignment" value={editForm.regular_assignment || ''} onChange={handleEditFormChange} className="border rounded p-1 w-full" /></div>
                        <div><span className="font-medium">Report:</span> <input name="report" value={editForm.report || ''} onChange={handleEditFormChange} className="border rounded p-1 w-full" /></div>
                        <div><span className="font-medium">Relief:</span> <input name="relief" value={editForm.relief || ''} onChange={handleEditFormChange} className="border rounded p-1 w-full" /></div>
                        <div><span className="font-medium">Today's Date:</span> <input name="todays_date" value={editForm.todays_date || ''} onChange={handleEditFormChange} className="border rounded p-1 w-full" /></div>
                        <div><span className="font-medium">Pass Number:</span> <input name="pass_number" value={editForm.pass_number || ''} onChange={handleEditFormChange} className="border rounded p-1 w-full" /></div>
                        <div><span className="font-medium">Title:</span> <input name="title" value={editForm.title || ''} onChange={handleEditFormChange} className="border rounded p-1 w-full" /></div>
                        <div><span className="font-medium">Employee Name:</span> <input name="employee_name" value={editForm.employee_name || ''} onChange={handleEditFormChange} className="border rounded p-1 w-full" /></div>
                        <div><span className="font-medium">RDOS:</span> <input name="rdos" value={editForm.rdos || ''} onChange={handleEditFormChange} className="border rounded p-1 w-full" /></div>
                        <div><span className="font-medium">Actual OT Date:</span> <input name="actual_ot_date" value={editForm.actual_ot_date || ''} onChange={handleEditFormChange} className="border rounded p-1 w-full" /></div>
                        <div><span className="font-medium">DIV:</span> <input name="div" value={editForm.div || ''} onChange={handleEditFormChange} className="border rounded p-1 w-full" /></div>
                      </div>
                      <div className="mb-2">
                        <span className="font-medium">Comments:</span>
                        <textarea name="comments" value={editForm.comments || ''} onChange={handleEditFormChange} className="border rounded p-1 w-full mt-1" rows={2} />
                      </div>
                    </div>
                  )}
                  {/* Hourly Exception Form Details (View Mode) */}
                  {filterType === 'hourly' && !isEditing && selectedFormDetails && selectedFormDetails.form && (
                    <div className="mb-4">
                      <h4 className="font-semibold text-gray-800 text-lg border-b pb-2 mb-2">Hourly Exception Claim Form Info</h4>
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
                    </div>
                  )}
                  {/* If no fields extracted */}
                  {!(selectedFormDetails.form.regular_assignment || selectedFormDetails.form.report || selectedFormDetails.form.relief || selectedFormDetails.form.todays_date || selectedFormDetails.form.pass_number || selectedFormDetails.form.employee_name || selectedFormDetails.form.title || selectedFormDetails.form.rdos || selectedFormDetails.form.actual_ot_date || selectedFormDetails.form.div || selectedFormDetails.form.supervisor_name || selectedFormDetails.form.supervisor_pass_no || selectedFormDetails.form.oto || selectedFormDetails.form.oto_amount_saved || selectedFormDetails.form.entered_in_uts || selectedFormDetails.form.comments) && (
                    <div className="text-gray-500 mb-4">No details were extracted from this form.</div>
                  )}
                  {/* Rows */}
                  <div>
                    <h4 className="font-semibold text-gray-800 text-lg border-b pb-2 mb-2">Rows</h4>
                    {selectedFormDetails.rows.length === 0 ? (
                      <div className="text-gray-500">No rows available.</div>
                    ) : (
                      <div className="overflow-x-auto">
                        <table className="min-w-full divide-y divide-gray-200">
                          <thead className="bg-gray-100">
                            <tr>
                              <th className="px-4 py-2 text-left text-xs font-bold text-gray-700 uppercase tracking-wider">Location</th>
                              <th className="px-4 py-2 text-left text-xs font-bold text-gray-700 uppercase tracking-wider">Run No.</th>
                              <th className="px-4 py-2 text-left text-xs font-bold text-gray-700 uppercase tracking-wider">Exception Time</th>
                              <th className="px-4 py-2 text-left text-xs font-bold text-gray-700 uppercase tracking-wider">Overtime</th>
                              <th className="px-4 py-2 text-left text-xs font-bold text-gray-700 uppercase tracking-wider">Bonus</th>
                              <th className="px-4 py-2 text-left text-xs font-bold text-gray-700 uppercase tracking-wider">Nite Diff.</th>
                              <th className="px-4 py-2 text-left text-xs font-bold text-gray-700 uppercase tracking-wider">TA Job No.</th>
                            </tr>
                          </thead>
                          <tbody className="bg-white divide-y divide-gray-200">
                            {isEditing && filterType === 'hourly' ? (
                              editRows.map((row: any, idx: number) => (
                                <tr key={idx}>
                                  <td className="px-4 py-2 text-sm text-gray-900"><input name="line_location" value={row.line_location || ''} onChange={e => handleEditRowChange(idx, 'line_location', e.target.value)} className="border rounded p-1 w-full" /></td>
                                  <td className="px-4 py-2 text-sm text-gray-900"><input name="run_no" value={row.run_no || ''} onChange={e => handleEditRowChange(idx, 'run_no', e.target.value)} className="border rounded p-1 w-full" /></td>
                                  <td className="px-4 py-2 text-sm text-gray-900">
                                    <input name="exception_time_from_hh" value={row.exception_time_from_hh || ''} onChange={e => handleEditRowChange(idx, 'exception_time_from_hh', e.target.value)} className="border rounded p-1 w-10 mr-1" placeholder="From HH" />:
                                    <input name="exception_time_from_mm" value={row.exception_time_from_mm || ''} onChange={e => handleEditRowChange(idx, 'exception_time_from_mm', e.target.value)} className="border rounded p-1 w-10 mr-1" placeholder="From MM" /> to
                                    <input name="exception_time_to_hh" value={row.exception_time_to_hh || ''} onChange={e => handleEditRowChange(idx, 'exception_time_to_hh', e.target.value)} className="border rounded p-1 w-10 ml-1 mr-1" placeholder="To HH" />:
                                    <input name="exception_time_to_mm" value={row.exception_time_to_mm || ''} onChange={e => handleEditRowChange(idx, 'exception_time_to_mm', e.target.value)} className="border rounded p-1 w-10" placeholder="To MM" />
                                  </td>
                                  <td className="px-4 py-2 text-sm text-gray-900">
                                    <input name="overtime_hh" value={row.overtime_hh || ''} onChange={e => handleEditRowChange(idx, 'overtime_hh', e.target.value)} className="border rounded p-1 w-10 mr-1" placeholder="HH" />:
                                    <input name="overtime_mm" value={row.overtime_mm || ''} onChange={e => handleEditRowChange(idx, 'overtime_mm', e.target.value)} className="border rounded p-1 w-10" placeholder="MM" />
                                  </td>
                                  <td className="px-4 py-2 text-sm text-gray-900">
                                    <input name="bonus_hh" value={row.bonus_hh || ''} onChange={e => handleEditRowChange(idx, 'bonus_hh', e.target.value)} className="border rounded p-1 w-10 mr-1" placeholder="HH" />:
                                    <input name="bonus_mm" value={row.bonus_mm || ''} onChange={e => handleEditRowChange(idx, 'bonus_mm', e.target.value)} className="border rounded p-1 w-10" placeholder="MM" />
                                  </td>
                                  <td className="px-4 py-2 text-sm text-gray-900">
                                    <input name="nite_diff_hh" value={row.nite_diff_hh || ''} onChange={e => handleEditRowChange(idx, 'nite_diff_hh', e.target.value)} className="border rounded p-1 w-10 mr-1" placeholder="HH" />:
                                    <input name="nite_diff_mm" value={row.nite_diff_mm || ''} onChange={e => handleEditRowChange(idx, 'nite_diff_mm', e.target.value)} className="border rounded p-1 w-10" placeholder="MM" />
                                  </td>
                                  <td className="px-4 py-2 text-sm text-gray-900"><input name="ta_job_no" value={row.ta_job_no || ''} onChange={e => handleEditRowChange(idx, 'ta_job_no', e.target.value)} className="border rounded p-1 w-full" /></td>
                                </tr>
                              ))
                            ) : (
                              selectedFormDetails.rows.map((row: any, idx: number) => (
                                <tr key={idx}>
                                  <td className="px-4 py-2 text-sm text-gray-900">{row.line_location || ''}</td>
                                  <td className="px-4 py-2 text-sm text-gray-900">{row.run_no || ''}</td>
                                  <td className="px-4 py-2 text-sm text-gray-900">{row.exception_time_from_hh || ''}:{row.exception_time_from_mm || ''} to {row.exception_time_to_hh || ''}:{row.exception_time_to_mm || ''}</td>
                                  <td className="px-4 py-2 text-sm text-gray-900">{row.overtime_hh || ''}:{row.overtime_mm || ''}</td>
                                  <td className="px-4 py-2 text-sm text-gray-900">{row.bonus_hh || ''}:{row.bonus_mm || ''}</td>
                                  <td className="px-4 py-2 text-sm text-gray-900">{row.nite_diff_hh || ''}:{row.nite_diff_mm || ''}</td>
                                  <td className="px-4 py-2 text-sm text-gray-900">{row.ta_job_no || ''}</td>
                                </tr>
                              ))
                            )}
                          </tbody>
                        </table>
                      </div>
                    )}
                  </div>
                  {/* Supervisor Full Details Section (all fields) */}
                  {filterType === 'supervisor' && selectedFormDetails && selectedFormDetails.form && (
                    <div className="mb-4">
                      <h4 className="font-semibold text-gray-800 text-lg border-b pb-2 mb-2">Supervisor Overtime Full Details</h4>
                      <div className="grid grid-cols-2 md:grid-cols-3 gap-4 mb-2">
                        {isEditing ? (
                          <>
                            <div><span className="font-medium">Regular Assignment:</span> <input name="regular_assignment" value={editForm.regular_assignment || ''} onChange={handleEditFormChange} className="border rounded p-1 w-full" /></div>
                            <div><span className="font-medium">Report Loc.:</span> <input name="report" value={editForm.report || ''} onChange={handleEditFormChange} className="border rounded p-1 w-full" /></div>
                            <div><span className="font-medium">Report Location:</span> <input name="report_loc" value={editForm.report_loc || ''} onChange={handleEditFormChange} className="border rounded p-1 w-full" /></div>
                            <div><span className="font-medium">Date:</span> <input name="todays_date" value={editForm.todays_date || ''} onChange={handleEditFormChange} className="border rounded p-1 w-full" /></div>
                            <div><span className="font-medium">Pass:</span> <input name="pass_number" value={editForm.pass_number || ''} onChange={handleEditFormChange} className="border rounded p-1 w-full" /></div>
                            <div><span className="font-medium">Title:</span> <input name="title" value={editForm.title || ''} onChange={handleEditFormChange} className="border rounded p-1 w-full" /></div>
                            <div><span className="font-medium">RC #:</span> <input name="rc_number" value={editForm.rc_number || ''} onChange={handleEditFormChange} className="border rounded p-1 w-full" /></div>
                            <div><span className="font-medium">Employee Name:</span> <input name="employee_name" value={editForm.employee_name || ''} onChange={handleEditFormChange} className="border rounded p-1 w-full" /></div>
                            <div><span className="font-medium">RDO's:</span> <input name="rdos" value={editForm.rdos || ''} onChange={handleEditFormChange} className="border rounded p-1 w-full" /></div>
                            <div><span className="font-medium">Date of Overtime:</span> <input name="date_of_overtime" value={editForm.date_of_overtime || ''} onChange={handleEditFormChange} className="border rounded p-1 w-full" /></div>
                            <div><span className="font-medium">Job #:</span> <input name="job_number" value={editForm.job_number || ''} onChange={handleEditFormChange} className="border rounded p-1 w-full" /></div>
                            <div><span className="font-medium">Overtime Location:</span> <input name="overtime_location" value={editForm.overtime_location || ''} onChange={handleEditFormChange} className="border rounded p-1 w-full" /></div>
                            <div><span className="font-medium">Report Time:</span> <input name="report_time" value={editForm.report_time || ''} onChange={handleEditFormChange} className="border rounded p-1 w-full" /></div>
                            <div><span className="font-medium">Relief Time:</span> <input name="relief_time" value={editForm.relief_time || ''} onChange={handleEditFormChange} className="border rounded p-1 w-full" /></div>
                            <div><span className="font-medium">Overtime Hours:</span> <input name="overtime_hours" value={editForm.overtime_hours || ''} onChange={handleEditFormChange} className="border rounded p-1 w-full" /></div>
                            <div><span className="font-medium">Acct #:</span> <input name="acct_number" value={editForm.acct_number || ''} onChange={handleEditFormChange} className="border rounded p-1 w-full" /></div>
                            <div><span className="font-medium">Amount:</span> <input name="amount" value={editForm.amount || ''} onChange={handleEditFormChange} className="border rounded p-1 w-full" /></div>
                          </>
                        ) : (
                          <>
                            <div><span className="font-medium">Regular Assignment:</span> {selectedFormDetails.form.regular_assignment || 'N/A'}</div>
                            <div><span className="font-medium">Report Loc.:</span> {selectedFormDetails.form.report || 'N/A'}</div>
                            <div><span className="font-medium">Report Location:</span> {selectedFormDetails.form.report_loc || 'N/A'}</div>
                            <div><span className="font-medium">Date:</span> {selectedFormDetails.form.todays_date || 'N/A'}</div>
                            <div><span className="font-medium">Pass:</span> {selectedFormDetails.form.pass_number || 'N/A'}</div>
                            <div><span className="font-medium">Title:</span> {selectedFormDetails.form.title || 'N/A'}</div>
                            <div><span className="font-medium">RC #:</span> {selectedFormDetails.form.rc_number || 'N/A'}</div>
                            <div><span className="font-medium">Employee Name:</span> {selectedFormDetails.form.employee_name || 'N/A'}</div>
                            <div><span className="font-medium">RDO's:</span> {selectedFormDetails.form.rdos || 'N/A'}</div>
                            <div><span className="font-medium">Date of Overtime:</span> {selectedFormDetails.form.date_of_overtime || 'N/A'}</div>
                            <div><span className="font-medium">Job #:</span> {selectedFormDetails.form.job_number || 'N/A'}</div>
                            <div><span className="font-medium">Overtime Location:</span> {selectedFormDetails.form.overtime_location || 'N/A'}</div>
                            <div><span className="font-medium">Report Time:</span> {selectedFormDetails.form.report_time || 'N/A'}</div>
                            <div><span className="font-medium">Relief Time:</span> {selectedFormDetails.form.relief_time || 'N/A'}</div>
                            <div><span className="font-medium">Overtime Hours:</span> {selectedFormDetails.form.overtime_hours || 'N/A'}</div>
                            <div><span className="font-medium">Acct #:</span> {selectedFormDetails.form.acct_number || 'N/A'}</div>
                            <div><span className="font-medium">Amount:</span> {selectedFormDetails.form.amount || 'N/A'}</div>
                          </>
                        )}
                      </div>
                      <div className="mb-2">
                        <h4 className="font-semibold text-gray-700 text-base mb-1">Reason for Overtime</h4>
                        <div className="flex flex-wrap gap-4">
                          {isEditing ? (
                            <>
                              <label><input type="checkbox" name="reason_rdo" checked={!!editForm.reason_rdo} onChange={e => setEditForm((prev: any) => ({ ...prev, reason_rdo: e.target.checked }))} /> RDO</label>
                              <label><input type="checkbox" name="reason_absentee_coverage" checked={!!editForm.reason_absentee_coverage} onChange={e => setEditForm((prev: any) => ({ ...prev, reason_absentee_coverage: e.target.checked }))} /> Absentee Coverage</label>
                              <label><input type="checkbox" name="reason_no_lunch" checked={!!editForm.reason_no_lunch} onChange={e => setEditForm((prev: any) => ({ ...prev, reason_no_lunch: e.target.checked }))} /> No Lunch</label>
                              <label><input type="checkbox" name="reason_early_report" checked={!!editForm.reason_early_report} onChange={e => setEditForm((prev: any) => ({ ...prev, reason_early_report: e.target.checked }))} /> Early Report</label>
                              <label><input type="checkbox" name="reason_late_clear" checked={!!editForm.reason_late_clear} onChange={e => setEditForm((prev: any) => ({ ...prev, reason_late_clear: e.target.checked }))} /> Late Clear</label>
                              <label><input type="checkbox" name="reason_save_as_oto" checked={!!editForm.reason_save_as_oto} onChange={e => setEditForm((prev: any) => ({ ...prev, reason_save_as_oto: e.target.checked }))} /> Save as OTO</label>
                              <label><input type="checkbox" name="reason_capital_support_go" checked={!!editForm.reason_capital_support_go} onChange={e => setEditForm((prev: any) => ({ ...prev, reason_capital_support_go: e.target.checked }))} /> Capital Support / GO</label>
                              <label><input type="checkbox" name="reason_other" checked={!!editForm.reason_other} onChange={e => setEditForm((prev: any) => ({ ...prev, reason_other: e.target.checked }))} /> Other</label>
                            </>
                          ) : (
                            <>
                              <div><input type="checkbox" checked={!!selectedFormDetails.form.reason_rdo} readOnly /> RDO</div>
                              <div><input type="checkbox" checked={!!selectedFormDetails.form.reason_absentee_coverage} readOnly /> Absentee Coverage</div>
                              <div><input type="checkbox" checked={!!selectedFormDetails.form.reason_no_lunch} readOnly /> No Lunch</div>
                              <div><input type="checkbox" checked={!!selectedFormDetails.form.reason_early_report} readOnly /> Early Report</div>
                              <div><input type="checkbox" checked={!!selectedFormDetails.form.reason_late_clear} readOnly /> Late Clear</div>
                              <div><input type="checkbox" checked={!!selectedFormDetails.form.reason_save_as_oto} readOnly /> Save as OTO</div>
                              <div><input type="checkbox" checked={!!selectedFormDetails.form.reason_capital_support_go} readOnly /> Capital Support / GO</div>
                              <div><input type="checkbox" checked={!!selectedFormDetails.form.reason_other} readOnly /> Other</div>
                            </>
                          )}
                        </div>
                      </div>
                      <div className="mb-2">
                        <span className="font-medium">Comments:</span>
                        {isEditing ? (
                          <textarea name="comments" value={editForm.comments || ''} onChange={handleEditFormChange} className="border rounded p-1 w-full mt-1" rows={2} />
                        ) : (
                          <div className="bg-gray-100 rounded p-2 text-gray-700 min-h-[2rem]">{selectedFormDetails.form.comments || 'N/A'}</div>
                        )}
                      </div>
                    </div>
                  )}
                </>
              )}
            </div>
            <div className="px-6 py-4 border-t border-gray-200 flex justify-end gap-2">
              {isEditing ? (
                <>
                  <button
                    onClick={handleSaveEdit}
                    className="bg-blue-600 text-white px-6 py-2 rounded-lg font-semibold hover:bg-blue-700 transition-colors disabled:opacity-50"
                    disabled={saveLoading}
                  >
                    {saveLoading ? 'Saving...' : 'Save'}
                  </button>
                  <button
                    onClick={handleCancelEdit}
                    className="bg-gray-400 text-white px-6 py-2 rounded-lg font-semibold hover:bg-gray-500 transition-colors"
                  >
                    Cancel
                  </button>
                </>
              ) : (
                <button
                  onClick={handleEdit}
                  className="bg-yellow-500 text-white px-6 py-2 rounded-lg font-semibold hover:bg-yellow-600 transition-colors"
                >
                  Edit
                </button>
              )}
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
    </div>
  );
};

export default Dashboard; 