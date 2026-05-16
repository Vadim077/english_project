import os
import json
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict
from openai import OpenAI
from dotenv import load_dotenv

# Загружаем переменные из .env
load_dotenv()

app = FastAPI(title="AI Language Trainer (Ultra-Light)")

# Разрешаем CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Настройка клиента NVIDIA
client = OpenAI(
    base_url="https://integrate.api.nvidia.com/v1",
    api_key=os.getenv("NVIDIA_API_KEY")
)

class ChatRequest(BaseModel):
    message: str
    history: List[Dict[str, str]]
    level: str
    scenario: str

@app.post("/chat")
async def chat(request: ChatRequest):
    print(f"\n--- Запрос получен ---")
    print(f"Ситуация: {request.scenario}")
    print(f"Сообщение: {request.message}")

    api_key = os.getenv("NVIDIA_API_KEY")
    if not api_key:
        return {"reply": "Ошибка: NVIDIA_API_KEY не найден в .env", "corrections": "Настройте .env"}

    system_prompt = f"""
    You are an English teacher and conversation partner. 
    Context: {request.scenario}
    Student Level: {request.level}
    
    Rules:
    1. Speak ONLY English.
    2. Adapt vocabulary to {request.level}.
    3. Respond ALWAYS in valid JSON: {{"reply": "...", "corrections": "..."}}
    4. Corrections must be in Russian.
    
    If the user message is "Let's start. You speak first as the character.", you must initiate the dialogue based on the scenario.
    """

    messages = [{"role": "system", "content": system_prompt}]
    messages.extend(request.history)
    messages.append({"role": "user", "content": request.message})

    try:
        print(f"Отправка запроса в NVIDIA (модель: meta/llama-3.3-70b-instruct)...")
        completion = client.chat.completions.create(
            model="meta/llama-3.3-70b-instruct",
            messages=messages,
            temperature=0.7,
            response_format={"type": "json_object"}
        )
        
        content = completion.choices[0].message.content
        print(f"✅ ИИ ответил: {content}")
        return json.loads(content)
    except Exception as e:
        print(f"❌ ОШИБКА ИИ: {str(e)}")
        return {"reply": f"Ошибка ИИ: {str(e)}", "corrections": "Посмотрите консоль сервера"}

if __name__ == "__main__":
    import uvicorn
    print("🚀 Сервер запущен на http://localhost:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)
