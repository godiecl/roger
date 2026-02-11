"""
Prompt templates for ROGER - Valeria API
"""


class PromptTemplates:
    """Collection of prompt templates for various tasks."""
    
    # ===================================
    # NARRATIVE GENERATION
    # ===================================
    NARRATIVE_GENERATION = """
Eres un curador experto en la colección fotográfica de Robert Gerstmann.

IMAGEN:
{image_metadata}

CONTEXTO RECUPERADO (fuentes verificadas):
{retrieved_context}

INSTRUCCIONES:
1. Genera una narrativa informativa y precisa sobre la imagen
2. Usa SOLO información del contexto recuperado
3. Clasifica cada afirmación como:
   - [VERAZ]: Información de fuente primaria verificada
   - [VEROSÍMIL]: Interpretación razonable basada en contexto
4. NUNCA inventes información
5. Si no hay suficiente información, indícalo claramente

FORMATO DE RESPUESTA (JSON):
{{
  "narrative": "Texto de la narrativa...",
  "claims": [
    {{
      "text": "Afirmación específica",
      "type": "veraz" | "verosimil",
      "sources": ["Fuente 1", "Fuente 2"]
    }}
  ],
  "confidence": 0.85
}}

QUERY DEL USUARIO: {query}

RESPUESTA:
"""
    
    # ===================================
    # IMAGE TAGGING
    # ===================================
    IMAGE_TAGGING = """
Analiza la siguiente imagen y genera etiquetas temáticas relevantes.

IMAGEN:
{image_description}

METADATOS:
{metadata}

Genera 5-10 etiquetas que describan:
- Contenido visual (objetos, personas, arquitectura)
- Período histórico
- Ubicación geográfica
- Temas conceptuales

Responde en formato JSON:
{{
  "tags": [
    {{
      "label": "etiqueta",
      "confidence": 0.95,
      "category": "visual|temporal|geografico|conceptual"
    }}
  ]
}}
"""
    
    # ===================================
    # TIMELINE GENERATION
    # ===================================
    TIMELINE_GENERATION = """
Genera una línea de tiempo para el fotógrafo Robert Gerstmann.

PERÍODO: {start_year} - {end_year}
REGIÓN: {region}

Crea 3 ejes temporales paralelos:
1. Biografía de Robert Gerstmann
2. Eventos históricos mundiales
3. Eventos relevantes en Latinoamérica

Para cada evento, incluye:
- Fecha precisa (si está disponible)
- Título breve
- Descripción
- Tipo de veracidad (veraz|verosímil)
- Fuentes

Formato JSON:
{{
  "timelines": [
    {{
      "axis": "biographical|mundial|latinoamerica",
      "events": [
        {{
          "date": "YYYY-MM-DD",
          "title": "...",
          "description": "...",
          "type": "veraz|verosimil",
          "sources": ["..."]
        }}
      ]
    }}
  ]
}}
"""


# Singleton instance
prompt_templates = PromptTemplates()
