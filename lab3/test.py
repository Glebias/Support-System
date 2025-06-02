import pytest
from io import StringIO
import sys
import main

# Тест для create_truth_table
def test_create_truth_table_simple_and():
    vars_list = ['a', 'b']
    table, dnf_rows, cnf_rows = main.create_truth_table(vars_list, "a&b")
    # Проверяем длину: 4 комбинации
    assert len(table) == 4
    # Из них только (1,1) даёт True
    assert dnf_rows == [(1, 1)]
    # Остальные три комбинации в cnf_rows
    assert set(cnf_rows) == {(0, 0), (0, 1), (1, 0)}

def test_create_truth_table_invalid_expr():
    with pytest.raises(ValueError):
        main.create_truth_table(['a'], "a&")

# Тест для combine_terms
def test_combine_terms_basic():
    terms = [(0, 0, 0), (0, 0, 1)]
    combined = main.combine_terms(terms)
    # Из двух термов должен получиться один (0,0,'X')
    assert (0, 0, 'X') in combined
    # Исходные термы при этом не должны присутствовать
    assert (0, 0, 0) not in combined
    assert (0, 0, 1) not in combined

def test_combine_terms_no_combination():
    terms = [(0, 0), (1, 1)]
    combined = main.combine_terms(terms)
    # Поскольку эти термы отличаются в двух позициях, оба остаются
    assert set(combined) == {(0, 0), (1, 1)}

# Тест для term_to_string (только для DNF)
def test_term_to_string_dnf():
    term = (1, 0, 'X')
    variables = ['a', 'b', 'c']
    s = main.term_to_string(term, variables, format_type='dnf')
    # val=1 → "a", val=0 → "¬b", 'X' пропускается
    assert "a" in s
    assert "¬b" in s
    assert "c" not in s

# Тест для draw_karnaugh (проверяем, что печатается нужная структура)
def test_draw_karnaugh_2vars_captures_output(capsys):
    # Функция f(a,b) = a
    vars_list = ['a', 'b']
    table, _, _ = main.create_truth_table(vars_list, "a")
    main.draw_karnaugh(table, vars_list, target_value=1)
    captured = capsys.readouterr().out
    # Проверяем наличие кодов Грея 0 и 1 в заголовке
    header_line = captured.splitlines()[0]
    assert "0" in header_line and "1" in header_line
    # Должны быть две строки с " |"
    lines = captured.splitlines()
    assert any(line.startswith("0 |") for line in lines[1:])
    assert any(line.startswith("1 |") for line in lines[1:])

def test_draw_karnaugh_invalid_vars(capsys):
    bad_table = [((0,), 0)]
    main.draw_karnaugh(bad_table, ['a'], target_value=1)
    captured = capsys.readouterr().out
    assert "Поддерживаются только 2–4 переменные" in captured

# Тест для simplify_dnf
def test_simplify_dnf_simple(capsys):
    vars_list = ['a', 'b']
    implicants = main.simplify_dnf("a&b", vars_list)
    # Для a&b единственный минтерм (1,1)
    assert implicants == [(1, 1)]
    captured = capsys.readouterr().out
    assert "--- СДНФ: карта Карно" in captured
    assert "СДНФ: начальные импликанты" in captured

# Тест для simplify_cnf
def test_simplify_cnf_simple(capsys):
    vars_list = ['a', 'b']
    implicants = main.simplify_cnf("a|b", vars_list)
    # Для a|b нуль только в (0,0)
    assert implicants == [(0, 0)]
    captured = capsys.readouterr().out
    assert "--- СКНФ: карта Карно" in captured
    assert "СКНФ: начальные импликанты" in captured

# Полный проход для более сложного выражения
def test_full_process(capsys):
    expr = "a&(b|!c)"
    vars_list = ['a', 'b', 'c']
    # Проверяем, что create_truth_table возвращает три списка
    tt, dnf_rows, cnf_rows = main.create_truth_table(vars_list, expr)
    assert isinstance(tt, list)
    assert isinstance(dnf_rows, list)
    assert isinstance(cnf_rows, list)

    # Минимизация СДНФ
    imp_dnf = main.simplify_dnf(expr, vars_list)
    captured1 = capsys.readouterr().out
    assert "--- СДНФ" in captured1

    # Минимизация СКНФ
    imp_cnf = main.simplify_cnf(expr, vars_list)
    captured2 = capsys.readouterr().out
    assert "--- СКНФ" in captured2
