FROM alpine:3.19

# Устанавливаем SQLite
RUN apk add --no-cache sqlite

# Создаём папку для данных
WORKDIR /data

# Копируем существующие базы данных (если есть)
COPY books.db /data/books.db
COPY login.db /data/login.db

# Скрипт для инициализации баз данных (если их нет)
COPY init.sh /init.sh
RUN chmod +x /init.sh

# Проверяем целостность баз данных
RUN sqlite3 /data/books.db "PRAGMA integrity_check;" || true
RUN sqlite3 /data/login.db "PRAGMA integrity_check;" || true

# Команда для запуска (просто держит контейнер живым)
CMD ["tail", "-f", "/dev/null"]

# Volume для персистентности данных
VOLUME ["/data"]