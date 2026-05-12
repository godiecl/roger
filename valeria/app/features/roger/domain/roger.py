from datetime import datetime
from typing import Any, Dict, Optional

from app.shared.domain.base_entity import BaseEntity


class RogerToolCall:
    def __init__(
        self,
        tool: str,
        args: Optional[Dict[str, Any]] = None,
        reason: Optional[str] = None
    ):
        self.tool = tool
        self.args = args or {}
        self.reason = reason


class RogerResponse(BaseEntity):
    def __init__(
        self,
        message: str,
        tool_used: Optional[str] = None,
        tool_args: Optional[Dict[str, Any]] = None,
        result: Optional[Any] = None,
        metadata: Optional[Dict[str, Any]] = None,
        id: Optional[int] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None
    ):
        super().__init__(id, created_at, updated_at)
        self.message = message
        self.tool_used = tool_used
        self.tool_args = tool_args or {}
        self.result = result
        self.metadata = metadata or {}

    def to_dict(self):
        return {
            "message": self.message,
            "tool_used": self.tool_used,
            "tool_args": self.tool_args,
            "result": self.result,
            "metadata": self.metadata
        }