"""
Unit tests for _parse_value in ApproveContributionUseCase.
Tests the pure parsing logic without requiring DB or async context.
"""

import pytest
from datetime import date

from app.features.contributions.application.approve_contribution_usecase import _parse_value
from app.shared.domain.exceptions import ValidationError
from app.features.taxonomy.infrastructure.persistence.taxonomy_model import (
    DateType, LocationType, SettingType, ConservationState,
)


class TestParseValueFloatFields:

    def test_latitude_parses_valid_float(self):
        assert _parse_value("latitude", "23.5") == 23.5

    def test_longitude_parses_negative_float(self):
        assert _parse_value("longitude", "-70.123") == -70.123

    def test_location_radius_parses_integer_string(self):
        assert _parse_value("location_radius_km", "5") == 5.0

    def test_latitude_invalid_raises_validation_error(self):
        with pytest.raises(ValidationError, match="no es un número válido"):
            _parse_value("latitude", "not-a-number")

    def test_longitude_empty_raises_validation_error(self):
        with pytest.raises(ValidationError):
            _parse_value("longitude", "")


class TestParseValueDateFields:

    def test_precise_date_parses_iso_format(self):
        result = _parse_value("precise_date", "1928-03-15")
        assert result == date(1928, 3, 15)

    def test_date_from_parses_correctly(self):
        result = _parse_value("date_from", "1920-01-01")
        assert result == date(1920, 1, 1)

    def test_date_to_parses_correctly(self):
        result = _parse_value("date_to", "1950-12-31")
        assert result == date(1950, 12, 31)

    def test_invalid_date_raises_validation_error(self):
        with pytest.raises(ValidationError, match="no es una fecha válida"):
            _parse_value("precise_date", "15/03/1928")

    def test_partial_date_raises_validation_error(self):
        with pytest.raises(ValidationError):
            _parse_value("date_from", "1928-03")


class TestParseValueEnumFields:

    def test_date_type_valid_value(self):
        result = _parse_value("date_type", DateType.PRECISE.value)
        assert result == DateType.PRECISE

    def test_location_type_valid_value(self):
        result = _parse_value("location_type", LocationType.APPROXIMATE.value)
        assert result == LocationType.APPROXIMATE

    def test_setting_type_valid_value(self):
        result = _parse_value("setting_type", SettingType.URBAN.value)
        assert result == SettingType.URBAN

    def test_conservation_state_valid_value(self):
        result = _parse_value("conservation_state", ConservationState.PRISTINE.value)
        assert result == ConservationState.PRISTINE

    def test_invalid_enum_value_raises_validation_error(self):
        with pytest.raises(ValidationError, match="no es válido para date_type"):
            _parse_value("date_type", "invalid_value")

    def test_invalid_enum_error_includes_valid_options(self):
        with pytest.raises(ValidationError, match="Opciones:"):
            _parse_value("location_type", "moon")


class TestParseValueStringFields:

    def test_unknown_field_returns_raw_string(self):
        assert _parse_value("geographic_location", "Antofagasta") == "Antofagasta"

    def test_description_field_passthrough(self):
        assert _parse_value("date_hypothesis", "Circa 1930") == "Circa 1930"

    def test_empty_string_passthrough_for_text_fields(self):
        assert _parse_value("landscape_features", "") == ""
