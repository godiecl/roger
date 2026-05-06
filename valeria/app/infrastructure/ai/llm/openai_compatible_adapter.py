"""
Adaptador para proveedores compatibles con la API de OpenAI.

Funciona con: OpenAI, Groq, Together AI, Mistral, Perplexity,
Anyscale, Fireworks, y cualquier proveedor que implemente
el estándar /v1/chat/completions de OpenAI.

Solo se necesita cambiar api_key, model y base_url en el .env.
"""

from openai import AsyncOpenAI
from app.shared.ports.llm_provider import ILLMProvider


class OpenAICompatibleAdapter(ILLMProvider):
    """
    Adaptador genérico para la API de OpenAI y sus compatibles.
    """

    def __init__(
        self,
        api_key: str,
        model: str,
        max_tokens: int = 1000,
        temperature: float = 0.7,
        base_url: str | None = None,
        name: str = "openai-compatible"
    ):
        self.client = AsyncOpenAI(api_key=api_key, base_url=base_url)
        self.model = model
        self.max_tokens = max_tokens
        self.temperature = temperature
        self._name = name

    @property
    def provider_name(self) -> str:
        return self._name

    async def complete(self, messages: list[dict]) -> str:
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            max_tokens=self.max_tokens,
            temperature=self.temperature
        )
        return response.choices[0].message.content or ""
