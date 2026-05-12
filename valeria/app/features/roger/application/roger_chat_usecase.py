from app.features.roger.domain.roger import RogerResponse


class RogerChatUseCase:
    def __init__(
        self,
        orchestrator,
        visual_description,
        semantic_search,
        ocr_service,
        object_detection,
        damage_analysis
    ):
        self.orchestrator = orchestrator
        self.visual_description = visual_description
        self.semantic_search = semantic_search
        self.ocr_service = ocr_service
        self.object_detection = object_detection
        self.damage_analysis = damage_analysis

    async def execute(self, message: str) -> RogerResponse:
        tool_call = await self.orchestrator.decide(message)

        tool = tool_call.get("tool")
        args = tool_call.get("args", {})

        if tool == "descripcion_visual":
            result = await self.visual_description.describe(args["image"])
            return RogerResponse(message, tool, args, result)

        if tool == "busqueda_semantica_texto":
            result = await self.semantic_search.search(
                query=args["query"],
                top_k=args.get("top_k", 5)
            )
            return RogerResponse(message, tool, args, result)

        if tool == "busqueda_visual_similaridad":
            if not self.visual_similarity:
                return RogerResponse(
                    message=message,
                    tool_used=tool,
                    tool_args=args,
                    result="La búsqueda por similitud visual todavía no está implementada."
                )

            result = await self.visual_similarity.search_similar(
                image_name=args["image"],
                top_k=args.get("top_k", 5)
            )
            return RogerResponse(message, tool, args, result)

        if tool == "ocr":
            result = await self.ocr_service.analyze(args["image"])
            return RogerResponse(message, tool, args, result)

        if tool == "deteccion_objetos":
            result = await self.object_detection.detect(args["image"])
            return RogerResponse(message, tool, args, result)

        if tool == "deterioro":
            result = await self.damage_analysis.analyze(args["image"])
            return RogerResponse(message, tool, args, result)

        return RogerResponse(
            message=message,
            tool_used="chat",
            result="No pude determinar una herramienta válida."
        )