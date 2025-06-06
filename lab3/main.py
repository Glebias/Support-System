import itertools
import re
from itertools import product, combinations
# from karno import karnau_min 

VALID_VARS = {'a', 'b', 'c', 'd', 'e'}
VALID_OPERATORS = {'&', '|', '!', '->', '~', '(', ')'}

# ---------- Проверка корректности введенного выражения ----------
def validate_input(expression):
    normalized = expression.replace('->', 'IMPL').replace('~', 'EQV')
    tokens = re.findall(r'[a-e]|IMPL|EQV|[&|!() ]', normalized)
    return all(token in VALID_VARS or token in VALID_OPERATORS or token in {'IMPL', 'EQV'} for token in tokens)

# ---------- Преобразование в синтаксис Python ----------
def transform_expression(expression):
    # Обрабатываем сначала двусимвольные операторы -> и ~
    expression = re.sub(r'([a-e)!]+)\s*->\s*([a-e(!]+)', r'(not (\1) or (\2))', expression)
    expression = re.sub(r'([a-e)!]+)\s*~\s*([a-e(!]+)', r'((\1) == (\2))', expression)
    # Затем заменяем однобайтовые: !, &, |
    return expression.replace('!', 'not ').replace('&', ' and ').replace('|', ' or ')

# ---------- Создание таблицы истинности и сбор минтермов/макстермов ----------
def create_truth_table(vars_list, expr):
    full_tt, dnf_rows, cnf_rows = [], [], []
    for combo in itertools.product([0, 1], repeat=len(vars_list)):
        context = dict(zip(vars_list, combo))
        try:
            outcome = eval(transform_expression(expr), {}, context)
        except Exception as err:
            raise ValueError(f"Ошибка при вычислении выражения: {err}")
        full_tt.append((combo, outcome))
        if outcome in (1, True):
            dnf_rows.append(combo)
        else:
            cnf_rows.append(combo)
    return full_tt, dnf_rows, cnf_rows

# ---------- Функция объединения терминов (Quine-McCluskey) ----------
def combine_terms(terms):
    result_set, marked = set(), set()
    for i in range(len(terms)):
        for j in range(i + 1, len(terms)):
            diff = [k for k in range(len(terms[i])) if terms[i][k] != terms[j][k]]
            if len(diff) == 1:
                new_term = list(terms[i])
                new_term[diff[0]] = 'X'
                result_set.add(tuple(new_term))
                marked.update({i, j})
    # Добавляем «не помеченные» (которые не вошли ни в одну пару) как есть
    for idx, term in enumerate(terms):
        if idx not in marked:
            result_set.add(term)
    return list(result_set)

# ---------- Преобразование терма в строку для вывода ----------
def term_to_string(term, variables, format_type):
    result = []
    for i, val in enumerate(term):
        if val == 'X':
            continue
        if format_type == 'dnf':
            # Если 0 → ставим отрицание, 1 → без отрицания
            neg = '¬' if val == 0 else ''
            result.append(f"{neg}{variables[i]}")
        else:  # format_type == 'cnf'
            # Для CNF: берем «литерал 0» → положительный, «литерал 1» → с ¬ (т.к. строим макстермы)
            neg = '¬' if val == 1 else ''
            result.append(f"{neg}{variables[i]}")
    joiner = ' & ' if format_type == 'dnf' else ' ∨ '
    return joiner.join(result) if result else ("1" if format_type == 'dnf' else "0")

def simplify_dnf(expression, variables):
    full_tt, dnf_rows, _ = create_truth_table(variables, expression)

    # Шаги метода «склейки» (Quine–McCluskey на первом уровне)
    print("\n--- СДНФ: минимизация методом склейки ---")
    implicants = [tuple(bits) for bits in dnf_rows]
    print("СДНФ: начальные импликанты:")
    for idx, term in enumerate(implicants, start=1):
        print(f"{idx}: {term_to_string(term, variables, 'dnf')}")
    step = 1
    while True:
        reduced = combine_terms(implicants)
        if reduced == implicants:
            break
        print(f"\nШаг склейки {step} (СДНФ):")
        for term in reduced:
            print(term_to_string(term, variables, 'dnf'))
        implicants = reduced
        step += 1

    return implicants, full_tt 

def simplify_cnf(expression, variables):
    full_tt, _, cnf_rows = create_truth_table(variables, expression)

    # Шаги метода «склейки» (Quine–McCluskey на первом уровне для макстермов)
    print("\n--- СКНФ: минимизация методом склейки ---")
    implicants = [tuple(bits) for bits in cnf_rows]
    print("СКНФ: начальные импликанты:")
    for idx, term in enumerate(implicants, start=1):
        print(f"{idx}: {term_to_string(term, variables, 'cnf')}")
    step = 1
    while True:
        reduced = combine_terms(implicants)
        if reduced == implicants:
            break
        print(f"\nШаг склейки {step} (СКНФ):")
        for term in reduced:
            print(term_to_string(term, variables, 'cnf'))
        implicants = reduced
        step += 1

    return implicants, full_tt  # Возвращаем также полную таблицу истинности

def expand_implicant(implicant_str):
    vars_combinations = [
        ''.join(bits) for bits in product('01', repeat=implicant_str.count('X'))
    ]
    results = []
    for bits in vars_combinations:
        term = list(implicant_str)
        bit_index = 0
        for i, ch in enumerate(implicant_str):
            if ch == 'X':
                term[i] = bits[bit_index]
                bit_index += 1
        results.append(''.join(term))
    return results

