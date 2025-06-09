"""
grouping.py
Группировка промаркированных абзацев в Blocks и Questions.
"""

from utils import extract_code_and_text

def group_paragraphs(labeled_paragraphs):
    """
    Вход: List[{"index": int, "text": str, "label": str}]
    Выход: {
      "general_instructions": [...],
      "blocks": [
         {
           "header": str,
           "instructions": [...],
           "questions": [
             {
               "text": str,
               "instructions": [...],
               "answer_options": [{"code": str, "text": str, "instruction": str}, ...],
               "rows": [{"code": str, "text": str, "instruction": str}, ...]
             }, ...
           ],
           "other": [...]
         }, ...
      ],
      "other": [...]
    }
    """
    result = {
        "general_instructions": [],
        "blocks": [],
        "other": []
    }

    current_block = None
    current_question = None
    mode = None  # None | "options" | "rows"
    in_first_block = False

    for item in labeled_paragraphs:
        text = item["text"]
        lbl = item["label"]

        # 1. Пока не встретили первый BLOCK_HEADER, собираем общие инструкции
        if not in_first_block and lbl != "BLOCK_HEADER":
            if lbl == "GENERAL_INSTRUCTION":
                result["general_instructions"].append(text)
            else:
                # если встретили что-то другое до BLOCK_HEADER, считаем его OTHER
                result["other"].append(text)
            continue

        # 2. Если встретили первый BLOCK_HEADER, переключаем флаг
        if lbl == "BLOCK_HEADER":
            in_first_block = True
            # Завершаем предыдущий блок
            if current_block:
                result["blocks"].append(current_block)
            # Начинаем новый
            current_block = {
                "header": text,
                "instructions": [],
                "questions": [],
                "other": []
            }
            current_question = None
            mode = None
            continue

        # 3. Внутри блока
        if lbl == "BLOCK_INSTRUCTION":
            if current_block:
                current_block["instructions"].append(text)
            continue

        if lbl == "QUESTION":
            # Начинаем новый вопрос
            if current_block is None:
                # Если всё же не инициализирован block, считаем как OTHER
                result["other"].append(text)
                continue
            current_question = {
                "text": text,
                "instructions": [],
                "answer_options": [],
                "rows": []
            }
            current_block["questions"].append(current_question)
            mode = None
            continue

        if lbl == "QUESTION_INSTRUCTION":
            if current_question:
                current_question["instructions"].append(text)
            else:
                # некорректный сценарий: помечаем в блоке как OTHER
                if current_block:
                    current_block["other"].append(text)
                else:
                    result["other"].append(text)
            continue

        if lbl == "ANSWER_OPTIONS_HEADER":
            mode = "options"
            continue

        if lbl == "ANSWER_OPTION" and mode == "options" and current_question:
            code, rest = extract_code_and_text(text)
            current_question["answer_options"].append({
                "code": code,
                "text": rest,
                "instruction": ""
            })
            continue

        if lbl == "ROWS_HEADER":
            mode = "rows"
            continue

        if lbl == "ROW_ITEM" and mode == "rows" and current_question:
            code, rest = extract_code_and_text(text)
            current_question["rows"].append({
                "code": code,
                "text": rest,
                "instruction": ""
            })
            continue

        # 4. Всё остальное (OTHER)
        if lbl == "OTHER":
            if current_block:
                current_block["other"].append(text)
            else:
                result["other"].append(text)
            continue

        # Если какой-то label не учтён, класть в OTHER
        if current_block:
            current_block["other"].append(text)
        else:
            result["other"].append(text)

    # В конец, после цикла, добавить последний блок
    if current_block:
        result["blocks"].append(current_block)

    return result 