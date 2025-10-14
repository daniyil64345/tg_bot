# utils.py
from ollama import chat  # імпортуємо прямо функцію chat

def ai_generate(text: str) -> str:
    """
    Редагує новину у журналістському стилі через Ollama.
    Повертає готовий рядок.
    """
    try:
        completion = chat(
            model="llama2",  # або інша локальна модель, яку встановив Ollama
            messages=[
                {"role": "system", "content": "Ти журналіст. Напиши коротко, зрозуміло, нейтрально, без води."},
                {"role": "user", "content": text}
            ]
        )
        return completion.get("content", text)
    except Exception as e:
        print(f"⚠️ AI помилка: {e}")
        return text