import pytest
from convertations import *
from binary_operations import sum, subtraction, binary_subtract, multiplication, binary_divide, float_sum_by_standart

def test_sum():
    assert sum(3, 5) == to_additive_code(8)
    assert sum(7, 2) == to_additive_code(9)

def test_subtraction():
    assert subtraction(5, 6) == to_additive_code(-1)
    assert subtraction(10, 52) == to_additive_code(-42)
    assert subtraction(60, 52) == to_additive_code(8)

def test_binary_subtract():
    assert binary_subtract("1010", "0101") == "0101"
    assert binary_subtract("1100", "0011") == "1001"

def test_multiplication():
    assert multiplication(3, 2) == to_forward_code(3*2)
    assert multiplication(4, 5) == to_forward_code(4*5)
    assert multiplication(12, 7) == to_forward_code(12*7)

def test_binary_divide():
    assert binary_divide(10, 2) == decimal_to_binary_fixed_point(5)
    assert binary_divide(10, 3) == decimal_to_binary_fixed_point(10/3)

def test_float_sum_by_standart():
    assert float_sum_by_standart(1.5, 2.5) == convert_digit_by_standart(4.0)
    assert float_sum_by_standart(3.12, 13.1) == convert_digit_by_standart(16.22)

if __name__ == "__main__":
    pytest.main()