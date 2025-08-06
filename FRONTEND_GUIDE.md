# Frontend Multi-Tenant HSE System

## 🎯 Panoramica

Il frontend è stato sviluppato con **Next.js 14** e supporta completamente il sistema multi-tenant del backend. Include:

- **Routing multi-tenant** con auto-detection
- **Autenticazione** integrata con il backend
- **Branding personalizzato** per ogni tenant
- **State management** con Zustand
- **UI responsiva** con Tailwind CSS
- **Docker support** per deployment

## 🏗️ Architettura

### Stack Tecnologico
- **Next.js 14** - App Router, Server Components
- **TypeScript** - Type safety completa
- **Tailwind CSS** - Styling utilitario
- **Zustand** - State management leggero
- **React Query** - Data fetching e caching
- **Axios** - HTTP client con interceptors

### Struttura Progetto
```
frontend/
├── src/
│   ├── app/                    # App Router (Next.js 14)
│   │   ├── auth/login/        # Pagina login
│   │   ├── dashboard/         # Dashboard principale
│   │   ├── tenant-select/     # Selezione tenant
│   │   └── layout.tsx         # Layout principale
│   ├── components/
│   │   ├── auth/              # Componenti autenticazione
│   │   ├── tenant/            # Componenti tenant
│   │   └── ui/                # Componenti UI riusabili
│   ├── stores/                # Zustand stores
│   ├── types/                 # TypeScript definitions
│   ├── lib/                   # Utilities e helper
│   └── config/                # Configurazioni
├── Dockerfile                 # Container configuration
└── docker-compose.frontend.yml
```

## 🔧 Configurazione e Avvio

### Requisiti
- **Node.js 20+**
- **Docker & Docker Compose**
- **Backend HSE** in esecuzione

### 1. Installazione Dipendenze
```bash
cd frontend
npm install
```

### 2. Configurazione Environment
```bash
cp .env.example .env.local
```

Configura le variabili:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_TENANT_MODE=saas
NODE_ENV=development
```

### 3. Avvio Sviluppo
```bash
npm run dev
```

### 4. Avvio Stack Completo (Docker)
```bash
# Dalla root del progetto
./start-fullstack.bat
```

## 🌐 Sistema Multi-Tenant

### Detection del Tenant
Il sistema supporta multiple modalità di identificazione:

1. **Subdomain Detection**
   - `demo.hse-system.com` → tenant "demo"
   - `enterprise.your-domain.com` → tenant "enterprise"

2. **Domain Mapping**
   - `company.com` → mappato al tenant specifico

3. **Query Parameters**
   - `app.com?tenant=demo` → tenant "demo"

4. **Manual Selection**
   - Pagina `/tenant-select` per selezione manuale

### Middleware Tenant
```typescript
// src/middleware.ts
export async function middleware(request: NextRequest) {
  // Auto-detection del tenant da hostname
  const tenantInfo = extractTenantFromHostname(hostname);
  
  // Reindirizzamento se tenant non trovato
  if (!tenantInfo && !publicRoutes.includes(pathname)) {
    return NextResponse.redirect('/tenant-select');
  }
}
```

## 🔐 Sistema di Autenticazione

### Store di Autenticazione
```typescript
// Zustand store con persistenza
const useAuthStore = create<AuthStore>()(
  persist(
    (set, get) => ({
      user: null,
      token: null,
      isAuthenticated: false,
      
      login: async (credentials) => {
        const response = await apiClient.post('/api/v1/auth/login', credentials);
        // Salva token e user info
      },
      
      logout: () => {
        // Cleanup completo
      }
    }),
    { name: 'auth-storage' }
  )
);
```

### Protezione Route
```typescript
<ProtectedRoute requiredPermissions={['permits.create']}>
  <PermitCreatePage />
</ProtectedRoute>
```

## 🎨 Branding Personalizzato

### Implementazione
```typescript
// Componente TenantBranding
export function TenantBranding({ tenant }: { tenant: TenantInfo }) {
  const { custom_branding } = tenant;
  const primaryColor = custom_branding?.primary_color || '#1976d2';
  
  return (
    <div>
      {/* Logo personalizzato */}
      {logoUrl && <Image src={logoUrl} alt="Logo" />}
      
      {/* CSS Variables per tema */}
      <style jsx>{`
        :global(:root) {
          --tenant-primary-color: ${primaryColor};
        }
      `}</style>
    </div>
  );
}
```

### CSS Customization
```css
/* Utilizza variabili CSS per temi dinamici */
.btn-primary {
  background-color: var(--tenant-primary-color, #1976d2);
}

.brand-text {
  color: var(--tenant-secondary-color, #424242);
}
```

## 🔄 State Management

### Tenant Store
```typescript
const useTenantStore = create<TenantState>()(
  persist(
    (set, get) => ({
      tenant: null,
      isLoading: false,
      
      autoDetectTenant: async () => {
        const tenant = await TenantDetection.autoDetectTenant();
        set({ tenant });
      },
      
      loadTenantByDomain: async (domain) => {
        const tenant = await TenantDetection.getTenantByDomain(domain);
        set({ tenant });
      }
    }),
    { name: 'tenant-storage' }
  )
);
```

### Auth Store
- Gestisce autenticazione utente
- Persistenza automatica del token
- Auto-refresh token
- Gestione errori e logout

## 🐳 Docker e Deployment

### Dockerfile Multi-stage
```dockerfile
# Build ottimizzato con multi-stage
FROM node:20-alpine AS deps
# Install dependencies

FROM node:20-alpine AS builder
# Build application

FROM node:20-alpine AS runner
# Production runtime
```

### Docker Compose
```yaml
services:
  frontend:
    build: ./frontend
    environment:
      - NEXT_PUBLIC_API_URL=http://backend:8000
    ports:
      - "3000:3000"
    depends_on:
      - backend

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf
```

### Nginx Reverse Proxy
- **Frontend**: Tutte le route tranne `/api/*`
- **Backend API**: Route `/api/*`
- **Rate Limiting**: Protezione API e auth
- **CORS**: Headers configurati
- **Multi-tenant**: Supporto subdomain

## 🛠️ Sviluppo

### Struttura Componenti
```typescript
// Componente tipico
interface ComponentProps {
  tenant?: TenantInfo;
  user?: User;
}

export function Component({ tenant, user }: ComponentProps) {
  const { isAuthenticated } = useAuthStore();
  
  if (!isAuthenticated) {
    return <LoginPrompt />;
  }
  
  return (
    <TenantBranding tenant={tenant}>
      {/* Component content */}
    </TenantBranding>
  );
}
```

### API Client
```typescript
// Axios con interceptors automatici
const apiClient = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL
});

