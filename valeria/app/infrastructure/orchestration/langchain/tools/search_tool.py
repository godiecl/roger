"""
Search tool for LangChain agents
"""

from typing import Optional
from langchain.tools import Tool

from app.infrastructure.rag.knowledge_base.image_kb import image_kb


class SearchTool:
    """Tool for searching the knowledge base."""
    
    @staticmethod
    async def search_images(query: str, n_results: int = 5) -> str:
        """
        Search for images in the knowledge base.
        
        Args:
            query: Search query
            n_results: Number of results
            
        Returns:
            Formatted search results as string
        """
        results = await image_kb.search(query, n_results=n_results)
        
        if not results:
            return "No results found."
        
        # Format results
        output = []
        for i, doc in enumerate(results, 1):
            metadata = doc['metadata']
            output.append(
                f"{i}. {metadata.get('title', 'Untitled')}\n"
                f"   Year: {metadata.get('year', 'N/A')}\n"
                f"   Location: {metadata.get('location', 'N/A')}\n"
                f"   Score: {doc['score']:.2f}\n"
            )
        
        return "\n".join(output)
    
    @classmethod
    def as_langchain_tool(cls) -> Tool:
        """Convert to LangChain Tool."""
        return Tool(
            name="SearchImages",
            func=lambda q: cls.search_images(q),
            description="""
            Search for images in the Gerstmann collection.
            Input: search query string
            Output: list of matching images with metadata
            """
        )


# Global instance
search_tool = SearchTool()
