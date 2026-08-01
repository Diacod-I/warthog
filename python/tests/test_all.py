import pytest
import warthog


def test_sum_as_string():
    assert warthog.sum_as_string(1, 1) == "2"
