import re


class TextCleaner:

    def clean(self, text: str) -> str:
        if not text:
            return ""
        # Remove null bytes
        text = text.replace("\x00", "")
        # Normalize unicode dashes and quotes
        text = text.replace("\u2019", "'").replace("\u2018", "'")
        text = text.replace("\u201c", '"').replace("\u201d", '"')
        text = text.replace("\u2013", "-").replace("\u2014", "-")
        # Remove excessive whitespace
        text = re.sub(r"\n{3,}", "\n\n", text)
        text = re.sub(r" {2,}", " ", text)
        # Remove page headers that are just numbers
        text = re.sub(r"^\d+\s*$", "", text, flags=re.MULTILINE)
        return text.strip()