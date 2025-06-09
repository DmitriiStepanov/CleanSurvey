# Clean Survey Generator MVP

Этот проект представляет собой минимальный прототип системы для автоматической обработки "грязных" Word-документов с анкетами и преобразования их в структурированные "чистые" документы.

## Функционал

- Извлечение всех непустых параграфов из .docx
- Классификация абзацев с помощью OpenAI GPT
- Группировка фрагментов по блокам анкеты и вопросам
- Генерация нового Word-документа с форматированием

## Структура проекта

```
/clean_survey_mvp/
├─ README.md
├─ requirements.txt
├─ main.py
├─ parser.py
├─ classifier.py
├─ grouping.py
├─ doc_generator.py
├─ utils.py
└─ examples/
    ├─ dirty_survey.docx
    └─ clean_survey_MVP.docx
```

## Установка и запуск

1. Клонировать репозиторий
2. Создать и активировать виртуальное окружение (Python 3.9+):
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/macOS
   venv\Scripts\activate     # Windows
   ```
3. Установить зависимости:
   ```bash
   pip install -r requirements.txt
   ```
4. Задать переменную окружения OPENAI_API_KEY:
   ```bash
   export OPENAI_API_KEY="твой_ключ"      # Linux/macOS
   setx OPENAI_API_KEY "твой_ключ"         # Windows
   ```
5. Запустить скрипт:
   ```bash
   python main.py --input examples/dirty_survey.docx --output examples/clean_survey_MVP.docx
   ```

## Ограничения MVP

- Нет поддержки фона и ротаций
- Нет обработки сложных условий
- Встроенные таблицы расплющиваются
- Базовое форматирование текста
- Ограниченная обработка ошибок 