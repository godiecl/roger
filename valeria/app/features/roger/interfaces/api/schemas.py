from typing import Any, Dict, Optional
from pydantic import BaseModel, Field


class RogerChatRequest(BaseModel):
    message: str = Field(..., min_length=1)


class RogerChatResponse(BaseModel):
    message: str
    tool_used: Optional[str] = None
    tool_args: Dict = {}
    result: Any = None
    metadata: Dict = {}