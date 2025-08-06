# Work Permit API Guide

## Overview
The Work Permit API allows you to create, read, update, and delete work permits in the HSE multi-tenant system.

## Base URL
```
http://localhost:8000/api/v1/permits
```

## Authentication
All endpoints require Bearer token authentication. Get your token from `/api/v1/auth/login`.

## Headers Required
- `Authorization: Bearer <your-token>`
- `Content-Type: application/json`
- `X-Tenant-Domain: <tenant-domain>` (for tenant isolation)

---

## CREATE Work Permit
**POST** `/api/v1/permits/`

### Request Body Schema

#### Required Fields ✅
- **`title`** (string, 5-255 chars): Titolo del permesso di lavoro
- **`description`** (string, min 10 chars): Descrizione dettagliata del lavoro

#### Optional Fields ⚪
- **`dpi_required`** (array of strings, default: []): DPI richiesti
  - Examples: `["respiratore", "imbracatura", "rilevatore_gas", "casco", "guanti"]`
- **`work_type`** (string): Tipo di lavoro
  - **Allowed values**: `"chimico"`, `"scavo"`, `"manutenzione"`, `"elettrico"`, `"meccanico"`, `"edile"`, `"pulizia"`, `"altro"`
- **`location`** (string): Ubicazione del lavoro
- **`duration_hours`** (integer, 1-168): Durata in ore (max 1 settimana)
- **`priority_level`** (string, default: "medium"): Livello di priorità
  - **Allowed values**: `"low"`, `"medium"`, `"high"`, `"critical"`
- **`custom_fields`** (object, default: {}): Campi personalizzati
- **`tags`** (array of strings, default: []): Tag di categorizzazione

### Example Request
```json
{
  "title": "Manutenzione Serbatoio A1",
  "description": "Pulizia interna e ispezione del serbatoio A1 per manutenzione ordinaria",
  "work_type": "manutenzione", 
  "location": "Area Stoccaggio - Serbatoio A1",
  "duration_hours": 4,
  "priority_level": "high",
  "dpi_required": ["respiratore", "imbracatura", "rilevatore_gas", "casco"],
  "tags": ["serbatoio", "manutenzione_ordinaria"],
  "custom_fields": {
    "department": "Maintenance",
    "equipment_id": "TANK_A1",
    "supervisor": "Mario Rossi"
  }
}
```

### Example Response (201 Created)
```json
{
  "id": 1,
  "tenant_id": 1,
  "title": "Manutenzione Serbatoio A1",
  "description": "Pulizia interna e ispezione del serbatoio A1...",
  "work_type": "manutenzione",
  "location": "Area Stoccaggio - Serbatoio A1", 
  "duration_hours": 4,
  "priority_level": "high",
  "dpi_required": ["respiratore", "imbracatura", "rilevatore_gas", "casco"],
  "tags": ["serbatoio", "manutenzione_ordinaria"],
  "custom_fields": {
    "department": "Maintenance",
    "equipment_id": "TANK_A1", 
    "supervisor": "Mario Rossi"
  },
  "status": "draft",
  "ai_confidence": 0.0,
  "ai_version": null,
  "created_by": 1,
  "approved_by": null,
  "created_at": "2025-08-05T15:08:49.140682",
  "updated_at": "2025-08-05T15:08:49.140682",
  "analyzed_at": null
}
```

---

## GET Work Permits List
**GET** `/api/v1/permits/`

### Query Parameters
- `page` (int, default: 1): Numero pagina
- `page_size` (int, default: 20, max: 100): Elementi per pagina  
- `status` (string): Filtra per status (`draft`, `analyzing`, `reviewed`, `approved`, `rejected`, `completed`)
- `work_type` (string): Filtra per tipo lavoro

### Example Request
```bash
GET /api/v1/permits/?page=1&page_size=10&status=draft&work_type=manutenzione
```

---

## GET Single Work Permit
**GET** `/api/v1/permits/{permit_id}`

### Example Response
```json
{
  "id": 1,
  "title": "Manutenzione Serbatoio A1",
  // ... full permit details
}
```

