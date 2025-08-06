'use client';

import { ProtectedRoute } from '@/components/auth/protected-route';
import { useAuthStore } from '@/stores/auth-store';
import { useTenantStore } from '@/stores/tenant-store';
import { TenantBranding } from '@/components/tenant/tenant-branding';

export default function DashboardPage() {
  const { user, logout } = useAuthStore();
  const { tenant } = useTenantStore();

  const handleLogout = () => {
    logout();
    window.location.href = '/auth/login';
  };

  return (
    <ProtectedRoute>
      <div className="min-h-screen bg-gray-50">
        {/* Header */}
        <header className="bg-white shadow">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between items-center py-6">
              <div className="flex items-center space-x-4">
                {tenant && <TenantBranding tenant={tenant} showName />}
              </div>
              
              <div className="flex items-center space-x-4">
                <div className="text-sm text-gray-500">
                  Welcome, {user?.first_name || user?.username}
                </div>
                <button
                  onClick={handleLogout}
                  className="bg-gray-100 hover:bg-gray-200 px-3 py-2 rounded-md text-sm text-gray-700"
                >
                  Logout
                </button>
              </div>
            </div>
          </div>
        </header>

        {/* Main Content */}
        <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
          <div className="px-4 py-6 sm:px-0">
            <div className="border-4 border-dashed border-gray-200 rounded-lg h-96 p-8">
              <div className="text-center">
                <h1 className="text-3xl font-bold text-gray-900 mb-4">
                  HSE Management Dashboard
                </h1>
                
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
                  {/* User Info Card */}
                  <div className="bg-white p-6 rounded-lg shadow">
                    <h3 className="text-lg font-medium text-gray-900 mb-2">User Information</h3>
                    <div className="space-y-1 text-sm text-gray-600">
                      <p><strong>Name:</strong> {user?.first_name} {user?.last_name}</p>
                      <p><strong>Email:</strong> {user?.email}</p>
                      <p><strong>Role:</strong> {user?.role}</p>
                      <p><strong>Department:</strong> {user?.department || 'N/A'}</p>
                    </div>
                  </div>

                  {/* Tenant Info Card */}
                  <div className="bg-white p-6 rounded-lg shadow">
                    <h3 className="text-lg font-medium text-gray-900 mb-2">Organization</h3>
                    <div className="space-y-1 text-sm text-gray-600">
                      <p><strong>Name:</strong> {tenant?.display_name}</p>
                      <p><strong>Domain:</strong> {tenant?.domain}</p>
                      <p><strong>Mode:</strong> {tenant?.deployment_mode}</p>
                      <p><strong>Status:</strong> {tenant?.is_active ? 'Active' : 'Inactive'}</p>
                    </div>
                  </div>

                  {/* Quick Actions Card */}
                  <div className="bg-white p-6 rounded-lg shadow">
                    <h3 className="text-lg font-medium text-gray-900 mb-2">Quick Actions</h3>
                    <div className="space-y-2">
                      <button className="w-full bg-blue-600 text-white py-2 px-4 rounded hover:bg-blue-700">
                        Create Work Permit
                      </button>
                      <button className="w-full bg-green-600 text-white py-2 px-4 rounded hover:bg-green-700">
                        Upload Document
                      </button>
                      <button className="w-full bg-gray-600 text-white py-2 px-4 rounded hover:bg-gray-700">
                        View Reports
                      </button>
                    </div>
                  </div>
                </div>

                <div className="text-gray-500">
                  <p>Multi-tenant HSE system is working correctly!</p>
                  <p className="text-sm mt-2">
                    Tenant ID: {tenant?.id} | User ID: {user?.id}
                  </p>
                </div>
              </div>
            </div>
          </div>
        </main>
      </div>
    </ProtectedRoute>
  );
}