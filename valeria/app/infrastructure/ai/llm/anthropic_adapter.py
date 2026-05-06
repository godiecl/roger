"""
Adaptador para Anthropic (Claude).

Anthropic tiene su propia API que difiere de OpenAI:
- El system prompt va en un campo separado, no en messages.
- La respuesta está en response.content[0].text.

Requiere: pip install anthropic
"""

from app.shared.ports.llm_provider import ILLMProvider


class AnthropicAdapter(ILLMProvider):
    """
    Adaptador para la API de Anthropic (Claude 3, Claude 3.5, etc.).
    """

    def __init__(
        self,
        api_key: str,
        model: str = "claude-3-5-sonnet-20241022",
        max_tokens: int = 1000,
        temperature: float = 0.7
    ):
        # Import lazy para no requerir el paquete si no se usa Anthropic
        try:
            import anthropic
            self.client = anthropic.AsyncAnthropic(api_key=api_key)
        except ImportError:
            raise ImportError(
                "El paquete 'anthropic' no está instalado. "
                "Ejecuta: pip install anthropic"
            )
        self.model = model
        self.max_tokens = max_tokens
        self.temperature = temperature

    @property
    def provider_name(self) -> str:
        return f"anthropic/{self.model}"

    async def complete(self, messages: list[dict]) -> str:
        # Anthropic separa el system prompt del resto de mensajes
        system = next(
            (m["content"] for m in messages if m["role"] == "system"),
            ""
        )
        chat_messages = [m for m in messages if m["role"] != "system"]

        response = await self.client.messages.create(
            model=self.model,
            max_tokens=self.max_tokens,
            temperature=self.temperature,
            system=system,
            messages=chat_messages
        )
        return response.content[0].text
