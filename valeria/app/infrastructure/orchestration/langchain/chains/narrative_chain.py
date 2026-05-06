"""
Narrative generation chain using LangChain for ROGER - Valeria API
"""

from typing import Dict, List, Any
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI

from app.config.settings import settings
from app.infrastructure.ai.prompts.templates import prompt_templates


class NarrativeChain:
    """
    LangChain chain for generating narratives with source traceability.
    """
    
    def __init__(self):
        self.llm = ChatOpenAI(
            model=settings.openai_model,
            api_key=settings.openai_api_key,
            temperature=settings.openai_temperature
        )
        
        self.prompt = PromptTemplate(
            input_variables=["image_metadata", "retrieved_context", "query"],
            template=prompt_templates.NARRATIVE_GENERATION
        )
        
        self.chain = LLMChain(llm=self.llm, prompt=self.prompt)
    
    async def generate(
        self,
        image_metadata: Dict[str, Any],
        retrieved_context: str,
        query: str = ""
    ) -> Dict[str, Any]:
        """
        Generate narrative for an image with source traceability.
        
        Args:
            image_metadata: Image metadata dict
            retrieved_context: Context from RAG retrieval
            query: Optional user query
            
        Returns:
            Dict with narrative, claims, sources, and confidence
        """
        result = await self.chain.ainvoke({
            "image_metadata": str(image_metadata),
            "retrieved_context": retrieved_context,
            "query": query or "Genera una descripción histórica completa"
        })
        
        # Parse JSON response
        import json
        try:
            narrative_data = json.loads(result['text'])
        except json.JSONDecodeError:
            # Fallback if JSON parsing fails
            narrative_data = {
                "narrative": result['text'],
                "claims": [],
                "confidence": 0.5
            }
        
        return narrative_data


# Global instance
narrative_chain = NarrativeChain()
