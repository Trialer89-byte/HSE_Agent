-- Script SQL per cancellare i dati vecchi di analisi AI
-- Questo forzerà la rigenerazione delle analisi con il formato corretto delle Citation

-- 1. Mostra quanti record hanno analisi AI
SELECT 
    COUNT(*) as total_permits,
    COUNT(ai_analysis) as permits_with_analysis,
    COUNT(analyzed_at) as permits_analyzed
FROM work_permits;

-- 2. Mostra i dettagli dei permessi con analisi
SELECT 
    id, 
    title, 
    status, 
    analyzed_at,
    CASE 
        WHEN ai_analysis IS NOT NULL THEN 'Has Analysis'
        ELSE 'No Analysis'
    END as analysis_status
FROM work_permits 
WHERE ai_analysis IS NOT NULL
ORDER BY analyzed_at DESC;

-- 3. BACKUP: Crea una tabella di backup dei dati attuali (opzionale ma raccomandato)
CREATE TABLE work_permits_analysis_backup AS
SELECT 
    id,
    title,
    ai_analysis,
    ai_confidence,
    ai_version,
    analyzed_at,
    content_analysis,
    risk_assessment,
    compliance_check,
    dpi_recommendations,
    action_items
FROM work_permits 
WHERE ai_analysis IS NOT NULL;

-- 4. PULIZIA: Cancella tutti i dati di analisi AI vecchi
UPDATE work_permits 
SET 
    ai_analysis = NULL,
    ai_confidence = 0.0,
    ai_version = NULL,
    analyzed_at = NULL,
    content_analysis = NULL,
    risk_assessment = NULL,
    compliance_check = NULL,
    dpi_recommendations = NULL,
    action_items = NULL
WHERE ai_analysis IS NOT NULL;

-- 5. Verifica che la pulizia sia completata
SELECT 
    COUNT(*) as total_permits,
    COUNT(ai_analysis) as permits_with_analysis,
    COUNT(analyzed_at) as permits_analyzed
FROM work_permits;

-- 6. Verifica la tabella di backup
SELECT COUNT(*) as backed_up_records FROM work_permits_analysis_backup;

COMMIT;