import { TenantInfo, TenantValidationResponse } from '@/types/tenant';
import apiClient from '@/config/api';

/**
 * Detect tenant from various sources
 */
export class TenantDetection {
  /**
   * Extract tenant info from current URL
   */
  static extractFromUrl(): { domain?: string; subdomain?: string } {
    if (typeof window === 'undefined') return {};

    const hostname = window.location.hostname;
    
    // Skip localhost and IP addresses
    if (hostname === 'localhost' || /^\d+\.\d+\.\d+\.\d+$/.test(hostname)) {
      return {};
    }

    // Check if it's a subdomain (e.g., demo.hse-system.com)
    const parts = hostname.split('.');
    if (parts.length >= 3) {
      return {
        domain: hostname,
        subdomain: parts[0]
      };
    }

    return { domain: hostname };
  }

  /**
   * Extract tenant from query parameters
   */
  static extractFromQuery(): { domain?: string } {
    if (typeof window === 'undefined') return {};

    const urlParams = new URLSearchParams(window.location.search);
    const domain = urlParams.get('tenant');
    
    return domain ? { domain } : {};
  }

  /**
   * Extract tenant from localStorage (fallback)
   */
  static extractFromStorage(): { domain?: string; tenantId?: string } {
    if (typeof window === 'undefined') return {};

    const domain = localStorage.getItem('tenant_domain');
    const tenantId = localStorage.getItem('tenant_id');
    
    return { domain: domain || undefined, tenantId: tenantId || undefined };
  }

  /**
   * Get tenant info by domain
   */
  static async getTenantByDomain(domain: string): Promise<TenantInfo> {
    const response = await apiClient.get<TenantInfo>(`/api/v1/public/tenants/by-domain`, {
      params: { domain }
    });
    return response.data;
  }

  /**
   * Get tenant info by subdomain
   */
  static async getTenantBySubdomain(subdomain: string): Promise<TenantInfo> {
    const response = await apiClient.get<TenantInfo>(`/api/v1/public/tenants/by-subdomain`, {
      params: { subdomain }
    });
    return response.data;
  }

  /**
   * Validate tenant access
   */
  static async validateTenantAccess(domain?: string, subdomain?: string): Promise<TenantValidationResponse> {
    const response = await apiClient.get<TenantValidationResponse>(`/api/v1/public/tenants/validate`, {
      params: { domain, subdomain }
    });
    return response.data;
  }

  /**
   * Auto-detect tenant from all available sources
   */
  static async autoDetectTenant(): Promise<TenantInfo | null> {
    try {
      // Try URL-based detection first
      const urlInfo = this.extractFromUrl();
      
      if (urlInfo.subdomain) {
        try {
          return await this.getTenantBySubdomain(urlInfo.subdomain);
        } catch (error) {
          console.warn('Failed to get tenant by subdomain:', error);
        }
      }

      if (urlInfo.domain) {
        try {
          return await this.getTenantByDomain(urlInfo.domain);
        } catch (error) {
          console.warn('Failed to get tenant by domain:', error);
        }
      }

      // Try query parameters
      const queryInfo = this.extractFromQuery();
      if (queryInfo.domain) {
        try {
          return await this.getTenantByDomain(queryInfo.domain);
        } catch (error) {
          console.warn('Failed to get tenant by query domain:', error);
        }
      }

      // Try localStorage as fallback
      const storageInfo = this.extractFromStorage();
      if (storageInfo.domain) {
        try {
          return await this.getTenantByDomain(storageInfo.domain);
        } catch (error) {
          console.warn('Failed to get tenant from storage:', error);
        }
      }

      return null;
    } catch (error) {
      console.error('Auto tenant detection failed:', error);
      return null;
    }
  }

  /**
   * Store tenant info in localStorage
   */
  static storeTenantInfo(tenant: TenantInfo): void {
    if (typeof window === 'undefined') return;

    localStorage.setItem('tenant_id', tenant.id.toString());
    localStorage.setItem('tenant_domain', tenant.domain || '');
    localStorage.setItem('tenant_info', JSON.stringify(tenant));
  }

  /**
   * Clear stored tenant info
   */
  static clearTenantInfo(): void {
    if (typeof window === 'undefined') return;

    localStorage.removeItem('tenant_id');
    localStorage.removeItem('tenant_domain');
    localStorage.removeItem('tenant_info');
  }

  /**
   * Get stored tenant info
   */
  static getStoredTenantInfo(): TenantInfo | null {
    if (typeof window === 'undefined') return null;

    try {
      const tenantInfo = localStorage.getItem('tenant_info');
      return tenantInfo ? JSON.parse(tenantInfo) : null;
    } catch (error) {
      console.error('Failed to parse stored tenant info:', error);
      return null;
    }
  }
}