from abc import ABC, abstractmethod

class BaseEditingStyle(ABC):
    @abstractmethod
    def process_text_chunks(self, full_text: str, max_words_per_chunk: int = 12) -> list[str]:
        """Splits raw text into fast-paced micro-caption chunks."""
        pass

    @abstractmethod
    def render_overlay(self, clip, text_chunk: str):
        """Applies style-specific visual overlays, fonts, and colors to a video clip segment."""
        pass
