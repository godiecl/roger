from app.features.roger.domain.roger_port import IRogerOrchestrator
from app.ml_models.orchestrator.qwen_orchestrator import QwenOrchestrator


class QwenOrchestratorAdapter(IRogerOrchestrator):
    def __init__(self):
        self.service = QwenOrchestrator()

    async def decide(self, message: str):
        return self.service.decide(message)