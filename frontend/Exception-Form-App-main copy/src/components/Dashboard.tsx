import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';

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
}

const Dashboard = () => {
  const [dashboard, setDashboard] = useState<any>(null);
  const [selectedFormDetails, setSelectedFormDetails] = useState<any>(null);
  const [detailsLoading, setDetailsLoading] = useState(false);
  const [detailsError, setDetailsError] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchDashboard = async () => {
      try {
        const response = await fetch('http://localhost:8000/api/dashboard');
        const data = await response.json();
        setDashboard(data);
      } catch (err) {
        setError('Failed to load dashboard data.');
      } finally {
        setLoading(false);
      }
    };
    fetchDashboard();
  }, []);

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

  // Calculate total overtime hours
  const calculateTotalOvertime = () => {
    const processedForms = dashboard?.processed_forms || []; // Use dashboard data
    let totalHours = 0;
    let totalMinutes = 0;

    processedForms.forEach(form => {
      const hours = parseInt(form.overtimeHH || '0');
      const minutes = parseInt(form.overtimeMM || '0');
      totalHours += hours;
      totalMinutes += minutes;
    });

    // Convert excess minutes to hours
    totalHours += Math.floor(totalMinutes / 60);
    totalMinutes = totalMinutes % 60;

    return { hours: totalHours, minutes: totalMinutes };
  };

  // Calculate total unique job numbers
  const calculateTotalJobNumbers = () => {
    const processedForms = dashboard?.processed_forms || []; // Use dashboard data
    const uniqueJobNumbers = new Set();
    
    processedForms.forEach(form => {
      if (form.taJobNo) {
        uniqueJobNumbers.add(form.taJobNo);
      }
    });

    return uniqueJobNumbers.size;
  };

  // Calculate total job numbers (including duplicates)
  const calculateTotalJobNumbersCount = () => {
    const processedForms = dashboard?.processed_forms || []; // Use dashboard data
    return processedForms.filter(form => form.taJobNo).length;
  };

  // Find most relevant job position
  const findMostRelevantJobPosition = () => {
    const processedForms = dashboard?.processed_forms || []; // Use dashboard data
    const jobPositionCounts: { [key: string]: number } = {};
    
    processedForms.forEach(form => {
      if (form.title) {
        jobPositionCounts[form.title] = (jobPositionCounts[form.title] || 0) + 1;
      }
    });

    if (Object.keys(jobPositionCounts).length === 0) {
      return { position: 'N/A', count: 0 };
    }

    const mostRelevant = Object.entries(jobPositionCounts).reduce((a, b) => 
      jobPositionCounts[a[0]] > jobPositionCounts[b[0]] ? a : b
    );

    return { position: mostRelevant[0], count: mostRelevant[1] };
  };

  // Find most relevant location
  const findMostRelevantLocation = () => {
    const processedForms = dashboard?.processed_forms || []; // Use dashboard data
    const locationCounts: { [key: string]: number } = {};
    
    processedForms.forEach(form => {
      if (form.location) {
        locationCounts[form.location] = (locationCounts[form.location] || 0) + 1;
      }
    });

    if (Object.keys(locationCounts).length === 0) {
      return { location: 'N/A', count: 0 };
    }

    const mostRelevant = Object.entries(locationCounts).reduce((a, b) => 
      locationCounts[a[0]] > locationCounts[b[0]] ? a : b
    );

    return { location: mostRelevant[0], count: mostRelevant[1] };
  };

  const totalOvertime = calculateTotalOvertime();
  const totalJobNumbers = calculateTotalJobNumbers();
  const totalJobNumbersCount = calculateTotalJobNumbersCount();
  const mostRelevantJob = findMostRelevantJobPosition();
  const mostRelevantLocation = findMostRelevantLocation();

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
        <h1 className="text-3xl font-bold text-gray-900">MTA Forms Dashboard</h1>
      </div>

      {/* Tracker Section */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5 gap-6 mb-8">
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
              <div className="text-2xl font-bold text-gray-900">{dashboard.total_forms}</div>
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
              <div className="text-2xl font-bold text-gray-900">{dashboard.total_overtime}</div>
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
              <div className="text-2xl font-bold text-gray-900">{dashboard.total_job_numbers}</div>
              <div className="text-xs text-gray-400 font-medium mt-1">
                {dashboard.unique_job_numbers} unique
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
                {dashboard.most_relevant_position.position}
              </div>
              <div className="text-xs text-gray-400 font-medium mt-1">
                {dashboard.most_relevant_position.count} forms
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
              <div className="text-sm font-medium text-gray-500 uppercase tracking-wide mb-1">Most Relevant Location</div>
              <div className="text-lg font-bold text-gray-900 truncate">
                {dashboard.most_relevant_location.location}
              </div>
              <div className="text-xs text-gray-400 font-medium mt-1">
                {dashboard.most_relevant_location.count} forms
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Uploaded Forms Table */}
      <div className="bg-white rounded-xl shadow-lg overflow-hidden border border-gray-200 mt-8">
        <div className="px-8 py-6 border-b border-gray-200 bg-gray-50">
          <h2 className="text-2xl font-bold text-gray-800">Uploaded Forms ({dashboard.forms.length})</h2>
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
              {dashboard.forms.map((form: any) => (
                <tr key={form.id} className="hover:bg-gray-50 transition-colors">
                  <td className="px-8 py-4 whitespace-nowrap">
                    <div className="text-sm font-semibold text-gray-900">{form.fileName || form.pass_number || 'N/A'}</div>
                  </td>
                  <td className="px-8 py-4 whitespace-nowrap">
                    <div className="text-sm text-gray-600">{formatDate(form.uploadDate || form.actual_ot_date)}</div>
                  </td>
                  <td className="px-8 py-4 whitespace-nowrap">
                    <span className="inline-flex px-3 py-1 text-xs font-bold rounded-full bg-green-100 text-green-800">processed</span>
                  </td>
                  <td className="px-8 py-4 whitespace-nowrap text-sm font-medium">
                    <button className="text-blue-600 hover:text-blue-900 font-semibold transition-colors" onClick={() => handleViewDetails(form.id)}>View Details</button>
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
                  {/* Grouped Header Fields */}
                  <div className="mb-4">
                    <h4 className="font-semibold text-gray-800 text-lg border-b pb-2 mb-2">Employee Info</h4>
                    <div className="grid grid-cols-2 md:grid-cols-3 gap-4 mb-2">
                      <div><span className="font-medium">Pass Number:</span> {selectedFormDetails.form.pass_number || 'N/A'}</div>
                      <div><span className="font-medium">Employee Name:</span> {selectedFormDetails.form.employee_name || 'N/A'}</div>
                      <div><span className="font-medium">Title:</span> {selectedFormDetails.form.title || 'N/A'}</div>
                      <div><span className="font-medium">RDOS:</span> {selectedFormDetails.form.rdos || 'N/A'}</div>
                      <div><span className="font-medium">Actual OT Date:</span> {selectedFormDetails.form.actual_ot_date || 'N/A'}</div>
                      <div><span className="font-medium">DIV:</span> {selectedFormDetails.form.div || 'N/A'}</div>
                    </div>
                    <h4 className="font-semibold text-gray-800 text-lg border-b pb-2 mb-2 mt-4">Supervisor Info</h4>
                    <div className="grid grid-cols-2 md:grid-cols-3 gap-4 mb-2">
                      <div><span className="font-medium">Supervisor Name:</span> {selectedFormDetails.form.supervisor_name || 'N/A'}</div>
                      <div><span className="font-medium">Supervisor Pass No.:</span> {selectedFormDetails.form.supervisor_pass_no || 'N/A'}</div>
                    </div>
                    <h4 className="font-semibold text-gray-800 text-lg border-b pb-2 mb-2 mt-4">Other Info</h4>
                    <div className="grid grid-cols-2 md:grid-cols-3 gap-4 mb-2">
                      <div><span className="font-medium">OTO:</span> {selectedFormDetails.form.oto || 'N/A'}</div>
                      <div><span className="font-medium">OTO Amount Saved:</span> {selectedFormDetails.form.oto_amount_saved || 'N/A'}</div>
                      <div><span className="font-medium">Entered in UTS:</span> {selectedFormDetails.form.entered_in_uts || 'N/A'}</div>
                    </div>
                    <h4 className="font-semibold text-gray-800 text-lg border-b pb-2 mb-2 mt-4">Comments</h4>
                    <div className="mb-2 bg-gray-100 rounded p-2 text-gray-700 min-h-[2rem]">{selectedFormDetails.form.comments || 'N/A'}</div>
                  </div>
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
                            {selectedFormDetails.rows.map((row: any, idx: number) => (
                              <tr key={idx}>
                                <td className="px-4 py-2 text-sm text-gray-900">{row.line_location || 'N/A'}</td>
                                <td className="px-4 py-2 text-sm text-gray-900">{row.run_no || 'N/A'}</td>
                                <td className="px-4 py-2 text-sm text-gray-900">{row.exception_time_from_hh || 'N/A'}:{row.exception_time_from_mm || 'N/A'} to {row.exception_time_to_hh || 'N/A'}:{row.exception_time_to_mm || 'N/A'}</td>
                                <td className="px-4 py-2 text-sm text-gray-900">{row.overtime_hh || 'N/A'}:{row.overtime_mm || 'N/A'}</td>
                                <td className="px-4 py-2 text-sm text-gray-900">{row.bonus_hh || 'N/A'}:{row.bonus_mm || 'N/A'}</td>
                                <td className="px-4 py-2 text-sm text-gray-900">{row.nite_diff_hh || 'N/A'}:{row.nite_diff_mm || 'N/A'}</td>
                                <td className="px-4 py-2 text-sm text-gray-900">{row.ta_job_no || 'N/A'}</td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    )}
                  </div>
                </>
              )}
            </div>
            <div className="px-6 py-4 border-t border-gray-200 flex justify-end">
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