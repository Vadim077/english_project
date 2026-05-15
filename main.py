import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="AI Language Trainer API")

# Настройка CORS для работы с index.html напрямую
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Инициализация клиента NVIDIA NIM
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
    if not os.getenv("NVIDIA_API_KEY"):
        raise HTTPException(status_code=500, detail="NVIDIA_API_KEY not found in .env")

    # Формируем системный промпт
    system_prompt = f"""
    You are an English teacher and conversation partner. 
    Context: {request.scenario}
    Student Level: {request.level}
    
    Rules:
    1. Speak ONLY English.
    2. Adapt your vocabulary to the student's level ({request.level}).
    3. Keep responses short and conversational.
    4. ALWAYS respond in valid JSON format with two fields:
       "reply": (your response in English)
       "corrections": (briefly analyze the student's last message in Russian. If no mistakes, say "Все верно!")
    
    Format example:
    {{
        "reply": "Hello! How can I help you today?",
        "corrections": "Все верно!"
    }}
    """

    # Подготовка сообщений для ИИ
    messages = [{"role": "system", "content": system_prompt}]
    # Добавляем историю (последние 10 сообщений)
    messages.extend(request.history[-10:])
    # Добавляем текущее сообщение пользователя
    messages.append({"role": "user", "content": request.message})

    try:
        completion = client.chat.completions.create(
            model="nvidia/llama-3.3-70b-instruct",
            messages=messages,
            temperature=0.7,
            max_tokens=1024,
            response_format={"type": "json_object"}
        )
        
        return completion.choices[0].message.content
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
