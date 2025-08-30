'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { apiCall } from '@/config/api';

export default function NewWorkPermitPage() {
  const router = useRouter();
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisResult, setAnalysisResult] = useState<any>(null);
  const [showAnalysis, setShowAnalysis] = useState(false);
  
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    work_type: 'manutenzione',
    location: '',
    risk_level: 'low',
    start_date: '',
    end_date: '',
    contractor_name: '',
    contractor_company: '',
    safety_requirements: '',
    equipment_required: '',
    hazards_identified: '',
    control_measures: '',
    risk_mitigation_actions: '',  // New field
  });

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setIsSubmitting(true);

    try {
      const response = await apiCall('/api/v1/permits/', {
        method: 'POST',
        body: JSON.stringify(formData),
      });

      if (response.id) {
        router.push('/work-permits');
      }
    } catch (error: any) {
      console.error('Error creating permit:', error);
      setError(error.message || 'Failed to create work permit');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handlePreviewAnalysis = async () => {
    setError(null);
    setIsAnalyzing(true);

    // Validate required fields
    if (!formData.title || !formData.description || !formData.work_type) {
      setError('Title, description, and work type are required for analysis');
      setIsAnalyzing(false);
      return;
    }

    try {
      const response = await apiCall('/api/v1/permits/analyze-preview', {
        method: 'POST',
        body: JSON.stringify({
          ...formData,
          analysis_type: 'comprehensive'
        }),
      });

      setAnalysisResult(response.analysis_result);
      setShowAnalysis(true);
    } catch (error: any) {
      console.error('Error analyzing permit:', error);
      setError(error.message || 'Failed to analyze work permit');
    } finally {
      setIsAnalyzing(false);
    }
  };

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
              <h1 className="text-xl font-semibold">New Work Permit</h1>
            </div>
            <div className="flex items-center">
              <button
                type="button"
                onClick={handlePreviewAnalysis}
                disabled={isAnalyzing || !formData.title || !formData.description}
                className="px-4 py-2 bg-purple-600 text-white rounded-md hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed mr-4"
              >
                {isAnalyzing ? 'Analyzing...' : 'Preview Analysis'}
              </button>
            </div>
          </div>
        </div>
      </nav>

      <main className="max-w-3xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          <form onSubmit={handleSubmit} className="bg-white shadow-md rounded-lg p-6">
            {error && (
              <div className="mb-4 p-4 bg-red-50 border border-red-200 text-red-600 rounded">
                {error}
              </div>
            )}

            {/* Basic Information */}
            <div className="mb-6">
              <h2 className="text-lg font-semibold mb-4">Basic Information</h2>
              
              <div className="mb-4">
                <label htmlFor="title" className="block text-sm font-medium text-gray-700 mb-1">
                  Permit Title *
                </label>
                <input
                  type="text"
                  id="title"
                  name="title"
                  value={formData.title}
                  onChange={handleChange}
                  required
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="e.g., Electrical Maintenance Work"
                />
              </div>

              <div className="mb-4">
                <label htmlFor="description" className="block text-sm font-medium text-gray-700 mb-1">
                  Description *
                </label>
                <textarea
                  id="description"
                  name="description"
                  value={formData.description}
                  onChange={handleChange}
                  required
                  rows={3}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Describe the work to be performed..."
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label htmlFor="work_type" className="block text-sm font-medium text-gray-700 mb-1">
                    Work Type *
                  </label>
                  <select
                    id="work_type"
                    name="work_type"
                    value={formData.work_type}
                    onChange={handleChange}
                    required
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="manutenzione">Manutenzione</option>
                    <option value="elettrico">Elettrico</option>
                    <option value="meccanico">Meccanico</option>
                    <option value="chimico">Chimico</option>
                    <option value="edile">Edile</option>
                    <option value="scavo">Scavo</option>
                    <option value="pulizia">Pulizia</option>
                    <option value="altro">Altro</option>
                  </select>
                </div>

                <div>
                  <label htmlFor="risk_level" className="block text-sm font-medium text-gray-700 mb-1">
                    Risk Level *
                  </label>
                  <select
                    id="risk_level"
                    name="risk_level"
                    value={formData.risk_level}
                    onChange={handleChange}
                    required
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="low">Low</option>
                    <option value="medium">Medium</option>
                    <option value="high">High</option>
                  </select>
                </div>
              </div>
            </div>

            {/* Location and Dates */}
            <div className="mb-6">
              <h2 className="text-lg font-semibold mb-4">Location and Schedule</h2>
              
              <div className="mb-4">
                <label htmlFor="location" className="block text-sm font-medium text-gray-700 mb-1">
                  Work Location *
                </label>
                <input
                  type="text"
                  id="location"
                  name="location"
                  value={formData.location}
                  onChange={handleChange}
                  required
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="e.g., Building A, Floor 3, Room 301"
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label htmlFor="start_date" className="block text-sm font-medium text-gray-700 mb-1">
                    Start Date *
                  </label>
                  <input
                    type="datetime-local"
                    id="start_date"
                    name="start_date"
                    value={formData.start_date}
                    onChange={handleChange}
                    required
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>

                <div>
                  <label htmlFor="end_date" className="block text-sm font-medium text-gray-700 mb-1">
                    End Date *
                  </label>
                  <input
                    type="datetime-local"
                    id="end_date"
                    name="end_date"
                    value={formData.end_date}
                    onChange={handleChange}
                    required
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>
              </div>
            </div>

            {/* Contractor Information */}
            <div className="mb-6">
              <h2 className="text-lg font-semibold mb-4">Contractor Information</h2>
              
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label htmlFor="contractor_name" className="block text-sm font-medium text-gray-700 mb-1">
                    Contractor Name *
                  </label>
                  <input
                    type="text"
                    id="contractor_name"
                    name="contractor_name"
                    value={formData.contractor_name}
                    onChange={handleChange}
                    required
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="Full name"
                  />
                </div>

                <div>
                  <label htmlFor="contractor_company" className="block text-sm font-medium text-gray-700 mb-1">
                    Company *
                  </label>
                  <input
                    type="text"
                    id="contractor_company"
                    name="contractor_company"
                    value={formData.contractor_company}
                    onChange={handleChange}
                    required
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="Company name"
                  />
                </div>
              </div>
            </div>

            {/* Safety Information */}
            <div className="mb-6">
              <h2 className="text-lg font-semibold mb-4">Safety Requirements</h2>
              
              <div className="mb-4">
                <label htmlFor="safety_requirements" className="block text-sm font-medium text-gray-700 mb-1">
                  Safety Requirements
                </label>
                <textarea
                  id="safety_requirements"
                  name="safety_requirements"
                  value={formData.safety_requirements}
                  onChange={handleChange}
                  rows={3}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="List safety requirements (PPE, training, etc.)"
                />
              </div>

              <div className="mb-4">
                <label htmlFor="equipment_required" className="block text-sm font-medium text-gray-700 mb-1">
                  Equipment Required
                </label>
                <textarea
                  id="equipment_required"
                  name="equipment_required"
                  value={formData.equipment_required}
                  onChange={handleChange}
                  rows={2}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="List required equipment and tools"
                />
              </div>

              <div className="mb-4">
                <label htmlFor="hazards_identified" className="block text-sm font-medium text-gray-700 mb-1">
                  Hazards Identified
                </label>
                <textarea
                  id="hazards_identified"
                  name="hazards_identified"
                  value={formData.hazards_identified}
                  onChange={handleChange}
                  rows={3}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="List potential hazards"
                />
              </div>

              <div className="mb-4">
                <label htmlFor="control_measures" className="block text-sm font-medium text-gray-700 mb-1">
                  Control Measures
                </label>
                <textarea
                  id="control_measures"
                  name="control_measures"
                  value={formData.control_measures}
                  onChange={handleChange}
                  rows={3}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Describe control measures to mitigate risks"
                />
              </div>
              
              <div className="mb-4">
                <label htmlFor="risk_mitigation_actions" className="block text-sm font-medium text-gray-700 mb-1">
                  Azioni di Mitigazione dei Rischi
                </label>
                <textarea
                  id="risk_mitigation_actions"
                  name="risk_mitigation_actions"
                  value={formData.risk_mitigation_actions}
                  onChange={handleChange}
                  rows={4}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Descrivere le azioni specifiche per mitigare i rischi identificati (es. formazione specifica, supervisione aggiuntiva, controlli periodici, etc.)"
                />
                <p className="mt-1 text-sm text-gray-500">
                  Le azioni di mitigazione verranno analizzate dagli agenti AI per verificare la conformità del permesso
                </p>
              </div>
            </div>

            {/* Submit Buttons */}
            <div className="flex justify-end space-x-4">
              <button
                type="button"
                onClick={() => router.push('/work-permits')}
                className="px-6 py-2 border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={isSubmitting}
                className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isSubmitting ? 'Creating...' : 'Create Permit'}
              </button>
            </div>
          </form>

          {/* Analysis Results */}
          {showAnalysis && analysisResult && (
            <div className="mt-6 bg-white shadow-md rounded-lg p-6">
              <div className="flex justify-between items-center mb-4">
                <h2 className="text-lg font-semibold">Analysis Preview</h2>
                <button
                  onClick={() => setShowAnalysis(false)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  ✕
                </button>
              </div>

              {/* Executive Summary */}
              {analysisResult.executive_summary && (
                <div className="mb-6">
                  <h3 className="font-semibold mb-2">Executive Summary</h3>
                  <div className="grid grid-cols-2 gap-4 p-4 bg-gray-50 rounded">
                    <div>
                      <span className="text-sm text-gray-600">Overall Score:</span>
                      <span className={`ml-2 font-semibold ${
                        analysisResult.executive_summary.overall_score > 0.7 ? 'text-green-600' :
                        analysisResult.executive_summary.overall_score > 0.4 ? 'text-yellow-600' :
                        'text-red-600'
                      }`}>
                        {Math.round(analysisResult.executive_summary.overall_score * 100)}%
                      </span>
                    </div>
                    <div>
                      <span className="text-sm text-gray-600">Critical Issues:</span>
                      <span className={`ml-2 font-semibold ${
                        analysisResult.executive_summary.critical_issues === 0 ? 'text-green-600' :
                        analysisResult.executive_summary.critical_issues <= 2 ? 'text-yellow-600' :
                        'text-red-600'
                      }`}>
                        {analysisResult.executive_summary.critical_issues}
                      </span>
                    </div>
                    <div>
                      <span className="text-sm text-gray-600">Compliance Level:</span>
                      <span className="ml-2 font-semibold text-blue-600 capitalize">
                        {analysisResult.executive_summary.compliance_level}
                      </span>
                    </div>
                    <div>
                      <span className="text-sm text-gray-600">Est. Time:</span>
                      <span className="ml-2 font-semibold">
                        {analysisResult.executive_summary.estimated_completion_time}
                      </span>
                    </div>
                  </div>
                </div>
              )}

              {/* Key Findings */}
              {analysisResult.executive_summary?.key_findings && (
                <div className="mb-6">
                  <h3 className="font-semibold mb-2">Key Findings</h3>
                  <ul className="list-disc list-inside space-y-1">
                    {analysisResult.executive_summary.key_findings.map((finding: string, index: number) => (
                      <li key={index} className="text-sm text-gray-700">{finding}</li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Action Items */}
              {analysisResult.action_items && analysisResult.action_items.length > 0 && (
                <div className="mb-6">
                  <h3 className="font-semibold mb-2">Action Items</h3>
                  <div className="space-y-3">
                    {analysisResult.action_items.map((item: any, index: number) => (
                      <div key={index} className="border-l-4 border-blue-500 pl-4 py-2 bg-blue-50">
                        <div className="flex justify-between items-start">
                          <div>
                            <h4 className="font-medium text-sm">{item.title}</h4>
                            <p className="text-sm text-gray-600 mt-1">{item.description}</p>
                            {item.suggested_action && (
                              <p className="text-sm text-blue-600 mt-1">
                                <strong>Action:</strong> {item.suggested_action}
                              </p>
                            )}
                          </div>
                          <span className={`px-2 py-1 text-xs rounded-full ${
                            item.priority === 'alta' ? 'bg-red-100 text-red-800' :
                            item.priority === 'media' ? 'bg-yellow-100 text-yellow-800' :
                            'bg-green-100 text-green-800'
                          }`}>
                            {item.priority}
                          </span>
                        </div>
                        {item.estimated_effort && (
                          <p className="text-xs text-gray-500 mt-2">
                            Effort: {item.estimated_effort} | Role: {item.responsible_role}
                          </p>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Risk Assessment */}
              {analysisResult.risk_assessment?.identified_risks && (
                <div className="mb-6">
                  <h3 className="font-semibold mb-2">Identified Risks</h3>
                  <div className="space-y-2">
                    {analysisResult.risk_assessment.identified_risks.map((risk: any, index: number) => (
                      <div key={index} className="flex justify-between items-center p-3 border rounded">
                        <span className="text-sm">{risk.risk}</span>
                        <div className="flex space-x-2">
                          <span className={`px-2 py-1 text-xs rounded ${
                            risk.level === 'alto' ? 'bg-red-100 text-red-800' :
                            risk.level === 'medio' ? 'bg-yellow-100 text-yellow-800' :
                            'bg-green-100 text-green-800'
                          }`}>
                            {risk.level}
                          </span>
                          <span className="px-2 py-1 text-xs bg-gray-100 text-gray-800 rounded">
                            {risk.probability}
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* DPI Recommendations */}
              {analysisResult.dpi_recommendations?.required_dpi && (
                <div className="mb-6">
                  <h3 className="font-semibold mb-2">Required PPE</h3>
                  <div className="flex flex-wrap gap-2">
                    {analysisResult.dpi_recommendations.required_dpi.map((dpi: string, index: number) => (
                      <span key={index} className="px-3 py-1 bg-blue-100 text-blue-800 text-sm rounded-full">
                        {dpi}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      </main>
    </div>
  );
}