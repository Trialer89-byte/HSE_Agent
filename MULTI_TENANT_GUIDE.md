# Guida al Sistema Multi-Tenant HSE

## Panoramica

Il sistema HSE è stato implementato con un'architettura multi-tenant che supporta diverse modalità di deployment:

### Modalità di Deployment

1. **SaaS Multi-tenant**: Tutti i clienti condividono la stessa istanza dell'applicazione e database, con isolamento logico dei dati
2. **On-Premise**: Ogni cliente ha un'installazione dedicata sui propri server con database isolato
3. **Hybrid**: Database dedicati ma infrastruttura gestita da noi

## Caratteristiche Principali

### Isolamento dei Dati
- **Automatic Tenant Filtering**: Tutti i query vengono automaticamente filtrati per tenant
- **Tenant Context**: Middleware che gestisce il contesto tenant per ogni richiesta
- **Security Validation**: Validazione che gli utenti possano accedere solo ai dati del proprio tenant

### Identificazione Tenant
Il sistema supporta tre metodi per identificare il tenant:
1. **JWT Token**: Il token contiene il `tenant_id` dell'utente
2. **Subdomain**: `azienda.hse-system.com` identifica automaticamente il tenant
3. **Header HTTP**: `X-Tenant-Domain` o `X-Tenant-ID`

### Configurazioni per Tenant
Ogni tenant può avere:
- Limiti personalizzati (utenti, documenti, storage)
- Impostazioni specifiche (file types, AI provider, workflow)
- Branding personalizzato (logo, colori)
- Configurazioni di sicurezza (2FA, IP restrictions, session timeout)

## Struttura del Database

### Modelli Principali

```python
# Tenant Model
class Tenant(Base, TimestampMixin):
    id = Column(Integer, primary_key=True)
    name = Column(String(255), unique=True)  # Identificatore unico
    display_name = Column(String(255))       # Nome visualizzato
    domain = Column(String(255), unique=True) # Dominio per routing
    deployment_mode = Column(Enum(DeploymentMode))
    subscription_plan = Column(Enum(SubscriptionPlan))
    # ... altri campi

# Tutti i modelli ereditano TenantMixin
class User(Base, TimestampMixin, TenantMixin):
    # tenant_id viene aggiunto automaticamente
    
class WorkPermit(Base, TimestampMixin, TenantMixin):
    # tenant_id viene aggiunto automaticamente

class Document(Base, TimestampMixin, TenantMixin):
    # tenant_id viene aggiunto automaticamente
```

### TenantMixin
```python
class TenantMixin:
    @declared_attr
    def tenant_id(cls):
        return Column(Integer, ForeignKey("tenants.id", ondelete="CASCADE"), 
                     nullable=False, index=True)
```

## API Endpoints

### Gestione Tenant (Super Admin)
- `POST /api/v1/admin/tenants/` - Crea nuovo tenant
- `GET /api/v1/admin/tenants/` - Lista tutti i tenant
- `GET /api/v1/admin/tenants/{id}` - Dettagli tenant
- `PUT /api/v1/admin/tenants/{id}` - Aggiorna tenant
- `DELETE /api/v1/admin/tenants/{id}` - Elimina tenant

### Endpoints Pubblici
- `GET /api/v1/public/tenants/by-domain?domain=example.com` - Info tenant per dominio
- `GET /api/v1/public/tenants/validate` - Valida accesso tenant

## Utilizzo del Sistema

### Per Sviluppatori

#### Query Tenant-Aware
```python
from app.core.tenant_queries import get_tenant_query_manager

@router.get("/permits")
@tenant_required
async def get_permits(db: Session = Depends(get_db)):
    query_manager = get_tenant_query_manager(db)
    permits = query_manager.query(WorkPermit).all()
    return permits
```

#### Creazione Record
```python
# Automatic tenant assignment
work_permit = query_manager.create(
    WorkPermit,
    title="New Permit",
    description="Description"
    # tenant_id viene assegnato automaticamente
)
```

### Per Amministratori di Sistema

#### Inizializzazione Tenant
```bash
cd backend
python init_tenants.py
```

Questo script crea:
- 3 tenant di esempio (SaaS, On-Premise, Small Business)
- Utenti di esempio per ogni tenant
- Super admin globale

#### Configurazione Tenant

