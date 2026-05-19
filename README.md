# AI Language Trainer

Веб-тренажер английского языка, построенный на стеке технологий **NVIDIA AI** (Llama 3.3, Riva Magpie-TTS, Flux.1). 

Проект отличается чистой модульной архитектурой на бэкенде и легковесным фронтендом, что делает его идеальным для изучения, масштабирования и демонстрации.

## 🌟 Ключевые возможности
- **Immersive Environment**: ИИ не просто общается, он генерирует визуальный фон (Flux.1) и полностью вживается в роль.
- **High-Fidelity Audio**: Использование gRPC-протокола NVIDIA Riva для генерации естественного голоса без задержек.
- **Smart Learning Tools**: 
  - Размытие текста для тренировки слуха.
  - Умные подсказки (генерация 3 вариантов ответа, если вы застряли).
  - Мгновенный перевод и анализ грамматических ошибок.

## 📁 Архитектура проекта
```text
LinguaFlow/
├── backend/                  # FastAPI микросервис
│   ├── config.py             # Настройки и API ключи
│   ├── main.py               # API роуты (Endpoints)
│   ├── models.py / schemas.py# Pydantic схемы валидации
│   ├── prompts.py            # Вынесенные системные промпты (Config as Code)
│   ├── services.py           # Логика общения с NVIDIA (LLM, TTS, Image)
│   └── storage.py            # In-Memory хранилище сессий
└── frontend/                 # Клиентская часть
    ├── index.html            # DOM структура
    ├── style.css             # Дизайн-система
    └── script.js             # Бизнес-логика фронтенда
```

## 🚀 Быстрый старт

### 1. Настройка и запуск Backend
Убедитесь, что у вас установлен Python 3.10+.
```bash
cd backend
python -m venv venv
# Активация: venv\Scripts\activate (Windows) или source venv/bin/activate (Mac/Linux)
pip install -r requirements.txt
```
Создайте файл `backend/.env` и добавьте ваши ключи:
```env
NVIDIA_API_KEY=ваш_ключ
RIVA_API_KEY=опционально_другой_ключ_для_голоса
FLUX_API_KEY=опционально_другой_ключ_для_картинок

```
Запуск сервера:
```bash
uvicorn main:app --reload
```
*API Документация будет доступна по адресу: http://localhost:8000/docs*

### 2. Запуск Frontend
Для корректной работы микрофона и модулей браузера, фронтенд лучше открывать через локальный сервер:
```bash
cd frontend
python -m http.server 3000
```
Откройте в браузере: `http://localhost:3000`

---
**Disclaimer**: Проект создан в образовательных целях. Архитектура намеренно упрощена (In-Memory Storage вместо PostgreSQL) для удобства развертывания на презентациях.

<img width="1372" height="808" alt="Диаграмма взаимодействия drawio" src="https://github.com/user-attachments/assets/78e733a6-24f8-4f3f-8218-cd02d4bf24c4" />
