from itertools import product
from typing import List, Set


class Term:
    def __init__(self, vars_: str):
        self.vars = vars_


def print_truth_table():
    print("\nТаблица истинности ОДС-3:")
    print("| X1 | X2 | X3 | s | c |")
    print("|----|----|----|---|---|")
    for x1, x2, x3 in product([0, 1], repeat=3):
        s = x1 ^ x2 ^ x3
        c = (x1 & x2) | (x1 & x3) | (x2 & x3)
        print(f"|  {x1} |  {x2} |  {x3} | {s} | {c} |")


def get_sdnf_s() -> List[str]:
    """Собирает список троичных строк, где сумма s = 1."""
    return [
        f"{x1}{x2}{x3}"
        for x1, x2, x3 in product([0, 1], repeat=3)
        if (x1 ^ x2 ^ x3) == 1
    ]


def get_sdnf_c() -> List[str]:
    """Собирает список троичных строк, где перенос c = 1."""
    return [
        f"{x1}{x2}{x3}"
        for x1, x2, x3 in product([0, 1], repeat=3)
        if ((x1 & x2) | (x1 & x3) | (x2 & x3)) == 1
    ]


def format_term(term: str, var_names: List[str]) -> str:
    parts = []
    for bit, var in zip(term, var_names):
        if bit == "-":
            continue
        parts.append(("¬" + var) if bit == "0" else var)
    return " ∧ ".join(parts) if parts else "1"


def can_glue(t1: str, t2: str) -> bool:
    diff = sum(1 for a, b in zip(t1, t2) if a != b)
    return diff == 1


def glue_terms(term1: str, term2: str) -> str:
    return "".join('-' if a != b else a for a, b in zip(term1, term2))


def minimize_sdnf(terms: List[str], var_names: List[str]) -> Set[str]:
    print("\nПроцесс минимизации:")
    new_terms = set(terms)
    minimized: Set[str] = set()
    iteration = 1

    while True:
        print(f"\nИтерация {iteration}:")
        terms_list = list(new_terms)
        new_set: Set[str] = set()
        used = [False] * len(terms_list)

        for i in range(len(terms_list)):
            for j in range(i + 1, len(terms_list)):
                t1, t2 = terms_list[i], terms_list[j]
                if can_glue(t1, t2):
                    glued = glue_terms(t1, t2)
                    new_set.add(glued)
                    used[i] = used[j] = True
                    print(
                        f"Склеиваем: ({format_term(t1, var_names)}) и ({format_term(t2, var_names)}) => "
                        f"{format_term(glued, var_names)}"
                    )

        if not new_set and not any(used):
            print("Склеиваний не найдено")

        for idx, t in enumerate(terms_list):
            if not used[idx]:
                minimized.add(t)

        if not new_set:
            break

        new_terms = new_set
        iteration += 1

    return minimized


def sdnf_for_s() -> Set[str]:
    terms = get_sdnf_s()
    var_names = ['X1', 'X2', 'X3']
    print("\nСДНФ для суммы (s):")
    print(" ∨ ".join(f"({format_term(t, var_names)})" for t in terms))

    minimized = minimize_sdnf(terms, var_names)
    print("\nМинимизированная СДНФ для s:")
    print(" ∨ ".join(f"({format_term(t, var_names)})" for t in minimized))
    return minimized


def sdnf_for_c() -> Set[str]:
    terms = get_sdnf_c()
    var_names = ['X1', 'X2', 'X3']
    print("\nСДНФ для переноса (c):")
    print(" ∨ ".join(f"({format_term(t, var_names)})" for t in terms))

    minimized = minimize_sdnf(terms, var_names)
    print("\nМинимизированная СДНФ для c:")
    print(" ∨ ".join(f"({format_term(t, var_names)})" for t in minimized))
    return minimized


def analyze_circuit(min_s: Set[str], min_c: Set[str]):
    print("\nАнализ логических элементов после минимизации:")

    # Инверторов по одному на вход X1, X2, X3
    inverters = 3

    # Для s
    and_gates_s = len(min_s)
    and_inputs_s = sum(3 - t.count('-') for t in min_s)
    or_inputs_s = len(min_s)

    # Для c
    and_gates_c = len(min_c)
    and_inputs_c = sum(3 - t.count('-') for t in min_c)
    or_inputs_c = len(min_c)

    print(f"Для реализации s ({len(min_s)} термов):")
    print(f"  - Схем И: {and_gates_s} (всего входов: {and_inputs_s})")
    print(f"  - Схема ИЛИ: 1 (на {or_inputs_s} входов)")

    print(f"\nДля реализации c ({len(min_c)} термов):")
    print(f"  - Схем И: {and_gates_c} (всего входов: {and_inputs_c})")
    print(f"  - Схема ИЛИ: 1 (на {or_inputs_c} входов)")

    print("\nОбщие элементы:")
    print(f"  - Инверторы: {inverters} (по одному на каждый вход)")

    # Приблизительный подсчет транзисторов
    transistor_count = inverters * 2  # по 2 транзистора на инвертор

    # Для каждой AND: 4 транзистора базовых + 2 за каждый вход
    for t in min_s:
        inputs = 3 - t.count('-')
        transistor_count += 4 + inputs * 2
    for t in min_c:
        inputs = 3 - t.count('-')
        transistor_count += 4 + inputs * 2

    # Для каждой OR: 4 транзистора базовых + 2 за каждый вход
    transistor_count += (4 + or_inputs_s * 2) + (4 + or_inputs_c * 2)

    print(f"\nОриентировочное количество транзисторов: {transistor_count}")


