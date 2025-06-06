import pytest
from main import get_variables, generate_truth_table, build_sdnf_sknf, build_index_form

TEST_CASES = [
    (
        # Выражение 1: (a→b)↔!c
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
        # Выражение 2: (a|b)&(b→!c)
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
        # Выражение 3: (a & b) | (c & d)
        "(a&b)|(c&d)",
        ['a', 'b', 'c', 'd'],
        [
            ([0,0,0,0], 0),
            ([0,0,0,1], 0),
            ([0,0,1,0], 0),
            ([0,0,1,1], 1),
            ([0,1,0,0], 0),
            ([0,1,0,1], 0),
            ([0,1,1,0], 0),
            ([0,1,1,1], 1),
            ([1,0,0,0], 0),
            ([1,0,0,1], 0),
            ([1,0,1,0], 0),
            ([1,0,1,1], 1),
            ([1,1,0,0], 1),
            ([1,1,0,1], 1),
            ([1,1,1,0], 1),
            ([1,1,1,1], 1)
        ],
        "(!a & !b & c & d) | (!a & b & c & d) | (a & !b & c & d) | (a & b & !c & !d) | (a & b & !c & d) | (a & b & c & !d) | (a & b & c & d)",
        "(a | b | c | d) & (a | b | c | !d) & (a | b | !c | d) & (a | !b | c | d) & (a | !b | c | !d) & (a | !b | !c | d) & (!a | b | c | d) & (!a | b | c | !d) & (!a | b | !c | d)",
        0b0001000100011111
    ),
    (
        # Выражение 4: !(a&b)↔(c|a)
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

@pytest.mark.parametrize(
    "expr,variables,expected_truth,expected_sdnf,expected_sknf,expected_index",
    TEST_CASES
)
def test_complex_expressions(
    expr, variables, expected_truth, expected_sdnf, expected_sknf, expected_index
):
    # Проверка списка переменных
    detected_vars = get_variables(expr)
    assert detected_vars == variables, (
        f"Ожидались переменные: {variables}, "
        f"получены: {detected_vars}"
    )

    # Генерация таблицы истинности
    truth_table = generate_truth_table(expr, variables)
    assert len(truth_table) == 2 ** len(variables), "Неверное число строк в таблице истинности"

    # Проверка результатов в таблице
    for (combo, res), (exp_combo, exp_res) in zip(truth_table, expected_truth):
        assert combo == exp_combo, f"Комбинация: {combo} != {exp_combo}"
        assert res == exp_res, f"Результат: {res} != {exp_res}"

    # Построение СДНФ и СКНФ
    sdnf, sknf, _, _ = build_sdnf_sknf(truth_table, variables)
    assert sdnf == expected_sdnf, (
        f"СДНФ:\nОжидалось: {expected_sdnf}\n"
        f"Получено: {sdnf}"
    )
    assert sknf == expected_sknf, (
        f"СКНФ:\nОжидалось: {expected_sknf}\n"
        f"Получено: {sknf}"
    )

    # Построение индексной формы
    index = build_index_form(truth_table)
    assert index == expected_index, (
        f"Индексная форма:\nОжидалось: {bin(expected_index)}\n"
        f"Получено: {bin(index)}"
    )
