import itertools
import re

VALID_VARS = {'a', 'b', 'c', 'd', 'e'}
VALID_OPERATORS = {'&', '|', '!', '->', '~', '(', ')'}

# Проверка корректности введенного выражения
def validate_input(expression):
    normalized = expression.replace('->', 'IMPL').replace('~', 'EQV')
    tokens = re.findall(r'[a-e]|IMPL|EQV|[&|!() ]', normalized)
    return all(token in VALID_VARS or token in VALID_OPERATORS or token in {'IMPL', 'EQV'} for token in tokens)

# Преобразование в синтаксис Python
def transform_expression(expression):
    expression = re.sub(r'([a-e)!]+)\s*->\s*([a-e(!]+)', r'(not (\1) or (\2))', expression)
    expression = re.sub(r'([a-e)!]+)\s*~\s*([a-e(!]+)', r'((\1) == (\2))', expression)
    return expression.replace('!', 'not ').replace('&', ' and ').replace('|', ' or ')

# Создание таблицы истинности и сбор минтермов/макстермов
def create_truth_table(vars_list, expr):
    table, dnf_rows, cnf_rows = [], [], []
    for combo in itertools.product([0, 1], repeat=len(vars_list)):
        context = dict(zip(vars_list, combo))
        try:
            outcome = eval(transform_expression(expr), {}, context)
        except Exception as err:
            raise ValueError(f"Ошибка при вычислении выражения: {err}")
        table.append((combo, outcome))
        (dnf_rows if outcome else cnf_rows).append(combo)
    return table, dnf_rows, cnf_rows

# Функция объединения терминов (Quine-McCluskey)
def combine_terms(terms):
    result_set, marked = set(), set()
    for i in range(len(terms)):
        for j in range(i + 1, len(terms)):
            diff = [idx for idx in range(len(terms[i])) if terms[i][idx] != terms[j][idx]]
            if len(diff) == 1:
                new_term = list(terms[i])
                new_term[diff[0]] = 'X'
                result_set.add(tuple(new_term))
                marked.update({i, j})
    for idx, term in enumerate(terms):
        if idx not in marked:
            result_set.add(term)
    return list(result_set)

# Преобразование терма в строку для вывода
def term_to_string(term, variables, format_type='dnf'):
    result = []
    for i, val in enumerate(term):
        if val == 'X':
            continue
        neg = '¬' if (val == 0 and format_type == 'dnf') or (val == 1 and format_type == 'cnf') else ''
        result.append(f"{neg}{variables[i]}")
    return (' & ' if format_type == 'dnf' else ' ∨ ').join(result)

# Метод отрисовки и печати карты Карно (для группировки 1 или 0)
def draw_karnaugh(truth_table, var_list, target_value=1):
    n = len(var_list)
    if n < 2 or n > 4:
        print("Поддерживаются только 2–4 переменные для карты Карно.")
        return

    # Разбиение переменных:
    # n=2: rows = [var0], cols = [var1]
    # n=3: rows = [var0], cols = [var1, var2]
    # n=4: rows = [var0, var1], cols = [var2, var3]
    if n == 2:
        rows, cols = var_list[:1], var_list[1:]
    elif n == 3:
        rows, cols = var_list[:1], var_list[1:]
    else:  # n == 4
        rows, cols = var_list[:2], var_list[2:]

    def gray_code(bits):
        return [format(i ^ (i >> 1), f'0{bits}b') for i in range(2 ** bits)]

    row_vals = gray_code(len(rows))
    col_vals = gray_code(len(cols))

    # Собираем значения в словарь: ключ = (строка, столбец), значение = 0/1
    value_grid = {}
    for assignment, res in truth_table:
        mapping = dict(zip(var_list, assignment))
        r_key = ''.join(str(mapping[v]) for v in rows)
        c_key = ''.join(str(mapping[v]) for v in cols)
        value_grid[(r_key, c_key)] = res

    # Печать заголовка
    print("   " + "  ".join(col_vals))
    for r in row_vals:
        line = f"{r} |"
        for c in col_vals:
            v = value_grid.get((r, c), ' ')
            # Если target_value == 1 (для СДНФ), печатаем '1' там, где в truth_table стоит 1
            # Если target_value == 0 (для СКНФ), печатаем '0' там, где в truth_table стоит 0
            mark = '1' if (v == 1 and target_value == 1) else ('0' if (v == 0 and target_value == 0) else ' ')
            line += f" {mark} "
        print(line)
    print()  # пустая строка после карты

# Минимизация СДНФ через метод склеивания и вывод карты Карно
def simplify_dnf(expression, variables):
    truth_table, dnf_rows, _ = create_truth_table(variables, expression)

    print("\n--- СДНФ: карта Карно (группируем '1') ---")
    draw_karnaugh(truth_table, variables, target_value=1)

    print("--- СДНФ: минимизация методом склейки ---")
    implicants = [tuple(item) for item in dnf_rows]
    print("СДНФ: начальные импликанты:")
    for idx, term in enumerate(implicants):
        print(f"{idx + 1}: {term}")
    step = 1
    while True:
        reduced = combine_terms(implicants)
        if reduced == implicants:
            break
        print(f"\nШаг склеивания {step} (СДНФ):")
        for term in reduced:
            print(term_to_string(term, variables, 'dnf'))
        implicants = reduced
        step += 1
    return implicants

# Минимизация СКНФ через метод склеивания и вывод карты Карно
def simplify_cnf(expression, variables):
    truth_table, _, cnf_rows = create_truth_table(variables, expression)

    print("\n--- СКНФ: карта Карно (группируем '0') ---")
    draw_karnaugh(truth_table, variables, target_value=0)

    print("--- СКНФ: минимизация методом склейки ---")
    implicants = [tuple(item) for item in cnf_rows]
    print("СКНФ: начальные импликанты:")
    for idx, term in enumerate(implicants):
        print(f"{idx + 1}: {term}")
    step = 1
    while True:
        reduced = combine_terms(implicants)
        if reduced == implicants:
            break
        print(f"\nШаг склеивания {step} (СКНФ):")
        for term in reduced:
            print(term_to_string(term, variables, 'cnf'))
        implicants = reduced
        step += 1
    return implicants

def main():
    while True:
        expr_input = input("Введите логическое выражение (используйте &, |, !, ->, ~): ").strip()
        if not validate_input(expr_input):
            print("Ошибка: найдены недопустимые символы.")
            continue
        used = sorted(set(re.findall(r'[a-e]', expr_input)))
        if len(used) > 5:
            print("Ошибка: разрешено максимум 5 переменных.")
            continue

        # Минимизация СДНФ (с выводом карты Карно и шагов склейки)
        dnf_result = simplify_dnf(expr_input, used)
        print("\nМинимизированная СДНФ:")
        print(' ∨ '.join([f"({term_to_string(t, used, 'dnf')})" for t in dnf_result]))

        # Минимизация СКНФ (с выводом карты Карно и шагов склейки)
        cnf_result = simplify_cnf(expr_input, used)
        print("\nМинимизированная СКНФ:")
        print(' ∧ '.join([f"({term_to_string(t, used, 'cnf')})" for t in cnf_result]))

        break

if __name__ == "__main__":
    main()
