"""
Create AI message use case — queries OpenAI and stores the response.
"""

from typing import Tuple

from app.features.manage_projects.domain.project_message import (
    ProjectMessage,
    IProjectMessageRepository
)
from app.features.manage_projects.domain.project_port import IProjectRepository
from app.shared.domain.exceptions import EntityNotFoundError, PermissionDeniedError
from app.config.settings import settings


class CreateAiMessageUseCase:
    """
    Use case for querying the AI assistant within a project chat.
    Persists both the user question and the AI answer.
    """

    def __init__(
        self,
        project_repository: IProjectRepository,
        message_repository: IProjectMessageRepository
    ):
        self.project_repository = project_repository
        self.message_repository = message_repository

    async def execute(
        self,
        project_id: int,
        user_id: int,
        question: str,
        sender_name: str
    ) -> Tuple[ProjectMessage, ProjectMessage]:
        """
        Ask the AI assistant a question and persist both messages.

        Returns:
            Tuple of (user_message, ai_message).

        Raises:
            EntityNotFoundError: If project not found.
            PermissionDeniedError: If user is not a project member.
            ValueError: If OpenAI API key is not configured.
        """
        if not settings.openai_api_key:
            raise ValueError(
                "OpenAI API key not configured. Set OPENAI_API_KEY environment variable."
            )

        project = await self.project_repository.get_by_id(project_id)
        if not project:
            raise EntityNotFoundError("Project", project_id)

        member = await self.project_repository.get_member(project_id, user_id)
        if not member and not project.is_owner(user_id):
            raise PermissionDeniedError("Only project members can use the AI assistant")

        # Persist the user's question
        user_message = await self.message_repository.create(ProjectMessage(
            project_id=project_id,
            user_id=user_id,
            content=question.strip(),
            message_type='user',
            sender_name=sender_name
        ))

        # Build conversation history (last 30 messages for context)
        history = await self.message_repository.list_by_project(
            project_id, skip=0, limit=30
        )

        # Build OpenAI messages list
        system_prompt = (
            f"Eres un asistente de investigación para el proyecto '{project.name}'. "
        )
        if project.description:
            system_prompt += f"Descripción: {project.description}. "
        system_prompt += (
            "Ayuda a los investigadores del Fondo Fotográfico Roberto Gerstmann "
            "con sus preguntas sobre el archivo, la investigación y el proyecto. "
            "Responde en español de manera clara y concisa."
        )

        openai_messages = [{"role": "system", "content": system_prompt}]
        for msg in history:
            role = "assistant" if msg.message_type == 'ai' else "user"
            openai_messages.append({"role": role, "content": msg.content})

        # Call OpenAI
        from openai import AsyncOpenAI
        client = AsyncOpenAI(api_key=settings.openai_api_key)

        response = await client.chat.completions.create(
            model=settings.openai_model,
            messages=openai_messages,
            max_tokens=settings.openai_max_tokens,
            temperature=settings.openai_temperature
        )

        ai_content = response.choices[0].message.content or "No se pudo generar una respuesta."

        # Persist AI response
        ai_message = await self.message_repository.create(ProjectMessage(
            project_id=project_id,
            user_id=user_id,
            content=ai_content,
            message_type='ai',
            sender_name='Asistente IA'
        ))

        return user_message, ai_message