---

## UPDATE Work Permit  
**PUT** `/api/v1/permits/{permit_id}`

### Request Body
Same as CREATE but all fields are optional. Only provided fields will be updated.

---

## DELETE Work Permit
**DELETE** `/api/v1/permits/{permit_id}`

### Response
```json
{
  "message": "Work permit deleted successfully"
}
```

---

## AI ANALYSIS Work Permit
**POST** `/api/v1/permits/{permit_id}/analyze`

### Request Body
```json
{
  "force_reanalysis": false,
  "include_draft_documents": false,
  "analysis_scope": ["content", "risk", "compliance", "dpi"],
  "orchestrator": "autogen"
}
```

### Orchestrator Options
- **`"autogen"`**: Full multi-agent AI analysis (slower, comprehensive)
- **`"fast"`**: Quick single-call analysis (faster, basic)
- **`"mock"`**: Mock analysis for testing (instant)

---

## GET Analysis Status
**GET** `/api/v1/permits/{permit_id}/analysis-status`

### Response
```json
{
  "permit_id": 1,
  "status": "completed",
  "last_analysis_at": "2025-08-05T15:10:00Z",
  "confidence_score": 0.85,
  "analysis_id": "analysis_12345",
  "error_message": null
}
```

---

## Error Responses

### 400 Bad Request - Validation Error
```json
{
  "detail": [
    {
      "type": "string_too_short",
      "loc": ["body", "title"],
      "msg": "String should have at least 5 characters"
    }
  ]
}
```

### 403 Forbidden - Permission Error
```json
{
  "error": {
    "type": "HTTPException",
    "message": "Permission 'own.permits.create' required",
    "status_code": 403
  }
}
```

### 404 Not Found
```json
{
  "error": {
    "type": "HTTPException", 
    "message": "Work permit not found",
    "status_code": 404
  }
}
```

---

## Permission Requirements

### By Role:
- **super_admin**: Full access to all permits across all tenants
- **admin**: Full access to all permits in their tenant
- **manager**: Can create/read/update permits in their department + own permits
- **operator**: Can create/read/update only their own permits  
- **viewer**: Can only read their own permits

### Specific Permissions:
- `own.permits.create` - Create work permits
- `own.permits.read` - Read own work permits
- `own.permits.update` - Update own work permits
- `own.permits.delete` - Delete own work permits
- `permits.analyze` - Run AI analysis on permits

---

## Testing with cURL

### 1. Login and Get Token
```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "superadmin", "password": "SuperAdmin123!"}'
```

### 2. Create Work Permit
```bash
curl -X POST "http://localhost:8000/api/v1/permits/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "X-Tenant-Domain: demo.hse-system.com" \
  -d '{
    "title": "Test Maintenance Work",
    "description": "Routine maintenance of equipment in area B",
    "work_type": "manutenzione",
    "location": "Area B - Equipment Room",
    "duration_hours": 3,
    "priority_level": "medium",
    "dpi_required": ["casco", "guanti", "scarpe_antinfortunistiche"]
  }'
```

### 3. List Work Permits  
```bash
curl -X GET "http://localhost:8000/api/v1/permits/" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "X-Tenant-Domain: demo.hse-system.com"
```

---

## Available Test Users

| Username | Password | Role | Tenant | Access Level |
|----------|----------|------|--------|--------------|
| `superadmin` | `SuperAdmin123!` | super_admin | All | Full system access |
| `admin_demo_company` | `Admin123!` | admin | Demo Company | Full tenant access |
| `admin_enterprise_corp` | `Admin123!` | admin | Enterprise Corp | Full tenant access |

---

## Tenant Domains
- `demo.hse-system.com` - Demo Company
- `enterprise.hse-system.com` - Enterprise Corp  
- `manufacturing.hse-system.com` - Small Manufacturing

---

## Notes
- All work permits are automatically assigned to the user's tenant
- Status starts as `"draft"` and can be updated through the workflow
- AI analysis is optional but provides valuable safety insights
- The system enforces data isolation between tenants
- File uploads for work permits are not yet implemented but the schema supports them