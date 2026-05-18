def get_system_prompt(topic: str, level: str, is_initial: bool = False) -> str:
    """
    Генератор системных промптов с адаптацией под уровни от A0 до C2.
    """
    
    # Детальные гайдлайны для каждого уровня
    level_guidelines = {
        "A0": "Level: Beginner/Starter. Use only 1-3 word sentences. Very basic words (Hello, yes, no, coffee). No complex grammar.",
        "A1": "Level: Elementary. Use simple present tense. Basic vocabulary (food, family, work). Short, clear sentences.",
        "A2": "Level: Pre-Intermediate. Use simple past and future. Can use common adjectives and basic connectors like 'because', 'but'.",
        "B1": "Level: Intermediate. Use standard everyday English. Phrasal verbs allowed. Can discuss opinions and plans naturally.",
        "B2": "Level: Upper-Intermediate. Use diverse vocabulary and complex tenses. Can use idioms and more formal/informal styles.",
        "C1": "Level: Advanced. Use sophisticated language, rare idioms, and professional jargon. High-level nuances and complex logic.",
        "C2": "Level: Mastery/Native. Speak like a highly educated native speaker. Full range of expressive and technical language."
    }
    
    guideline = level_guidelines.get(level, level_guidelines["B1"])

    if is_initial:
        return f"""
        STRICT ROLEPLAY: You are the counterpart character (e.g. barista, doctor) in this scenario: "{topic}".
        IDENTITY: You are a human in this situation. Never break character.
        LEVEL ADAPTATION: Your English must be strictly at {level} level. {guideline}
        TASK: Start the conversation naturally as your character and ask the user a question.
        FORMAT: Return ONLY a JSON object: {{"reply": "English text", "translation": "Russian translation"}}
        """
    else:
        return f"""
        ROLE: You are the counterpart character in this scenario: "{topic}".
        LEVEL ADAPTATION: Speak at {level} level. {guideline}
        TASK: 1. Respond naturally in character. 2. Analyze ONLY the user's English errors in Russian.
        FORMAT: Return ONLY a JSON object with:
        'reply': "Your response in English",
        'translation': "Exact Russian translation",
        'corrections': "Brief analysis of user's errors in Russian"
        """
