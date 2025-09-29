"""
Basic tests that don't require your app - they verify pytest works
"""
def test_addition():
    assert 1 + 1 == 2

def test_string_operations():
    assert "hello".upper() == "HELLO"
    assert " world".strip() == "world"

def test_list_operations():
    numbers = [1, 2, 3]
    assert len(numbers) == 3
    assert sum(numbers) == 6

def test_dictionary():
    person = {"name": "John", "age": 30}
    assert person["name"] == "John"
    assert "age" in person
