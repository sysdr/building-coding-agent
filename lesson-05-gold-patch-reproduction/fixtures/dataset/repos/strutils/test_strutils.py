import strutils


def test_upper():
    assert strutils.upper("ok") == "OK"
