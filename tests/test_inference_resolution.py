"""Mathematical design fixture, not an evaluation of any detector."""
import pytest

from check_inference_resolution import resolution


def test_conditions_do_not_multiply_independent_table_signs():
    result = resolution(4, 3)
    assert result["table_level"] == {"assignments": 16, "extreme": 1, "minimum_one_sided_p": 0.0625}
    assert result["naive_condition_level"]["assignments"] == 4096
    assert result["naive_condition_level"]["minimum_one_sided_p"] == 1 / 4096
    assert resolution(4, 1)["table_level"] == result["table_level"]


def test_invalid_enumeration_dimensions_fail():
    for args in ((0, 3), (True, 3), (4, 0), (21, 1)):
        with pytest.raises(ValueError):
            resolution(*args)
