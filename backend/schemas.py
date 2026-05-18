from pydantic import BaseModel

class ScenarioRequest(BaseModel):
    topic: str
    level: str

class MessageRequest(BaseModel):
    text: str
