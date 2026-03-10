package com.mcagents.orchestrator

import com.google.gson.Gson
import com.google.gson.JsonObject
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.OkHttpClient
import okhttp3.Request
import okhttp3.RequestBody.Companion.toRequestBody

class McOrchestratorClient(
    private val baseUrl: String = System.getenv("MC_ORCHESTRATOR_URL") ?: "http://localhost:8080"
) {
    private val http = OkHttpClient()
    private val gson = Gson()

    fun orchestrate(title: String, description: String): String {
        val payload = mapOf(
            "feature_id" to "idea-${System.currentTimeMillis()}",
            "title" to title,
            "description" to description,
            "constraints" to listOf("Keep implementation modular", "Return testable code"),
            "target_stack" to "intellij-plugin-request"
        )

        val body = gson.toJson(payload)
            .toRequestBody("application/json".toMediaType())

        val request = Request.Builder()
            .url("$baseUrl/api/v1/orchestrate")
            .post(body)
            .build()

        http.newCall(request).execute().use { response ->
            if (!response.isSuccessful) {
                return "Request failed: HTTP ${response.code}"
            }

            val responseBody = response.body?.string().orEmpty()
            val json = gson.fromJson(responseBody, JsonObject::class.java)
            return json.get("merged_summary")?.asString ?: responseBody
        }
    }
}
