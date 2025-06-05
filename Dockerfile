# Базовый образ
FROM python:3.11-slim

# Установка зависимостей ОС
RUN apt-get update && apt-get install -y \
    gcc \
    default-libmysqlclient-dev \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Установка зависимостей Python
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Установка рабочей директории
WORKDIR /code

# Копирование исходников
COPY . .
