import streamlit as st
import tempfile
import os
import logging
import traceback
from datetime import datetime
from main import process_survey

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Получаем API ключ из секретов Streamlit
API_KEY = st.secrets["OPENAI_API_KEY"]
os.environ["OPENAI_API_KEY"] = API_KEY

# Проверка наличия API ключа
if not API_KEY:
    logger.error("OPENAI_API_KEY не установлен")
    st.error("Ошибка конфигурации: API ключ не найден. Пожалуйста, свяжитесь с администратором.")
    st.stop()

st.set_page_config(page_title="Генератор чистовой анкеты", layout="centered")
st.title("Генератор чистовой анкеты")
st.write("Загрузите черновую анкету в формате .docx. После обработки вы сможете скачать чистовой файл.")

# Инициализация состояния сессии
if 'processed_files' not in st.session_state:
    st.session_state.processed_files = []
if 'current_file' not in st.session_state:
    st.session_state.current_file = None
if 'is_processing' not in st.session_state:
    st.session_state.is_processing = False
if 'error_message' not in st.session_state:
    st.session_state.error_message = None

uploaded_file = st.file_uploader("Загрузите файл .docx", type=["docx"])

# Если загружен новый файл
if uploaded_file and uploaded_file != st.session_state.current_file:
    try:
        logger.info(f"Начало обработки нового файла: {uploaded_file.name}")
        st.session_state.current_file = uploaded_file
        st.session_state.is_processing = True
        st.session_state.error_message = None
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as tmp_input:
            tmp_input.write(uploaded_file.read())
            input_path = tmp_input.name
        output_path = input_path.replace(".docx", "_clean.docx")

        st.info("Обработка может занять несколько минут. Пожалуйста, дождитесь завершения!")
        progress_bar = st.progress(0)

        # Функция для обновления прогресс-бара
        def update_progress(progress):
            progress_bar.progress(progress / 100)
            logger.debug(f"Прогресс обработки: {progress}%")

        # Запуск обработки с callback для прогресс-бара
        with st.spinner("Обработка анкеты..."):
            process_survey(input_path, output_path, progress_callback=update_progress)

        logger.info(f"Файл успешно обработан: {output_path}")
        st.success("Готово! Скачайте чистовой файл ниже.")
        with open(output_path, "rb") as f:
            st.download_button(
                "Скачать чистовой docx", 
                f, 
                file_name=f"clean_survey_{datetime.now().strftime('%Y%m%d_%H%M%S')}.docx"
            )
        
        # Сохраняем пути к файлам в состоянии сессии
        st.session_state.processed_files.append((input_path, output_path))
        st.session_state.is_processing = False

    except Exception as e:
        logger.error(f"Ошибка при обработке файла: {str(e)}")
        logger.error(traceback.format_exc())
        st.session_state.error_message = f"Произошла ошибка при обработке файла: {str(e)}"
        st.error(st.session_state.error_message)
        st.session_state.is_processing = False

# Если файл уже обработан, показываем кнопку скачивания
elif st.session_state.current_file and not st.session_state.is_processing:
    st.success("Файл уже обработан! Скачайте чистовой файл ниже.")
    output_path = st.session_state.processed_files[-1][1]
    try:
        with open(output_path, "rb") as f:
            st.download_button(
                "Скачать чистовой docx", 
                f, 
                file_name=f"clean_survey_{datetime.now().strftime('%Y%m%d_%H%M%S')}.docx"
            )
    except Exception as e:
        logger.error(f"Ошибка при скачивании файла: {str(e)}")
        st.error("Ошибка при скачивании файла. Попробуйте очистить временные файлы и загрузить документ заново.")

# Показываем ошибку, если она есть
if st.session_state.error_message:
    st.error(st.session_state.error_message)

# Добавляем кнопку очистки, если есть обработанные файлы
if st.session_state.processed_files:
    if st.button("Очистить временные файлы"):
        try:
            for input_path, output_path in st.session_state.processed_files:
                logger.info(f"Удаление временных файлов: {input_path}, {output_path}")
                os.remove(input_path)
                os.remove(output_path)
            st.session_state.processed_files = []
            st.session_state.current_file = None
            st.session_state.error_message = None
            logger.info("Временные файлы успешно удалены")
            st.success("Временные файлы удалены")
            st.experimental_rerun()
        except Exception as e:
            logger.error(f"Ошибка при удалении временных файлов: {str(e)}")
            st.error(f"Ошибка при удалении файлов: {str(e)}") 