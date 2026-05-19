from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import List, Optional, Literal


class TimelineAxis(str, Enum):
    BIOGRAPHICAL = "biographical"   # Vida y viajes de Gerstmann
    HISTORICAL = "historical"       # Contexto mundial / latinoamericano en la época
    EXPEDITION = "expedition"       # Expedición o proyecto específico fotografiado


class EventType(str, Enum):
    TRAVEL = "travel"
    HISTORICAL = "historical"
    PERSONAL = "personal"
    POLITICAL = "political"
    CULTURAL = "cultural"
    NATURAL = "natural"
    OTHER = "other"


class SourceType(str, Enum):
    VERAZ = "veraz"         # Fuente primaria verificada
    VEROSIMIL = "verosimil" # Inferencia razonada por IA


@dataclass
class TimelineEvent:
    date_label: str          # ej. "Marzo 1928", "1920s", "circa 1930"
    title: str
    description: str
    axis: TimelineAxis
    event_type: EventType
    source_type: SourceType
    year: Optional[int] = None
    id: Optional[int] = None


@dataclass
class Timeline:
    """Línea de tiempo contextual generada para una fotografía específica."""
    photograph_id: int
    events: List[TimelineEvent]
    provider: str
    context_summary: str         # párrafo introductorio del contexto histórico
    generation_time_ms: int
    is_approved: bool = False
    approved_by: Optional[int] = None
    approved_at: Optional[datetime] = None
    id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def events_by_axis(self, axis: TimelineAxis) -> List[TimelineEvent]:
        return [e for e in self.events if e.axis == axis]

    def verified_events(self) -> List[TimelineEvent]:
        return [e for e in self.events if e.source_type == SourceType.VERAZ]

    def approve(self, user_id: int) -> None:
        self.is_approved = True
        self.approved_by = user_id
        self.approved_at = datetime.utcnow()


@dataclass
class CollectionClusterSummary:
    """Resumen de un cluster con su estimación temporal, para la narrativa de colección."""
    cluster_id: int
    label: str
    photograph_count: int
    centroid_photograph_id: Optional[int]
    year_representative: Optional[int]   # año mediana de las fotografías del cluster
    year_min: Optional[int]
    year_max: Optional[int]
    date_source: Literal["metadata", "rag", "none"]


@dataclass
class CollectionNarrative:
    """Narrativa temporal unificada de una colección completa, generada desde un clustering job."""
    job_id: int
    collection_narrative: str        # 3-5 párrafos describiendo el corpus
    temporal_arc: str                # 2-3 oraciones sobre el arco temporal
    thematic_threads: List[str]      # hilos temáticos recurrentes
    historical_significance: str     # párrafo sobre significado histórico
    ordered_clusters: List[CollectionClusterSummary]
    photograph_count: int
    provider: str
    generation_time_ms: int
    year_min: Optional[int] = None
    year_max: Optional[int] = None
    created_at: Optional[datetime] = None
