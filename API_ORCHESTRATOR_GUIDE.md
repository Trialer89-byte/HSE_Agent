# 🤖 AI Orchestrator API Guide

Guida all'utilizzo dei diversi orchestratori AI per l'analisi dei permessi di lavoro HSE.

## 📡 Endpoint di Analisi

```
POST /api/v1/permits/{permit_id}/analyze
```

## 🎛️ Parametri della Richiesta

```json
{
  "force_reanalysis": false,
  "include_draft_documents": false,
  "analysis_scope": ["content", "risk", "compliance", "dpi"],
  "orchestrator": "ai"
}
```

### 🔧 Parametro `orchestrator`

Scegli il tipo di analisi AI:

| Valore | Descrizione | Tempo | Costo | Qualità |
|--------|-------------|-------|-------|---------|
| `"ai"` | **Gemini Multi-Agent** - Analisi completa con 5 agenti specializzati | 30-60s | Alto | ⭐⭐⭐⭐⭐ |
| `"fast"` | **Gemini Veloce** - Analisi semplificata con 1 agente | 10-30s | Medio | ⭐⭐⭐⭐ |
| `"mock"` | **Simulazione** - Risultati istantanei per test | <1s | Gratis | ⭐⭐⭐ |

## 🤖 Orchestratori Disponibili

### 1. AI Orchestrator (`"ai"`)
**Analisi multi-agente completa con Gemini**

**Agenti coinvolti:**
- 🔍 **ContentAnalysisAgent** - Analisi qualità e completezza contenuto
- ⚠️ **RiskAnalysisAgent** - Identificazione e valutazione rischi
- ✅ **ComplianceCheckerAgent** - Verifica conformità normativa
- 🦺 **DPISpecialistAgent** - Raccomandazioni DPI specifiche
- 📚 **DocumentCitationAgent** - Generazione citazioni strutturate

**Caratteristiche:**
- Analisi parallela per prestazioni ottimali
- Ricerca dinamica documenti tramite vector service
- Timeout aggressivi (60s totale, 15s per agente)
- Citazioni strutturate con riferimenti precisi

**Quando usarlo:**
- Analisi di produzione per permessi critici
- Necessità di analisi dettagliata e conforme
- Quando servono citazioni normative precise

### 2. Fast AI Orchestrator (`"fast"`)
**Analisi AI veloce e semplificata**

**Caratteristiche:**
- Un solo agente (ContentAnalysisAgent)
- Timeout ridotti (30s totale, 10s per agente)
- Raccomandazioni DPI e rischi base per tipo lavoro
- Fallback automatico in caso di timeout

**Quando usarlo:**
- Analisi rapide per permessi standard
- Quando serve un buon compromesso tempo/qualità
- Per evitare blocking dell'interfaccia utente

### 3. Mock Orchestrator (`"mock"`)
**Simulazione per test e sviluppo**

**Caratteristiche:**
- Risultati istantanei (0.001s)
- Dati realistici basati sul tipo di lavoro
- Nessuna chiamata AI (gratis)
- Perfect per sviluppo e demo

**Quando usarlo:**
- Test e sviluppo dell'applicazione
- Demo senza costi AI
- Verifica struttura dati e API

## 📝 Esempi di Utilizzo

### Analisi Completa con Gemini
```bash
curl -X POST "http://localhost:8000/api/v1/permits/1/analyze" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "orchestrator": "ai",
    "force_reanalysis": false,
    "analysis_scope": ["content", "risk", "compliance", "dpi"]
  }'
```

### Analisi Veloce
```bash
curl -X POST "http://localhost:8000/api/v1/permits/1/analyze" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "orchestrator": "fast"
  }'
```

### Test con Mock
```bash
curl -X POST "http://localhost:8000/api/v1/permits/1/analyze" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "orchestrator": "mock"
  }'
```

## 🔧 Configurazione Gemini

### Variabili di Ambiente
```env
# .env file
AI_PROVIDER=gemini
GEMINI_API_KEY=your-gemini-api-key-here
GEMINI_MODEL=gemini-1.5-flash
```

### Test Configurazione
```bash
# Nel container Docker
docker exec hse-agent-backend-1 python test_gemini_config.py
```

## 📊 Struttura Risposta

Tutti gli orchestratori restituiscono la stessa struttura:

```json
{
  "analysis_id": "string",
  "permit_id": 1,
  "confidence_score": 0.85,
  "processing_time": 25.3,
  "executive_summary": {
    "overall_score": 0.8,
    "critical_issues": 2,
    "recommendations": 5,
    "compliance_level": "parziale",
    "estimated_completion_time": "2-4 ore",
    "key_findings": ["..."],
    "next_steps": ["..."]
  },
  "action_items": [
    {
      "id": "ACT_001",
      "type": "risk_mitigation",
      "priority": "alta",
      "title": "...",
      "description": "...",
      "suggested_action": "...",
      "consequences_if_ignored": "...",
      "references": ["D.Lgs 81/2008"],
      "estimated_effort": "1-2 ore",
      "responsible_role": "RSPP",
      "frontend_display": {
        "icon": "alert-triangle",
        "color": "red"
      }
    }
  ],
  "citations": {
    "normative": [
      {
        "document_info": {
          "title": "D.Lgs 81/2008",
          "type": "normativa",
          "code": "D.Lgs 81/2008"
        },
        "relevance": {
          "score": 0.9,
          "context": "Riferimento normativo applicabile"
        },
        "key_requirements": [],
        "frontend_display": {
          "icon": "book",
          "color": "blue"
        }
      }
    ],
    "procedures": [],
    "guidelines": []
  },
  "completion_roadmap": {
    "immediate": ["..."],
    "short_term": ["..."],
    "long_term": ["..."]
  },
  "performance_metrics": {
    "total_processing_time": 25.3,
    "agents_successful": 5,
    "agents_total": 5,
    "analysis_method": "AI Multi-Agent"
  }
}
```

## 🎯 Raccomandazioni d'Uso

### Per Produzione
- Usa `"ai"` per permessi critici (chimico, elettrico, spazi confinati)
- Usa `"fast"` per permessi standard (manutenzione, pulizia)
- Configura timeout adeguati nel load balancer (90s minimo)

### Per Sviluppo
- Usa `"mock"` per test rapidi e sviluppo UI
- Usa `"fast"` per test realistici senza costi eccessivi
- Testa sempre con `"ai"` prima del deployment

### Per Demo
- Usa `"mock"` per demo istantanee
- Dati realistici basati sul tipo di lavoro
- Zero costi e latenza

## 🔍 Troubleshooting

### Errori Comuni

**"Agent timeout"**
```
Soluzione: Aumenta timeout o usa "fast" orchestrator
```

**"Gemini API quota exceeded"**
```
Soluzione: Controlla quota API o usa "mock" temporaneamente
```

**"Citation validation error"**
```
Soluzione: Questa dovrebbe essere risolta con la fix recente
```

### Logs Utili
```bash
# Container logs
docker logs hse-agent-backend-1 -f

# Specific analysis logs
docker exec hse-agent-backend-1 grep "PermitRouter" /app/logs/app.log
```