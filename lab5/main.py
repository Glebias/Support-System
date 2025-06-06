from typing import List, Set

def format_term(term: str, var_names: List[str]) -> str:
    """
    Преобразует строку бинарного терма (с '0','1','-') в логическое выражение вида
    ¬A ∧ B ∧ ¬C ∧ D (если var_names = ['A','B','C','D']).
    """
    parts = []
    for bit, var in zip(term, var_names):
        if bit == "-":
            continue
        parts.append(("¬" + var) if bit == "0" else var)
    return " ∧ ".join(parts) if parts else "1"


def can_glue(t1: str, t2: str) -> bool:
    """
    Возвращает True, если строки t1 и t2 различаются ровно в одной позиции,
    и их можно «склеить».
    """
    return sum(a != b for a, b in zip(t1, t2)) == 1


def glue_terms(term1: str, term2: str) -> str:
    """
    Склеивает два терма одинаковой длины, различающиеся в одной позиции,
    заменяя отличающийся бит на '-'.
    """
    return "".join('-' if a != b else a for a, b in zip(term1, term2))


def minimize_sdnf(terms: List[str], var_names: List[str]) -> Set[str]:
    """
    Выполняет минимизацию списка термов (в виде строк "0101", "0-11" и т.п.)
    методом итеративного склеивания (Quine–McCluskey без построения таблицы примаров).
    Возвращает множество минимизированных термов и печатает процесс «склейки».
    """
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
                        f"Склеиваем: ({format_term(t1, var_names)}) и "
                        f"({format_term(t2, var_names)}) => {format_term(glued, var_names)}"
                    )

        # Если новых склеиваний нет и ни один термин не был использован
        if not new_set and not any(used):
            print("Склеиваний не найдено")

        # Добавляем в результат все термы, которые не склеивались
        for idx, t in enumerate(terms_list):
            if not used[idx]:
                minimized.add(t)

        if not new_set:
            break

        new_terms = new_set
        iteration += 1

    return minimized


def generate_counter_truth_tables():
    """
    Формирует:
      - table_rows: список словарей с полями для таблицы истинности
      - minterms_T: четыре списка «минтермов» (строки 'Q3Q2Q1Q0') для каждого T_i, где T_i = 1.

    Q3 Q2 Q1 Q0 — текущие биты (q4s,q3s,q2s,q1s),
    Q3+ Q2+ Q1+ Q0+ = (Q - 1) mod 16 — следующие.
    T_i = Q_i XOR Q_i+.
    """
    table_rows = []
    minterms_T = [[] for _ in range(4)]
    
    for state in range(16):
        # Текущее состояние (Q3, Q2, Q1, Q0)
        bits = tuple(int(b) for b in format(state, '04b'))
        Q3, Q2, Q1, Q0 = bits

        # Следующее состояние = (state - 1) mod 16
        next_state = (state - 1) % 16
        bits_n = tuple(int(b) for b in format(next_state, '04b'))
        Q3n, Q2n, Q1n, Q0n = bits_n

        # Вычисляем T_i = Q_i XOR Q_i+
        T3 = Q3 ^ Q3n
        T2 = Q2 ^ Q2n
        T1 = Q1 ^ Q1n
        T0 = Q0 ^ Q0n

        # Строка для таблицы истинности
        row = {
            "№": state,
            "q4s": Q3,
            "q3s": Q2,
            "q2s": Q1,
            "q1s": Q0,
            "V": 1,
            "h4": T3,
            "h3": T2,
            "h2": T1,
            "h1": T0,
        }
        table_rows.append(row)

        # Собираем минтермы для каждого T_i
        bin_str = f"{Q3}{Q2}{Q1}{Q0}"
        if T3 == 1:
            minterms_T[3].append(bin_str)
        if T2 == 1:
            minterms_T[2].append(bin_str)
        if T1 == 1:
            minterms_T[1].append(bin_str)
        if T0 == 1:
            minterms_T[0].append(bin_str)

    return table_rows, minterms_T


def print_truth_table(table_rows):
    """
    Печатает таблицу истинности в формате, полностью совпадающем с примером:
       №  q4s  q3s  q2s  q1s    V   h4   h3   h2   h1
       0   0    0    0    0    1    1    1    1    1
       1   0    0    0    1    1    0    0    0    1
       ...
      15   1    1    1    1    1    0    0    0    1
    """
    # Заголовок (ровно так, как в примере)
    print(" №  q4s  q3s  q2s  q1s    V   h4   h3   h2   h1")
    for row in table_rows:
        print(
            f"{row['№']:>3}   "
            f"{row['q4s']:>1}    "
            f"{row['q3s']:>1}    "
            f"{row['q2s']:>1}    "
            f"{row['q1s']:>1}    "
            f"{row['V']:>1}    "
            f"{row['h4']:>1}    "
            f"{row['h3']:>1}    "
            f"{row['h2']:>1}    "
            f"{row['h1']:>1}"
        )


def synthesize_and_minimize_counter():

    var_names = ['Q3', 'Q2', 'Q1', 'Q0']
    table_rows, minterms_T = generate_counter_truth_tables()

    # 1) Печатаем таблицу истинности
    print("\n=== Таблица истинности ===\n")
    print_truth_table(table_rows)

    # 2) Обработка для T3, T2, T1, T0
    for idx in range(3, -1, -1):
        Ti = f"T{idx}"
        minterms = minterms_T[idx]
        print(f"\n=== Синтаксис и минимизация для {Ti} ===")

        if not minterms:
            print(f"{Ti} всегда равен 0")
            continue

        # Печать списка минтермов
        print(f"Минтермы, где {Ti}=1: {', '.join(minterms)}")

        # Построение исходной СДНФ
        sdnf_str = " ∨ ".join(f"({format_term(m, var_names)})" for m in minterms)
        print(f"СДНФ: {sdnf_str}")

        # Минимизация методом Квайна–Мак-Класки
        minimized = minimize_sdnf(minterms, var_names)

        # Итоговая минимизированная СДНФ
        print(f"\nМинимизированная СДНФ для {Ti}:")
        final_str = " ∨ ".join(f"({format_term(m, var_names)})" for m in sorted(minimized))
        print(final_str)


if __name__ == "__main__":
    synthesize_and_minimize_counter()
