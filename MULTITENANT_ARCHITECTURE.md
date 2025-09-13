# Multitenant Architecture Guide

## Overview

The HSE Agent system implements a comprehensive multitenant architecture that provides complete isolation between different organizations while sharing the same infrastructure. This document explains how multitenancy is implemented across all system components.

## Architecture Components

### 1. Database Layer (PostgreSQL)

#### Tenant Model
- **Primary Entity**: `Tenant` table stores organization information
- **Subscription Plans**: Enterprise, Professional, Basic
- **Deployment Modes**: SaaS, On-Premise, Hybrid
- **Settings**: Configurable limits (max_users, max_documents, AI features)

#### Tenant Isolation
- **Foreign Keys**: All major entities include `tenant_id` foreign key
- **User Model**: Users belong to specific tenant via `tenant_id`
- **Work Permits**: Isolated per tenant via `tenant_id`
- **Documents**: Tenant-specific document storage
- **Unique Constraints**: Username/email unique per tenant (not globally)

```sql
-- Example constraint ensuring tenant isolation
CONSTRAINT _tenant_username_uc UNIQUE (tenant_id, username)
```

### 2. Authentication & Authorization

#### Multi-level Role System
1. **super_admin**: Cross-tenant access, system management
2. **admin**: Full tenant access, user management
3. **manager**: Department-level access
4. **operator**: Own resources + department documents
5. **viewer**: Read-only access to own resources

#### Permission System
- **Wildcard Permissions**: `tenant.*`, `department.*`, `own.*`
- **Granular Control**: Specific resource permissions
- **Tenant Boundaries**: Non-super_admin users restricted to own tenant

#### JWT Token Integration
- **Tenant Context**: JWT tokens include `tenant_id`
- **Automatic Isolation**: Middleware extracts tenant from token
- **Session Management**: Tenant context maintained throughout request

### 3. Middleware & Request Processing

#### Tenant Middleware (`app/middleware/tenant.py`)
Automatically handles tenant context for every request:

```python
# Tenant extraction methods (in priority order):
1. JWT Token (most common)
2. Subdomain routing (company.hse-system.com)
3. Custom headers (X-Tenant-ID, X-Tenant-Domain)
```

#### Public Endpoints
- Health checks, authentication endpoints bypass tenant middleware
- Admin endpoints handle their own tenant validation
- Test endpoints for development

### 4. Vector Database (Weaviate)

#### Multitenant Configuration
```yaml
# docker-compose.simple.yml
weaviate:
  environment:
    - MULTI_TENANCY_ENABLED=true
    - TENANT_ACTIVITY_TIMEOUT=60m
```

#### Document Isolation
- **Storage**: Every document includes `tenant_id` field
- **Search**: All queries filtered by tenant_id
- **Schema**: Tenant field included in vector schema
- **Operations**: CRUD operations respect tenant boundaries

```python
# Example: Search with tenant isolation
where_filter = {
    "path": ["tenant_id"],
    "operator": "Equal", 
    "valueInt": tenant_id
}
```

### 5. API Layer

#### Tenant Context Injection
- **Request State**: `request.state.tenant_id` available in all endpoints
- **Automatic Filtering**: Database queries automatically filtered by tenant
- **Permission Checks**: Role-based access control per tenant

#### Endpoint Security
- **Protected Routes**: Most API endpoints require tenant context
- **Cross-tenant Prevention**: Users cannot access other tenants' data
- **Admin Overrides**: Super admins can access cross-tenant resources

### 6. File Storage & Object Storage

#### MinIO Configuration
- **Bucket Strategy**: Tenant-specific buckets or prefixed paths
- **Access Control**: Tenant-aware file access policies
- **Document Management**: File uploads tagged with tenant_id

### 7. Caching Layer (Redis)

#### Cache Key Strategy
- **Tenant Prefixes**: Cache keys include tenant identifier
- **Isolation**: No cross-tenant cache pollution
- **Session Storage**: User sessions tied to specific tenant

## Tenant Management

