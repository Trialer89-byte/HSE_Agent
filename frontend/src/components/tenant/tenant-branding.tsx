interface Tenant {
  id: number;
  domain: string;
  display_name: string;
  settings?: any;
}

interface TenantBrandingProps {
  tenant: Tenant;
}

export function TenantBranding({ tenant }: TenantBrandingProps) {
  return (
    <div className="text-center">
      <div className="mx-auto h-12 w-12 bg-blue-600 rounded-lg flex items-center justify-center">
        <span className="text-white font-bold text-xl">
          {tenant.display_name.charAt(0).toUpperCase()}
        </span>
      </div>
    </div>
  );
}