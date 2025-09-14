'use client';

import { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { apiCall, apiCallWithTimeout } from '@/config/api';

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
  equipment_required?: string;
  hazards_identified?: string;
  dpi_required?: string[];  // DPI field
  risk_mitigation_actions?: string[];  // Mitigating actions field
  created_by?: string;
  created_at: string;
  approved_by?: string;
  approved_at?: string;
  rejection_reason?: string;
  analyzed_at?: string;
  ai_version?: string;
  ai_analysis?: any;
  risk_assessment?: any;
  action_items?: any[];
}

export default function WorkPermitDetailPage() {
  const params = useParams();
  const router = useRouter();
  const [permit, setPermit] = useState<WorkPermit | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  const [isUpdating, setIsUpdating] = useState(false);

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
      // Force fresh analysis with proper request body and extended timeout
      await apiCallWithTimeout(`/api/v1/permits/${permit.id}/analyze`, {
        method: 'POST',
        body: JSON.stringify({
          orchestrator: "advanced",
          force_reanalysis: true  // Force fresh analysis, ignore cache
        }),
      }, 120000); // 120 second timeout for AI analysis
      // Poll for analysis result with longer delay for advanced orchestrator
      setTimeout(() => fetchPermit(permit.id.toString()), 10000);
    } catch (error: any) {
      console.error('Error analyzing permit:', error);
      alert('Failed to analyze permit: ' + error.message);
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleUpdatePermit = async (formData: FormData) => {
    if (!permit) return;
    
    setIsUpdating(true);
    try {
      const updateData = {
        title: formData.get('title')?.toString(),
        description: formData.get('description')?.toString(),
        work_type: formData.get('work_type')?.toString(),
        location: formData.get('location')?.toString(),
        risk_level: formData.get('risk_level')?.toString(),
        start_date: formData.get('start_date') ? new Date(formData.get('start_date') as string).toISOString() : null,
        end_date: formData.get('end_date') ? new Date(formData.get('end_date') as string).toISOString() : null,
        status: formData.get('status')?.toString(),
        dpi_required: formData.get('dpi_required') ? formData.get('dpi_required')?.toString().split(',').map(s => s.trim()).filter(s => s) : [],
        risk_mitigation_actions: formData.get('risk_mitigation_actions') ? formData.get('risk_mitigation_actions')?.toString().split(',').map(s => s.trim()).filter(s => s) : [],
      };

      // Remove null/undefined values
      const cleanedData = Object.fromEntries(
        Object.entries(updateData).filter(([_, value]) => value !== null && value !== undefined && value !== '')
      );

      await apiCall(`/api/v1/permits/${permit.id}`, {
        method: 'PUT',
        body: JSON.stringify(cleanedData),
      });
      
      setIsEditModalOpen(false);
      fetchPermit(permit.id.toString());
    } catch (error: any) {
      console.error('Error updating permit:', error);
      alert('Failed to update permit: ' + error.message);
    } finally {
      setIsUpdating(false);
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
              <button
                onClick={() => setIsEditModalOpen(true)}
                className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
              >
                Edit
              </button>
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
{isAnalyzing ? '🧠 AI Analysis in progress... (may take up to 2 minutes)' : '🤖 AI Analysis'}
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
                  {permit.custom_fields?.workers_count && (
                    <div>
                      <dt className="text-sm font-medium text-gray-500">Workers Count</dt>
                      <dd className="mt-1 text-sm text-gray-900">
                        {permit.custom_fields.workers_count} workers
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
                  {permit.dpi_required && permit.dpi_required.length > 0 && (
                    <div>
                      <h4 className="text-sm font-medium text-gray-700">DPI Richiesti</h4>
                      <ul className="mt-1 text-sm text-gray-600 list-disc list-inside">
                        {Array.isArray(permit.dpi_required) 
                          ? permit.dpi_required.map((dpi, index) => (
                              <li key={index}>{dpi}</li>
                            ))
                          : <li>{permit.dpi_required}</li>
                        }
                      </ul>
                    </div>
                  )}
                  {permit.risk_mitigation_actions && permit.risk_mitigation_actions.length > 0 && (
                    <div>
                      <h4 className="text-sm font-medium text-gray-700">Azioni di Mitigazione dei Rischi</h4>
                      <ul className="mt-1 text-sm text-gray-600 list-disc list-inside">
                        {Array.isArray(permit.risk_mitigation_actions) 
                          ? permit.risk_mitigation_actions.map((action, index) => (
                              <li key={index}>{action}</li>
                            ))
                          : <li>{permit.risk_mitigation_actions}</li>
                        }
                      </ul>
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

              {/* AI Analysis - Comprehensive Display */}
              {(permit.ai_analysis || permit.risk_assessment || permit.action_items) && (
                <div className="bg-white shadow rounded-lg p-6">
                  <h3 className="text-lg font-semibold mb-4">🤖 AI Analysis Results</h3>
                  
                  {/* Analysis Metadata */}
                  <div className="bg-gray-50 rounded-lg p-4 mb-4">
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                      {permit.ai_version && (
                        <div>
                          <span className="text-gray-500">AI Version:</span>
                          <span className="ml-2 font-mono text-xs">{permit.ai_version}</span>
                        </div>
                      )}
                      {permit.analyzed_at && (
                        <div className="col-span-2">
                          <span className="text-gray-500">Analyzed:</span>
                          <span className="ml-2">{new Date(permit.analyzed_at).toLocaleString()}</span>
                        </div>
                      )}
                    </div>
                  </div>



                  {/* Risk Assessment */}
                  {permit.risk_assessment && Object.keys(permit.risk_assessment).length > 0 && (
                    <div className="mb-6">
                      <h4 className="font-semibold text-gray-900 mb-3">⚠️ Risk Assessment</h4>
                      <div className="bg-red-50 rounded-lg p-3">
                        <pre className="text-xs text-gray-700 whitespace-pre-wrap overflow-x-auto">
                          {JSON.stringify(permit.risk_assessment, null, 2)}
                        </pre>
                      </div>
                    </div>
                  )}

                  {/* DPI Analysis from DPIEvaluatorAgent */}
                  {permit.ai_analysis?.specialist_results && (
                    (() => {
                      const dpiEvaluator = permit.ai_analysis.specialist_results.find((result: any) => 
                        result.specialist === 'DPI_Evaluator'
                      );
                      
                      if (!dpiEvaluator) return null;
                      
                      return (
                        <div className="mb-6">
                          <h4 className="font-semibold text-gray-900 mb-3">🦺 DPI Analysis</h4>
                          <div className="bg-orange-50 border border-orange-200 rounded-lg p-4 space-y-4">
                            
                            {/* DPI Adequacy Status */}
                            {dpiEvaluator.existing_measures_evaluation?.dpi_adequacy && (
                              <div className="flex items-center">
                                <span className="text-sm text-gray-600 w-32">DPI Status:</span>
                                <span className={`font-semibold px-2 py-1 rounded text-xs ${
                                  dpiEvaluator.existing_measures_evaluation.dpi_adequacy === 'ADEGUATI' ? 'bg-green-100 text-green-800' :
                                  dpiEvaluator.existing_measures_evaluation.dpi_adequacy === 'PARZIALI' ? 'bg-yellow-100 text-yellow-800' :
                                  'bg-red-100 text-red-800'
                                }`}>
                                  {dpiEvaluator.existing_measures_evaluation.dpi_adequacy}
                                </span>
                              </div>
                            )}

                            {/* Current DPI */}
                            {dpiEvaluator.existing_measures_evaluation?.existing_dpi && 
                             dpiEvaluator.existing_measures_evaluation.existing_dpi.length > 0 && (
                              <div>
                                <span className="text-sm font-medium text-gray-700">📋 Current DPI:</span>
                                <ul className="mt-2 ml-4 text-sm text-gray-600 list-disc space-y-1">
                                  {dpiEvaluator.existing_measures_evaluation.existing_dpi.map((dpi: any, index: number) => (
                                    <li key={index}>{String(dpi)}</li>
                                  ))}
                                </ul>
                              </div>
                            )}

                            {/* Required/Missing DPI */}
                            {dpiEvaluator.dpi_requirements && dpiEvaluator.dpi_requirements.length > 0 && (
                              <div>
                                <span className="text-sm font-medium text-gray-700">⚠️ Required DPI:</span>
                                <ul className="mt-2 ml-4 text-sm text-gray-600 list-disc space-y-1">
                                  {dpiEvaluator.dpi_requirements.map((dpi: any, index: number) => (
                                    <li key={index} className="text-orange-700 font-medium">{String(dpi)}</li>
                                  ))}
                                </ul>
                              </div>
                            )}


                          </div>
                        </div>
                      );
                    })()
                  )}

                  {/* Action Items */}
                  {permit.action_items && permit.action_items.length > 0 && (
                    <div className="mb-6">
                      <h4 className="font-semibold text-gray-900 mb-3">🎯 Action Items</h4>
                      <div className="space-y-3">
                        {permit.action_items.map((item: any, index: number) => (
                          <div key={index} className={`border rounded-lg p-4 ${
                            item.priority === 'alta' ? 'bg-red-50 border-red-200' :
                            item.priority === 'media' ? 'bg-yellow-50 border-yellow-200' :
                            'bg-blue-50 border-blue-200'
                          }`}>
                            <div className="flex items-start justify-between">
                              <div className="flex-1">
                                <div className="flex items-center mb-2">
                                  <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${
                                    item.priority === 'alta' ? 'bg-red-100 text-red-800' :
                                    item.priority === 'media' ? 'bg-yellow-100 text-yellow-800' :
                                    'bg-blue-100 text-blue-800'
                                  }`}>
                                    {item.priority === 'alta' ? '🔴 Alta' :
                                     item.priority === 'media' ? '🟡 Media' : '🔵 Bassa'}
                                  </span>
                                  <span className="ml-2 text-xs text-gray-500">
                                    {item.type?.replace('_', ' ') || 'Safety Action'}
                                  </span>
                                </div>
                                
                                <div className="mb-3">
                                  <p className="text-sm font-medium text-gray-900">
                                    {item.suggested_action || 'Azione di sicurezza'}
                                  </p>
                                </div>

                                {item.references && item.references.length > 0 && (
                                  <div className="mt-2">
                                    <p className="text-xs text-gray-600">
                                      <strong>Riferimenti normativi:</strong> {item.references.join(', ')}
                                    </p>
                                  </div>
                                )}
                              </div>
                              
                              <div className="ml-4 flex-shrink-0">
                                {item.frontend_display?.icon && (
                                  <span className="text-lg">
                                    {item.frontend_display.icon === 'alert-triangle' ? '⚠️' :
                                     item.frontend_display.icon === 'shield-check' ? '🛡️' :
                                     item.frontend_display.icon === 'file-text' ? '📋' : '📋'}
                                  </span>
                                )}
                              </div>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Raw AI Analysis (for debugging) */}
                  {permit.ai_analysis && Object.keys(permit.ai_analysis).length > 1 && (
                    <details className="mt-4">
                      <summary className="cursor-pointer font-semibold text-gray-700 hover:text-gray-900">
                        🔧 Raw AI Analysis Data (Debug)
                      </summary>
                      <div className="mt-3 bg-gray-50 rounded-lg p-3">
                        <pre className="text-xs text-gray-600 whitespace-pre-wrap overflow-x-auto">
                          {JSON.stringify(permit.ai_analysis, null, 2)}
                        </pre>
                      </div>
                    </details>
                  )}

                  {/* Analysis Errors */}
                  {permit.ai_analysis?.errors && permit.ai_analysis.errors.length > 0 && (
                    <div className="mt-4 bg-red-50 border border-red-200 rounded-lg p-4">
                      <h4 className="font-semibold text-red-700 mb-2">🚨 Analysis Errors</h4>
                      <ul className="text-sm text-red-600 list-disc list-inside space-y-1">
                        {permit.ai_analysis.errors.map((error: string, index: number) => (
                          <li key={index}>{error}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>
        </div>
      </main>

      {/* Edit Modal */}
      {isEditModalOpen && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6">
              <div className="flex justify-between items-center mb-4">
                <h3 className="text-lg font-semibold">Edit Work Permit</h3>
                <button
                  onClick={() => setIsEditModalOpen(false)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  ✕
                </button>
              </div>
              
              <form action={handleUpdatePermit} className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {/* Title */}
                  <div className="md:col-span-2">
                    <label className="block text-sm font-medium text-gray-700 mb-1">Title</label>
                    <input
                      name="title"
                      type="text"
                      defaultValue={permit?.title}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      required
                    />
                  </div>

                  {/* Description */}
                  <div className="md:col-span-2">
                    <label className="block text-sm font-medium text-gray-700 mb-1">Description</label>
                    <textarea
                      name="description"
                      rows={4}
                      defaultValue={permit?.description}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      required
                    />
                  </div>

                  {/* Work Type */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Work Type</label>
                    <select
                      name="work_type"
                      defaultValue={permit?.work_type}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    >
                      <option value="">Select type</option>
                      <option value="chimico">Chimico</option>
                      <option value="scavo">Scavo</option>
                      <option value="manutenzione">Manutenzione</option>
                      <option value="elettrico">Elettrico</option>
                      <option value="meccanico">Meccanico</option>
                      <option value="edile">Edile</option>
                      <option value="pulizia">Pulizia</option>
                      <option value="altro">Altro</option>
                    </select>
                  </div>

                  {/* Status */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Status</label>
                    <select
                      name="status"
                      defaultValue={permit?.status}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    >
                      <option value="draft">Draft</option>
                      <option value="analyzing">Analyzing</option>
                      <option value="reviewed">Reviewed</option>
                      <option value="approved">Approved</option>
                      <option value="rejected">Rejected</option>
                      <option value="completed">Completed</option>
                    </select>
                  </div>

                  {/* Location */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Location</label>
                    <input
                      name="location"
                      type="text"
                      defaultValue={permit?.location}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>

                  {/* Risk Level */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Risk Level</label>
                    <select
                      name="risk_level"
                      defaultValue={permit?.risk_level}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    >
                      <option value="low">Low</option>
                      <option value="medium">Medium</option>
                      <option value="high">High</option>
                      <option value="critical">Critical</option>
                    </select>
                  </div>


                  {/* Workers Count */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Workers Count</label>
                    <input
                      name="workers_count"
                      type="number"
                      min="1"
                      defaultValue={permit?.custom_fields?.workers_count || ''}
                      placeholder="Number of workers"
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>

                  {/* Start Date */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Start Date</label>
                    <input
                      name="start_date"
                      type="datetime-local"
                      defaultValue={permit?.start_date ? new Date(permit.start_date).toISOString().slice(0, 16) : ''}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>

                  {/* End Date */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">End Date</label>
                    <input
                      name="end_date"
                      type="datetime-local"
                      defaultValue={permit?.end_date ? new Date(permit.end_date).toISOString().slice(0, 16) : ''}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>

                  {/* DPI Required */}
                  <div className="md:col-span-2">
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      DPI Required (comma-separated)
                    </label>
                    <input
                      name="dpi_required"
                      type="text"
                      defaultValue={permit?.dpi_required?.join(', ')}
                      placeholder="Guanti isolanti, Elmetto dielettrico, Calzature isolanti"
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>

                  {/* Risk Mitigation Actions */}
                  <div className="md:col-span-2">
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Risk Mitigation Actions (comma-separated)
                    </label>
                    <textarea
                      name="risk_mitigation_actions"
                      rows={3}
                      defaultValue={permit?.risk_mitigation_actions?.join(', ')}
                      placeholder="Procedura LOTO, Verifica assenza tensione, Coordinamento con sala controllo"
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>
                </div>

                {/* Modal Footer */}
                <div className="flex justify-end space-x-3 pt-4 border-t">
                  <button
                    type="button"
                    onClick={() => setIsEditModalOpen(false)}
                    className="px-4 py-2 text-gray-700 bg-gray-200 rounded-md hover:bg-gray-300"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    disabled={isUpdating}
                    className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
                  >
                    {isUpdating ? 'Updating...' : 'Update Permit'}
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}