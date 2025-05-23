import pytest
from main import HashTable  # замени имя файла при необходимости

@pytest.fixture
def ht():
    return HashTable()

def test_insert_and_get(ht):
    ht.insert("AB", "Alpha")
    assert ht.get("AB") == "Alpha"

def test_update(ht):
    ht.insert("CD", "Charlie")
    ht.update("CD", "Delta")
    assert ht.get("CD") == "Delta"

def test_delete(ht):
    ht.insert("EF", "Echo")
    ht.delete("EF")
    assert ht.get("EF") is None

def test_get_missing_key(ht):
    assert ht.get("ZZ") is None

def test_update_missing_key(ht):
    with pytest.raises(KeyError):
        ht.update("GH", "Ghost")

def test_delete_missing_key(ht):
    with pytest.raises(KeyError):
        ht.delete("IJ")

def test_invalid_key_short(ht):
    with pytest.raises(ValueError):
        ht.insert("A", "TooShort")

def test_invalid_key_char(ht):
    with pytest.raises(ValueError):
        ht.insert("A1", "InvalidChar")

def test_collision_handling():
    ht = HashTable(table_size=4)  # маленький размер для коллизий
    ht._hash = lambda k: 0  # форсируем коллизию
    ht.insert("AA", "First")
    ht.insert("BB", "Second")
    ht.insert("CC", "Third")
    assert ht.get("AA") == "First"
    assert ht.get("BB") == "Second"
    assert ht.get("CC") == "Third"

def test_collision_update():
    ht = HashTable(table_size=4)
    ht._hash = lambda k: 0
    ht.insert("AA", "One")
    ht.insert("BB", "Two")
    ht.update("BB", "Updated")
    assert ht.get("BB") == "Updated"

def test_full_table():
    ht = HashTable(table_size=3)
    ht._hash = lambda k: 0
    ht.insert("AA", "One")
    ht.insert("BB", "Two")
    ht.insert("CC", "Three")
    with pytest.raises(Exception, match="Hash table is full"):
        ht.insert("DD", "Overflow")

def test_display_output(ht, capsys):
    ht.insert("AB", "Alpha")
    ht.display()
    captured = capsys.readouterr()
    assert "AB" in captured.out
    assert "Alpha" in captured.out

def test_invalid_characters():
    ht = HashTable()
    with pytest.raises(ValueError):
        ht._char_to_index("@")

def test_insert_overwrites_value(ht):
    ht.insert("AB", "Alpha")
    ht.insert("AB", "NewAlpha")
    assert ht.get("AB") == "NewAlpha"
