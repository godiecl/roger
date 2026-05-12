ROGER_ORCHESTRATOR_SCHEMA = {
    "type": "object",
    "properties": {
        "tool": {
            "type": "string",
            "enum": [
                "descripcion_visual",
                "busqueda_visual_similaridad",
                "busqueda_semantica_texto",
                "ocr",
                "deteccion_objetos",
                "deterioro",
                "chat"
            ]
        },
        "args": {
            "type": "object",
            "properties": {
                "image": {
                    "type": ["string", "null"]
                },
                "query": {
                    "type": ["string", "null"]
                },
                "top_k": {
                    "type": "integer"
                }
            },
            "required": ["image", "query", "top_k"]
        }
    },
    "required": ["tool", "args"]
}