"""
Script to index documents into the RAG knowledge base
"""

import asyncio
import sys
from pathlib import Path
from typing import List, Dict, Any

# Add app directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.infrastructure.rag.knowledge_base.image_kb import image_kb
from app.infrastructure.rag.indexing.document_processor import document_processor


async def index_sample_documents():
    """Index sample historical documents."""
    print("=" * 60)
    print("ROGER - Knowledge Base Indexer")
    print("=" * 60)
    
    # Sample historical documents about Robert Gerstmann
    sample_docs: List[Dict[str, Any]] = [
        {
            "id": "bio_001",
            "text": """
            Robert Gerstmann (1896-1964) fue un fotógrafo alemán que desarrolló 
            gran parte de su carrera en Chile y Latinoamérica. Llegó a Chile en 
            1924 y se convirtió en uno de los documentalistas visuales más 
            importantes del país durante la primera mitad del siglo XX.
            """,
            "metadata": {
                "source": "Biografía Gerstmann - UCN",
                "year": 1896,
                "type": "veraz",
                "category": "biographical"
            }
        },
        {
            "id": "norte_001",
            "text": """
            En la década de 1930, Gerstmann realizó extensos viajes fotográficos 
            por el norte de Chile, documentando la vida en las salitreras, el 
            desierto de Atacama, y las ciudades de Antofagasta e Iquique.
            """,
            "metadata": {
                "source": "Archivo Histórico UCN",
                "year": 1930,
                "type": "veraz",
                "category": "work"
            }
        },
        {
            "id": "tecnica_001",
            "text": """
            Gerstmann utilizaba cámaras de gran formato y placas de vidrio, 
            lo que le permitía capturar detalles extraordinarios de paisajes 
            y arquitectura. Su dominio técnico de la fotografía era excepcional 
            para la época.
            """,
            "metadata": {
                "source": "Análisis Técnico - Colección Gerstmann",
                "year": 1930,
                "type": "verosimil",
                "category": "technique"
            }
        }
    ]
    
    print(f"\n📚 Indexing {len(sample_docs)} documents...")
    
    for doc in sample_docs:
        try:
            # Process document
            processed = document_processor.process_document(doc)
            
            # Index each chunk
            for chunk in processed:
                doc_id = await image_kb.add_document(chunk)
                print(f"  ✅ Indexed: {chunk['id']}")
            
        except Exception as e:
            print(f"  ❌ Error indexing {doc['id']}: {str(e)}")
    
    print("\n" + "=" * 60)
    print("✅ Knowledge base indexing completed!")
    print("=" * 60)
    
    # Test search
    print("\n🔍 Testing search...")
    results = await image_kb.search("fotografías del norte de Chile", n_results=3)
    
    if results:
        print(f"\nFound {len(results)} results:")
        for i, result in enumerate(results, 1):
            print(f"\n{i}. Score: {result['score']:.3f}")
            print(f"   Text: {result['text'][:100]}...")
            print(f"   Metadata: {result['metadata']}")
    else:
        print("No results found.")


if __name__ == "__main__":
    asyncio.run(index_sample_documents())
