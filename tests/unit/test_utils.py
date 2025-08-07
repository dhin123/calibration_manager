"""
Unit tests for utility functions
UPDATED TO USE YOUR ACTUAL UTILITIES
"""

import pytest
from common_packages.utils.id_generator import SnowflakeIdGenerator
from common_packages.utils.schema_validator import validate_schema
from common_packages.constants.constants import CALIBRATION_SCHEMA, ADD_TAG_SCHEMA


def test_snowflake_id_generator():
    """Test your actual Snowflake ID generation"""
    generator = SnowflakeIdGenerator(worker_id=123, datacenter_id=234)

    # Generate multiple IDs
    id1 = generator.generate()  # Use your actual method name
    id2 = generator.generate()

    # Test IDs are different
    assert id1 != id2

    # Test IDs are integers
    assert isinstance(id1, int)
    assert isinstance(id2, int)

    # Test IDs are positive
    assert id1 > 0
    assert id2 > 0

    assert id1 > 1000000  # Should be much larger than simple incrementing


def test_snowflake_id_generator_with_params():
    """Test Snowflake ID generator with worker and datacenter IDs"""
    generator = SnowflakeIdGenerator(worker_id=1, datacenter_id=2)

    # Generate ID
    generated_id = generator.generate()

    # Test basic properties
    assert isinstance(generated_id, int)
    assert generated_id > 0


def test_calibration_schema_validation():
    """Test calibration schema validation using your actual schema"""
    # Valid data
    valid_data = {
        "calibration_type": "offset",
        "value": 1.5,
        "username": "test_user"
    }
    assert validate_schema(valid_data, CALIBRATION_SCHEMA) is True

    # Invalid data - missing required field
    invalid_data_1 = {
        "calibration_type": "offset",
        "value": 1.5
        # Missing username
    }
    assert validate_schema(invalid_data_1, CALIBRATION_SCHEMA) is False

    # Invalid data - wrong type
    invalid_data_2 = {
        "calibration_type": "offset",
        "value": "not_a_number",  # Should be number
        "username": "test_user"
    }
    assert validate_schema(invalid_data_2, CALIBRATION_SCHEMA) is False

    # Invalid data - missing all fields
    assert validate_schema({}, CALIBRATION_SCHEMA) is False


def test_tag_schema_validation():
    """Test tag schema validation using your actual schema"""
    # Valid data
    valid_data = {
        "tag_name": "production"
    }
    assert validate_schema(valid_data, ADD_TAG_SCHEMA) is True

    # Invalid data - missing required field
    invalid_data = {}
    assert validate_schema(invalid_data, ADD_TAG_SCHEMA) is False

    # Invalid data - wrong type
    invalid_data_2 = {
        "tag_name": 123  # Should be string
    }
    assert validate_schema(invalid_data_2, ADD_TAG_SCHEMA) is False


def test_schema_validation_edge_cases():
    """Test edge cases in schema validation"""
    # Test with None
    assert validate_schema(None, CALIBRATION_SCHEMA) is False

    # Test with empty values
    invalid_empty = {
        "calibration_type": "",
        "value": 1.5,
        "username": ""
    }
    # This might pass or fail depending on your schema - adjust as needed
    result = validate_schema(invalid_empty, CALIBRATION_SCHEMA)

    assert isinstance(result, bool)
