# Web_fast_API

## Инструкции по запуску проекта

Для запуска проекта выполните следующие шаги:

1. **Установите зависимости**:
    ```sh
    pip install -r requirements.txt
    ```

2. **Заполните файл `.env`**:
    - Используйте шаблон [.env.template](.env.template) для создания файла `.env`.

3. **Создайте первую миграцию для базы данных**:
    ```sh
    alembic -c backend/alembic.ini revision --autogenerate -m "initial migration"
    ```

4. **Примените миграцию**:
    ```sh
    alembic -c backend/alembic.ini upgrade head
    ```
   **Или**
   ```sh
    alembic -c backend/alembic.ini upgrade {unique id migration}
    ```

5. **Запустите проект**:
    ```sh
    fastapi dev backend/app/main.py
    ```

## P.s Создание директории alembic:

1. **Создайте директорию alembic**:
   ```sh
   mkdir -p app/alembic/versions
   ```

2. **Инициализируйте Alembic в созданной директории**:
   ```sh
   alembic -c backend/alembic.ini init app/alembic
   ```
3. **Смотреть шаг 3**.