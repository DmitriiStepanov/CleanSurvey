"""
classifier.py
Классификация каждого абзаца в одну из меток через OpenAI GPT.
"""

from openai import OpenAI
import os
import time
import logging
from tenacity import retry, stop_after_attempt, wait_exponential

LABELS = [
    "GENERAL_INSTRUCTION",
    "BLOCK_HEADER",
    "BLOCK_INSTRUCTION",
    "QUESTION",
    "QUESTION_INSTRUCTION",
    "ANSWER_OPTIONS_HEADER",
    "ANSWER_OPTION",
    "ROWS_HEADER",
    "ROW_ITEM",
    "OTHER"
]

def build_prompt(batch):
    prompt = (
        "You are a labeling assistant. Given each paragraph below (in Russian), "
        "return exactly one label from the list:\n"
        + ", ".join(LABELS)
        + ".\n\n"
        "For each paragraph, output the label ON A SEPARATE LINE without any additional commentary.\n\n"
        "Paragraphs:\n"
    )
    for item in batch:
        prompt += f'"""{item["text"]}"""\n'
    return prompt

def get_labels_with_retry(paragraphs, api_key, max_retries=3):
    client = OpenAI(
        api_key=api_key,
        http_client=None  # Отключаем использование прокси
    )
    
    @retry(stop=stop_after_attempt(max_retries), wait=wait_exponential(multiplier=1, min=4, max=10))
    def _get_labels():
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Вы - помощник для классификации текста анкеты. Классифицируйте каждый параграф как: GENERAL_INSTRUCTION (общие инструкции), BLOCK_HEADER (заголовок блока), BLOCK_INSTRUCTION (инструкция к блоку), QUESTION (вопрос), QUESTION_INSTRUCTION (инструкция к вопросу), ANSWER_OPTION (вариант ответа), ROW (строка матрицы), OTHER (другое)."},
                {"role": "user", "content": "\n".join(paragraphs)}
            ],
            temperature=0.3,
            max_tokens=1000
        )
        return response.choices[0].message.content.strip().split("\n")

    return _get_labels()

def label_paragraphs(paragraphs, progress_callback=None, batch_size=3):
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("Переменная окружения OPENAI_API_KEY не установлена.")

    labels = []
    total_batches = (len(paragraphs) + batch_size - 1) // batch_size

    for i in range(0, len(paragraphs), batch_size):
        batch = paragraphs[i:i + batch_size]
        batch_num = i // batch_size + 1
        logging.info(f"Обработка батча {batch_num} из {total_batches}")

        try:
            batch_texts = [p['text'] for p in batch]
            batch_labels = get_labels_with_retry(batch_texts, api_key)
            
            # Проверяем количество полученных меток
            if len(batch_labels) != len(batch):
                logging.warning(f"Ожидали {len(batch)} меток, получили {len(batch_labels)}. Заполняем недостающие как OTHER.")
                batch_labels.extend(["OTHER"] * (len(batch) - len(batch_labels)))
            
            labels.extend(batch_labels)
            
            # Обновляем прогресс
            if progress_callback:
                progress = (batch_num / total_batches) * 100
                progress_callback(progress)

        except Exception as e:
            logging.error(f"Ошибка при обработке батча {batch_num}: {str(e)}")
            labels.extend(["OTHER"] * len(batch))
            
            # Обновляем прогресс даже при ошибке
            if progress_callback:
                progress = (batch_num / total_batches) * 100
                progress_callback(progress)

    return labels 