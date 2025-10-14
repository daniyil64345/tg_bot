import subprocess
import json
import asyncio

async def ai_generate(text: str) -> str:
    """Редагує новину через Ollama CLI локально."""
    try:
        # Викликаємо Ollama модель Mistral
        result = await asyncio.to_thread(
            subprocess.run,
            ["ollama", "chat", "mistral", "--json"],
            input=json.dumps({"prompt": f"Напиши коротко і зрозуміло: {text}"}).encode(),
            capture_output=True
        )
        output = json.loads(result.stdout)
        return output.get("response", text)
    except Exception as e:
        print(f"⚠️ AI помилка: {e}")
        return text