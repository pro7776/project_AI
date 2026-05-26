#!/bin/sh

echo "Инициализация баз данных..."

# Создаём books.db если не существует
if [ ! -f /data/books.db ]; then
    echo "Создание books.db..."
    sqlite3 /data/books.db "CREATE TABLE IF NOT EXISTS books (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        Title TEXT,
        Author TEXT,
        Year REAL,
        Genre TEXT,
        Description TEXT,
        Rating REAL,
        Rating_Count INTEGER
    );"
    echo "Таблица books создана"
fi

# Создаём login.db если не существует
if [ ! -f /data/login.db ]; then
    echo "Создание login.db..."
    sqlite3 /data/login.db "CREATE TABLE IF NOT EXISTS all_login (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        login TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        system TEXT NOT NULL CHECK(system IN ('users', 'administrator'))
    );"
    echo "Таблица all_login создана"
fi

echo "Базы данных готовы"