"""
Base LLM interface for ROGER - Valeria API
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Optional, Any


class BaseLLM(ABC):
    """Abstract base class for LLM implementations."""
    
    @abstractmethod
    async def generate(
        self,
        prompt: str,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        **kwargs
    ) -> str:
        """
        Generate text from a prompt.
        
        Args:
            prompt: Input prompt
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature (0-1)
            **kwargs: Additional model-specific parameters
            
        Returns:
            Generated text
        """
        pass
    
    @abstractmethod
    async def generate_json(
        self,
        prompt: str,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate JSON response from a prompt.
        
        Args:
            prompt: Input prompt
            max_tokens: Maximum tokens to generate
            **kwargs: Additional model-specific parameters
            
        Returns:
            Parsed JSON response
        """
        pass
    
    @abstractmethod
    async def chat(
        self,
        messages: List[Dict[str, str]],
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        **kwargs
    ) -> str:
        """
        Chat completion with message history.
        
        Args:
            messages: List of messages [{"role": "user/assistant", "content": "..."}]
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            **kwargs: Additional parameters
            
        Returns:
            Assistant's response
        """
        pass
