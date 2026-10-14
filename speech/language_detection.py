"""Language detection utilities.
A small heuristic detector for Devanagari (Hindi/Nepali), Assamese/Bengali,
and English (Latin script). This is not a replacement for a robust
language-detection library but serves for offline mock-mode and tests.
"""
from typing import Optional

# sample Unicode script ranges
DEVANAGARI_RANGE = (0x0900, 0x097F)
BENGALI_RANGE = (0x0980, 0x09FF)


def detect_language(text: str) -> Optional[str]:
    if not text:
        return None
    for ch in text:
        code = ord(ch)
        if DEVANAGARI_RANGE[0] <= code <= DEVANAGARI_RANGE[1]:
            # Devanagari used by Hindi and Nepali; we default to Hindi if
            # keywords match Nepali indicators this could be refined.
            return "hi"
        if BENGALI_RANGE[0] <= code <= BENGALI_RANGE[1]:
            # Assamese uses the Assamese script which overlaps Bengali range.
            return "as"
    # fallback to English
    return "en"
