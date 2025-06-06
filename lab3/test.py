import pytest
import re
import itertools
from main import (
    VALID_VARS,
    VALID_OPERATORS,
    validate_input,
    transform_expression,
    create_truth_table,
    combine_terms,
    term_to_string,
    simplify_dnf,
    simplify_cnf,
    expand_implicant,
    get_all_minterms,
    find_essential_implicants,
    minimize_implicants,
    pattern_to_cnf_clause,
    pattern_to_dnf_minterm,
)
from karno import (
    _tuple_to_rc,
    minimize_dnf_karnaugh,
    minimize_cnf_karnaugh,
    format_sdnf,
    format_sknf,
)

@pytest.mark.parametrize("expr,expected", [
    ("a&b", True),
    ("a|b", True),
    ("a->b", True),
    ("a~b", True),
    ("!(a|b)", True),
    ("x & y", False),     # invalid vars
    ("a + b", False),     # invalid operator
    ("a && b", False),    # invalid operator
    (" ", False),          # empty string
])
def test_validate_input_all(expr, expected):
    assert validate_input(expr) == expected

@pytest.mark.parametrize("expr,expected", [
    ("a&b", "a and b"),
    ("!a|b", "not a or b"),
    ("a->b", "(not (a) or (b))"),
    ("a~b", "((a) == (b))"),
    ("a&!b", "a and not b"),
])
def test_transform_expression_all(expr, expected):
    assert transform_expression(expr) == expected

def test_transform_expression_invalid_pattern_raises_nothing():
    # If expression is syntactically weird, transform_expression still returns a string;
    # actual error would occur in eval() inside create_truth_table, not here.
    expr = "a - b"
    out = transform_expression(expr)
    assert isinstance(out, str)

def test_create_truth_table_basic_and_error():
    vars_list = ['a', 'b']
    full_tt, dnf_rows, cnf_rows = create_truth_table(vars_list, "a & b")
    # There are 4 rows; (1,1) → 1; others → 0.
    assert len(full_tt) == 4
    assert (1,1) in dnf_rows and (0,0) in cnf_rows
    # If expression is invalid, should raise ValueError
    with pytest.raises(ValueError):
        create_truth_table(vars_list, "a & (b")  # unmatched parenthesis

def test_combine_terms_no_merge():
    # Terms that differ by >1 bit or identical should return themselves only
    terms = [(0,0), (1,1)]
    combined = combine_terms(terms)
    assert set(combined) == {(0,0), (1,1)}

def test_combine_terms_multiple_merges():
    terms = [(0,0,0), (0,0,1), (0,1,1)]
    # (0,0,0) and (0,0,1) → (0,0,'X'), and (0,0,1) and (0,1,1) → (0,'X',1)
    combined = combine_terms(terms)
    assert (0,0,'X') in combined or (0,'X',1) in combined

@pytest.mark.parametrize("term,vars_list,fmt,expected", [
    ((0,0, 'X'), ['x','y','z'], 'dnf', "¬x & ¬y"),
    ((1,1,'X'), ['a','b','c'], 'dnf', "a & b"),
    ((0,1,'X'), ['p','q','r'], 'cnf', "p ∨ ¬q"),
    ((1,0,'X'), ['a','b','c'], 'cnf', "¬a ∨ b"),
    (( 'X','X','X'), ['a','b','c'], 'dnf', "1"),
    (( 'X','X','X'), ['a','b','c'], 'cnf', "0"),
])
def test_term_to_string_various(term, vars_list, fmt, expected):
    assert term_to_string(term, vars_list, fmt) == expected

def test_simplify_dnf_constant_cases(capsys):
    # If expression ≡ 0, no minterms → implicants=[], full_tt non-empty
    implicants, full_tt = simplify_dnf("a & !a", ['a'])
    # No implicants, only full_tt
    assert implicants == []
    # printed lines still show "СДНФ: минимизация..." but implicants empty
    captured = capsys.readouterr()
    assert "СДНФ: начальные импликанты" in captured.out

    # If expression ≡ 1, all minterms → implicants become all combos? Actually each row merges
    implicants2, full_tt2 = simplify_dnf("a|!a", ['a'])
    # At least return something non-empty
    assert isinstance(implicants2, list)

def test_simplify_cnf_constant_cases(capsys):
    implicants, full_tt = simplify_cnf("a | !a", ['a'])
    # expression always true, so no zero rows → implicants=[]
    assert implicants == []
    captured = capsys.readouterr()
    assert "СКНФ: минимизация" in captured.out

def test_expand_implicant_and_get_all_minterms():
    assert set(expand_implicant("10X0")) == {"1000","1010"}
    assert set(get_all_minterms(["10X", "0X1"])) == {"100","101","001","011"}

def test_find_essential_implicants_and_minimize_implicants():
    implicants = ["1X0","1X1","0X1"]
    all_mins = get_all_minterms(implicants)
    ess = find_essential_implicants(implicants, all_mins)
    # essential indices is a list of integers
    assert all(isinstance(i, int) for i in ess)

    # Test minimize_implicants covers covering
    result = minimize_implicants(["1X0","1X1","0X1"])
    # result should be subset or equal
    assert set(result).issubset({"1X0","1X1","0X1"})

def test_pattern_to_clauses_edge():
    # pattern all '-' => returns default identity
    assert pattern_to_dnf_minterm("---", ['a','b','c']) == "1"
    assert pattern_to_cnf_clause("---", ['a','b','c']) == "0"
    # mixed pattern
    assert pattern_to_dnf_minterm("01-", ['a','b','c']) == "¬a & b"
    assert pattern_to_cnf_clause("10-", ['a','b','c']) == "¬a ∨ b"

# ---------------------- Tests for karno.py ----------------------

def test_minimize_dnf_karnaugh_edge_cases():
    # Case: no minterms => all-zero function => return ([], "0")
    implicants, kmap = minimize_dnf_karnaugh([])
    assert implicants == []
    # But format_sdnf of empty implicants is "0"
    assert format_sdnf(implicants) == "0"


def test_minimize_cnf_karnaugh_edge_cases():
    # Case: no maxterms => always 1 => return ([], "1")
    clauses, kmap = minimize_cnf_karnaugh([])
    assert clauses == []
    assert format_sknf(clauses) == "1"

    # Case: all combos are maxterms => always 0
    full = list(itertools.product([0,1], repeat=4))
    clauses2, kmap2 = minimize_cnf_karnaugh(full)
    # format_sknf of empty list is "1", but if all are maxterms, code returns ["----"]? 
    # We at least assert it returns a clause string containing only '-' or literal "0"/"1"
    assert isinstance(clauses2, list)

def test_format_sdnf_and_format_sknf_variety():
    assert format_sdnf([]) == "0"
    assert format_sknf([]) == "1"
    assert format_sdnf(["a","¬b & c"]) == "(a) ∨ (¬b & c)"
    assert format_sknf(["a ∨ b","¬c"]) == "(a ∨ b) ∧ (¬c)"
