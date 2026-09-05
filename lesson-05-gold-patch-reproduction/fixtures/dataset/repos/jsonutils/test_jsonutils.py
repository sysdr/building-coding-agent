import jsonutils


def test_keys():
    assert jsonutils.keys({"a": 1, "b": 2}) == ["a", "b"]
