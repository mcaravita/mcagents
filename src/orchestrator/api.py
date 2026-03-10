from __future__ import annotations

from fastapi import APIRouter, FastAPI
from pydantic import BaseModel

from src.common.models import (
    ArchitecturePlan,
    DeveloperResult,
    DevelopmentTask,
    FeatureRequest,
    OrchestrationResult,
    ReviewReport,
)
from src.orchestrator.service import AgentOrchestrator

app = FastAPI(title="Multi-Agent Coding Orchestrator", version="0.1.0")
router = APIRouter(prefix="/api/v1", tags=["orchestrator"])
orchestrator = AgentOrchestrator()


class DeveloperTaskInput(BaseModel):
    feature: FeatureRequest
    task: DevelopmentTask


@router.post("/orchestrate", response_model=OrchestrationResult)
def orchestrate(feature: FeatureRequest) -> OrchestrationResult:
    return orchestrator.run(feature)


@router.post("/architect/plan", response_model=ArchitecturePlan)
def architect_plan(feature: FeatureRequest) -> ArchitecturePlan:
    return orchestrator.plan(feature)


@router.post("/developer/implement", response_model=DeveloperResult)
def developer_implement(payload: DeveloperTaskInput) -> DeveloperResult:
    return orchestrator.implement_task(feature=payload.feature, task=payload.task)


@router.post("/review/validate", response_model=ReviewReport)
def review_validate(result: DeveloperResult) -> ReviewReport:
    return orchestrator.review_result(result)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


app.include_router(router)
