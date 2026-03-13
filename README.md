# Агрегатор объявлений с *carsensor.net*

[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.13-blue?style=for-the-badge&logo=python)](https://python.org)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.9-blue?style=for-the-badge&logo=typescript)](https://www.typescriptlang.org)
[![Docker](https://img.shields.io/badge/Docker-✓-blue?style=for-the-badge&logo=docker)](https://docker.com)

Платформа для автоматического сбора, хранения и умного поиска автомобильных объявлений с японского сайта [carsensor.net](https://www.carsensor.net). Проект состоит из трёх основных компонентов: бекенда на FastAPI со встроенным скрапером, Telegram-бота с поддержкой LLM и веб-интерфейса на React.

## Возможности

*   **Автоматический сбор данных**: Фоновый воркер парсит новые объявления с сайта, переводит с японского конвертирует валюту в рубли по текущему курсу и сохраняет их в базу данных.
*   **REST API**: Полноценное API с JWT-авторизацией и гибкой фильтрацией.
*   **Умный Telegram-бот**: Понимает запросы на естественном языке (например, *найди красную BMW до 2 млн*) благодаря интеграции с LLM (OpenRouter).
*   **Веб-интерфейс**: Интуитивный веб-интерфейс для просмотра, фильтрации и сортировки объявлений.
*   **Docker-контейнеризация**: Все сервисы упакованы в Docker для лёгкого развёртывания.

## Настройка и запуск

## 1. Клонирование репозитория

```shell
git clone git@github.com:antonlukisha/auto-ads-service.git
cd cd auto-ads-service
```
## 2. Настройка переменных окружения
Скопируйте пример файла с переменными окружения:
```shell
cp .env.example .env
```
Откройте .env:

| Переменная | Описание | Где взять                                               |
|------------|----------|---------------------------------------------------------|
| `POSTGRES_USER` | Имя пользователя БД | `postgres` (или любое другое имя) |
| `POSTGRES_PASSWORD` | Пароль для БД | Придумайте пароль, например `123` (для локальной разработки)         |
| `POSTGRES_DB` | Название базы данных | Можно оставить `auto-ads-service`                       |
| `POSTGRES_DSN` | Строка подключения к БД | `postgresql://postgres:123@postgres:5432/auto-ads-service` (замените `123` на ваш пароль)                    |
| `JWT_SECRET_KEY` | Секретный ключ для JWT | Сгенерировать самостоятельно (см. инструкцию ниже)      |
| `TELEGRAM_TOKEN` | Токен Telegram бота | Получить у [@BotFather](https://t.me/botfather)         |
| `LLM_API_KEY` | API ключ OpenRouter | Получить на [openrouter.ai/keys](https://openrouter.ai/keys) |
| `LLM_MODEL` | Модель LLM | `stepfun/step-3.5-flash:free`(или другая модель которая поддерживает Function Calling)        |
| `LLM_URL` | URL OpenRouter API | `https://openrouter.ai/api/v1`                          |
## 3. Генерация JWT_SECRET_KEY
На Linux/Mac:

```bash
openssl rand -hex 32
```
На Windows (PowerShell):
```powershell
-join ((1..32) | ForEach { '{0:x2}' -f (Get-Random -Max 256) })
```
## 4. Запуск проекта
```shell
docker-compose up -d --build
```

## 5. Создание демо-администратора
После успешного запуска выполните seed для создания демо-администратора (Логин: `admin`, Пароль: `admin_pass`):
```shell
docker exec auto-ads-backend uv run create-demo-seed
```

## 6. Проверка работоспособности
```shell
docker ps | grep auto-ads
```

---

## Автор

[![Gmail](https://img.shields.io/badge/-Gmail-D14836?style=flat-square&logo=Gmail&logoColor=white)](mailto:anton.lukisha.dev@gmail.com)
[![GitHub](https://img.shields.io/badge/-GitHub-333?style=flat-square&logo=GitHub&logoColor=white)](https://github.com/antonlukisha)
[![Telegram](https://img.shields.io/badge/-Telegram-27A7E7?style=flat-square&logo=Telegram&logoColor=white)](https://t.me/lukanlo)
