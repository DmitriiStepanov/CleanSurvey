#!/bin/bash

# Создаем виртуальное окружение
python3 -m venv venv
source venv/bin/activate

# Устанавливаем зависимости
pip install -r requirements.txt

# Создаем директорию для логов
mkdir -p logs
touch logs/survey_generator.log
chmod 644 logs/survey_generator.log

# Копируем конфигурацию supervisor
sudo cp supervisor.conf /etc/supervisor/conf.d/survey_generator.conf

# Копируем конфигурацию logrotate
sudo cp logrotate.conf /etc/logrotate.d/survey_generator

# Перезапускаем supervisor
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl restart survey_generator

echo "Установка завершена!" 