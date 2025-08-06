'use client';

import { TenantInfo } from '@/types/tenant';
import Image from 'next/image';

interface TenantBrandingProps {
  tenant: TenantInfo;
  showName?: boolean;
}

export function TenantBranding({ tenant, showName = false }: TenantBrandingProps) {
  const { custom_branding } = tenant;
  
  // Extract branding variables
  const logoUrl = typeof custom_branding?.logo_url === 'string' ? custom_branding.logo_url : undefined;
  const primaryColor = (typeof custom_branding?.primary_color === 'string' ? custom_branding.primary_color : undefined) || '#1976d2';
  const secondaryColor = (typeof custom_branding?.secondary_color === 'string' ? custom_branding.secondary_color : undefined) || '#424242';

  return (
    <div className="text-center">
      {/* Logo */}
      <div className="flex justify-center">
        {logoUrl ? (
          <div className="w-16 h-16 relative">
            <Image
              src={logoUrl}
              alt={`${tenant.display_name} logo`}
              fill
              className="object-contain"
              onError={(e) => {
                // Fallback to default logo on error
                e.currentTarget.style.display = 'none';
              }}
            />
          </div>
        ) : (
          <div
            className="w-16 h-16 rounded-lg flex items-center justify-center text-white text-2xl font-bold"
            style={{ backgroundColor: primaryColor }}
          >
            {tenant.display_name.charAt(0).toUpperCase()}
          </div>
        )}
      </div>

      {/* Organization name */}
      {showName && (
        <h1
          className="mt-4 text-xl font-semibold"
          style={{ color: primaryColor }}
        >
          {tenant.display_name}
        </h1>
      )}

      {/* Apply custom CSS variables for theme */}
      <style jsx>{`
        :global(:root) {
          --tenant-primary-color: ${primaryColor};
          --tenant-secondary-color: ${secondaryColor};
        }
      `}</style>
    </div>
  );
}