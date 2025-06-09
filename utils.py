"""
utils.py
Вспомогательные функции для проекта.
"""

import os
from docx.shared import RGBColor

def validate_docx_path(path: str):
    """
    Проверяет существование файла и расширение .docx.
    """
    if not os.path.isfile(path):
        raise FileNotFoundError(f"Файл '{path}' не найден.")
    if not path.lower().endswith(".docx"):
        raise ValueError(f"Файл '{path}' не является .docx.")

def extract_code_and_text(line: str):
    """
    Разделяет строку вида "1 Мужской" → ("1", "Мужской").
    Если нет пробела, возвращает (line, "").
    """
    parts = line.strip().split(" ", 1)
    if len(parts) == 2:
        return parts[0], parts[1]
    return parts[0], ""

def set_run_color(run, rgb_tuple):
    """
    Устанавливает цвет текста для Run из python-docx.
    rgb_tuple: (R, G, B) с 0–255.
    """
    run.font.color.rgb = RGBColor(*rgb_tuple) 