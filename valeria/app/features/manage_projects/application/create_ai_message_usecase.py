"""
Create AI message use case.

Este use case es completamente agnóstico al proveedor de LLM:
solo depende de ILLMProvider, nunca de Groq, OpenAI ni Anthropic.
El proveedor se inyecta desde fuera (infraestructura).
"""

from typing import Tuple

from app.features.manage_projects.domain.project_message import (
    ProjectMessage,
    IProjectMessageRepository
)
from app.features.manage_projects.domain.project_port import IProjectRepository
from app.shared.domain.exceptions import EntityNotFoundError, PermissionDeniedError
from app.shared.ports.llm_provider import ILLMProvider


class CreateAiMessageUseCase:
    """
    Consulta al asistente IA dentro del chat de un proyecto
    y persiste tanto la pregunta del usuario como la respuesta.
    """

    def __init__(
        self,
        project_repository: IProjectRepository,
        message_repository: IProjectMessageRepository,
        llm_provider: ILLMProvider
    ):
        self.project_repository = project_repository
        self.message_repository = message_repository
        self.llm = llm_provider

    async def execute(
        self,
        project_id: int,
        user_id: int,
        question: str,
        sender_name: str,
        context: str | None = None
    ) -> Tuple[ProjectMessage, ProjectMessage]:
        """
        Pregunta al LLM y persiste ambos mensajes (pregunta + respuesta).

        Returns:
            Tuple (user_message, ai_message).
        """
        project = await self.project_repository.get_by_id(project_id)
        if not project:
            raise EntityNotFoundError("Project", project_id)

        member = await self.project_repository.get_member(project_id, user_id)
        if not member and not project.is_owner(user_id):
            raise PermissionDeniedError("Solo los miembros del proyecto pueden usar el asistente IA.")

        # Persistir pregunta del usuario
        user_message = await self.message_repository.create(ProjectMessage(
            project_id=project_id,
            user_id=user_id,
            content=question.strip(),
            message_type='user',
            sender_name=sender_name
        ))

        # Construir el system prompt
        system_prompt = (
            "Eres un asistente de investigación especializado en colecciones patrimoniales. "
            "Tu rol es apoyar a investigadores, curadores y colaboradores en el estudio, descripción "
            "y análisis de fondos documentales, fotográficos, audiovisuales y archivísticos.\n\n"
            "PRINCIPIOS DE TRABAJO:\n"
            "- Prioriza la precisión histórica y documental por sobre la especulación.\n"
            "- Cuando no tengas certeza sobre un dato, indícalo explícitamente en lugar de inventarlo.\n"
            "- Ayuda a contextualizar piezas dentro de su época, territorio y colección.\n"
            "- Responde siempre en el idioma en que te hablen, de forma clara y concisa.\n\n"
            f"PROYECTO ACTUAL: '{project.name}'."
        )
        if project.description:
            system_prompt += f"\nDescripción: {project.description}."
        if project.ai_instructions:
            system_prompt += (
                f"\n\nCONTEXTO ESPECÍFICO DEL PROYECTO "
                f"(tiene prioridad sobre cualquier otra consideración):\n{project.ai_instructions}"
            )
        if context:
            system_prompt += f"\n\nCONTEXTO ADICIONAL (documento subido por el usuario):\n{context}"

        # Historial de conversación (últimos 30 mensajes)
        history = await self.message_repository.list_by_project(project_id, skip=0, limit=30)
        messages = [{"role": "system", "content": system_prompt}]
        for msg in history:
            role = "assistant" if msg.message_type == "ai" else "user"
            messages.append({"role": role, "content": msg.content})

        # Llamar al proveedor (agnóstico)
        ai_content = await self.llm.complete(messages)
        if not ai_content:
            ai_content = "No se pudo generar una respuesta."

        # Persistir respuesta IA
        ai_message = await self.message_repository.create(ProjectMessage(
            project_id=project_id,
            user_id=user_id,
            content=ai_content,
            message_type='ai',
            sender_name='Asistente IA'
        ))

        return user_message, ai_message
