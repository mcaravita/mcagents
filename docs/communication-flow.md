# Communication Flow and Interfaces

## Roles

- Architect agent input: feature description + constraints + target stack.
- Architect agent output: architecture plan with dependencies, patterns, guidelines, tasks.
- Developer agent input: one task + architecture plan + feature context.
- Developer agent output: code artifacts + rationale.
- Review agent input: developer result.
- Review agent output: approval flag + issues + revised artifacts.

## Message contracts

### 1) FeatureRequest

```json
{
  "feature_id": "feat-001",
  "title": "Add user profile endpoint",
  "description": "Expose authenticated profile endpoint",
  "constraints": ["Use FastAPI", "Add tests"],
  "target_stack": "python-fastapi",
  "context_files": ["src/api/users.py"]
}
```

### 2) ArchitecturePlan

```json
{
  "feature_id": "feat-001",
  "summary": "Layered architecture ...",
  "dependencies": ["validation library"],
  "patterns": ["Hexagonal Architecture"],
  "guidelines": ["Keep business logic outside controllers"],
  "tasks": [
    {
      "task_id": "feat-001-task-1",
      "title": "Define domain models",
      "description": "...",
      "acceptance_criteria": ["..."],
      "priority": "high",
      "owner_agent": "developer-1"
    }
  ]
}
```

### 3) DeveloperResult

```json
{
  "task_id": "feat-001-task-1",
  "agent_name": "developer-1",
  "rationale": "Implemented task ...",
  "artifacts": [
    {
      "task_id": "feat-001-task-1",
      "language": "python",
      "file_path": "generated/domain_models.py",
      "code": "def execute(): ...",
      "notes": ["..."]
    }
  ]
}
```

### 4) ReviewReport

```json
{
  "task_id": "feat-001-task-1",
  "approved": true,
  "issues": [
    {
      "severity": "warning",
      "message": "Artifact contains TODO placeholders.",
      "suggestion": "Complete TODO blocks before merge."
    }
  ],
  "revised_artifacts": []
}
```

## Orchestration sequence

1. `POST /api/v1/orchestrate` with `FeatureRequest`.
2. Orchestrator calls architect and receives `ArchitecturePlan`.
3. For each task, orchestrator routes to assigned developer agent.
4. Each `DeveloperResult` is validated by review agent.
5. Failed review loops through feedback integration.
6. Final merged artifacts and summary are returned.