### Default Setup
```python
# Default tenant creation (create_admin.py)
tenant = Tenant(
    name="Default Company",
    domain="default.hse-enterprise.local",
    settings={
        "max_users": 100,
        "max_documents": 1000,
        "ai_analysis_enabled": True,
        "require_approval": True
    },
    subscription_plan=SubscriptionPlan.ENTERPRISE,
    is_active=True
)
```

### Admin User Creation
- **Super Admin**: Can create and manage tenants
- **Tenant Admins**: Manage users within their tenant
- **Default Credentials**: admin/HSEAdmin2024! (change in production)

## Security Features

### Tenant Isolation Guarantees
1. **Database Level**: Foreign key constraints prevent cross-tenant access
2. **Application Level**: Middleware and permissions enforce boundaries
3. **API Level**: Endpoint-level validation and filtering
4. **Storage Level**: File and vector storage respect tenant boundaries

### Network Security
- **Docker Networks**: Isolated container communication
- **Service Discovery**: Hostname-based service resolution
- **Port Management**: Controlled external access

## Development & Testing

### Local Development
- **Single Tenant**: Default tenant for development
- **Multi-tenant Testing**: Create additional tenants for testing
- **Admin Access**: Super admin can switch between tenants

### Production Deployment
- **Subdomain Routing**: `company1.hse-system.com`, `company2.hse-system.com`
- **Custom Domains**: Support for custom tenant domains
- **Load Balancing**: Tenant-aware request routing

## Configuration Examples

### Environment Variables
```bash
# Multitenant settings
MULTI_TENANCY_ENABLED=true
DEFAULT_TENANT_DOMAIN=default.hse-enterprise.local
TENANT_ACTIVITY_TIMEOUT=60m
```

### Docker Compose
```yaml
services:
  backend:
    environment:
      - MULTITENANT_MODE=enabled
    networks:
      - hse-network
  
  weaviate:
    environment:
      - MULTI_TENANCY_ENABLED=true
    networks:
      - hse-network
```

## Monitoring & Maintenance

### Tenant Metrics
- **Usage Tracking**: Per-tenant resource usage
- **Performance Monitoring**: Tenant-specific performance metrics
- **Audit Logging**: Tenant-aware audit trails

### Maintenance Tasks
- **Tenant Cleanup**: Inactive tenant cleanup procedures
- **Data Migration**: Tenant data migration tools
- **Backup Strategy**: Tenant-specific backup procedures

## Best Practices

### Security
1. **Never bypass tenant checks** in custom code
2. **Always validate tenant context** in API endpoints
3. **Use tenant-aware queries** for all database operations
4. **Implement audit logging** for cross-tenant operations

### Performance
1. **Index tenant_id fields** in database tables
2. **Use tenant-specific caching** strategies
3. **Monitor per-tenant resource usage**
4. **Implement tenant-aware rate limiting**

### Development
1. **Test with multiple tenants** during development
2. **Validate tenant isolation** in unit tests
3. **Use tenant context** in all business logic
4. **Follow permission patterns** consistently

## Troubleshooting

### Common Issues
1. **Missing tenant context**: Check middleware configuration
2. **Cross-tenant data access**: Verify permission checks
3. **Authentication failures**: Validate JWT tenant claims
4. **Vector search issues**: Confirm tenant filtering in Weaviate

### Debug Tools
- **Tenant extraction logs**: Check middleware logs
- **Permission validation**: Use permission debugging endpoints
- **Database queries**: Monitor tenant_id filtering in SQL logs
- **Vector operations**: Verify tenant isolation in Weaviate logs

## Future Enhancements

### Planned Features
1. **Tenant-specific branding**: Custom UI themes per tenant
2. **Advanced analytics**: Tenant performance dashboards
3. **Resource quotas**: Configurable tenant limits
4. **Automated scaling**: Tenant-based resource allocation

This architecture ensures complete tenant isolation while maintaining shared infrastructure efficiency, providing enterprise-grade multitenancy for the HSE Agent system.