// Auto-add tenant headers
apiClient.interceptors.request.use((config) => {
  const tenantDomain = localStorage.getItem('tenant_domain');
  if (tenantDomain) {
    config.headers['X-Tenant-Domain'] = tenantDomain;
  }
  return config;
});
```

## 🚦 Flow di Autenticazione

### 1. Accesso Iniziale
```
User → Homepage → Tenant Detection → Tenant Select/Login
```

### 2. Login Flow
```
Login Page → API Auth → Store Token → Dashboard
```

### 3. Protected Routes
```
Route Access → Check Auth → Check Permissions → Allow/Deny
```

## ⚡ Performance

### Ottimizzazioni Implementate
- **Server Components** per rendering lato server
- **Image Optimization** con Next.js Image
- **Bundle Splitting** automatico
- **Caching** con React Query
- **Lazy Loading** dei componenti

### Monitoring
- Health check endpoint: `/health`
- Performance metrics con Next.js
- Error boundary per handling errori

## 🔧 Personalizzazione

### Aggiungere Nuove Pagine
1. Creare in `src/app/nuova-pagina/page.tsx`
2. Avvolgere con `<ProtectedRoute>` se necessario
3. Aggiungere al routing di Nginx se richiesto

### Aggiungere Nuovi Store
```typescript
interface NewStore {
  data: any[];
  loading: boolean;
  fetchData: () => Promise<void>;
}

export const useNewStore = create<NewStore>()((set) => ({
  data: [],
  loading: false,
  fetchData: async () => {
    set({ loading: true });
    // API call
    set({ data: result, loading: false });
  }
}));
```

## 🚀 Deployment in Produzione

### Environment Variables
```env
NEXT_PUBLIC_API_URL=https://api.your-domain.com
NEXT_PUBLIC_TENANT_MODE=saas
NODE_ENV=production
```

### SSL Configuration
1. Ottenere certificati SSL
2. Configurare Nginx per HTTPS
3. Aggiornare `docker-compose.yml`

### Multi-Instance Deployment
- Load balancer davanti a Nginx
- Database condiviso per SaaS
- Database dedicati per on-premise

## 🐛 Troubleshooting

### Problemi Comuni

1. **Tenant non rilevato**
   - Verificare hostname/domain
   - Controllare API backend
   - Verificare localStorage

2. **Errori di autenticazione**
   - Verificare token in localStorage
   - Controllare scadenza token
   - Verificare API backend

3. **Problemi di CORS**
   - Verificare configurazione Nginx
   - Controllare headers API
   - Verificare environment variables

### Debug Mode
```bash
# Abilitare debug logging
NODE_ENV=development npm run dev
```

### Testing
```bash
# Unit tests
npm run test

# E2E tests
npm run test:e2e

# Build test
npm run build
```

## 📱 Mobile Support

Il frontend è completamente responsive e supporta:
- **Mobile-first design**
- **Touch interactions**
- **Progressive Web App** (PWA) ready
- **Offline capabilities** con Service Workers

## 🔮 Roadmap Future

- [ ] PWA completa con offline support
- [ ] Dashboard analytics avanzata
- [ ] Drag & drop file upload
- [ ] Real-time notifications
- [ ] Dark mode per tenant
- [ ] Multi-language support
- [ ] Advanced caching strategies

## 📋 Comandi Utili

```bash
# Sviluppo
npm run dev                 # Start dev server
npm run build              # Build per produzione
npm run start              # Start produzione
npm run lint               # Linting

# Docker
docker-compose -f docker-compose.frontend.yml up --build
docker-compose -f docker-compose.frontend.yml down

# Testing
npm run test               # Unit tests
npm run test:watch         # Watch mode
```

Il frontend è ora completamente integrato con il sistema multi-tenant e pronto per la produzione! 🎉