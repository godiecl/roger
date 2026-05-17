"""
Unit tests for generate_timeline domain entities.
"""

import pytest
from datetime import datetime

from app.features.generate_timeline.domain.timeline import (
    Timeline, TimelineEvent, TimelineAxis, EventType, SourceType,
)


def make_event(
    axis=TimelineAxis.BIOGRAPHICAL,
    source_type=SourceType.VEROSIMIL,
    event_type=EventType.TRAVEL,
    year=1928,
):
    return TimelineEvent(
        date_label="Marzo 1928",
        title="Viaje a Antofagasta",
        description="Gerstmann llega al norte de Chile",
        axis=axis,
        event_type=event_type,
        source_type=source_type,
        year=year,
    )


def make_timeline(events=None, **kwargs):
    return Timeline(
        photograph_id=1,
        events=events or [],
        provider="groq/llama-3.3-70b",
        context_summary="Contexto histórico de Chile en 1928.",
        generation_time_ms=2100,
        **kwargs,
    )


class TestTimelineAxis:

    def test_enum_values(self):
        assert TimelineAxis.BIOGRAPHICAL == "biographical"
        assert TimelineAxis.HISTORICAL == "historical"
        assert TimelineAxis.EXPEDITION == "expedition"


class TestEventType:

    def test_all_expected_types_exist(self):
        types = {e.value for e in EventType}
        assert "travel" in types
        assert "historical" in types
        assert "political" in types
        assert "cultural" in types
        assert "other" in types


class TestSourceType:

    def test_veraz_value(self):
        assert SourceType.VERAZ == "veraz"

    def test_verosimil_value(self):
        assert SourceType.VEROSIMIL == "verosimil"


class TestTimelineEvent:

    def test_create_event(self):
        event = make_event()
        assert event.title == "Viaje a Antofagasta"
        assert event.axis == TimelineAxis.BIOGRAPHICAL
        assert event.source_type == SourceType.VEROSIMIL
        assert event.year == 1928

    def test_event_without_year(self):
        event = TimelineEvent(
            date_label="Circa 1920s",
            title="Período de viajes",
            description="Etapa inicial de expediciones",
            axis=TimelineAxis.EXPEDITION,
            event_type=EventType.TRAVEL,
            source_type=SourceType.VEROSIMIL,
            year=None,
        )
        assert event.year is None


class TestTimeline:

    def test_events_by_axis_returns_matching(self):
        bio = make_event(axis=TimelineAxis.BIOGRAPHICAL)
        hist = make_event(axis=TimelineAxis.HISTORICAL)
        exp = make_event(axis=TimelineAxis.EXPEDITION)
        tl = make_timeline(events=[bio, hist, exp])

        assert tl.events_by_axis(TimelineAxis.BIOGRAPHICAL) == [bio]
        assert tl.events_by_axis(TimelineAxis.HISTORICAL) == [hist]
        assert tl.events_by_axis(TimelineAxis.EXPEDITION) == [exp]

    def test_events_by_axis_returns_empty_when_no_match(self):
        bio = make_event(axis=TimelineAxis.BIOGRAPHICAL)
        tl = make_timeline(events=[bio])
        assert tl.events_by_axis(TimelineAxis.HISTORICAL) == []

    def test_verified_events_returns_only_veraz(self):
        veraz = make_event(source_type=SourceType.VERAZ)
        verosimil = make_event(source_type=SourceType.VEROSIMIL)
        tl = make_timeline(events=[veraz, verosimil])

        verified = tl.verified_events()
        assert len(verified) == 1
        assert verified[0].source_type == SourceType.VERAZ

    def test_verified_events_empty_when_all_verosimil(self):
        tl = make_timeline(events=[make_event(source_type=SourceType.VEROSIMIL)])
        assert tl.verified_events() == []

    def test_approve_sets_fields(self):
        tl = make_timeline()
        assert tl.is_approved is False
        assert tl.approved_by is None
        assert tl.approved_at is None

        tl.approve(user_id=7)

        assert tl.is_approved is True
        assert tl.approved_by == 7
        assert isinstance(tl.approved_at, datetime)

    def test_approve_records_correct_user(self):
        tl = make_timeline()
        tl.approve(user_id=42)
        assert tl.approved_by == 42

    def test_default_not_approved(self):
        tl = make_timeline()
        assert tl.is_approved is False

    def test_events_by_axis_multiple_in_same_axis(self):
        bio1 = make_event(axis=TimelineAxis.BIOGRAPHICAL)
        bio2 = make_event(axis=TimelineAxis.BIOGRAPHICAL)
        hist = make_event(axis=TimelineAxis.HISTORICAL)
        tl = make_timeline(events=[bio1, bio2, hist])

        result = tl.events_by_axis(TimelineAxis.BIOGRAPHICAL)
        assert len(result) == 2
