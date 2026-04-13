"""
LLM Factory — crea el proveedor correcto según LLM_PROVIDER en el .env.

Proveedores soportados:
  groq              → Groq (llama-3.3-70b, mixtral, etc.) — gratis
  openai            → OpenAI (gpt-4o, gpt-4o-mini, etc.)
  anthropic         → Anthropic (claude-3-5-sonnet, claude-3-opus, etc.)
  openai_compatible → Cualquier API compatible: Together, Mistral,
                      Perplexity, Fireworks, Anyscale, etc.
                      Requiere LLM_API_KEY, LLM_MODEL y LLM_BASE_URL.

Para cambiar de proveedor basta con editar el .env:
  LLM_PROVIDER=groq          → usa GROQ_API_KEY y GROQ_MODEL
  LLM_PROVIDER=openai        → usa OPENAI_API_KEY y OPENAI_MODEL
  LLM_PROVIDER=anthropic     → usa ANTHROPIC_API_KEY y ANTHROPIC_MODEL
  LLM_PROVIDER=openai_compatible → usa LLM_API_KEY, LLM_MODEL, LLM_BASE_URL
"""

from app.shared.ports.llm_provider import ILLMProvider
from app.infrastructure.ai.llm.openai_compatible_adapter import OpenAICompatibleAdapter
from app.infrastructure.ai.llm.anthropic_adapter import AnthropicAdapter
from app.config.settings import settings

# URLs base para proveedores OpenAI-compatibles conocidos
_KNOWN_BASE_URLS: dict[str, str] = {
    "groq":       "https://api.groq.com/openai/v1",
    "together":   "https://api.together.xyz/v1",
    "mistral":    "https://api.mistral.ai/v1",
    "perplexity": "https://api.perplexity.ai",
    "fireworks":  "https://api.fireworks.ai/inference/v1",
    "anyscale":   "https://api.endpoints.anyscale.com/v1",
}


def create_llm_provider() -> ILLMProvider:
    """
    Instancia y retorna el proveedor LLM configurado en el .env.
    Lanza ValueError si el proveedor no está soportado o le falta configuración.
    """
    provider = settings.llm_provider.lower().strip()

    if provider == "groq":
        if not settings.groq_api_key:
            raise ValueError("LLM_PROVIDER=groq pero GROQ_API_KEY no está configurada.")
        return OpenAICompatibleAdapter(
            api_key=settings.groq_api_key,
            model=settings.groq_model,
            max_tokens=settings.llm_max_tokens,
            temperature=settings.llm_temperature,
            base_url=_KNOWN_BASE_URLS["groq"],
            name=f"groq/{settings.groq_model}"
        )

    if provider == "openai":
        if not settings.openai_api_key:
            raise ValueError("LLM_PROVIDER=openai pero OPENAI_API_KEY no está configurada.")
        return OpenAICompatibleAdapter(
            api_key=settings.openai_api_key,
            model=settings.openai_model,
            max_tokens=settings.llm_max_tokens,
            temperature=settings.llm_temperature,
            name=f"openai/{settings.openai_model}"
        )

    if provider == "anthropic":
        if not settings.anthropic_api_key:
            raise ValueError("LLM_PROVIDER=anthropic pero ANTHROPIC_API_KEY no está configurada.")
        return AnthropicAdapter(
            api_key=settings.anthropic_api_key,
            model=settings.anthropic_model or "claude-3-5-sonnet-20241022",
            max_tokens=settings.llm_max_tokens,
            temperature=settings.llm_temperature
        )

    if provider == "openai_compatible":
        if not settings.llm_api_key or not settings.llm_model or not settings.llm_base_url:
            raise ValueError(
                "LLM_PROVIDER=openai_compatible requiere LLM_API_KEY, LLM_MODEL y LLM_BASE_URL."
            )
        return OpenAICompatibleAdapter(
            api_key=settings.llm_api_key,
            model=settings.llm_model,
            max_tokens=settings.llm_max_tokens,
            temperature=settings.llm_temperature,
            base_url=settings.llm_base_url,
            name=f"openai_compatible/{settings.llm_model}"
        )

    # Soporte para nombres de proveedores OpenAI-compatibles directamente
    if provider in _KNOWN_BASE_URLS:
        if not settings.llm_api_key or not settings.llm_model:
            raise ValueError(
                f"LLM_PROVIDER={provider} requiere LLM_API_KEY y LLM_MODEL."
            )
        return OpenAICompatibleAdapter(
            api_key=settings.llm_api_key,
            model=settings.llm_model,
            max_tokens=settings.llm_max_tokens,
            temperature=settings.llm_temperature,
            base_url=_KNOWN_BASE_URLS[provider],
            name=f"{provider}/{settings.llm_model}"
        )

    raise ValueError(
        f"LLM_PROVIDER='{provider}' no está soportado. "
        f"Opciones: groq, openai, anthropic, openai_compatible, "
        f"{', '.join(_KNOWN_BASE_URLS.keys())}"
    )
