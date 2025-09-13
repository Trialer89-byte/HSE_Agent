# Guida Test con Swagger UI

## 1. Login e Ottieni Token
1. Vai a: http://localhost:8000/api/docs
2. Trova **POST /api/v1/auth/login**
3. Clicca "Try it out"
4. Inserisci nel body:
```json
{
  "username": "superadmin",
  "password": "SuperAdmin123!"
}
```
5. Clicca "Execute"
6. Copia il valore di `access_token` dalla risposta

## 2. Autorizza Swagger
1. Clicca il pulsante "Authorize" 🔐 in alto
2. Nel campo inserisci: `Bearer <token-copiato>`
   - Esempio: `Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...`
3. Clicca "Authorize" poi "Close"

## 3. Test Create Work Permit
1. Trova **POST /api/v1/permits**
2. Clicca "Try it out"
3. Inserisci nel body:
```json
{
  "title": "Manutenzione Serbatoio A1",
  "description": "Pulizia interna del serbatoio A1 con ispezione delle valvole di sicurezza",
  "work_type": "manutenzione",
  "location": "Area Stoccaggio - Serbatoio A1",
  "duration_hours": 4,
  "priority_level": "high",
  "dpi_required": ["respiratore", "imbracatura", "rilevatore_gas", "casco"],
  "tags": ["serbatoio", "manutenzione_ordinaria"]
}
```
4. **IMPORTANTE**: Prima di Execute, aggiungi negli headers:
   - `X-Tenant-Domain: demo.hse-system.com`
5. Clicca "Execute"

## 4. Test AI Analysis
1. Crea prima un permit (step 3) e nota l'`id` nella risposta
2. Trova **POST /api/v1/permits/{permit_id}/analyze**
3. Inserisci l'`id` del permit nel campo path
4. Nel body inserisci:
```json
{
  "orchestrator": "fast",
  "force_reanalysis": false,
  "analysis_scope": ["content", "risk", "compliance", "dpi"]
}
```
5. Aggiungi header: `X-Tenant-Domain: demo.hse-system.com`
6. Clicca "Execute" e attendi l'analisi

## 5. Test Analysis Preview (senza salvare)
1. Trova **POST /api/v1/permits/analyze-preview**
2. Nel body inserisci:
```json
{
  "title": "Test Saldatura Pipeline",
  "description": "Riparazione saldatura della pipeline principale con lavori a caldo",
  "work_type": "manutenzione",
  "location": "Area Produzione B",
  "duration_hours": 6,
  "workers_count": 2,
  "equipment": ["saldatrice", "bombole gas", "dispositivi taglio"],
  "orchestrator": "mock"
}
```
3. Aggiungi header: `X-Tenant-Domain: demo.hse-system.com`
4. Clicca "Execute" per analisi istantanea

## Headers Personalizzati in Swagger
Purtroppo Swagger UI standard non ha un campo facile per headers custom.
Opzioni:
1. Modifica il comando cURL generato aggiungendo `-H "X-Tenant-Domain: demo.hse-system.com"`
2. Usa un tool come Postman o Insomnia
3. Usa il terminale con cURL direttamente

## Credenziali Disponibili
- **superadmin** / **SuperAdmin123!** (accesso a tutti i tenant)
- **admin_demo_company** / **Admin123!** (solo Demo Company)
- **admin_enterprise_corp** / **Admin123!** (solo Enterprise Corp)