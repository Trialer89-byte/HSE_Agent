'use client';

import { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { apiCall } from '@/config/api';

interface WorkPermit {
  id: number;
  permit_number?: string;
  title: string;
  description: string;
  work_type: string;
  location: string;
  status: string;
  risk_level?: string;
  start_date?: string;
  end_date?: string;
  contractor_name?: string;
  contractor_company?: string;
  safety_requirements?: string;
  equipment_required?: string;
  hazards_identified?: string;
  control_measures?: string;
  created_by?: string;
  created_at: string;
  approved_by?: string;
  approved_at?: string;
  rejection_reason?: string;
  analyzed_at?: string;
  ai_confidence?: number;
  ai_version?: string;
  ai_analysis?: any;
  content_analysis?: any;
  risk_assessment?: any;
  compliance_check?: any;
  dpi_recommendations?: any;
  action_items?: any[];
}

export default function WorkPermitDetailPage() {
  const params = useParams();
  const router = useRouter();
  const [permit, setPermit] = useState<WorkPermit | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);

  useEffect(() => {
    if (params.id) {
      fetchPermit(params.id as string);
    }
  }, [params.id]);

  const fetchPermit = async (id: string) => {
    try {
      setIsLoading(true);
      const response = await apiCall(`/api/v1/permits/${id}`, {
        method: 'GET',
      });
      setPermit(response);
    } catch (error: any) {
      console.error('Error fetching permit:', error);
      setError(error.message || 'Failed to fetch work permit');
      if (error.message?.includes('404')) {
        router.push('/work-permits');
      }
    } finally {
      setIsLoading(false);
    }
  };

  const handleApprove = async () => {
    if (!permit) return;
    
    try {
      await apiCall(`/api/v1/permits/${permit.id}/approve`, {
        method: 'POST',
        body: JSON.stringify({ comments: 'Approved via web interface' }),
      });
      fetchPermit(permit.id.toString());
    } catch (error: any) {
      console.error('Error approving permit:', error);
      alert('Failed to approve permit: ' + error.message);
    }
  };

  const handleReject = async () => {
    if (!permit) return;
    
    const reason = prompt('Please provide a reason for rejection:');
    if (!reason) return;
    
    try {
      await apiCall(`/api/v1/permits/${permit.id}/reject`, {
        method: 'POST',
        body: JSON.stringify({ reason }),
      });
      fetchPermit(permit.id.toString());
    } catch (error: any) {
      console.error('Error rejecting permit:', error);
      alert('Failed to reject permit: ' + error.message);
    }
  };

  const handleAnalyze = async () => {
    if (!permit) return;
    
    setIsAnalyzing(true);
    try {
      await apiCall(`/api/v1/permits/${permit.id}/analyze`, {
        method: 'POST',
        body: JSON.stringify({}),
      });
      // Poll for analysis result
      setTimeout(() => fetchPermit(permit.id.toString()), 2000);
    } catch (error: any) {
      console.error('Error analyzing permit:', error);
      alert('Failed to analyze permit: ' + error.message);
    } finally {
      setIsAnalyzing(false);
    }
  };

  const getStatusColor = (status: string | undefined) => {
    if (!status) return 'bg-gray-100 text-gray-800';
    
    switch (status.toLowerCase()) {
      case 'approved':
      case 'approvato':
        return 'bg-green-100 text-green-800';
      case 'pending':
      case 'in_attesa':
        return 'bg-yellow-100 text-yellow-800';
      case 'rejected':
      case 'rifiutato':
        return 'bg-red-100 text-red-800';
      case 'expired':
      case 'scaduto':
        return 'bg-gray-100 text-gray-800';
      case 'draft':
      case 'bozza':
        return 'bg-blue-100 text-blue-800';
      default:
        return 'bg-blue-100 text-blue-800';
    }
  };

  const getRiskColor = (risk: string | undefined) => {
    if (!risk) return 'bg-gray-100 text-gray-800 border-gray-300';
    
    switch (risk.toLowerCase()) {
      case 'high':
      case 'alto':
        return 'bg-red-100 text-red-800 border-red-300';
      case 'medium':
      case 'medio':
        return 'bg-yellow-100 text-yellow-800 border-yellow-300';
      case 'low':
      case 'basso':
        return 'bg-green-100 text-green-800 border-green-300';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-300';
    }
  };

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-2 text-gray-600">Loading permit details...</p>
        </div>
      </div>
    );
  }

  if (error || !permit) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <p className="text-red-600">{error || 'Permit not found'}</p>
          <button
            onClick={() => router.push('/work-permits')}
            className="mt-4 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
          >
            Back to Permits
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <button
                onClick={() => router.push('/work-permits')}
                className="mr-4 text-gray-500 hover:text-gray-700"
              >
                ← Back
              </button>
              <h1 className="text-xl font-semibold">Work Permit Details</h1>
            </div>
            <div className="flex items-center space-x-2">
              {permit.status === 'pending' && (
                <>
                  <button
                    onClick={handleApprove}
                    className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700"
                  >
                    Approve
                  </button>
                  <button
                    onClick={handleReject}
                    className="px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700"
                  >
                    Reject
                  </button>
                </>
              )}
              <button
                onClick={handleAnalyze}
                disabled={isAnalyzing}
                className="px-4 py-2 bg-purple-600 text-white rounded-md hover:bg-purple-700 disabled:opacity-50"
              >
                {isAnalyzing ? 'Analyzing...' : 'AI Analysis'}
              </button>
            </div>
          </div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          {/* Header */}
          <div className="bg-white shadow rounded-lg p-6 mb-6">
            <div className="flex justify-between items-start">
              <div>
                <h2 className="text-2xl font-bold text-gray-900">{permit.title}</h2>
                <p className="text-sm text-gray-500 mt-1">Permit #{permit.permit_number}</p>
              </div>
              <div className="flex space-x-2">
                <span className={`px-3 py-1 rounded-full text-sm font-semibold ${getStatusColor(permit.status)}`}>
                  {permit.status}
                </span>
                {permit.risk_level && (
                  <span className={`px-3 py-1 rounded-full text-sm font-semibold border ${getRiskColor(permit.risk_level)}`}>
                    {permit.risk_level} Risk
                  </span>
                )}
              </div>
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Main Content */}
            <div className="lg:col-span-2 space-y-6">
              {/* Description */}
              <div className="bg-white shadow rounded-lg p-6">
                <h3 className="text-lg font-semibold mb-3">Description</h3>
                <p className="text-gray-700">{permit.description}</p>
              </div>

              {/* Work Details */}
              <div className="bg-white shadow rounded-lg p-6">
                <h3 className="text-lg font-semibold mb-3">Work Details</h3>
                <dl className="grid grid-cols-2 gap-4">
                  <div>
                    <dt className="text-sm font-medium text-gray-500">Work Type</dt>
                    <dd className="mt-1 text-sm text-gray-900 capitalize">{permit.work_type.replace('_', ' ')}</dd>
                  </div>
                  <div>
                    <dt className="text-sm font-medium text-gray-500">Location</dt>
                    <dd className="mt-1 text-sm text-gray-900">{permit.location}</dd>
                  </div>
                  {permit.start_date && (
                    <div>
                      <dt className="text-sm font-medium text-gray-500">Start Date</dt>
                      <dd className="mt-1 text-sm text-gray-900">
                        {new Date(permit.start_date).toLocaleString()}
                      </dd>
                    </div>
                  )}
                  {permit.end_date && (
                    <div>
                      <dt className="text-sm font-medium text-gray-500">End Date</dt>
                      <dd className="mt-1 text-sm text-gray-900">
                        {new Date(permit.end_date).toLocaleString()}
                      </dd>
                    </div>
                  )}
                </dl>
              </div>

              {/* Contractor Information */}
              {(permit.contractor_name || permit.contractor_company) && (
                <div className="bg-white shadow rounded-lg p-6">
                  <h3 className="text-lg font-semibold mb-3">Contractor Information</h3>
                  <dl className="grid grid-cols-2 gap-4">
                    <div>
                      <dt className="text-sm font-medium text-gray-500">Name</dt>
                      <dd className="mt-1 text-sm text-gray-900">{permit.contractor_name || 'N/A'}</dd>
                    </div>
                    <div>
                      <dt className="text-sm font-medium text-gray-500">Company</dt>
                      <dd className="mt-1 text-sm text-gray-900">{permit.contractor_company || 'N/A'}</dd>
                    </div>
                  </dl>
                </div>
              )}

              {/* Safety Information */}
              <div className="bg-white shadow rounded-lg p-6">
                <h3 className="text-lg font-semibold mb-3">Safety Information</h3>
                <div className="space-y-4">
                  {permit.safety_requirements && (
                    <div>
                      <h4 className="text-sm font-medium text-gray-700">Safety Requirements</h4>
                      <p className="mt-1 text-sm text-gray-600">{permit.safety_requirements}</p>
                    </div>
                  )}
                  {permit.equipment_required && (
                    <div>
                      <h4 className="text-sm font-medium text-gray-700">Equipment Required</h4>
                      <p className="mt-1 text-sm text-gray-600">{permit.equipment_required}</p>
                    </div>
                  )}
                  {permit.hazards_identified && (
                    <div>
                      <h4 className="text-sm font-medium text-gray-700">Hazards Identified</h4>
                      <p className="mt-1 text-sm text-gray-600">{permit.hazards_identified}</p>
                    </div>
                  )}
                  {permit.control_measures && (
                    <div>
                      <h4 className="text-sm font-medium text-gray-700">Control Measures</h4>
                      <p className="mt-1 text-sm text-gray-600">{permit.control_measures}</p>
                    </div>
                  )}
                </div>
              </div>
            </div>

            {/* Sidebar */}
            <div className="space-y-6">
              {/* Metadata */}
              <div className="bg-white shadow rounded-lg p-6">
                <h3 className="text-lg font-semibold mb-3">Permit Information</h3>
                <dl className="space-y-3">
                  <div>
                    <dt className="text-sm font-medium text-gray-500">Created By</dt>
                    <dd className="mt-1 text-sm text-gray-900">{permit.created_by || 'System'}</dd>
                  </div>
                  <div>
                    <dt className="text-sm font-medium text-gray-500">Created At</dt>
                    <dd className="mt-1 text-sm text-gray-900">
                      {new Date(permit.created_at).toLocaleString()}
                    </dd>
                  </div>
                  {permit.approved_by && (
                    <div>
                      <dt className="text-sm font-medium text-gray-500">Approved By</dt>
                      <dd className="mt-1 text-sm text-gray-900">{permit.approved_by}</dd>
                    </div>
                  )}
                  {permit.approved_at && (
                    <div>
                      <dt className="text-sm font-medium text-gray-500">Approved At</dt>
                      <dd className="mt-1 text-sm text-gray-900">
                        {new Date(permit.approved_at).toLocaleString()}
                      </dd>
                    </div>
                  )}
                  {permit.rejection_reason && (
                    <div>
                      <dt className="text-sm font-medium text-gray-500">Rejection Reason</dt>
                      <dd className="mt-1 text-sm text-red-600">{permit.rejection_reason}</dd>
                    </div>
                  )}
                </dl>
              </div>

              {/* AI Analysis */}
              {permit.ai_analysis && permit.ai_analysis.executive_summary && (
                <div className="bg-white shadow rounded-lg p-6">
                  <h3 className="text-lg font-semibold mb-3">AI Analysis</h3>
                  <div className="space-y-3">
                    {permit.ai_confidence !== undefined && (
                      <div>
                        <span className="text-sm font-medium text-gray-500">Confidence Score: </span>
                        <span className={`font-semibold ${
                          permit.ai_confidence > 0.7 ? 'text-green-600' :
                          permit.ai_confidence > 0.4 ? 'text-yellow-600' :
                          'text-red-600'
                        }`}>
                          {(permit.ai_confidence * 100).toFixed(0)}%
                        </span>
                      </div>
                    )}
                    {permit.ai_analysis.executive_summary && (
                      <>
                        <div>
                          <span className="text-sm font-medium text-gray-500">Compliance Level: </span>
                          <span className="font-semibold">{permit.ai_analysis.executive_summary.compliance_level}</span>
                        </div>
                        {permit.ai_analysis.executive_summary.key_findings && permit.ai_analysis.executive_summary.key_findings.length > 0 && (
                          <div>
                            <p className="text-sm font-medium text-gray-500 mb-1">Key Findings:</p>
                            <ul className="text-sm text-gray-600 list-disc list-inside">
                              {permit.ai_analysis.executive_summary.key_findings.map((finding: string, index: number) => (
                                <li key={index}>{finding}</li>
                              ))}
                            </ul>
                          </div>
                        )}
                        {permit.ai_analysis.executive_summary.next_steps && permit.ai_analysis.executive_summary.next_steps.length > 0 && (
                          <div>
                            <p className="text-sm font-medium text-gray-500 mb-1">Next Steps:</p>
                            <ul className="text-sm text-gray-600 list-disc list-inside">
                              {permit.ai_analysis.executive_summary.next_steps.map((step: string, index: number) => (
                                <li key={index}>{step}</li>
                              ))}
                            </ul>
                          </div>
                        )}
                      </>
                    )}
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}