def get_all_minterms(implicants_str):
    all_minterms = set()
    for impl in implicants_str:
        all_minterms.update(expand_implicant(impl))
    return all_minterms

def find_essential_implicants(implicants_str, all_minterms):
    coverage = {m: [] for m in all_minterms}
    for idx, impl in enumerate(implicants_str):
        for m in expand_implicant(impl):
            coverage[m].append(idx)
    essential_indices = set()
    for m, idx_list in coverage.items():
        if len(idx_list) == 1:
            essential_indices.add(idx_list[0])
    return sorted(list(essential_indices))

def minimize_implicants(implicants_str):
    all_minterms = get_all_minterms(implicants_str)
    essential_indices = find_essential_implicants(implicants_str, all_minterms)
    essential_impls = [implicants_str[i] for i in essential_indices]

    covered_by_essential = set()
    for i in essential_indices:
        covered_by_essential.update(expand_implicant(implicants_str[i]))

    remaining_minterms = list(all_minterms - covered_by_essential)
    remaining_indices = [i for i in range(len(implicants_str)) if i not in essential_indices]

    if not remaining_minterms:
        return essential_impls

    remaining_impls = [implicants_str[i] for i in remaining_indices]
    for r in range(1, len(remaining_impls) + 1):
        for combo in combinations(range(len(remaining_impls)), r):
            covered = set()
            for idx in combo:
                covered.update(expand_implicant(remaining_impls[idx]))
            if set(remaining_minterms).issubset(covered):
                chosen_impls = [remaining_impls[i] for i in combo]
                return essential_impls + chosen_impls

    return implicants_str

# def print_coverage_table(implicants):
#     implicants_str = [''.join(str(ch) for ch in impl) for impl in implicants]
#     all_minterms = sorted(get_all_minterms(implicants_str))

#     col_width = max(max(len(m) for m in all_minterms), 1)
#     row_label_width = max(len(s) for s in implicants_str)

#     header = ' ' * (row_label_width + 2)
#     for m in all_minterms:
#         header += m.center(col_width + 2)
#     print(header)

#     # Строки-импликанты
#     for impl in implicants_str:
#         line = impl.ljust(row_label_width) + '  '
#         covered = set(expand_implicant(impl))
#         for m in all_minterms:
#             if m in covered:
#                 line += 'X'.center(col_width + 2)
#             else:
#                 line += ' '.center(col_width + 2)
#         print(line)

# def execute_second_task(implicants_input):

#     print("\nТаблица покрытия для импликант:")
#     print_coverage_table(implicants_input)
#     print()

#     implicants_str = [''.join(str(ch) for ch in impl) for impl in implicants_input]
#     minimized = minimize_implicants(implicants_str)
#     print("Минимальный набор импликант (таблично-расчётный метод):")
#     for imp in minimized:
#         print("  -", imp)

def pattern_to_cnf_clause(pattern, var_names):
    lits = []
    for bit, name in zip(pattern, var_names):
        if bit == '1':
            # В импликанте эта переменная – «1» (без ¬) → в макстерме ее дополняем: «¬name» → ставим name' 
            lits.append(f"¬{name}")
        elif bit == '0':
            # В импликанте – «0» → литерал «¬name» → в макстерме дополняем: «name»
            lits.append(f"{name}")
        # Если '-', пропустить
    return " ∨ ".join(lits) if lits else "0"  # если все '-', то это тождественная 0 (но такого обычно не бывает)

def pattern_to_dnf_minterm(pattern, var_names):
    literals = []
    for bit, var in zip(pattern, var_names):
        if bit == '0':
            literals.append(f"¬{var}")  # Отрицание для '0'
        elif bit == '1':
            literals.append(var)         # Без отрицания для '1'
        # Пропускаем '-' (безразличное значение)
    
    return " & ".join(literals) if literals else "1"  # Пустой минтерм = 1

# def main():
#     while True:
#         expr_input = input("Введите логическое выражение (используйте &, |, !, ->, ~): ").strip()
#         if not expr_input:
#             continue
#         if not validate_input(expr_input):
#             print("Ошибка: найдены недопустимые символы.")
#             continue

#         used_vars = sorted(set(re.findall(r'[a-e]', expr_input)))
#         if not used_vars:
#             print("Ошибка: не найдены переменные a–e.")
#             continue
#         if len(used_vars) > 5:
#             print("Ошибка: разрешено максимум 5 переменных.")
#             continue

#         # ---------------- СДНФ ----------------
#         dnf_implicants, full_tt = simplify_dnf(expr_input, used_vars)
#         print("\nСДНФ (после склейки):")
#         print(' ∨ '.join([f"({term_to_string(t, used_vars, 'dnf')})" for t in dnf_implicants]) or "0")

#         # Таблично-расчётная минимизация DNF
#         execute_second_task(dnf_implicants)

#         # ---------------- СКНФ ----------------
#         cnf_implicants, full_tt_cnf = simplify_cnf(expr_input, used_vars)
#         print("\nСКНФ (после склейки):")
#         print(' ∧ '.join([f"({term_to_string(t, used_vars, 'cnf')})" for t in cnf_implicants]) or "1")

#         execute_second_task(cnf_implicants)

#         print("Минимизация с помощью карт Карно--------------")
#         _, dnf_tt, cnf_tt = create_truth_table(used_vars, expr_input)
#         karnau_min(dnf_tt,cnf_tt)

#         break  # Выходим после одного расчёта

# if __name__ == "__main__":
#     main()
