from __future__ import annotations

from src.agents.base import AgentContext, BaseAgent
from src.common.models import (
    ArchitecturePlan,
    DevelopmentTask,
    FeatureRequest,
    Priority,
)
from src.llm.provider import GenerationRequest


class ArchitectAgent(BaseAgent):
    def __init__(self, context: AgentContext) -> None:
        super().__init__(name="architect", context=context)

    def plan_feature(self, feature: FeatureRequest) -> ArchitecturePlan:
        system_prompt = (
            "You are a software architect. Produce architecture, dependencies, patterns, "
            "guidelines and implementation tasks."
        )
        user_prompt = (
            f"Feature title: {feature.title}\n"
            f"Description: {feature.description}\n"
            f"Target stack: {feature.target_stack}\n"
            f"Constraints: {', '.join(feature.constraints) if feature.constraints else 'none'}"
        )
        _ = self.context.provider.generate(
            GenerationRequest(system_prompt=system_prompt, user_prompt=user_prompt)
        )

        global_prompt = (
            "Implement this feature with strict separation of concerns, explicit typing, "
            "and testable components. Respect architectural guidelines and keep side effects isolated."
        )

        tasks = [
            DevelopmentTask(
                task_id=f"{feature.feature_id}-task-1",
                title="Define domain models",
                description="Create or update domain entities and DTO contracts for the feature.",
                acceptance_criteria=[
                    "Input/output models are explicit and validated",
                    "Backward compatibility is preserved",
                ],
                developer_prompt_seed=(
                    "Define schema and domain contracts first. Document assumptions and default values."
                ),
                priority=Priority.HIGH,
                owner_agent="developer-1",
            ),
            DevelopmentTask(
                task_id=f"{feature.feature_id}-task-2",
                title="Implement application logic",
                description="Implement use-case logic, service layer and integrations.",
                acceptance_criteria=[
                    "Business rules from description are enforced",
                    "Error paths are handled",
                ],
                developer_prompt_seed=(
                    "Focus on use-case orchestration. Keep infrastructure details behind interfaces."
                ),
                priority=Priority.HIGH,
                owner_agent="developer-2",
            ),
            DevelopmentTask(
                task_id=f"{feature.feature_id}-task-3",
                title="Expose API and tests",
                description="Add API endpoint wiring and automated tests.",
                acceptance_criteria=[
                    "Endpoint contract matches models",
                    "Unit or integration tests cover key flows",
                ],
                developer_prompt_seed=(
                    "Create API handlers and tests aligned with contracts, including negative cases."
                ),
                priority=Priority.MEDIUM,
                owner_agent="developer-1",
            ),
        ]

        return ArchitecturePlan(
            feature_id=feature.feature_id,
            summary=(
                f"Architecture for {feature.title}: layered design with explicit contracts "
                "between API, application service and domain."
            ),
            dependencies=["validation library", "test framework", "logging"],
            patterns=["Hexagonal Architecture", "Repository Pattern", "DTO Mapping"],
            guidelines=[
                "Keep business logic outside controllers",
                "Define strict input and output schemas",
                "Write tests for success and failure paths",
                "Avoid leaking infrastructure details to domain layer",
            ],
            global_prompt=global_prompt,
            tasks=tasks,
        )
