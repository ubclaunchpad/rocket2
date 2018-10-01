"""Sample unit test."""


# see https://docs.pytest.org/en/latest/
def inc(x):
    """
    Increment the given number by 1.

    :param x: Number to increment
    :return: Incremented number
    """
    return x + 1


def test_answer():
    """Test the functionality of `inc`."""
    assert inc(4) == 5
