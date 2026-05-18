from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import schemas, services, storage, prompts

app = FastAPI(
    title="AI Language Trainer API",
    description="Modular Professional Platform with NVIDIA NIM & Riva",
    version="1.4.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- ENDPOINTS ---

@app.post("/api/session/start", tags=["Session"])
async def start_session(req: schemas.ScenarioRequest):
    """Initializes a new practice session and generates a background image."""
    storage.session_state.reset(req.topic, req.level)
    # Генерируем картинку в фоне
    storage.session_state.background_image = await services.generate_image(req.topic)
    return {"status": "initialized", "has_image": storage.session_state.background_image is not None}

@app.get("/api/session/background", tags=["Session"])
async def get_background():
    """Returns the generated background image."""
    return {"image": storage.session_state.background_image}

@app.post("/api/chat/init", tags=["Chat"])
async def init_chat():
    """Generates the scenario-aware opening line from the AI counterpart."""
    try:
        system_msg = prompts.get_system_prompt(
            storage.session_state.topic, 
            storage.session_state.level, 
            is_initial=True
        )
        data = await services.call_llm(system_msg, [{"role": "user", "content": "Start scene."}])
        audio = await services.generate_speech(data['reply'])
        
        msg = {
            "id": 1, "role": "assistant", 
            "text": data['reply'], "translation": data['translation'], 
            "corrections": "Start!", "audio": audio
        }
        storage.session_state.messages.append(msg)
        return msg
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/chat/message", tags=["Chat"])
async def process_message(req: schemas.MessageRequest):
    """Processes user input and returns AI response with audio."""
    try:
        storage.session_state.messages.append({"role": "user", "content": req.text})
        system_msg = prompts.get_system_prompt(storage.session_state.topic, storage.session_state.level)
        history = [{"role": m.get("role", "user"), "content": m.get("text", m.get("content"))} for m in storage.session_state.messages]
        data = await services.call_llm(system_msg, history)
        audio = await services.generate_speech(data['reply'])
        
        ai_msg = {
            "id": len(storage.session_state.messages)+1, "role": "assistant",
            "text": data['reply'], "translation": data['translation'], 
            "corrections": data['corrections'], "audio": audio
        }
        storage.session_state.messages.append(ai_msg)
        return ai_msg
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/chat/history", tags=["Chat"])
async def get_history():
    return storage.session_state.messages

@app.post("/api/chat/hints", tags=["Chat"])
async def get_hints():
    """Generates 3 smart hints for the user to continue the dialogue."""
    try:
        history = [{"role": m.get("role", "user"), "content": m.get("text", m.get("content"))} for m in storage.session_state.messages]
        
        prompt = f"""
        ROLE: Expert English Tutor. 
        CONTEXT: Roleplay in "{storage.session_state.topic}". User Level: {storage.session_state.level}.
        TASK: Based on the chat history, suggest 3 distinct ways for the USER to reply now.
        
        FORMAT: Return ONLY a JSON object with a list 'hints' containing 3 strings:
        1. Simple (basic English)
        2. Natural (common everyday English)
        3. Advanced (using idioms or complex structures)
        
        JSON: {{"hints": ["Option 1", "Option 2", "Option 3"]}}
        """
        
        data = await services.call_llm(prompt, history)
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "online", "engine": "NVIDIA"}
