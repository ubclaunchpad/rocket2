# see https://docs.pytest.org/en/latest/
def inc(x):
    return x + 1


def test_answer():
    assert inc(4) == 5
