# src/generation/generator.py
import os
from groq import Groq
from src.generation.prompt_builder import build_prompt, SYSTEM_PROMPT

class Generator:
    def __init__(self, model: str = "openai/gpt-oss-20b"):
        self.client = Groq(api_key=os.environ["GROQ_API_KEY"])
        self.model = model

    def generate_answer(self, query: str, chunks: list[dict]) -> str:
        prompt = build_prompt(query, chunks)

        response = self.client.chat.completions.create(
            model=self.model,
            max_tokens=1024,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
        )

        return response.choices[0].message.content