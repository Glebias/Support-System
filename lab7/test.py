import pytest
from main import (
    diag_index_to_coords,
    DiagMatrixProcessor,
    f4, f6, f9, f11,
    DiagMatrixProcessor,
    parse_binary_matrix,
    generate_test_matrix
)

def test_diag_index_to_coords_invalid():
    with pytest.raises(IndexError):
        diag_index_to_coords(-1, 3)
    with pytest.raises(IndexError):
        diag_index_to_coords(9, 3)

@pytest.mark.parametrize("x,y,expected", [
    (0, 0, 0),
    (0, 1, 0),
    (1, 0, 1),
    (1, 1, 0),
])
def test_f4(x, y, expected):
    assert f4(x, y) == expected

@pytest.mark.parametrize("x,y,expected", [
    (0, 0, 0),
    (0, 1, 1),
    (1, 0, 1),
    (1, 1, 0),
])
def test_f6(x, y, expected):
    assert f6(x, y) == expected

@pytest.mark.parametrize("x,y,expected", [
    (0, 0, 1),
    (0, 1, 0),
    (1, 0, 0),
    (1, 1, 1),
])
def test_f9(x, y, expected):
    assert f9(x, y) == expected

@pytest.mark.parametrize("x,y,expected", [
    (0, 0, 1),
    (0, 1, 1),
    (1, 0, 0),
    (1, 1, 1),
])
def test_f11(x, y, expected):
    assert f11(x, y) == expected


# === Тесты для DiagMatrixProcessor ===

def test_get_word():
    matrix = [
        [0, 0],
        [1, 1],
        [0, 0],
        [1, 1],
    ]
    processor = DiagMatrixProcessor(matrix)
    word = processor.get_word(col=0, start_row=0)
    assert isinstance(word, int)


def test_update_matrix_from_word():
    matrix = [[0] * 2 for _ in range(16)]
    processor = DiagMatrixProcessor(matrix)
    word = 0b1010101010101010
    processor.update_matrix_from_word(col=1, start_row=0, word=word)

    for i in range(16):
        expected_bit = (word >> (15 - i)) & 1
        assert processor.mat[i][1] == expected_bit


def test_process():
    matrix = [[0, 1], [1, 0]]
    processor = DiagMatrixProcessor(matrix)
    result = processor.process(0, 1, f6)
    assert isinstance(result, list)
    assert all(isinstance(k, int) and isinstance(v, int) for k, v in result)


def test_add_fields_with_v():
    matrix = generate_test_matrix()
    processor = DiagMatrixProcessor(matrix)
    before_word = processor.get_word(2, 3)
    processor.add_fields_with_v(v_value=0b101)
    after_word = processor.get_word(2, 3)
    assert before_word != after_word


def test_execute_variant3():
    matrix = generate_test_matrix()
    processor = DiagMatrixProcessor(matrix)
    result = processor.execute_variant3(0, 1, 0b101)
    assert 'f6' in result
    assert 'f9' in result
    assert 'f4' in result
    assert 'f11' in result
    assert isinstance(result['f6'], list)


def test_get_sorted_words():
    matrix = [[0]*16 for _ in range(16)]
    processor = DiagMatrixProcessor(matrix)
    words = processor.get_sorted_words()
    assert len(words) == 256
    assert words == sorted(words)

def test_parse_binary_matrix_invalid_rows():
    input_str = "\n".join(["1 0 1"] * 17)  # 17 строк
    with pytest.raises(ValueError):
        parse_binary_matrix(input_str)

def test_parse_binary_matrix_invalid_bits():
    input_str = "1 0 1\n0 1"  # Вторая строка слишком короткая
    with pytest.raises(ValueError):
        parse_binary_matrix(input_str)

def test_select_and_sum_fields_with_v():
    # Создаем тестовую матрицу 4x4
    matrix = [
        [0] * 16 for _ in range(16)
    ]

    # Устанавливаем несколько слов с V=5 (биты 13-15 = 101)
    # Для упрощения: используем только 1 слово на позиции col=0, start_row=0

    def set_bits(word, bit_start, length, value):
        """Устанавливает определённые биты в слове"""
        mask = ((1 << length) - 1) << bit_start
        word &= ~mask
        word |= (value << bit_start) & mask
        return word

    # Собираем слово
    test_word = 0
    test_word = set_bits(test_word, 13, 3, 0b101)  # V = 5
    test_word = set_bits(test_word, 10, 3, 0b011)  # A = 3
    test_word = set_bits(test_word, 7, 3, 0b100)   # B = 4

    # Записываем его в матрицу
    processor = DiagMatrixProcessor(matrix)
    processor.update_matrix_from_word(0, 0, test_word)

    # Вызываем тестируемый метод
    result = processor.select_and_sum_fields_with_v(v_value=0b101)

    # Проверяем результат
    assert len(result) == 2
    index, sum_ab = result[0]
    assert index == 0  # col=0, start_row=0 => index=0*4+0=0
    assert sum_ab == 7  # 3 + 4 = 7