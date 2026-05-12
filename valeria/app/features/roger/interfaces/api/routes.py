from fastapi import APIRouter

from app.features.roger.interfaces.api.schemas import (
    RogerChatRequest,
    RogerChatResponse
)
from app.features.roger.application.roger_chat_usecase import RogerChatUseCase
from app.features.roger.infrastructure.adapters.qwen_orchestrator_adapter import QwenOrchestratorAdapter
from app.features.roger.infrastructure.adapters.blip_description_adapter import BlipDescriptionAdapter
from app.features.roger.infrastructure.adapters.clip_search_adapter import ClipSearchAdapter
from app.features.roger.infrastructure.adapters.ocr_adapter import OCRAdapter
from app.features.roger.infrastructure.adapters.yolo_detection_adapter import YOLODetectionAdapter
from app.features.roger.infrastructure.adapters.damage_adapter import DamageAdapter


router = APIRouter(prefix="/roger", tags=["ROGER"])


@router.post("/chat", response_model=RogerChatResponse)
async def roger_chat(request: RogerChatRequest):
    usecase = RogerChatUseCase(
        orchestrator=QwenOrchestratorAdapter(),
        visual_description=BlipDescriptionAdapter(),
        semantic_search=ClipSearchAdapter(),
        ocr_service=OCRAdapter(),
        object_detection=YOLODetectionAdapter(),
        damage_analysis=DamageAdapter()
    )

    response = await usecase.execute(request.message)
    return response.to_dict()