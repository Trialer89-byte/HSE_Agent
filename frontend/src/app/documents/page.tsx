'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { apiCall } from '@/config/api';
import Link from 'next/link';

interface Document {
  id: number;
  filename: string;
  file_type: string;
  file_size: number;
  description?: string;
  category: string;
  tags: string[];
  uploaded_by: string;
  uploaded_at: string;
  analysis_status?: string;
  analysis_result?: any;
}

export default function DocumentsPage() {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [showUploadForm, setShowUploadForm] = useState(false);
  const [uploadForm, setUploadForm] = useState({
    title: '',
    document_type: 'normativa',
    document_code: '',
    category: '',
    subcategory: '',
    authority: '',
    scope: '',
    industry_sectors: ''
  });
  const router = useRouter();

  useEffect(() => {
    fetchDocuments();
  }, []);

  const fetchDocuments = async () => {
    try {
      setIsLoading(true);
      const response = await apiCall('/api/v1/documents/', {
        method: 'GET',
      });
      setDocuments(response.documents || response.data || []);
    } catch (error: any) {
      console.error('Error fetching documents:', error);
      setError(error.message || 'Failed to fetch documents');
      if (error.message?.includes('401') || error.message?.includes('Unauthorized')) {
        router.push('/auth/login');
      }
    } finally {
      setIsLoading(false);
    }
  };

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.files && event.target.files[0]) {
      const file = event.target.files[0];
      setSelectedFile(file);
      setUploadForm(prev => ({
        ...prev,
        title: file.name.replace(/\.[^/.]+$/, '') // Auto-populate title from filename
      }));
      setShowUploadForm(true);
    }
  };

  const handleUpload = async () => {
    if (!selectedFile || !uploadForm.title.trim()) {
      alert('Please select a file and provide a title');
      return;
    }

    setUploading(true);
    const formData = new FormData();
    formData.append('file', selectedFile);
    formData.append('title', uploadForm.title.trim());
    formData.append('document_type', uploadForm.document_type);
    
    // Add optional fields if provided
    if (uploadForm.document_code.trim()) formData.append('document_code', uploadForm.document_code.trim());
    if (uploadForm.category.trim()) formData.append('category', uploadForm.category.trim());
    if (uploadForm.subcategory.trim()) formData.append('subcategory', uploadForm.subcategory.trim());
    if (uploadForm.authority.trim()) formData.append('authority', uploadForm.authority.trim());
    if (uploadForm.scope.trim()) formData.append('scope', uploadForm.scope.trim());
    if (uploadForm.industry_sectors.trim()) formData.append('industry_sectors', uploadForm.industry_sectors.trim());

    // Debug logging
    console.log('FormData contents:');
    for (const [key, value] of formData.entries()) {
      console.log(`${key}:`, value);
    }

    try {
      // Use direct fetch instead of apiCall to avoid header issues
      const url = `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/v1/documents/upload`;
      
      // Get auth headers manually
      const headers: any = {};
      if (typeof window !== 'undefined') {
        const token = localStorage.getItem('auth_token');
        if (token) {
          headers['Authorization'] = `Bearer ${token}`;
        }
        
        const tenantId = localStorage.getItem('tenant_id');
        if (tenantId) {
          headers['X-Tenant-ID'] = tenantId;
        }
      }

      const response = await fetch(url, {
        method: 'POST',
        headers: headers, // Don't set Content-Type for FormData
        body: formData,
      });

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`Upload failed: ${errorText}`);
      }

      await response.json();
      
      // Reset form
      setSelectedFile(null);
      setShowUploadForm(false);
      setUploadForm({
        title: '',
        document_type: 'normativa',
        document_code: '',
        category: '',
        subcategory: '',
        authority: '',
        scope: '',
        industry_sectors: ''
      });
      
      fetchDocuments();
      alert('Document uploaded successfully!');
    } catch (error: any) {
      console.error('Error uploading document:', error);
      alert('Failed to upload document: ' + (error.message || 'Unknown error'));
    } finally {
      setUploading(false);
    }
  };

  const handleFormChange = (field: string, value: string) => {
    setUploadForm(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
  };

  const getFileIcon = (fileType: string | undefined) => {
    if (!fileType) return '📎';
    
    const type = fileType.toLowerCase();
    if (type.includes('pdf')) {
      return '📄';
    } else if (type.includes('word') || type.includes('doc')) {
      return '📝';
    } else if (type.includes('excel') || type.includes('sheet')) {
      return '📊';
    } else if (type.includes('image')) {
      return '🖼️';
    } else {
      return '📎';
    }
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 flex items-center justify-center">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-orange-500/30 border-t-orange-500 rounded-full animate-spin mx-auto"></div>
          <p className="mt-6 text-slate-400 font-medium">Loading document vault...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 flex items-center justify-center">
        <div className="text-center p-8 bg-slate-800/40 backdrop-blur-sm border border-slate-700/50 rounded-2xl">
          <div className="text-4xl mb-4">⚠️</div>
          <p className="text-red-400 font-mono text-sm mb-6">ERROR: {error}</p>
          <Link
            href="/dashboard"
            className="px-6 py-3 bg-gradient-to-r from-orange-500 to-red-600 hover:from-orange-600 hover:to-red-700 text-white font-bold rounded-xl transition-all duration-200"
          >
            ← RETURN TO CONTROL CENTER
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
      {/* Industrial Background */}
      <div className="absolute inset-0 opacity-5">
        <div className="absolute inset-0" style={{
          backgroundImage: `url("data:image/svg+xml,%3Csvg width='100' height='100' viewBox='0 0 100 100' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='%23ffffff' fill-opacity='0.1'%3E%3Cpath d='M0 0h25v25H0zM75 0h25v25H75zM25 25h25v25H25zM0 75h25v25H0zM75 75h25v25H75z'/%3E%3C/g%3E%3C/svg%3E")`,
        }} />
      </div>

      {/* Header */}
      <header className="relative z-10 bg-slate-800/50 backdrop-blur-sm border-b border-slate-700/50">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <Link
                href="/dashboard"
                className="flex items-center space-x-2 text-slate-300 hover:text-white transition-colors"
              >
                <span className="text-xl">←</span>
                <span className="text-sm uppercase tracking-wide">Control Center</span>
              </Link>
              <div className="w-px h-6 bg-slate-700"></div>
              <div className="flex items-center space-x-3">
                <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-blue-600 rounded-lg flex items-center justify-center">
                  <span className="text-white font-black text-lg">📋</span>
                </div>
                <div>
                  <h1 className="text-xl font-black text-white tracking-tight">DOCUMENT VAULT</h1>
                  <p className="text-slate-400 text-xs uppercase tracking-wide">HSE Documentation System</p>
                </div>
              </div>
            </div>
            
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2 px-3 py-1 bg-slate-700/50 rounded-lg border border-slate-600/50">
                <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
                <span className="text-slate-300 text-xs font-semibold uppercase tracking-wide">Archive Active</span>
              </div>
              <input
                type="file"
                id="file-upload"
                className="hidden"
                onChange={handleFileSelect}
                accept=".pdf,.doc,.docx,.txt"
              />
              <label
                htmlFor="file-upload"
                className="px-6 py-2 bg-gradient-to-r from-blue-500 to-blue-600 hover:from-blue-600 hover:to-blue-700 text-white font-bold rounded-xl transition-all duration-200 text-sm cursor-pointer"
              >
                + UPLOAD DOCUMENT
              </label>
              {showUploadForm && (
                <button
                  onClick={() => {setShowUploadForm(false); setSelectedFile(null);}}
                  className="px-4 py-2 bg-slate-700/50 hover:bg-slate-600/50 border border-slate-600/50 text-slate-300 hover:text-white rounded-lg transition-all duration-200 text-sm font-medium"
                >
                  CANCEL
                </button>
              )}
            </div>
          </div>
        </div>
      </header>

      {/* Upload Form Modal */}
      {showUploadForm && (
        <div className="fixed inset-0 bg-slate-900/80 backdrop-blur-sm overflow-y-auto h-full w-full z-50">
          <div className="relative top-20 mx-auto p-6 border border-slate-700/50 w-11/12 md:w-3/4 lg:w-1/2 shadow-2xl rounded-2xl bg-slate-800/90 backdrop-blur-sm">
            <div className="mt-3">
              <div className="flex items-center space-x-3 mb-6">
                <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-blue-600 rounded-lg flex items-center justify-center">
                  <span className="text-white font-black text-sm">+</span>
                </div>
                <h3 className="text-xl font-black text-white tracking-tight">UPLOAD DOCUMENT</h3>
              </div>
              
              {selectedFile && (
                <div className="mb-6 p-4 bg-slate-700/40 border border-slate-600/50 rounded-xl">
                  <p className="text-sm text-slate-300">Selected file: <span className="font-mono text-orange-400">{selectedFile.name}</span></p>
                  <p className="text-xs text-slate-400">Size: {(selectedFile.size / 1024 / 1024).toFixed(2)} MB</p>
                </div>
              )}

              <div className="space-y-4">
                {/* Title */}
                <div>
                  <label className="block text-sm font-bold text-slate-200 uppercase tracking-wide mb-2">
                    Document Title <span className="text-red-400">*</span>
                  </label>
                  <input
                    type="text"
                    value={uploadForm.title}
                    onChange={(e) => handleFormChange('title', e.target.value)}
                    className="w-full px-4 py-3 bg-slate-900/50 border border-slate-600/50 rounded-xl text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent font-mono"
                    placeholder="Enter document title..."
                    required
                  />
                </div>

                {/* Document Type */}
                <div>
                  <label className="block text-sm font-bold text-slate-200 uppercase tracking-wide mb-2">
                    Classification <span className="text-red-400">*</span>
                  </label>
                  <select
                    value={uploadForm.document_type}
                    onChange={(e) => handleFormChange('document_type', e.target.value)}
                    className="w-full px-4 py-3 bg-slate-900/50 border border-slate-600/50 rounded-xl text-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent font-mono"
                    required
                  >
                    <option value="normativa">NORMATIVA (Legal Document/Regulation)</option>
                    <option value="istruzione_operativa">ISTRUZIONE OPERATIVA (Operating Procedure)</option>
                    <option value="manuale">MANUALE (Manual)</option>
                    <option value="procedura">PROCEDURA (Procedure)</option>
                    <option value="altro">ALTRO (Other)</option>
                  </select>
                </div>

                {/* Document Code */}
                <div>
                  <label className="block text-sm font-bold text-slate-200 uppercase tracking-wide mb-2">
                    Document Code
                  </label>
                  <input
                    type="text"
                    value={uploadForm.document_code}
                    onChange={(e) => handleFormChange('document_code', e.target.value)}
                    className="w-full px-4 py-3 bg-slate-900/50 border border-slate-600/50 rounded-xl text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent font-mono"
                    placeholder="e.g., D.Lgs 81/08, ISO 45001"
                  />
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {/* Category */}
                  <div>
                    <label className="block text-sm font-bold text-slate-200 uppercase tracking-wide mb-2">
                      Category
                    </label>
                    <input
                      type="text"
                      value={uploadForm.category}
                      onChange={(e) => handleFormChange('category', e.target.value)}
                      className="w-full px-4 py-3 bg-slate-900/50 border border-slate-600/50 rounded-xl text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent font-mono"
                      placeholder="e.g., Safety, Environmental"
                    />
                  </div>

                  {/* Subcategory */}
                  <div>
                    <label className="block text-sm font-bold text-slate-200 uppercase tracking-wide mb-2">
                      Subcategory
                    </label>
                    <input
                      type="text"
                      value={uploadForm.subcategory}
                      onChange={(e) => handleFormChange('subcategory', e.target.value)}
                      className="w-full px-4 py-3 bg-slate-900/50 border border-slate-600/50 rounded-xl text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent font-mono"
                      placeholder="e.g., PPE, Chemical Handling"
                    />
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {/* Authority */}
                  <div>
                    <label className="block text-sm font-bold text-slate-200 uppercase tracking-wide mb-2">
                      Authority
                    </label>
                    <input
                      type="text"
                      value={uploadForm.authority}
                      onChange={(e) => handleFormChange('authority', e.target.value)}
                      className="w-full px-4 py-3 bg-slate-900/50 border border-slate-600/50 rounded-xl text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent font-mono"
                      placeholder="e.g., INAIL, EU"
                    />
                  </div>

                  {/* Scope */}
                  <div>
                    <label className="block text-sm font-bold text-slate-200 uppercase tracking-wide mb-2">
                      Scope
                    </label>
                    <input
                      type="text"
                      value={uploadForm.scope}
                      onChange={(e) => handleFormChange('scope', e.target.value)}
                      className="w-full px-4 py-3 bg-slate-900/50 border border-slate-600/50 rounded-xl text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent font-mono"
                      placeholder="e.g., Construction, Manufacturing"
                    />
                  </div>
                </div>

                {/* Industry Sectors */}
                <div>
                  <label className="block text-sm font-bold text-slate-200 uppercase tracking-wide mb-2">
                    Industry Sectors
                  </label>
                  <input
                    type="text"
                    value={uploadForm.industry_sectors}
                    onChange={(e) => handleFormChange('industry_sectors', e.target.value)}
                    className="w-full px-4 py-3 bg-slate-900/50 border border-slate-600/50 rounded-xl text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent font-mono"
                    placeholder="e.g., Construction, Chemical, Manufacturing (comma-separated)"
                  />
                </div>
              </div>

              <div className="flex justify-end space-x-4 mt-8">
                <button
                  onClick={() => {setShowUploadForm(false); setSelectedFile(null);}}
                  className="px-6 py-3 bg-slate-700/50 hover:bg-slate-600/50 border border-slate-600/50 text-slate-300 hover:text-white rounded-xl transition-all duration-200 font-medium"
                >
                  CANCEL
                </button>
                <button
                  onClick={handleUpload}
                  disabled={uploading || !uploadForm.title.trim()}
                  className="px-6 py-3 bg-gradient-to-r from-blue-500 to-blue-600 hover:from-blue-600 hover:to-blue-700 disabled:from-slate-600 disabled:to-slate-700 text-white font-bold rounded-xl transition-all duration-200 disabled:cursor-not-allowed"
                >
                  {uploading ? (
                    <div className="flex items-center space-x-2">
                      <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
                      <span>UPLOADING...</span>
                    </div>
                  ) : (
                    <span>🚀 UPLOAD TO VAULT</span>
                  )}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Main Content */}
      <main className="relative z-10 max-w-7xl mx-auto px-6 py-8">
        {documents.length === 0 ? (
          <div className="text-center py-24">
            <div className="w-24 h-24 bg-slate-800/40 rounded-2xl flex items-center justify-center mx-auto mb-6">
              <span className="text-4xl">📋</span>
            </div>
            <h3 className="text-2xl font-black text-white mb-2">VAULT EMPTY</h3>
            <p className="text-slate-400 mb-8">Initialize document archive with first upload</p>
            <label
              htmlFor="file-upload"
              className="inline-flex items-center space-x-3 px-8 py-4 bg-gradient-to-r from-blue-500 to-blue-600 hover:from-blue-600 hover:to-blue-700 text-white font-bold rounded-xl transition-all duration-200 transform hover:scale-105 cursor-pointer"
            >
              <span>📁</span>
              <span>UPLOAD FIRST DOCUMENT</span>
              <span className="text-blue-200">→</span>
            </label>
          </div>
        ) : (
          <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
            {documents.map((doc) => (
              <div key={doc.id} className="bg-slate-800/40 backdrop-blur-sm border border-slate-700/50 rounded-2xl overflow-hidden shadow-2xl hover:bg-slate-700/40 hover:border-slate-600/50 transition-all duration-300">
                <div className="p-6">
                  <div className="flex items-start justify-between mb-4">
                    <div className="flex items-center space-x-4">
                      <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-blue-600 rounded-xl flex items-center justify-center text-2xl">
                        {getFileIcon(doc.file_type)}
                      </div>
                      <div className="flex-1">
                        <p className="text-lg font-bold text-white truncate">
                          {doc.filename}
                        </p>
                        <p className="text-sm text-slate-400 font-mono">
                          {formatFileSize(doc.file_size)}
                        </p>
                      </div>
                    </div>
                  </div>
                  
                  <div className="space-y-3 mb-4">
                    <div className="flex items-center space-x-2">
                      <span className="text-slate-500">👤</span>
                      <span className="text-slate-300 text-sm">{doc.uploaded_by}</span>
                    </div>
                    <div className="flex items-center space-x-2">
                      <span className="text-slate-500">📅</span>
                      <span className="text-slate-300 text-sm font-mono">
                        {new Date(doc.uploaded_at).toLocaleDateString()}
                      </span>
                    </div>
                    {doc.category && (
                      <div className="flex items-center space-x-2">
                        <span className="text-slate-500">🏷️</span>
                        <span className="text-slate-300 text-sm">{doc.category}</span>
                      </div>
                    )}
                  </div>

                  {doc.tags && doc.tags.length > 0 && (
                    <div className="mb-4 flex flex-wrap gap-2">
                      {doc.tags.map((tag, index) => (
                        <span
                          key={index}
                          className="px-2 py-1 text-xs font-semibold bg-blue-500/20 text-blue-300 border border-blue-500/30 rounded-lg uppercase tracking-wide"
                        >
                          {tag}
                        </span>
                      ))}
                    </div>
                  )}
                </div>
                
                <div className="bg-slate-900/30 px-6 py-4 border-t border-slate-700/50">
                  <div className="flex justify-between items-center">
                    <button
                      className="flex items-center space-x-2 px-4 py-2 bg-gradient-to-r from-green-500 to-green-600 hover:from-green-600 hover:to-green-700 text-white font-bold rounded-lg transition-all duration-200 text-sm"
                      onClick={() => window.open(`/api/v1/documents/${doc.id}/download`, '_blank')}
                    >
                      <span>⬇️</span>
                      <span>DOWNLOAD</span>
                    </button>
                    {doc.analysis_status && (
                      <div className="flex items-center space-x-2">
                        <div className="w-2 h-2 bg-orange-400 rounded-full"></div>
                        <span className="text-xs text-slate-400 uppercase tracking-wide">
                          Analysis: {doc.analysis_status}
                        </span>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </main>
    </div>
  );
}