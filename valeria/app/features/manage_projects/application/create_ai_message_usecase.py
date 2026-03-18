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
        sender_name: str,
        context: str | None = None
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
        use_groq = bool(settings.groq_api_key)
        if not use_groq and not settings.openai_api_key:
            raise ValueError(
                "No hay API key configurada. Agrega GROQ_API_KEY en el .env (gratis en console.groq.com) "
                "o OPENAI_API_KEY."
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
            "Eres un asistente de investigación especializado en el Fondo Fotográfico Robert Gerstmann. "
            "Tu rol es apoyar a investigadores, curadores y colaboradores que trabajan con el archivo fotográfico y cinematográfico de Gerstmann.\n\n"
            "CONTEXTO GENERAL SOBRE Robert GERSTMANN:\n"
            "Robert Gerstmann (1896–1964) fue un fotógrafo y cineasta alemán que documentó gran parte de Sudamérica, "
            "especialmente Chile y Bolivia, durante la primera mitad del siglo XX. "
            "Su profesión original era ingeniería eléctrica. Llegó a Sudamérica en 1924 y se instaló en Santiago de Chile en 1929. "
            "Recorrió Chile, Bolivia y otros países tomando miles de fotografías de paisajes, pueblos, ciudades y culturas indígenas. "
            "Su trabajo ayudó a mostrar el territorio sudamericano al mundo. "
            "Fotografió paisajes de todo Chile, desde el norte desértico hasta la Patagonia, y participó en expediciones "
            "a lugares poco documentados como Isla de Pascua, Juan Fernández y la Antártica. "
            "Entre sus publicaciones destacan: 'Chile: 280 grabados en cobre' (1932), 'Bolivia' (1928) y 'Chile en 235 cuadros' (1959). "
            "Se le considera uno de los primeros grandes fotógrafos documentales de Chile; sus imágenes ayudaron a construir "
            "la imagen visual del país en el siglo XX. "
            "Parte de su archivo fotográfico se conserva en instituciones chilenas, incluyendo material en el norte del país.\n\n"
            f"Estás asistiendo en el proyecto '{project.name}'. "
        )
        if project.description:
            system_prompt += f"Descripción del proyecto: {project.description}. "
        system_prompt += (
            "\nResponde siempre en el idioma que te hablen de manera clara y concisa. "
            "Cuando no tengas certeza sobre algún dato, indícalo explícitamente en lugar de inventar información."
        )
        if project.ai_instructions:
            system_prompt += (
                f"\n\nINSTRUCCIONES ESPECÍFICAS DEL PROYECTO "
                f"(Solo puedes responder especificamente de proyectos y estudios fotograficos con prioridad en el contexto general de Robert Gerstmann tienen prioridad sobre cualquier otra fuente de información):\n{project.ai_instructions}"
            )
        if context:
            system_prompt += f"\n\nCONTEXTO ADICIONAL (documento subido por el usuario):\n{context}"

        openai_messages = [{"role": "system", "content": system_prompt}]
        for msg in history:
            role = "assistant" if msg.message_type == 'ai' else "user"
            openai_messages.append({"role": role, "content": msg.content})

        # Use Groq if configured, otherwise fall back to OpenAI
        from openai import AsyncOpenAI
        if use_groq:
            client = AsyncOpenAI(
                api_key=settings.groq_api_key,
                base_url="https://api.groq.com/openai/v1"
            )
            model = settings.groq_model
            max_tokens = settings.groq_max_tokens
            temperature = settings.groq_temperature
        else:
            client = AsyncOpenAI(api_key=settings.openai_api_key)
            model = settings.openai_model
            max_tokens = settings.openai_max_tokens
            temperature = settings.openai_temperature

        response = await client.chat.completions.create(
            model=model,
            messages=openai_messages,
            max_tokens=max_tokens,
            temperature=temperature
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
