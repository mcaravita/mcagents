from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Literal

from pydantic import BaseModel, Field


class Priority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class FeatureRequest(BaseModel):
    feature_id: str = Field(..., description="Unique id for the requested feature")
    title: str
    description: str
    constraints: list[str] = Field(default_factory=list)
    target_stack: str = Field(default="generic")
    context_files: list[str] = Field(default_factory=list)


class DevelopmentTask(BaseModel):
    task_id: str
    title: str
    description: str
    acceptance_criteria: list[str] = Field(default_factory=list)
    developer_prompt_seed: str = Field(default="")
    priority: Priority = Priority.MEDIUM
    owner_agent: str = Field(default="developer-1")


class ArchitecturePlan(BaseModel):
    feature_id: str
    summary: str
    dependencies: list[str] = Field(default_factory=list)
    patterns: list[str] = Field(default_factory=list)
    guidelines: list[str] = Field(default_factory=list)
    global_prompt: str = Field(default="")
    tasks: list[DevelopmentTask] = Field(default_factory=list)


class CodeArtifact(BaseModel):
    task_id: str
    language: str
    file_path: str
    code: str
    notes: list[str] = Field(default_factory=list)


class DeveloperResult(BaseModel):
    task_id: str
    agent_name: str
    rationale: str
    artifacts: list[CodeArtifact] = Field(default_factory=list)


class ReviewIssue(BaseModel):
    severity: Literal["info", "warning", "error"]
    message: str
    suggestion: str | None = None


class ReviewReport(BaseModel):
    task_id: str
    approved: bool
    issues: list[ReviewIssue] = Field(default_factory=list)
    revised_artifacts: list[CodeArtifact] = Field(default_factory=list)


class OrchestrationResult(BaseModel):
    feature_id: str
    architecture: ArchitecturePlan
    developer_results: list[DeveloperResult]
    review_reports: list[ReviewReport]
    final_artifacts: list[CodeArtifact]
    merged_summary: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
