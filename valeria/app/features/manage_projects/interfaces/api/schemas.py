"""
Pydantic schemas for projects API.
"""

from pydantic import BaseModel, Field, EmailStr, field_validator
from typing import Optional, List
from datetime import datetime, date

from app.features.manage_projects.domain.project_role import ProjectRole


# --- Project schemas ---

class ProjectCreateRequest(BaseModel):
    """Request to create a project."""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    ai_instructions: Optional[str] = None

    @field_validator('start_date')
    @classmethod
    def start_date_not_in_past(cls, v: Optional[date]) -> Optional[date]:
        if v and v < date.today():
            raise ValueError('La fecha de inicio no puede ser anterior a hoy')
        return v


class ProjectUpdateRequest(BaseModel):
    """Request to update a project."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    is_active: Optional[bool] = None
    ai_instructions: Optional[str] = None


class ProjectResponse(BaseModel):
    """Project response schema."""
    id: int
    name: str
    description: Optional[str]
    start_date: Optional[date]
    end_date: Optional[date]
    owner_id: int
    is_active: bool
    ai_instructions: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ProjectListResponse(BaseModel):
    """Project list response schema."""
    total: int
    skip: int
    limit: int
    projects: List[ProjectResponse]


# --- Member schemas ---

class AddMemberRequest(BaseModel):
    """Request to add a member to a project by email."""
    email: EmailStr = Field(..., description="Email of the user to invite")
    role: ProjectRole = Field(
        ProjectRole.OBSERVADOR,
        description="Role to assign within the project"
    )


class MemberResponse(BaseModel):
    """Project member response schema."""
    id: int
    project_id: int
    user_id: int
    role: ProjectRole
    user_email: Optional[str] = None
    user_full_name: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class MemberListResponse(BaseModel):
    """Member list response schema."""
    total: int
    members: List[MemberResponse]


# --- Chat / Message schemas ---

class MessageCreateRequest(BaseModel):
    """Request to create a user message in project chat."""
    content: str = Field(..., min_length=1, max_length=5000)


class AiMessageRequest(BaseModel):
    """Request to ask the AI assistant a question."""
    question: str = Field(..., min_length=1, max_length=2000)
    context: Optional[str] = Field(None, description="Texto de contexto extra (ej. contenido de PDF)")


class MessageResponse(BaseModel):
    """Project message response schema."""
    id: int
    project_id: int
    user_id: int
    content: str
    message_type: str
    sender_name: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class MessageListResponse(BaseModel):
    """Message list response schema."""
    total: int
    messages: List[MessageResponse]


class AiMessageResponse(BaseModel):
    """Response for AI query — includes user question and AI answer."""
    user_message: MessageResponse
    ai_message: MessageResponse


# --- Invitation schemas ---

class InviteRequest(BaseModel):
    """Request to invite a user to a project by email."""
    email: EmailStr = Field(..., description="Email of the user to invite")


class InvitationResponse(BaseModel):
    """Project invitation response schema."""
    id: int
    project_id: int
    project_name: str
    invited_by_email: str
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


class InvitationListResponse(BaseModel):
    """Invitation list response schema."""
    total: int
    invitations: List[InvitationResponse]


class SentInvitationResponse(BaseModel):
    """Invitation sent by the project leader — includes invited user email."""
    id: int
    project_id: int
    invited_email: str
    invited_by_email: str
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


class SentInvitationListResponse(BaseModel):
    total: int
    invitations: List[SentInvitationResponse]


class PdfContextResponse(BaseModel):
    """Response after uploading a PDF for AI context."""
    filename: str
    pages: int
    text: str
    char_count: int


# --- Project photographs ---

class AttachPhotographsRequest(BaseModel):
    """Request to associate one or more photographs with a project."""
    photograph_ids: List[int] = Field(..., min_length=1, description="IDs de fotografías a asociar")
    notes: Optional[str] = Field(default=None, max_length=500)


class AttachPhotographsResponse(BaseModel):
    """Response after attaching photographs."""
    added: int
    skipped: int
    project_id: int


class ProjectPhotographResponse(BaseModel):
    id: int
    project_id: int
    photograph_id: int
    added_by: Optional[int]
    added_at: datetime
    notes: Optional[str]

    class Config:
        from_attributes = True


class ProjectPhotographListResponse(BaseModel):
    total: int
    items: List[ProjectPhotographResponse]
