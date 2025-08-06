@echo off
cd /d "C:\Users\federicoreginato\Documents\GitHub\hse-agent"

:MENU
cls
echo ========================================
echo    VISUALIZZATORE DOCUMENTI HSE
echo ========================================
echo.
echo 1. Visualizza documento in PostgreSQL
echo 2. Visualizza documento in Weaviate
echo 3. Query diretta PostgreSQL
echo 4. Test connessione database
echo 5. Informazioni su Weaviate
echo 6. Esci
echo.
set /p choice=Scegli un'opzione (1-6): 

if "%choice%"=="1" goto POSTGRES
if "%choice%"=="2" goto WEAVIATE  
if "%choice%"=="3" goto QUERY
if "%choice%"=="4" goto TEST
if "%choice%"=="5" goto BROWSER
if "%choice%"=="6" goto EXIT

echo Scelta non valida!
pause
goto MENU

:POSTGRES
echo.
echo === VISUALIZZAZIONE POSTGRESQL ===
py view_document_postgres.py
echo.
pause
goto MENU

:WEAVIATE
echo.
echo === VISUALIZZAZIONE WEAVIATE ===
py view_weaviate_simple.py
echo.
pause
goto MENU

:QUERY
echo.
echo === QUERY DIRETTA POSTGRESQL ===
docker exec hse-agent-db-1 psql -U hse_user -d hse_db -c "SELECT id, title, document_code, LENGTH(content_summary) as summary_len FROM documents;"
echo.
echo Per sessione interattiva PostgreSQL:
echo docker exec -it hse-agent-db-1 psql -U hse_user -d hse_db
echo.
pause
goto MENU

:TEST
echo.
echo === TEST CONNESSIONI ===
echo.
echo Test PostgreSQL:
docker exec hse-agent-db-1 psql -U hse_user -d hse_db -c "SELECT COUNT(*) as total_documents FROM documents;"
echo.
echo Test Weaviate:
curl -s http://localhost:8080/v1/meta | findstr "hostname"
if errorlevel 1 (
    echo ERRORE: Weaviate non raggiungibile
) else (
    echo OK: Weaviate raggiungibile
)
echo.
pause
goto MENU

:BROWSER
echo.
echo === INFORMAZIONI WEAVIATE ===
echo.
echo Weaviate è attivo su: http://localhost:8080
echo.
echo API endpoints disponibili:
echo - Meta info: http://localhost:8080/v1/meta
echo - Schema: http://localhost:8080/v1/schema
echo - GraphQL: http://localhost:8080/v1/graphql
echo.
echo Per testare GraphQL con curl:
echo curl -X POST http://localhost:8080/v1/graphql -H "Content-Type: application/json" -d "{\"query\": \"{ Aggregate { HSEDocument { meta { count } } } }\"}"
echo.
pause
goto MENU

:EXIT
echo Arrivederci!
exit