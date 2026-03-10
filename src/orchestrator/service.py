from __future__ import annotations

import os
from collections import defaultdict

from src.agents.architect import ArchitectAgent
from src.agents.base import AgentContext
from src.agents.developer import DeveloperAgent
from src.agents.reviewer import ReviewAgent
from src.common.models import (
    CodeArtifact,
    DeveloperResult,
    DevelopmentTask,
    FeatureRequest,
    OrchestrationResult,
    ReviewReport,
)
from src.llm.provider import build_provider


class AgentOrchestrator:
    def __init__(self) -> None:
        provider = build_provider()
        context = AgentContext(provider=provider)
        self.architect = ArchitectAgent(context=context)
        self.review_agent = ReviewAgent(context=context)
        self.developer_agents = {
            "developer-1": DeveloperAgent(name="developer-1", context=context),
            "developer-2": DeveloperAgent(name="developer-2", context=context),
        }
        self.max_review_rounds = int(os.getenv("ORCHESTRATOR_MAX_REVIEW_ROUNDS", "2"))

    def plan(self, feature: FeatureRequest):
        return self.architect.plan_feature(feature)

    def implement_task(self, feature: FeatureRequest, task: DevelopmentTask):
        plan = self.architect.plan_feature(feature)
        agent = self.developer_agents.get(task.owner_agent, self.developer_agents["developer-1"])
        return agent.implement_task(feature=feature, plan=plan, task=task)

    def review_result(self, developer_result: DeveloperResult):
        return self.review_agent.review(developer_result)

    def run(self, feature: FeatureRequest) -> OrchestrationResult:
        plan = self.architect.plan_feature(feature)
        developer_results: list[DeveloperResult] = []
        review_reports: list[ReviewReport] = []

        for task in plan.tasks:
            agent = self.developer_agents.get(task.owner_agent, self.developer_agents["developer-1"])
            dev_result = agent.implement_task(feature=feature, plan=plan, task=task)

            report = self.review_agent.review(dev_result)
            rounds = 1
            while not report.approved and rounds < self.max_review_rounds:
                dev_result = self._apply_review_feedback(dev_result, report)
                report = self.review_agent.review(dev_result)
                rounds += 1

            developer_results.append(dev_result)
            review_reports.append(report)

        final_artifacts = self._collect_final_artifacts(developer_results, review_reports)
        merged_summary = self._build_summary(feature.feature_id, plan.tasks, review_reports)

        return OrchestrationResult(
            feature_id=feature.feature_id,
            architecture=plan,
            developer_results=developer_results,
            review_reports=review_reports,
            final_artifacts=final_artifacts,
            merged_summary=merged_summary,
        )

    @staticmethod
    def _apply_review_feedback(
        developer_result: DeveloperResult,
        report: ReviewReport,
    ) -> DeveloperResult:
        patched = developer_result.model_copy(deep=True)
        suggestions = [issue.suggestion for issue in report.issues if issue.suggestion]

        for artifact in patched.artifacts:
            artifact.notes.extend(suggestions)
            if "pass" in artifact.code:
                artifact.code = artifact.code.replace("pass", "return None")

        patched.rationale += " | Updated after reviewer feedback."
        return patched

    @staticmethod
    def _collect_final_artifacts(
        developer_results: list[DeveloperResult],
        review_reports: list[ReviewReport],
    ) -> list[CodeArtifact]:
        report_map = {report.task_id: report for report in review_reports}
        grouped: dict[str, list[CodeArtifact]] = defaultdict(list)

        for result in developer_results:
            report = report_map.get(result.task_id)
            if report and report.revised_artifacts:
                grouped[result.task_id].extend(report.revised_artifacts)
            else:
                grouped[result.task_id].extend(result.artifacts)

        merged: list[CodeArtifact] = []
        for task_id in sorted(grouped.keys()):
            merged.extend(grouped[task_id])
        return merged

    @staticmethod
    def _build_summary(
        feature_id: str,
        tasks: list[DevelopmentTask],
        reports: list[ReviewReport],
    ) -> str:
        total = len(tasks)
        approved = sum(1 for report in reports if report.approved)
        return (
            f"Feature {feature_id}: completed {total} tasks, "
            f"review approved {approved}/{total}."
        )
