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
  build.gradle.kts
  settings.gradle.kts
  src/main/kotlin/com/mcagents/orchestrator/
    McOrchestratorAction.kt
    McOrchestratorClient.kt
  src/main/resources/META-INF/plugin.xml
```

## Avvio rapido

1. Crea virtualenv e installa dipendenze:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

2. Configura variabili:

```powershell
Copy-Item .env.example .env
```

3. Avvia API:

```powershell
uvicorn src.main:app --reload --port 8080
```

4. Test endpoint:

```powershell
Invoke-RestMethod -Method Post -Uri http://localhost:8080/api/v1/orchestrate `
  -ContentType "application/json" `
  -Body (@{
    feature_id = "feat-001"
    title = "Add user profile endpoint"
    description = "Expose profile read API with auth and validation"
    constraints = @("Use FastAPI", "Add tests")
    target_stack = "python-fastapi"
  } | ConvertTo-Json)
```

## Endpoint principali

- `POST /api/v1/orchestrate`: esegue pipeline completa architect -> developer -> review.
- `POST /api/v1/architect/plan`: solo output dell'architect.
- `POST /api/v1/developer/implement`: implementazione singolo task.
- `POST /api/v1/review/validate`: review su codice generato.

## Integrazione IntelliJ

La cartella `intellij-plugin` contiene un plugin minimale:

- aggiunge action `Send Selection to MC Orchestrator`
- legge il testo selezionato
- chiama `POST /api/v1/orchestrate`
- mostra il risultato in dialog

### Build plugin

```powershell
cd intellij-plugin
.\gradlew.bat buildPlugin
```

Output ZIP in `intellij-plugin/build/distributions`.

## Note operative

- `src/llm/provider.py` usa un endpoint OpenAI-compatible; se mancano key/url lavora in modalita mock deterministica.
- Gli agenti usano contratti Pydantic condivisi in `src/common/models.py`.
- Il coordinamento e la riconciliazione dei feedback sono centralizzati in `src/orchestrator/service.py`.
