"""
parser.py
Извлечение всех непустых параграфов из Word-документа.
"""

from docx import Document

def parse_docx(input_path: str):
    """
    Открывает .docx и возвращает список словарей:
    [{"index": 1, "text": "параграф"}, ...]
    """
    doc = Document(input_path)
    paragraphs = []
    idx = 1
    for para in doc.paragraphs:
        text = para.text.strip()
        if text:
            paragraphs.append({"index": idx, "text": text})
            idx += 1
    return paragraphs 