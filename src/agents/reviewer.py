from __future__ import annotations

from src.agents.base import AgentContext, BaseAgent
from src.common.models import CodeArtifact, DeveloperResult, ReviewIssue, ReviewReport
from src.llm.provider import GenerationRequest


class ReviewAgent(BaseAgent):
    def __init__(self, context: AgentContext) -> None:
        super().__init__(name="reviewer", context=context)

    def review(self, result: DeveloperResult) -> ReviewReport:
        system_prompt = "You are a strict code reviewer. Flag correctness and quality issues."
        user_prompt = (
            f"Task id: {result.task_id}\n"
            f"Developer: {result.agent_name}\n"
            f"Artifacts: {len(result.artifacts)}"
        )
        _ = self.context.provider.generate(
            GenerationRequest(system_prompt=system_prompt, user_prompt=user_prompt)
        )

        issues: list[ReviewIssue] = []
        revised_artifacts: list[CodeArtifact] = []

        for artifact in result.artifacts:
            if "TODO" in artifact.code:
                issues.append(
                    ReviewIssue(
                        severity="warning",
                        message="Artifact contains TODO placeholders.",
                        suggestion="Complete TODO blocks before merge.",
                    )
                )

            if "def execute():" in artifact.code and "pass" in artifact.code:
                issues.append(
                    ReviewIssue(
                        severity="error",
                        message="Function execute is empty.",
                        suggestion="Add task-specific implementation.",
                    )
                )

            if not issues:
                revised_artifacts.append(artifact)
                continue

            patched = artifact.model_copy()
            patched.code = artifact.code.replace("pass", "return None")
            patched.notes.append("Reviewer applied minimal safe patch for empty pass branch.")
            revised_artifacts.append(patched)

        approved = all(issue.severity != "error" for issue in issues)

        return ReviewReport(
            task_id=result.task_id,
            approved=approved,
            issues=issues,
            revised_artifacts=revised_artifacts,
        )
