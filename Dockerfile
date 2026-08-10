FROM python:3.11-slim

#Установка системных зависимостей
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

#Установка Poetry
RUN pip install poetry

#Рабочая папка
WORKDIR /app

#Зависимости
COPY pyproject.toml poetry.lock ./

RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi

#Копировать проект
COPY . .

#Запуск
CMD ["poetry", "run", "python", "main.py"]