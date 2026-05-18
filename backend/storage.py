class AppState:
    """Manages the in-memory state of the application for the current session."""
    def __init__(self):
        self.messages = []
        self.topic = ""
        self.level = "B1"
        self.background_image = None
    
    def reset(self, topic: str, level: str):
        self.messages = []
        self.topic = topic
        self.level = level
        self.background_image = None

session_state = AppState()
