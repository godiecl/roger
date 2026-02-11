"""
Search service adapter implementation
"""
from typing import List, Dict
from sqlalchemy import select, func, or_, and_
from sqlalchemy.ext.asyncio import AsyncSession
import structlog

from app.features.search_filter.domain.search_port import SearchPort
from app.features.search_filter.domain.search_query import SearchQuery
from app.features.search_filter.domain.search_result import SearchResult
from app.features.view_images.domain.image import Image
from app.features.view_images.infrastructure.persistence.image_model import ImageModel
from app.infrastructure.rag.vector_stores.chroma_store import ChromaVectorStore

logger = structlog.get_logger()


class SearchService(SearchPort):
    """
    Search service adapter that implements SearchPort.
    Combines traditional database queries with semantic search.
    """

    def __init__(self, db_session: AsyncSession, vector_store: ChromaVectorStore = None):
        """
        Initialize the search service.

        Args:
            db_session: Database session
            vector_store: ChromaDB vector store for semantic search
        """
        self.db_session = db_session
        self.vector_store = vector_store

    async def search(
        self,
        query: SearchQuery,
        skip: int = 0,
        limit: int = 100
    ) -> SearchResult:
        """
        Perform filtered search using database queries.
        """
        # Build query
        stmt = select(ImageModel)

        # Apply filters
        conditions = []

        if query.only_public:
            conditions.append(ImageModel.is_public == True)

        if query.query_text:
            # Text search in title, description, location
            search_term = f"%{query.query_text}%"
            conditions.append(
                or_(
                    ImageModel.title.ilike(search_term),
                    ImageModel.description.ilike(search_term),
                    ImageModel.location.ilike(search_term)
                )
            )

        if query.year_from:
            conditions.append(ImageModel.year >= query.year_from)

        if query.year_to:
            conditions.append(ImageModel.year <= query.year_to)

        if query.locations:
            location_conditions = [
                ImageModel.location.ilike(f"%{loc}%") for loc in query.locations
            ]
            conditions.append(or_(*location_conditions))

        if query.author:
            conditions.append(ImageModel.author.ilike(f"%{query.author}%"))

        # TODO: Add tags filtering when we implement proper JSON queries

        if conditions:
            stmt = stmt.where(and_(*conditions))

        # Get total count
        count_stmt = select(func.count()).select_from(stmt.subquery())
        total_result = await self.db_session.execute(count_stmt)
        total_count = total_result.scalar() or 0

        # Apply pagination
        stmt = stmt.offset(skip).limit(limit)

        # Execute query
        result = await self.db_session.execute(stmt)
        image_models = result.scalars().all()

        # Convert to domain entities
        images = [self._model_to_entity(model) for model in image_models]

        return SearchResult(
            images=images,
            total_count=total_count,
            query=query.query_text or "",
            search_type="keyword"
        )

    async def semantic_search(
        self,
        query_text: str,
        limit: int = 10,
        only_public: bool = True
    ) -> SearchResult:
        """
        Perform semantic search using vector embeddings.
        """
        if not self.vector_store:
            logger.warning("Vector store not available, falling back to keyword search")
            # Fallback to keyword search
            query = SearchQuery(
                query_text=query_text,
                only_public=only_public,
                semantic_search=False
            )
            return await self.search(query, skip=0, limit=limit)

        try:
            # Query vector store
            results = await self.vector_store.similarity_search(
                collection_name="images",
                query_text=query_text,
                n_results=limit
            )

            # Extract image IDs and scores
            image_ids = [int(doc["metadata"]["image_id"]) for doc in results]
            scores = [doc["score"] for doc in results]

            # Fetch images from database
            stmt = select(ImageModel).where(ImageModel.id.in_(image_ids))
            if only_public:
                stmt = stmt.where(ImageModel.is_public == True)

            result = await self.db_session.execute(stmt)
            image_models = result.scalars().all()

            # Create a mapping for ordering
            id_to_model = {model.id: model for model in image_models}

            # Order results by relevance scores
            ordered_images = []
            ordered_scores = []
            for image_id, score in zip(image_ids, scores):
                if image_id in id_to_model:
                    ordered_images.append(self._model_to_entity(id_to_model[image_id]))
                    ordered_scores.append(score)

            return SearchResult(
                images=ordered_images,
                total_count=len(ordered_images),
                query=query_text,
                relevance_scores=ordered_scores,
                search_type="semantic"
            )

        except Exception as e:
            logger.error("Semantic search failed", error=str(e))
            # Fallback to keyword search
            query = SearchQuery(
                query_text=query_text,
                only_public=only_public,
                semantic_search=False
            )
            return await self.search(query, skip=0, limit=limit)

    async def get_facets(self, query: SearchQuery) -> dict:
        """
        Get faceted search results (aggregations).
        """
        facets = {
            "years": [],
            "locations": [],
            "authors": [],
            "total": 0
        }

        try:
            # Build base query with filters
            stmt = select(ImageModel)

            conditions = []
            if query.only_public:
                conditions.append(ImageModel.is_public == True)

            if conditions:
                stmt = stmt.where(and_(*conditions))

            # Get year facets
            year_stmt = (
                select(ImageModel.year, func.count(ImageModel.id))
                .select_from(stmt.subquery())
                .group_by(ImageModel.year)
                .order_by(ImageModel.year.desc())
            )
            year_result = await self.db_session.execute(year_stmt)
            facets["years"] = [
                {"year": year, "count": count}
                for year, count in year_result.all()
                if year is not None
            ]

            # Get location facets (top 20)
            location_stmt = (
                select(ImageModel.location, func.count(ImageModel.id))
                .select_from(stmt.subquery())
                .group_by(ImageModel.location)
                .order_by(func.count(ImageModel.id).desc())
                .limit(20)
            )
            location_result = await self.db_session.execute(location_stmt)
            facets["locations"] = [
                {"location": loc, "count": count}
                for loc, count in location_result.all()
                if loc is not None
            ]

            # Get author facets
            author_stmt = (
                select(ImageModel.author, func.count(ImageModel.id))
                .select_from(stmt.subquery())
                .group_by(ImageModel.author)
                .order_by(func.count(ImageModel.id).desc())
            )
            author_result = await self.db_session.execute(author_stmt)
            facets["authors"] = [
                {"author": author, "count": count}
                for author, count in author_result.all()
                if author is not None
            ]

            # Get total count
            count_stmt = select(func.count()).select_from(stmt.subquery())
            total_result = await self.db_session.execute(count_stmt)
            facets["total"] = total_result.scalar() or 0

        except Exception as e:
            logger.error("Failed to get facets", error=str(e))

        return facets

    def _model_to_entity(self, model: ImageModel) -> Image:
        """Convert SQLAlchemy model to domain entity."""
        return Image(
            id=model.id,
            title=model.title,
            file_path=model.file_path,
            description=model.description,
            year=model.year,
            location=model.location,
            author=model.author,
            tags=model.tags or [],
            collection_id=model.collection_id,
            metadata=model.metadata or {},
            is_public=model.is_public,
            created_at=model.created_at,
            updated_at=model.updated_at
        )
