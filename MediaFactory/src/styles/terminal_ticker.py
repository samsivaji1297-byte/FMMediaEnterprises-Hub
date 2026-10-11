from .base_style import BaseEditingStyle

class TerminalTickerStyle(BaseEditingStyle):
    """Cyberpunk/Terminal code ticker style for raw operator authority."""
    
    def process_text_chunks(self, full_text: str, max_words_per_chunk: int = 15) -> list[str]:
        words = full_text.split()
        chunks = []
        for i in range(0, len(words), max_words_per_chunk):
            chunks.append("> " + " ".join(words[i:i + max_words_per_chunk]))
        return chunks if chunks else ["> " + full_text]

    def render_overlay(self, clip, text_chunk: str):
        # Code-style text rendering with monospace font and cyan/green highlights
        pass
