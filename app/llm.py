import os
from typing import Optional

import httpx


class LLMClient:
    def __init__(self, api_key: Optional[str], model: str) -> None:
        self.api_key = api_key
        self.model = model

    async def review_image(self, prompt: str) -> tuple[str, Optional[str]]:
        if not self.api_key:
            return (
                "LLM לא מוגדר. הגדירו OPENAI_API_KEY כדי לקבל ביקורת אוטומטית.",
                None,
            )

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": "את/ה מבקר/ת תמונות מקצועי/ת. כתוב/י ביקורת תמציתית וברורה.",
                },
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.4,
        }

        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json=payload,
            )
            response.raise_for_status()
            data = response.json()

        content = data["choices"][0]["message"]["content"].strip()
        return content, self.model


def build_llm_client() -> LLMClient:
    api_key = os.getenv("OPENAI_API_KEY")
    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    return LLMClient(api_key=api_key, model=model)
