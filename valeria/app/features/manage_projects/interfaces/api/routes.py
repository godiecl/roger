"""
FastAPI routes for projects (RF-10: Grupos de Proyectos).
"""

import time
from collections import defaultdict

from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession

# In-memory AI rate limiter: {user_id: [timestamp, ...]}
_ai_rate_limit: dict[int, list[float]] = defaultdict(list)
_AI_RATE_LIMIT = 10
_AI_RATE_WINDOW = 3600  # 1 hour in seconds

from app.features.manage_projects.interfaces.api.schemas import (
    ProjectCreateRequest,
    ProjectUpdateRequest,
    ProjectResponse,
    ProjectListResponse,
    MemberResponse,
    MemberListResponse,
    MessageCreateRequest,
    AiMessageRequest,
    MessageResponse,
    MessageListResponse,
    AiMessageResponse,
    InviteRequest,
    InvitationResponse,
    InvitationListResponse,
    SentInvitationResponse,
    SentInvitationListResponse,
    PdfContextResponse
)
from app.features.manage_projects.application.create_project_usecase import (
    CreateProjectUseCase
)
from app.features.manage_projects.application.list_projects_usecase import (
    ListProjectsUseCase
)
from app.features.manage_projects.application.get_project_usecase import (
    GetProjectUseCase
)
from app.features.manage_projects.application.update_project_usecase import (
    UpdateProjectUseCase
)
from app.features.manage_projects.application.delete_project_usecase import (
    DeleteProjectUseCase
)
from app.features.manage_projects.application.remove_member_usecase import (
    RemoveMemberUseCase
)
from app.features.manage_projects.application.list_members_usecase import (
    ListMembersUseCase
)
from app.features.manage_projects.application.create_invitation_usecase import (
    CreateInvitationUseCase
)
from app.features.manage_projects.application.accept_invitation_usecase import (
    AcceptInvitationUseCase
)
from app.features.manage_projects.application.decline_invitation_usecase import (
    DeclineInvitationUseCase
)
from app.features.manage_projects.application.list_invitations_usecase import (
    ListInvitationsUseCase
)
from app.features.manage_projects.infrastructure.adapters.project_invitation_repository import (
    ProjectInvitationRepository
)
from app.features.manage_projects.application.create_message_usecase import (
    CreateMessageUseCase
)
from app.features.manage_projects.application.list_messages_usecase import (
    ListMessagesUseCase
)
from app.features.manage_projects.application.create_ai_message_usecase import (
    CreateAiMessageUseCase
)
from app.features.manage_projects.infrastructure.adapters.project_repository import (
    ProjectRepository
)
from app.features.manage_projects.infrastructure.adapters.project_message_repository import (
    ProjectMessageRepository
)
from app.features.authenticate.infrastructure.adapters.user_repository import (
    UserRepository
)
from app.features.authenticate.interfaces.api.dependencies import get_current_user_id
from app.infrastructure.database.session import get_db
from app.shared.domain.exceptions import (
    EntityNotFoundError,
    PermissionDeniedError,
    ValidationError,
    BusinessRuleViolationError
)


router = APIRouter(prefix="/projects", tags=["Projects"])
invitations_router = APIRouter(prefix="/invitations", tags=["Invitations"])


# ============================================================
# PROJECT CRUD ENDPOINTS
# ============================================================

@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    request: ProjectCreateRequest,
    owner_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """Create a new research project. The requesting user becomes owner and LIDER."""
    try:
        repository = ProjectRepository(db)
        usecase = CreateProjectUseCase(repository)
        project = await usecase.execute(
            name=request.name,
            owner_id=owner_id,
            description=request.description,
            start_date=request.start_date,
            end_date=request.end_date
        )
        return ProjectResponse.model_validate(project.__dict__)
    except ValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("", response_model=ProjectListResponse)