def format_dnf_term(term: str, var_names: List[str]) -> str:
    """Используется при печати минимизированной СДНФ."""
    parts = []
    for i, bit in enumerate(term):
        if bit == '-':
            continue
        parts.append(f"!{var_names[i]}" if bit == '0' else var_names[i])
    return "&".join(parts) if parts else "1"


def parse_dnf_term(term: str, var_names: List[str]) -> str:
    """
    Преобразует текст вида '!A&B&C&D' в строку '0101' (без пробелов),
    используя фиксированный список var_names столбцом.
    """
    # Словарь для A,B,C,D
    values = {var: None for var in var_names}
    for literal in term.split('&'):
        literal = literal.strip()
        if literal.startswith('!'):
            values[literal[1:]] = '0'
        else:
            values[literal] = '1'
    # Любые не упомянутые переменные — don’t care
    return ''.join(values[var] if values[var] is not None else '-' for var in var_names)


def parse_function(input_str: str, var_names: List[str]) -> List[Term]:
    """Парсит СДНФ вида '(A&!B&C)|(B&C)' в список Term."""
    terms: List[Term] = []
    for raw in input_str.split('|'):
        t = raw.strip().strip('()')
        if not t:
            continue
        bin_str = parse_dnf_term(t, var_names)
        terms.append(Term(bin_str))
    return terms


def to_bcd(n: int) -> tuple:
    """Возвращает 4-битный BCD-код (8421) для числа n (0–9)."""
    return tuple(int(bit) for bit in format(n, '04b'))


def print_bcd_converter():
    print("\n=== Преобразователь Д8421 в Д8421+6 ===")
    var_names = ['A', 'B', 'C', 'D']
    sdnf_Y = [[] for _ in range(4)]  # термы для Y1..Y4

    print("D8421\t\tD8421+6")
    print("A B C D\t\tY1 Y2 Y3 Y4")
    print("--------------------------")

    for i in range(10):
        A, B, C, D = to_bcd(i)
        result = (i + 6) % 10
        Y1, Y2, Y3, Y4 = to_bcd(result)

        print(f"{A} {B} {C} {D}\t\t{Y1}  {Y2}  {Y3}  {Y4}")

        term = f"{'A' if A else '!A'}&{'B' if B else '!B'}&{'C' if C else '!C'}&{'D' if D else '!D'}"
        for j, y in enumerate((Y1, Y2, Y3, Y4)):
            if y == 1:
                sdnf_Y[j].append(term)

    # Печать СДНФ и минимизация для каждого выхода
    for idx, output_terms in enumerate(sdnf_Y, start=1):
        Ti = f"Y{idx}"
        print(f"\nСДНФ для {Ti}:")
        if not output_terms:
            print("0  (функция тождественно 0)")
            continue

        sdnf_str = " ∨ ".join(f"({t})" for t in output_terms)
        print(sdnf_str)

        # Собираем минтермы в бинарный вид
        terms_bin = [parse_dnf_term(t, var_names) for t in output_terms]

        # Минимизация
        minimized = minimize_sdnf(terms_bin, var_names.copy())

        print(f"\nМинимизированная СДНФ для {Ti}:")
        print(
            " ∨ ".join(f"({format_dnf_term(m, var_names)})" for m in minimized)
        )


def get_sdnf_4bit() -> (List[List[str]], List[str]):
    """
    Собирает полную СДНФ (список минтермов) для каждого выходного бита Y1..Y4
    преобразователя D8421 → D8421+6.
    Возвращает кортеж: (список из 4 списков битовых строк, var_names).
    """
    var_names = ["A", "B", "C", "D"]
    sdnf_terms = [[] for _ in range(4)]  # для Y1..Y4

    for digit in range(10):
        A, B, C, D = to_bcd(digit)
        result = (digit + 6) % 10
        Y1, Y2, Y3, Y4 = to_bcd(result)

        bit_pattern = f"{A}{B}{C}{D}"
        if Y1 == 1:
            sdnf_terms[0].append(bit_pattern)
        if Y2 == 1:
            sdnf_terms[1].append(bit_pattern)
        if Y3 == 1:
            sdnf_terms[2].append(bit_pattern)
        if Y4 == 1:
            sdnf_terms[3].append(bit_pattern)

    return sdnf_terms, var_names


def print_sdnf_for_4bit():
    sdnf_terms, var_names = get_sdnf_4bit()

    for idx, terms in enumerate(sdnf_terms, start=1):
        print(f"\n--- СДНФ (4 бита) для Y{idx} ---")
        if not terms:
            print("0  (функция тождественно 0)")
            continue

        dnf_clauses = [
            f"({format_term(bits, var_names)})"
            for bits in terms
        ]
        sdnf_str = " ∨ ".join(dnf_clauses)
        print(sdnf_str)


def process_bcd_conversion(number: int):
    print(f"\n=== Обработка числа {number} ===")
    decimal = number % 10
    result = (decimal + 6) % 10
    in_bits = to_bcd(decimal)
    out_bits = to_bcd(result)

    print(f"Входное число: {number} (используется: {decimal}, результат: {result})")
    print("Вход (Д8421):", ' '.join(map(str, in_bits)))
    print("Выход (Д8421+6):", ' '.join(map(str, out_bits)), f"(десятичное: {result})")


def main():
    print_truth_table()
    minimized_s = sdnf_for_s()
    minimized_c = sdnf_for_c()
    analyze_circuit(minimized_s, minimized_c)

    print_bcd_converter()
    print_sdnf_for_4bit()

    while True:
        try:
            num = int(input("\nВведите целое число (для выхода введите отрицательное число): "))
            if num < 0:
                break
            process_bcd_conversion(num)
        except ValueError:
            print("Некорректный ввод. Повторите.")


if __name__ == "__main__":
    main()
