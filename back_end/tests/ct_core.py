import numpy as np
import pytest

from app.ct_core import convert_int64_to_float


def test_int64_in_dict():
    input_data = {"a": np.int64(42), "b": "string", "c": 3.14}
    expected_output = {"a": 42.0, "b": "string", "c": 3.14}
    assert convert_int64_to_float(input_data) == expected_output


def test_int64_in_list():
    input_data = [1, np.int64(2), 3.0]
    expected_output = [1.0, 2.0, 3.0]
    assert convert_int64_to_float(input_data) == expected_output


def test_nested_structures():
    input_data = {"list": [np.int64(1), {"nested_int": np.int64(2)}], "tuple": (np.int64(3), [np.int64(4)])}
    expected_output = {"list": [1.0, {"nested_int": 2.0}], "tuple": (3.0, [4.0])}
    assert convert_int64_to_float(input_data) == expected_output


def test_set():
    input_data = {np.int64(1), np.int64(2), 3}
    expected_output = {1.0, 2.0, 3.0}
    assert convert_int64_to_float(input_data) == expected_output


def test_tuple():
    input_data = (np.int64(1), "a", 2.0)
    expected_output = (1.0, "a", 2.0)
    assert convert_int64_to_float(input_data) == expected_output


def test_no_conversion_needed():
    input_data = {"a": "string", "b": 3.14}
    expected_output = {"a": "string", "b": 3.14}
    assert convert_int64_to_float(input_data) == expected_output


def test_numpy_array():
    input_data = np.array([np.int64(1), np.int64(2), 3])
    expected_output = np.array([1.0, 2.0, 3.0])
    result = convert_int64_to_float(input_data)
    np.testing.assert_array_equal(result, expected_output)


def test_mixed_types():
    input_data = [{"a": np.int64(1)}, (np.int64(2), [np.int64(3), "string"]), set([np.int64(4), 5])]
    expected_output = [{"a": 1.0}, (2.0, [3.0, "string"]), {4.0, 5.0}]
    assert convert_int64_to_float(input_data) == expected_output


def test_large_int():
    large_int = np.int64(1234567890123456789)
    expected_output = float(large_int)
    assert convert_int64_to_float(large_int) == expected_output


def test_non_int64_numpy_types():
    input_data = {"a": np.float64(3.14), "b": np.int32(42)}
    expected_output = {"a": 3.14, "b": 42}
    assert convert_int64_to_float(input_data) == expected_output


def test_custom_objects():
    class CustomObject:
        def __init__(self, value):
            self.value = value

    obj = CustomObject(np.int64(10))
    result = convert_int64_to_float(obj)
    assert result is obj


def test_none_value():
    input_data = {"a": None, "b": np.int64(1)}
    expected_output = {"a": None, "b": 1.0}
    assert convert_int64_to_float(input_data) == expected_output


def test_empty_structures():
    assert convert_int64_to_float({}) == {}
    assert convert_int64_to_float([]) == []
    assert convert_int64_to_float(set()) == set()
    assert convert_int64_to_float(()) == ()
