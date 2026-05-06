"""
ILLMProvider — puerto abstracto para cualquier proveedor de LLM.

El dominio y los use cases solo conocen esta interfaz.
Los adaptadores concretos (Groq, OpenAI, Anthropic, etc.) viven en infraestructura.
"""

from abc import ABC, abstractmethod


class ILLMProvider(ABC):
    """
    Contrato que debe cumplir cualquier proveedor de LLM.
    Recibe una lista de mensajes en formato estándar OpenAI
    (role: system|user|assistant, content: str) y devuelve
    la respuesta del modelo como string.
    """

    @abstractmethod
    async def complete(self, messages: list[dict]) -> str:
        """
        Envía los mensajes al LLM y retorna el texto de la respuesta.

        Args:
            messages: Lista de dicts con claves 'role' y 'content'.
                      role puede ser 'system', 'user' o 'assistant'.

        Returns:
            Texto generado por el modelo.
        """
        ...

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Nombre legible del proveedor, para logs y diagnóstico."""
        ...
