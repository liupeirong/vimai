from vimai import add_numbers


def test_add_numbers_returns_sum() -> None:
    assert add_numbers(2, 3) == 5
