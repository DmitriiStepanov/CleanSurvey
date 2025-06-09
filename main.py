"""
main.py
Точка входа: связывает parser → classifier → grouping → doc_generator.
"""

import os
import sys
import argparse
import logging
from parser import parse_docx
from classifier import label_paragraphs
from grouping import group_paragraphs
from doc_generator import generate_clean_doc
from utils import validate_docx_path
from docx import Document

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

def process_survey(input_path, output_path, progress_callback=None):
    logging.info(f"Начинаем обработку файла: {input_path}")
    
    # Читаем документ
    doc = Document(input_path)
    paragraphs = [{"text": p.text, "index": i} for i, p in enumerate(doc.paragraphs) if p.text.strip()]
    logging.info(f"Получено {len(paragraphs)} непустых параграфов.")
    
    # Классифицируем параграфы
    labels = label_paragraphs(paragraphs, progress_callback)
    
    # Добавляем метки к параграфам
    labeled_paragraphs = [{"text": p["text"], "index": p["index"], "label": l} for p, l in zip(paragraphs, labels)]
    
    # Группируем параграфы
    survey_structure = group_paragraphs(labeled_paragraphs)
    
    # Генерируем чистый документ
    generate_clean_doc(survey_structure, output_path)
    logging.info(f"Чистый документ сохранён: {output_path}")

def main():
    setup_logging()
    parser = argparse.ArgumentParser(description="Clean Survey MVP")
    parser.add_argument("--input", "-i", required=True, help="Путь к dirty_survey.docx")
    parser.add_argument("--output", "-o", required=True, help="Путь для сохранения clean_survey_MVP.docx")
    args = parser.parse_args()

    try:
        validate_docx_path(args.input)
    except Exception as e:
        logging.error(f"Ошибка: {e}")
        sys.exit(1)

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        logging.error("Переменная окружения OPENAI_API_KEY не установлена.")
        sys.exit(1)

    process_survey(args.input, args.output)

if __name__ == "__main__":
    main() 