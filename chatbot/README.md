# ChatBot (aiogram)

## Описание
Асинхронный Telegram-бот для поддержки клиентов и работы с администраторами. Архитектура — модульная, поддерживает параллельные чаты, HMAC-авторизацию и гибкую настройку.

## Структура проекта
```
chatbot/
├── config/           # Конфиги и логирование
├── db/               # Модели и интерфейс хранилища
├── handlers/         # Обработчики команд и сообщений
├── keyboards/        # Клавиатуры для UI
├── middlewares/      # Авторизация, троттлинг
├── services/         # Логика управления чатами, API
├── utils/            # Вспомогательные функции
├── .env              # Переменные окружения
├── .gitignore
├── bot.py            # Точка входа
├── requirements.txt  # Зависимости
```

## Быстрый старт
1. Клонируйте репозиторий и перейдите в папку проекта:
   ```bash
   git clone <repo-url>
   cd chatbot
   ```
2. Создайте и активируйте виртуальное окружение:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```
3. Установите зависимости:
   ```bash
   pip install -r requirements.txt
   ```
4. Скопируйте и настройте конфиг:
   ```bash
   cp config/config.yaml.example config/config.yaml
   # отредактируйте config/config.yaml под свои ключи и параметры
   ```
5. Запустите бота:
   ```bash
   python bot.py
   ```

## Запуск бота напрямую
```bash
python bot.py
```

## Конфигурация
- Все параметры (API-ключи, секреты, режимы работы) задаются в `config/config.yaml`.
- Пример:
  ```yaml
  admin_source: api  # 'api' или 'json'
  admin_api:
    url: "https://example.com/api/v1/tg/all"
    api_key: "your-api-key"
    api_secret: "your-api-secret"
  admin_json_path: "admins.json"
  ```

## Примечания
- Не коммитьте `config/config.yaml` и `.env` — они в .gitignore.
- Для локального теста можно использовать `admin_source: json` и файл `admins.json`.

---

**Вопросы/PR — welcome!** 