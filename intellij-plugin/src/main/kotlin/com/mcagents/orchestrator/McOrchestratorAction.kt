package com.mcagents.orchestrator

import com.intellij.openapi.actionSystem.AnAction
import com.intellij.openapi.actionSystem.AnActionEvent
import com.intellij.openapi.actionSystem.CommonDataKeys
import com.intellij.openapi.ui.Messages

class McOrchestratorAction : AnAction("Send Selection to MC Orchestrator") {
    private val client = McOrchestratorClient()

    override fun actionPerformed(event: AnActionEvent) {
        val editor = event.getData(CommonDataKeys.EDITOR)
        if (editor == null) {
            Messages.showWarningDialog("Open an editor and select text first.", "MC Orchestrator")
            return
        }

        val selection = editor.selectionModel.selectedText
        if (selection.isNullOrBlank()) {
            Messages.showWarningDialog("Select a feature description before running the action.", "MC Orchestrator")
            return
        }

        val result = try {
            client.orchestrate("Feature from IntelliJ", selection)
        } catch (ex: Exception) {
            "Error calling orchestrator: ${ex.message}"
        }

        Messages.showInfoMessage(result, "MC Orchestrator Result")
    }
}
