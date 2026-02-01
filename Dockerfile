FROM python:3.12-slim

WORKDIR /app
# Устанавливаем системные зависимости
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*
# Копируем зависимости
COPY requirements.txt .
# Устанавливаем Python зависимости
RUN pip install --no-cache-dir -r requirements.txt
# Копируем приложение
COPY . .
# Создаем не-root пользователя
RUN useradd -m -u 1000 fastapi && chown -R fastapi:fastapi /app
USER fastapi
# Запускаем приложение
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]