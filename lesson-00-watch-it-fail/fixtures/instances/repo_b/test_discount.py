from discount import apply_discount

def test_discount():
    assert apply_discount(200, 10) == 180

if __name__ == "__main__":
    test_discount()
    print("OK")
