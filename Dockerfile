# Используем официальный образ Python
FROM python:3.9-slim

# Устанавливаем зависимости
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Копируем файлы проекта в рабочую директорию
COPY . /app
WORKDIR /app

# Открываем порт для приложения
EXPOSE 8501

# Запускаем приложение Streamlit
CMD ["streamlit", "run", "app.py"]
