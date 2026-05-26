FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем всё
COPY app/ ./app/

# ОТЛАДКА: выводим список файлов
RUN echo "=== Файлы в /app ===" && ls -la /app/
RUN echo "=== Файлы в /app/app ===" && ls -la /app/app/
RUN echo "=== Файлы в /app/app/templates ===" && ls -la /app/app/templates/ 2>/dev/null || echo "Нет папки templates"
RUN echo "=== Файлы в /app/app/static ===" && ls -la /app/app/static/ 2>/dev/null || echo "Нет папки static"

EXPOSE 5000

# Меняем способ запуска - запускаем файл напрямую, а не как модуль
CMD ["python", "/app/app/main.py"]