import pytest
from main import get_variables, generate_truth_table, build_sdnf_sknf, build_index_form

# Тестовые кейсы с использованием всех операторов
TEST_CASES = [
    (
        # Выражение 1: Импликация + Эквивалентность + NOT
        "(a→b)↔!c",
        ['a', 'b', 'c'],
        [
            ([0,0,0], 1),
            ([0,0,1], 0),
            ([0,1,0], 1),
            ([0,1,1], 0),
            ([1,0,0], 0),
            ([1,0,1], 1),
            ([1,1,0], 1),
            ([1,1,1], 0)
        ],
        "(!a & !b & !c) | (!a & b & !c) | (a & !b & c) | (a & b & !c)",
        "(a | b | !c) & (a | !b | !c) & (!a | b | c) & (!a | !b | !c)",
        0b10100110
    ),
    (
        # Выражение 2: OR + AND + Импликация + NOT
        "(a|b)&(b→!c)",
        ['a', 'b', 'c'],
        [
            ([0,0,0], 0),
            ([0,0,1], 0),
            ([0,1,0], 1),
            ([0,1,1], 0),
            ([1,0,0], 1),
            ([1,0,1], 1),
            ([1,1,0], 1),
            ([1,1,1], 0)
        ],
        "(!a & b & !c) | (a & !b & !c) | (a & !b & c) | (a & b & !c)",
        "(a | b | c) & (a | b | !c) & (a | !b | !c) & (!a | !b | !c)",
        0b00101110
    ),
    (
        # Выражение 3: NOT + AND + OR + Эквивалентность
        "!(a&b)↔(c|a)",
        ['a', 'b', 'c'],
        [
            ([0,0,0], 0),
            ([0,0,1], 1),
            ([0,1,0], 0),
            ([0,1,1], 1),
            ([1,0,0], 1),
            ([1,0,1], 1),
            ([1,1,0], 0),
            ([1,1,1], 0)
        ],
        "(!a & !b & c) | (!a & b & c) | (a & !b & !c) | (a & !b & c)",
        "(a | b | c) & (a | !b | c) & (!a | !b | c) & (!a | !b | !c)",
        0b01011100
    )
]

@pytest.mark.parametrize("expr,variables,expected_truth,expected_sdnf,expected_sknf,expected_index", TEST_CASES)
def test_complex_expressions(expr, variables, expected_truth, expected_sdnf, expected_sknf, expected_index):
    # Проверка определения переменных
    detected_vars = get_variables(expr)
    assert detected_vars == variables, f"Ошибка в определении переменных. Ожидалось: {variables}, Получено: {detected_vars}"
    
    # Генерация таблицы истинности
    truth_table = generate_truth_table(expr, variables)
    assert len(truth_table) == 2**len(variables), "Неверное количество комбинаций"
    
    # Проверка результатов вычислений
    for (combo, res), (exp_combo, exp_res) in zip(truth_table, expected_truth):
        assert combo == exp_combo, f"Неверная комбинация: {combo} ≠ {exp_combo}"
        assert res == exp_res, f"Ошибка для {combo}: ожидалось {exp_res}, получено {res}"
    
    # Проверка нормальных форм
    sdnf, sknf, _, _ = build_sdnf_sknf(truth_table, variables)
    assert sdnf == expected_sdnf, f"СДНФ не совпадает:\nОжидалось: {expected_sdnf}\nПолучено: {sdnf}"
    assert sknf == expected_sknf, f"СКНФ не совпадает:\nОжидалось: {expected_sknf}\nПолучено: {sknf}"
    
    # Проверка индексной формы
    index = build_index_form(truth_table)
    assert index == expected_index, f"Индекс: {bin(index)} ≠ Ожидаемый: {bin(expected_index)}"

# Запуск: pytest -v test_logic.py