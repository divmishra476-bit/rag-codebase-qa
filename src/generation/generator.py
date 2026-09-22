# src/generation/generator.py
from groq import Groq
from src.generation.prompt_builder import build_prompt, SYSTEM_PROMPT
from src.config import settings

class Generator:
    def __init__(self, model: str = None):
        self.client = Groq(api_key=settings.groq_api_key)
        self.model = model or settings.generation_model

    def generate_answer(self, query: str, chunks: list[dict]) -> str:
        prompt = build_prompt(query, chunks)
        response = self.client.chat.completions.create(
            model=self.model,
            max_tokens=settings.max_tokens,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
        )
        return response.choices[0].message.content

    def stream_answer(self, query: str, chunks: list[dict]):
        prompt = build_prompt(query, chunks)
        stream = self.client.chat.completions.create(
            model=self.model,
            max_tokens=settings.max_tokens,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            stream=True,
        )
        for chunk in stream:
            delta = chunk.choices[0].delta.content
            if delta:
                yield delta