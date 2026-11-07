package com.example.mobilereader.data.analysis

import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import kotlinx.serialization.Serializable
import kotlinx.serialization.encodeToString
import kotlinx.serialization.json.Json
import java.net.HttpURLConnection
import java.net.URL

// то, что отправляем на сервер
@Serializable
data class AnalyzeRequest(
    val selected_text: String,
    val context: String,
    val book_title: String = "",
    val language: String = "",
)

// то, что получаем обратно
@Serializable
data class AnalyzeResult(
    val meaning: String = "",
    val translation: String = "",
    val nuance: String = "",
    val tone: String = "",
)

object AnalysisClient {
    // адрес сервера на компьютере (10.0.2.2 это localhost для эмулятора)
    private const val BASE_URL = "http://192.168.1.108:8000"
    private val json = Json { ignoreUnknownKeys = true }

    suspend fun analyze(request: AnalyzeRequest): AnalyzeResult = withContext(Dispatchers.IO) {
        val payload = Json.encodeToString(request)
        post("/api/analyze", payload) { body ->
            json.decodeFromString<AnalyzeResult>(body)
        }
    }

    // обычный пост-запрос без лишних библиотек
    private fun <T> post(path: String, payload: String, parse: (String) -> T): T {
        val connection = URL(BASE_URL + path).openConnection() as HttpURLConnection
        try {
            connection.requestMethod = "POST"
            connection.connectTimeout = 10_000
            connection.readTimeout = 180_000
            connection.doOutput = true
            connection.setRequestProperty("Content-Type", "application/json")
            connection.outputStream.use { it.write(payload.toByteArray()) }
            val code = connection.responseCode
            if (code != 200) throw Exception("сервер ответил ошибкой $code")
            return parse(connection.inputStream.bufferedReader().readText())
        } finally {
            connection.disconnect()
        }
    }
}

// вырезает абзац с выделением из текста страницы
fun extractParagraph(pageText: String, selectedText: String): String {
    val index = pageText.indexOf(selectedText)
    if (index < 0) return selectedText
    val start = pageText.lastIndexOf("\n\n", index).let { if (it < 0) 0 else it + 2 }
    val end = pageText.indexOf("\n\n", index + selectedText.length)
        .let { if (it < 0) pageText.length else it }
    return pageText.substring(start, end).trim()
}