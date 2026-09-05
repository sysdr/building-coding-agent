import timeutils


def test_is_weekend():
    assert timeutils.is_weekend(6) is True
