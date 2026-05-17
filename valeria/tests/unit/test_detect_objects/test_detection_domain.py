"""
Unit tests for detect_objects domain entities.
"""

import pytest
from app.features.detect_objects.domain.detection import (
    Detection, DetectedObject, DetectionStatus, ObjectCategory,
)


def make_object(label="person", category=ObjectCategory.PERSON, confidence=0.95):
    return DetectedObject(label=label, category=category, confidence=confidence)


def make_detection(objects=None, **kwargs):
    kwargs.setdefault("provider", "claude-vision")
    return Detection(
        photograph_id=1,
        objects=objects if objects is not None else [],
        scene_description="A street in Antofagasta",
        detection_time_ms=1200,
        **kwargs,
    )


class TestDetectionStatus:

    def test_enum_values(self):
        assert DetectionStatus.PENDING == "pending"
        assert DetectionStatus.COMPLETED == "completed"
        assert DetectionStatus.FAILED == "failed"


class TestObjectCategory:

    def test_all_expected_categories_exist(self):
        categories = {c.value for c in ObjectCategory}
        assert "person" in categories
        assert "building" in categories
        assert "vehicle" in categories
        assert "vegetation" in categories
        assert "other" in categories


class TestDetectedObject:

    def test_create_with_required_fields(self):
        obj = DetectedObject(
            label="hombre con sombrero",
            category=ObjectCategory.PERSON,
            confidence=0.92,
        )
        assert obj.label == "hombre con sombrero"
        assert obj.category == ObjectCategory.PERSON
        assert obj.confidence == 0.92
        assert obj.description is None
        assert obj.id is None

    def test_create_with_optional_description(self):
        obj = DetectedObject(
            label="edificio",
            category=ObjectCategory.BUILDING,
            confidence=0.88,
            description="Estructura de adobe de dos pisos",
        )
        assert obj.description == "Estructura de adobe de dos pisos"


class TestDetection:

    def test_object_count_empty(self):
        d = make_detection(objects=[])
        assert d.object_count() == 0

    def test_object_count_multiple(self):
        objects = [
            make_object("person", ObjectCategory.PERSON),
            make_object("horse", ObjectCategory.ANIMAL),
            make_object("cart", ObjectCategory.VEHICLE),
        ]
        d = make_detection(objects=objects)
        assert d.object_count() == 3

    def test_objects_by_category_returns_matching(self):
        person1 = make_object("hombre", ObjectCategory.PERSON)
        person2 = make_object("mujer", ObjectCategory.PERSON)
        animal = make_object("perro", ObjectCategory.ANIMAL)
        d = make_detection(objects=[person1, person2, animal])

        persons = d.objects_by_category(ObjectCategory.PERSON)
        assert len(persons) == 2
        assert all(o.category == ObjectCategory.PERSON for o in persons)

    def test_objects_by_category_returns_empty_when_no_match(self):
        d = make_detection(objects=[make_object("tree", ObjectCategory.VEGETATION)])
        assert d.objects_by_category(ObjectCategory.VEHICLE) == []

    def test_default_status_is_completed(self):
        d = make_detection()
        assert d.status == DetectionStatus.COMPLETED

    def test_failed_status_can_be_set(self):
        d = make_detection(status=DetectionStatus.FAILED)
        assert d.status == DetectionStatus.FAILED

    def test_provider_stored_correctly(self):
        d = make_detection(provider="gpt-4v")
        assert d.provider == "gpt-4v"
