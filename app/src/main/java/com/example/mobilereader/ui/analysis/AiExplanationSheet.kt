package com.example.mobilereader.ui.analysis

import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.ModalBottomSheet
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import com.example.mobilereader.data.analysis.AnalysisClient
import com.example.mobilereader.data.analysis.AnalyzeRequest
import com.example.mobilereader.data.analysis.AnalyzeResult

private sealed interface SheetState {
    data object Loading : SheetState
    data class Done(val result: AnalyzeResult) : SheetState
    data class Fail(val message: String) : SheetState
}

// всплывающая панель с разбором выделенного текста
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun AiExplanationSheet(request: AnalyzeRequest?, onDismiss: () -> Unit) {
    if (request == null) return
    var state by remember(request) { mutableStateOf<SheetState>(SheetState.Loading) }

    LaunchedEffect(request) {
        state = SheetState.Loading
        state = try {
            SheetState.Done(AnalysisClient.analyze(request))
        } catch (e: Exception) {
            SheetState.Fail(e.message ?: "неизвестная ошибка")
        }
    }

    ModalBottomSheet(onDismissRequest = onDismiss) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .verticalScroll(rememberScrollState())
                .padding(20.dp),
            verticalArrangement = Arrangement.spacedBy(12.dp),
        ) {
            Text("Разбор ИИ", style = MaterialTheme.typography.titleLarge)
            Text("«${request.selected_text}»", style = MaterialTheme.typography.bodyMedium)

            when (val current = state) {
                is SheetState.Loading -> CircularProgressIndicator()
                is SheetState.Fail -> Text(current.message, color = MaterialTheme.colorScheme.error)
                is SheetState.Done -> {
                    val r = current.result
                    if (r.translation.isNotBlank()) Block("Перевод", r.translation)
                    if (r.meaning.isNotBlank()) Block("Скрытый смысл", r.meaning)
                    if (r.nuance.isNotBlank()) Block("Нюанс / этимология", r.nuance)
                    if (r.tone.isNotBlank()) Block("Окрас", r.tone)
                }
            }
        }
    }
}

@Composable
private fun Block(title: String, text: String) {
    Column {
        Text(title, style = MaterialTheme.typography.labelLarge)
        Text(text, style = MaterialTheme.typography.bodyMedium)
    }
}