Esempio di configurazione tenant:
```json
{
  "settings": {
    "max_file_size_mb": 50,
    "allowed_file_types": [".pdf", ".docx"],
    "ai_analysis_enabled": true,
    "require_approval": true,
    "audit_retention_days": 365
  },
  "custom_branding": {
    "logo_url": "https://company.com/logo.png",
    "primary_color": "#1976d2",
    "secondary_color": "#424242"
  }
}
```

## Sicurezza

### Isolamento Dati
- **Row Level Security**: Ogni query viene automaticamente filtrata per tenant
- **Validation**: Controlli che impediscono accesso cross-tenant
- **Audit**: Logging completo delle azioni per tenant

### Controlli Accesso
- **RBAC**: Role-Based Access Control all'interno del tenant
- **IP Restrictions**: Limitazioni IP per tenant enterprise
- **2FA**: Two-Factor Authentication obbligatorio per alcuni tenant
- **Session Management**: Timeout personalizzati per tenant

## Deployment

### SaaS Multi-tenant
1. Un'unica istanza dell'applicazione
2. Database condiviso con isolamento logico
3. Scaling orizzontale dell'applicazione
4. Backup centralizzato

### On-Premise
1. Installazione dedicata per cliente
2. Database isolato completamente
3. Configurazione specifica per ambiente cliente
4. Manutenzione e aggiornamenti dedicati

### Configurazione Database

#### SaaS (condiviso)
```env
DATABASE_URL=postgresql://user:pass@localhost:5432/hse_saas
```

#### On-Premise (dedicato)
```python
# Configurato nel modello Tenant
tenant.database_url = "postgresql://client:pass@client-db:5432/hse_client"
```

## Testing

### Test Multi-tenancy

```python
# Esempio di test
def test_tenant_isolation():
    # Crea due tenant
    tenant1 = create_tenant("tenant1")
    tenant2 = create_tenant("tenant2")
    
    # Crea dati per tenant1
    with tenant_context.set_tenant(tenant1.id):
        permit1 = create_work_permit("Permit for tenant1")
    
    # Verifica che tenant2 non veda i dati di tenant1
    with tenant_context.set_tenant(tenant2.id):
        permits = query_manager.query(WorkPermit).all()
        assert permit1 not in permits
```

### Headers per Testing

```bash
# Test con header tenant
curl -H "X-Tenant-Domain: demo.hse-system.com" \
     -H "Authorization: Bearer {token}" \
     http://localhost:8000/api/v1/permits

# Test con subdomain
curl -H "Host: demo.hse-system.com" \
     -H "Authorization: Bearer {token}" \
     http://localhost:8000/api/v1/permits
```

## Monitoring e Metriche

### Metriche per Tenant
- Numero di utenti attivi
- Documenti caricati
- Storage utilizzato
- Richieste API per tenant
- Performance per tenant

### Alerting
- Superamento limiti per tenant
- Errori di isolamento dati
- Problemi di connessione database (on-premise)
- Scadenza trial

## Troubleshooting

### Problemi Comuni

1. **Tenant non trovato**
   - Verificare configurazione dominio
   - Controllare stato attivo del tenant

2. **Accesso negato cross-tenant**
   - Verificare JWT token contiene tenant_id corretto
   - Controllare middleware tenant

3. **Database connection error (on-premise)**
   - Verificare database_url nel tenant
   - Testare connettività database

### Log e Debug

```python
# Abilitare debug logging
import logging
logging.getLogger("app.middleware.tenant").setLevel(logging.DEBUG)
logging.getLogger("app.core.tenant_queries").setLevel(logging.DEBUG)
```

## Best Practices

### Sviluppo
1. Utilizzare sempre `@tenant_required` per endpoint che richiedono tenant
2. Usare `TenantQueryManager` per tutte le operazioni database
3. Non bypassare mai i filtri tenant
4. Testare sempre l'isolamento dati

### Produzione
1. Monitorare metriche per tenant
2. Backup regolari (separati per on-premise)
3. Alerting su superamento limiti
4. Audit logging completo

### Sicurezza
1. Validare sempre tenant_id nei JWT
2. Non esporre dati cross-tenant nelle API
3. Logging di tutti gli accessi cross-tenant tentati
4. Review regolare dei permessi tenant

## Roadmap Future

- [ ] Supporto per database sharding
- [ ] Migration tool tra modalità deployment
- [ ] Dashboard amministratore avanzato
- [ ] Backup automatico per tenant
- [ ] Billing e usage tracking
- [ ] API rate limiting per tenant