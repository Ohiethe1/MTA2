import React, { useEffect, useState } from 'react';

interface AuditLog {
  id: string;
  user: string;
  action: string;
  target: string;
  timestamp: string;
  details?: string;
}

const AuditTrail: React.FC = () => {
  const [logs, setLogs] = useState<AuditLog[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchAuditLogs = async () => {
      try {
        const response = await fetch('http://localhost:8000/api/audit-trail');
        if (!response.ok) throw new Error('Failed to fetch audit logs');
        const data = await response.json();
        setLogs(data.logs || []);
      } catch (err: any) {
        setError(err.message || 'Unknown error');
      } finally {
        setLoading(false);
      }
    };
    fetchAuditLogs();
  }, []);

  return (
    <div className="max-w-4xl mx-auto mt-10 bg-white p-8 rounded shadow">
      <h2 className="text-2xl font-bold mb-6">Audit Trail</h2>
      {loading && <div>Loading audit logs...</div>}
      {error && <div className="text-red-600">{error}</div>}
      {!loading && !error && logs.length === 0 && (
        <div className="text-gray-500">No audit logs found.</div>
      )}
      {!loading && !error && logs.length > 0 && (
        <table className="w-full table-auto border-collapse">
          <thead>
            <tr className="bg-gray-100">
              <th className="px-4 py-2 text-left">User</th>
              <th className="px-4 py-2 text-left">Action</th>
              <th className="px-4 py-2 text-left">Target</th>
              <th className="px-4 py-2 text-left">Timestamp</th>
              <th className="px-4 py-2 text-left">Details</th>
            </tr>
          </thead>
          <tbody>
            {logs.map(log => (
              <tr key={log.id} className="border-b hover:bg-gray-50">
                <td className="px-4 py-2">{log.user}</td>
                <td className="px-4 py-2">{log.action}</td>
                <td className="px-4 py-2">{log.target}</td>
                <td className="px-4 py-2">{new Date(log.timestamp).toLocaleString()}</td>
                <td className="px-4 py-2">{log.details || '-'}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
};

export default AuditTrail; 