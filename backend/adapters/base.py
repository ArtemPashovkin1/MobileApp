from dataclasses import dataclass


@dataclass
class AnalysisResult:
    meaning: str
    translation: str
    nuance: str
    tone: str


class LLMAdapter:
    name: str = "base"

    def analyze(self, selected_text: str, context: str, book_title: str, language: str) -> AnalysisResult:
        raise NotImplementedError