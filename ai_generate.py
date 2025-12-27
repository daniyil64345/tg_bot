
# ai_generate.py
import asyncio
import subprocess

async def ai_generate(text: str) -> dict:
 
    if not text or not text.strip():
        return {"caption": "Немає тексту для генерації", "keywords": ""}

    prompt = f"Напиши коротко і зрозуміло (до 250 символів): {text}"

    try:

        result = await asyncio.to_thread(
            subprocess.run,
            ["ollama", "run", "mistral"],
            input=prompt.encode("utf-8"),
            capture_output=True,
            timeout=25
        )

        output = result.stdout.decode("utf-8").strip()
        if not output:
            output = result.stderr.decode("utf-8").strip()

        caption = output[:800].rsplit(" ", 1)[0] + "..." if len(output) > 800 else output
        return {"caption": caption, "keywords": ""}

    except subprocess.TimeoutExpired:
        print("⚠️ AI помилка: ollama process timeout")
        return {"caption": text[:500], "keywords": ""}

    except Exception as e:
        print(f"⚠️ AI помилка: {e}")
        return {"caption": text[:500], "keywords": ""}
