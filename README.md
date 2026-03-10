# Multi-Agent Coding Orchestrator

Questo progetto implementa un flusso con ruoli distinti:

- `Architect Agent`: analizza feature request, dipendenze, pattern e linee guida.
- `Developer Agent(s)`: implementano task piccoli seguendo direttive dell'architect.
- `Review Agent`: valida il codice generato, segnala issue e propone fix.
- `Orchestrator`: coordina il dialogo tra agenti e compone la risposta finale.

## Architettura ad alto livello

1. Un client (CLI, plugin IntelliJ, altro servizio) invia una `FeatureRequest`.
2. L'orchestrator invoca `ArchitectAgent.plan_feature`.
3. Il piano viene diviso in task e assegnato a `DeveloperAgent`.
4. Il codice proposto passa a `ReviewAgent`.
5. L'orchestrator integra feedback e restituisce `OrchestrationResult`.

## Struttura

```text
src/
  agents/
    architect.py
    developer.py
    reviewer.py
  common/
    models.py
  llm/
    provider.py
  orchestrator/
    service.py
    api.py
  main.py
intellij-plugin/
  ...
Dockerfile
docker-compose.yml
```

## Configurazione

1. Copia il file environment:

```powershell
Copy-Item .env.example .env
```

2. Opzionale: abilita modello reale in `.env`:

- `OPENAI_API_KEY=...`
- `OPENAI_BASE_URL=https://api.openai.com/v1`
- `MODEL_NAME=gpt-4.1-mini`

Se non imposti la key, il sistema usa fallback mock deterministico.

## Avvio con Docker Compose

```powershell
docker compose up --build -d
```

Verifica servizio:

```powershell
Invoke-RestMethod -Method Get -Uri http://localhost:8080/health
```

Stop:

```powershell
docker compose down
```

## Esempio step by step

1. Avvia stack:

```powershell
docker compose up --build -d
```

2. Invia feature request completa:

```powershell
Invoke-RestMethod -Method Post -Uri http://localhost:8080/api/v1/orchestrate `
  -ContentType "application/json" `
  -Body (@{
    feature_id = "feat-001"
    title = "Add user profile endpoint"
    description = "Expose authenticated profile endpoint with validation and tests"
    constraints = @("Use FastAPI", "Keep backward compatibility", "Include negative tests")
    target_stack = "python-fastapi"
    context_files = @("src/orchestrator/api.py")
  } | ConvertTo-Json)
```

3. Leggi output:

- `architecture`: piano architect (dipendenze, pattern, guideline, task)
- `developer_results`: artefatti prodotti dai developer agents
- `review_reports`: esito review con issue/suggerimenti
- `final_artifacts`: versione finale aggregata
- `merged_summary`: riepilogo orchestrazione

4. Salva risultato su file locale (opzionale):

```powershell
$response = Invoke-RestMethod -Method Post -Uri http://localhost:8080/api/v1/orchestrate `
  -ContentType "application/json" `
  -Body (Get-Content .\examples.feature-request.json -Raw)

$response | ConvertTo-Json -Depth 20 | Set-Content .\out.orchestration-result.json
```

5. Spegni stack:

```powershell
docker compose down
```

## Endpoint principali

- `POST /api/v1/orchestrate`: pipeline completa architect -> developer -> review.
- `POST /api/v1/architect/plan`: solo output architect.
- `POST /api/v1/developer/implement`: implementazione task singolo.
- `POST /api/v1/review/validate`: validazione review.

## Integrazione IntelliJ

La cartella `intellij-plugin` contiene un plugin minimale:

- action `Send Selection to MC Orchestrator`
- legge testo selezionato
- chiama `POST /api/v1/orchestrate`
- mostra risultato in dialog

Build plugin:

```powershell
cd intellij-plugin
.\gradlew.bat buildPlugin
```

Output ZIP in `intellij-plugin/build/distributions`.
