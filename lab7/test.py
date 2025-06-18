import pytest
import random
from main import (
    f4, f6, f9, f11,
    build_matrix, print_matrix,
    get_word, set_word,
    read_addressed_column, set_addressed_column,
    execute_log_operations,
    compare_binary,
    selection_sort_bin, selection_sort,
    process_bin16, sum_by_key
)

def test_f4():
    assert f4(0, 0) == 0
    assert f4(0, 1) == 1
    assert f4(1, 0) == 0
    assert f4(1, 1) == 0


def test_f6():
    assert f6(0, 0) == 0
    assert f6(0, 1) == 1
    assert f6(1, 0) == 1
    assert f6(1, 1) == 0


def test_f9():
    assert f9(0, 0) == 1
    assert f9(0, 1) == 0
    assert f9(1, 0) == 0
    assert f9(1, 1) == 1


def test_f11():
    assert f11(0, 0) == 1
    assert f11(0, 1) == 0
    assert f11(1, 0) == 1
    assert f11(1, 1) == 1

def test_build_matrix_default():
    random.seed(0)
    mat = build_matrix()
    assert len(mat) == 16
    assert all(len(row) == 16 for row in mat)
    for row in mat:
        for val in row:
            assert val in (0, 1)


def test_build_matrix_custom():
    random.seed(1)
    mat = build_matrix(4)
    assert len(mat) == 4
    assert all(len(row) == 4 for row in mat)
    for row in mat:
        for val in row:
            assert val in (0, 1)

def test_print_matrix(capsys):
    mat = [[1, 0], [0, 1]]
    print_matrix(mat)
    captured = capsys.readouterr()
    assert captured.out == "1 0\n0 1\n"

def test_get_set_word():
    mat = [[0,1,0],[1,1,1],[0,1,1]]
    assert get_word(mat, 1) == [1, 1, 1]
    new_word = [1,0,0]
    mat2 = set_word([row[:] for row in mat], 0, new_word)
    assert get_word(mat2, 0) == new_word

def test_read_set_addressed_column():
    mat = [[0,1,2],[3,4,5],[6,7,8]]
    assert read_addressed_column(mat, 1) == [3, 7, 2]
    new_col = [8,9,10]
    mat2 = set_addressed_column([row[:] for row in mat], 1, new_col)
    assert read_addressed_column(mat2, 1) == new_col

def test_execute_log_operations():
    mat = [[0,1],[1,1]]
    mat2 = execute_log_operations(f6, 0, 1, 0, [row[:] for row in mat])
    assert get_word(mat2, 0) == [1, 0]

@pytest.mark.parametrize("s,a,expected", [
    ([1,0,1], [1,1,0], (False, True)),  # s < a
    ([0,1], [0,1], (False, False)),      # equal
    ([1,1,0], [1,0,1], (True, False)),  # s > a
])
def test_compare_binary(s, a, expected):
    assert compare_binary(s, a) == expected

def test_selection_sort_bin():
    nums = [[1,0],[0,1],[1,1]]
    sorted_nums = selection_sort_bin(nums.copy())
    assert sorted_nums == [[0,1],[1,0],[1,1]]

def test_selection_sort():
    mat = [
        [0,0,0,0,0,0],
        [0,1,0,0,1,1],
        [0,0,0,0,1,1],
        [1,0,0,0,0,1],
        [1,1,1,1,1,0],
        [1,0,0,0,1,1],
    ]
    sorted_mat = selection_sort([row[:] for row in mat])
    expected = [
        [0,0,0,1,1,1],
        [0,0,0,0,1,0],
        [0,0,0,0,1,1],
        [1,1,1,1,0,1],
        [1,0,0,0,1,0],
        [1,0,0,0,0,1],
    ]
    assert sorted_mat == expected

def test_sum_by_key_zero_matrix(capsys):
    mat = [[0]*16 for _ in range(16)]
    key = [0,0,0]
    mat2 = sum_by_key([row[:] for row in mat], key)
    assert mat2 == mat
    captured = capsys.readouterr()
    assert captured.out.count("Слово:") == 16