export enum DeploymentMode {
  SAAS = 'saas',
  ON_PREMISE = 'on_premise',
  HYBRID = 'hybrid'
}

export enum SubscriptionPlan {
  BASIC = 'basic',
  PROFESSIONAL = 'professional',
  ENTERPRISE = 'enterprise',
  CUSTOM = 'custom'
}

export interface TenantInfo {
  id: number;
  display_name: string;
  domain?: string;
  custom_branding: Record<string, unknown>;
  is_active: boolean;
  deployment_mode: DeploymentMode;
}

export interface Tenant {
  id: number;
  name: string;
  display_name: string;
  domain?: string;
  deployment_mode: DeploymentMode;
  subscription_plan: SubscriptionPlan;
  max_users: number;
  max_documents: number;
  max_storage_gb: number;
  is_active: boolean;
  trial_expires_at?: string;
  enforce_2fa: boolean;
  session_timeout_minutes: number;
  created_at: string;
  updated_at: string;
  custom_branding?: {
    logo_url?: string;
    primary_color?: string;
    secondary_color?: string;
    [key: string]: unknown;
  };
  settings?: {
    max_file_size_mb?: number;
    allowed_file_types?: string[];
    ai_analysis_enabled?: boolean;
    require_approval?: boolean;
    audit_retention_days?: number;
    [key: string]: unknown;
  };
}

export interface TenantWithStats extends Tenant {
  user_count: number;
  document_count: number;
  storage_used_gb: number;
}

export interface TenantContext {
  tenant: TenantInfo | null;
  isLoading: boolean;
  error: string | null;
  setTenant: (tenant: TenantInfo | null) => void;
  loadTenantByDomain: (domain: string) => Promise<void>;
  loadTenantBySubdomain: (subdomain: string) => Promise<void>;
  validateTenantAccess: (domain?: string, subdomain?: string) => Promise<boolean>;
}

export interface TenantValidationResponse {
  valid: boolean;
  tenant_id?: number;
  display_name?: string;
  deployment_mode?: string;
  message?: string;
}