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
  "title": "Manutenzione Serbatoio",
  "description": "Pulizia interna",
  "work_type": "maintenance",
  "location": "Area A",
  "duration_hours": 4,
  "priority_level": "high"
}
```
4. **IMPORTANTE**: Prima di Execute, aggiungi negli headers:
   - `X-Tenant-Domain: demo.hse-system.com`
5. Clicca "Execute"

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