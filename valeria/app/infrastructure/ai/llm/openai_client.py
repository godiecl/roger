"""
OpenAI LLM client for ROGER - Valeria API
"""

import json
from typing import List, Dict, Optional, Any
from openai import AsyncOpenAI

from app.infrastructure.ai.llm.base_llm import BaseLLM
from app.config.settings import settings


class OpenAIClient(BaseLLM):
    """OpenAI LLM client implementation."""
    
    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.openai_api_key)
        self.model = settings.openai_model
        self.max_tokens = settings.openai_max_tokens
        self.temperature = settings.openai_temperature
    
    async def generate(
        self,
        prompt: str,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        **kwargs
    ) -> str:
        """Generate text using OpenAI."""
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens or self.max_tokens,
            temperature=temperature if temperature is not None else self.temperature,
            **kwargs
        )
        
        return response.choices[0].message.content
    
    async def generate_json(
        self,
        prompt: str,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Generate JSON response using OpenAI."""
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens or self.max_tokens,
            response_format={"type": "json_object"},
            **kwargs
        )
        
        content = response.choices[0].message.content
        return json.loads(content)
    
    async def chat(
        self,
        messages: List[Dict[str, str]],
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        **kwargs
    ) -> str:
        """Chat completion with message history."""
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            max_tokens=max_tokens or self.max_tokens,
            temperature=temperature if temperature is not None else self.temperature,
            **kwargs
        )
        
        return response.choices[0].message.content


# Global OpenAI client instance
openai_client = OpenAIClient()