async def list_projects(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """List projects where the current user is owner or member."""
    repository = ProjectRepository(db)
    usecase = ListProjectsUseCase(repository)
    projects = await usecase.execute(user_id=user_id, skip=skip, limit=limit)
    return ProjectListResponse(
        total=len(projects),
        skip=skip,
        limit=limit,
        projects=[ProjectResponse.model_validate(p.__dict__) for p in projects]
    )


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: int,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """Get a specific project. Only accessible by project members."""
    try:
        repository = ProjectRepository(db)
        usecase = GetProjectUseCase(repository)
        project = await usecase.execute(project_id=project_id, user_id=user_id)
        return ProjectResponse.model_validate(project.__dict__)
    except EntityNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except PermissionDeniedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.put("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: int,
    request: ProjectUpdateRequest,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """Update a project. Only LIDER or INVESTIGADOR members can update."""
    try:
        repository = ProjectRepository(db)
        usecase = UpdateProjectUseCase(repository)
        project = await usecase.execute(
            project_id=project_id,
            user_id=user_id,
            name=request.name,
            description=request.description,
            start_date=request.start_date,
            end_date=request.end_date,
            is_active=request.is_active,
            ai_instructions=request.ai_instructions
        )
        return ProjectResponse.model_validate(project.__dict__)
    except EntityNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except PermissionDeniedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except ValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: int,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """Delete a project. Only the owner can delete it."""
    try:
        repository = ProjectRepository(db)
        usecase = DeleteProjectUseCase(repository)
        await usecase.execute(project_id=project_id, user_id=user_id)
        return None
    except EntityNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except PermissionDeniedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


# ============================================================
# MEMBER MANAGEMENT ENDPOINTS
# ============================================================

@router.post(
    "/{project_id}/members",
    response_model=InvitationResponse,
    status_code=status.HTTP_201_CREATED
)
async def invite_member(
    project_id: int,
    request: InviteRequest,
    requesting_user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """Invite a user by email. Creates a pending invitation. Only LIDER can invite."""
    user_repo = UserRepository(db)
    user = await user_repo.get_by_email(str(request.email))
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No se encontró ningún usuario con el correo '{request.email}'"
        )
    inviter = await user_repo.get_by_id(requesting_user_id)

    try:
        project_repo = ProjectRepository(db)
        invitation_repo = ProjectInvitationRepository(db)
        usecase = CreateInvitationUseCase(project_repo, invitation_repo)
        invitation = await usecase.execute(
            project_id=project_id,
            invited_user_id=user.id,
            requesting_user_id=requesting_user_id
        )
        project = await project_repo.get_by_id(project_id)
        return InvitationResponse(
            id=invitation.id,
            project_id=invitation.project_id,
            project_name=project.name if project else "",
            invited_by_email=inviter.email if inviter else "",
            status=invitation.status,
            created_at=invitation.created_at
        )
    except EntityNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except PermissionDeniedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except BusinessRuleViolationError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


@router.get("/{project_id}/invitations", response_model=SentInvitationListResponse)
async def list_project_invitations(
    project_id: int,
    requesting_user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """List invitations sent for this project. Only LIDER can view."""
    try:
        project_repo = ProjectRepository(db)
        project = await project_repo.get_by_id(project_id)
        if not project:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

        requester_member = await project_repo.get_member(project_id, requesting_user_id)
        from app.features.manage_projects.domain.project_role import ProjectRole
        if not project.is_owner(requesting_user_id) and (
            not requester_member or not ProjectRole.can_manage_members(requester_member.role)
        ):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No permission")

        invitation_repo = ProjectInvitationRepository(db)
        user_repo = UserRepository(db)
        invitations = await invitation_repo.list_by_project(project_id)

        result = []
        for inv in invitations:
            invited = await user_repo.get_by_id(inv.invited_user_id)
            inviter = await user_repo.get_by_id(inv.invited_by_user_id)
            result.append(SentInvitationResponse(
                id=inv.id,
                project_id=inv.project_id,
                invited_email=invited.email if invited else "",
                invited_by_email=inviter.email if inviter else "",
                status=inv.status,
                created_at=inv.created_at
            ))
        return SentInvitationListResponse(total=len(result), invitations=result)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.delete(
    "/{project_id}/members/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
async def remove_member(
    project_id: int,
    user_id: int,
    requesting_user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """Remove a member. Only LIDER can remove. The owner cannot be removed."""
    try:
        repository = ProjectRepository(db)
        usecase = RemoveMemberUseCase(repository)
        await usecase.execute(
            project_id=project_id,
            user_id=user_id,
            requesting_user_id=requesting_user_id
        )
        return None
    except EntityNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except PermissionDeniedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except BusinessRuleViolationError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


@router.get("/{project_id}/members", response_model=MemberListResponse)
async def list_members(
    project_id: int,
    requesting_user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """List all project members. Only members can view the list."""
    try:
        repository = ProjectRepository(db)
        usecase = ListMembersUseCase(repository)
        members = await usecase.execute(
            project_id=project_id,
            requesting_user_id=requesting_user_id
        )
        return MemberListResponse(
            total=len(members),
            members=[MemberResponse.model_validate(m.__dict__) for m in members]
        )
    except EntityNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except PermissionDeniedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


# ============================================================
# INVITATION ENDPOINTS (per-user, not per-project)
# ============================================================

@invitations_router.get("", response_model=InvitationListResponse)
async def list_my_invitations(
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """List all pending invitations for the current user."""
    invitation_repo = ProjectInvitationRepository(db)
    project_repo = ProjectRepository(db)
    user_repo = UserRepository(db)
    usecase = ListInvitationsUseCase(invitation_repo)
    invitations = await usecase.execute(user_id=user_id)

    result = []
    for inv in invitations:
        project = await project_repo.get_by_id(inv.project_id)
        inviter = await user_repo.get_by_id(inv.invited_by_user_id)
        result.append(InvitationResponse(
            id=inv.id,
            project_id=inv.project_id,
            project_name=project.name if project else "",
            invited_by_email=inviter.email if inviter else "",
            status=inv.status,
            created_at=inv.created_at
        ))
    return InvitationListResponse(total=len(result), invitations=result)


@invitations_router.patch("/{invitation_id}/accept", response_model=MemberResponse)
async def accept_invitation(
    invitation_id: int,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """Accept a pending invitation. The user becomes an OBSERVADOR member."""
    try:
        project_repo = ProjectRepository(db)
        invitation_repo = ProjectInvitationRepository(db)
        usecase = AcceptInvitationUseCase(project_repo, invitation_repo)
        member = await usecase.execute(invitation_id=invitation_id, requesting_user_id=user_id)
        return MemberResponse.model_validate(member.__dict__)
    except EntityNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except PermissionDeniedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except BusinessRuleViolationError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


@invitations_router.patch("/{invitation_id}/decline", status_code=status.HTTP_204_NO_CONTENT)
async def decline_invitation(
    invitation_id: int,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """Decline a pending invitation."""
    try:
        invitation_repo = ProjectInvitationRepository(db)
        usecase = DeclineInvitationUseCase(invitation_repo)
        await usecase.execute(invitation_id=invitation_id, requesting_user_id=user_id)
        return None
    except EntityNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except PermissionDeniedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except BusinessRuleViolationError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


# ============================================================
# CHAT ENDPOINTS
# ============================================================

@router.get("/{project_id}/messages", response_model=MessageListResponse)
async def list_messages(
    project_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """List chat messages for a project. Only members can view messages."""
    try:
        project_repo = ProjectRepository(db)
        message_repo = ProjectMessageRepository(db)
        usecase = ListMessagesUseCase(project_repo, message_repo)
        messages = await usecase.execute(
            project_id=project_id,
            user_id=user_id,
            skip=skip,
            limit=limit
        )
        total = await message_repo.count_by_project(project_id)
        return MessageListResponse(
            total=total,
            messages=[MessageResponse.model_validate(m.__dict__) for m in messages]
        )
    except EntityNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except PermissionDeniedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.post(
    "/{project_id}/messages",
    response_model=MessageResponse,
    status_code=status.HTTP_201_CREATED
)
async def create_message(
    project_id: int,
    request: MessageCreateRequest,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """Send a message to the project chat. Only members can send messages."""
    user_repo = UserRepository(db)
    current_user = await user_repo.get_by_id(user_id)
    sender_name = (
        current_user.full_name or current_user.email
        if current_user else "Usuario"
    )

    try:
        project_repo = ProjectRepository(db)
        message_repo = ProjectMessageRepository(db)
        usecase = CreateMessageUseCase(project_repo, message_repo)
        message = await usecase.execute(
            project_id=project_id,
            user_id=user_id,
            content=request.content,
            sender_name=sender_name
        )
        return MessageResponse.model_validate(message.__dict__)
    except EntityNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except PermissionDeniedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.post(
    "/{project_id}/messages/ai",
    response_model=AiMessageResponse,
    status_code=status.HTTP_201_CREATED
)
async def ask_ai(
    project_id: int,
    request: AiMessageRequest,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """Ask the AI assistant a question within the project context."""
    # Rate limiting: 10 AI requests per user per hour
    now = time.time()
    _ai_rate_limit[user_id] = [t for t in _ai_rate_limit[user_id] if now - t < _AI_RATE_WINDOW]
    if len(_ai_rate_limit[user_id]) >= _AI_RATE_LIMIT:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Has alcanzado el límite de {_AI_RATE_LIMIT} consultas a la IA por hora. Intenta de nuevo más tarde."
        )
    _ai_rate_limit[user_id].append(now)

    user_repo = UserRepository(db)
    current_user = await user_repo.get_by_id(user_id)
    sender_name = (
        current_user.full_name or current_user.email
        if current_user else "Usuario"
    )

    try:
        project_repo = ProjectRepository(db)
        message_repo = ProjectMessageRepository(db)
        usecase = CreateAiMessageUseCase(project_repo, message_repo)
        user_msg, ai_msg = await usecase.execute(
            project_id=project_id,
            user_id=user_id,
            question=request.question,
            sender_name=sender_name,
            context=request.context
        )
        return AiMessageResponse(
            user_message=MessageResponse.model_validate(user_msg.__dict__),
            ai_message=MessageResponse.model_validate(ai_msg.__dict__)
        )
    except EntityNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except PermissionDeniedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Error al consultar la IA: {str(e)}"
        )


@router.post("/{project_id}/context/pdf", response_model=PdfContextResponse)
async def upload_pdf_context(
    project_id: int,
    file: UploadFile = File(...),
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """Extract text from a PDF to use as context for the AI assistant."""
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Solo se aceptan archivos PDF")

    # Verify the user is a project member
    project_repo = ProjectRepository(db)
    project = await project_repo.get_by_id(project_id)
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Proyecto no encontrado")
    member = await project_repo.get_member(project_id, user_id)
    if not member and not project.is_owner(user_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No eres miembro de este proyecto")

    try:
        import pdfplumber
        import io
        content = await file.read()
        text_parts = []
        num_pages = 0
        with pdfplumber.open(io.BytesIO(content)) as pdf:
            num_pages = len(pdf.pages)
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(page_text)
        full_text = "\n\n".join(text_parts).strip()
        if not full_text:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                detail="No se pudo extraer texto del PDF (puede ser una imagen escaneada)")
        # Limit to ~15000 chars to stay within Groq/OpenAI context limits
        if len(full_text) > 15000:
            full_text = full_text[:15000] + "\n\n[... texto truncado por límite de contexto ...]"
        return PdfContextResponse(
            filename=file.filename,
            pages=num_pages,
            text=full_text,
            char_count=len(full_text)
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Error al procesar el PDF: {str(e)}")
