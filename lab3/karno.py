from itertools import combinations

# Gray-код для двух бит
_gray2 = ['00', '01', '11', '10']

def _tuple_to_rc(bit_tuple):
    row_bits = f"{bit_tuple[0]}{bit_tuple[1]}"
    col_bits = f"{bit_tuple[2]}{bit_tuple[3]}"
    r = _gray2.index(row_bits)
    c = _gray2.index(col_bits)
    return r, c

def _generate_all_groups():
    groups = []
    # 1) Группы размера 8: две соседние строки
    for r in range(4):
        r2 = (r + 1) % 4
        cells = {(r, c) for c in range(4)} | {(r2, c) for c in range(4)}
        groups.append(cells)
    # 2) Группы размера 8: два соседних столбца
    for c in range(4):
        c2 = (c + 1) % 4
        cells = {(r, c) for r in range(4)} | {(r, c2) for r in range(4)}
        groups.append(cells)
    # 3) Группы размера 4: одна строка из 4 ячеек
    for r in range(4):
        cells = {(r, c) for c in range(4)}
        groups.append(cells)
    # 4) Группы размера 4: один столбец
    for c in range(4):
        cells = {(r, c) for r in range(4)}
        groups.append(cells)
    # 5) Группы размера 4: все 2×2 «квартеты» (учитываем wrap-around)
    for r in range(4):
        r2 = (r + 1) % 4
        for c in range(4):
            c2 = (c + 1) % 4
            cells = {(r, c), (r, c2), (r2, c), (r2, c2)}
            groups.append(cells)
    # 6) Группы размера 2: горизонтальные пары
    for r in range(4):
        for c in range(4):
            c2 = (c + 1) % 4
            groups.append({(r, c), (r, c2)})
    # 7) Группы размера 2: вертикальные пары
    for r in range(4):
        for c in range(4):
            r2 = (r + 1) % 4
            groups.append({(r, c), (r2, c)})
    # 8) Группы размера 1: одиночные ячейки
    for r in range(4):
        for c in range(4):
            groups.append({(r, c)})
    return groups

# Кэшируем все возможные группы
_ALL_KMAP_GROUPS = _generate_all_groups()

def _find_prime_groups(kmap, target_value):
    valid_groups = []
    for group in _ALL_KMAP_GROUPS:
        if all(kmap[cell] == target_value for cell in group):
            valid_groups.append(group)
    # Оставляем только те, которые не содержатся строго в другой
    prime_groups = []
    for g in valid_groups:
        if not any((g < h) for h in valid_groups):
            prime_groups.append(g)
    return prime_groups

def _group_to_implicant(group, bit_map, is_dnf):
    tuples = [bit_map[cell] for cell in group]
    n = 4
    literals = []
    for i in range(n):
        bits = [t[i] for t in tuples]
        if all(b == bits[0] for b in bits):
            var = chr(ord('a') + i)
            val = bits[0]
            if is_dnf:
                lit = var if val == 1 else f"¬{var}"
            else:
                lit = var if val == 0 else f"¬{var}"
            literals.append(lit)
    if not literals:
        # Если группа «покрывает» все возможные комбинации => постоянная 1 (для ДНФ)
        # или постоянная 0 (для КНФ).
        return ["1"] if is_dnf else ["0"]
    if is_dnf:
        return [" & ".join(literals)]
    else:
        return [" ∨ ".join(literals)]

def minimize_dnf_karnaugh(minterms):
    # 1) Построим kmap: для каждой из 16 ячеек (r,c) проставим 1, если tuple в minterms, иначе 0.
    kmap = {}
    bit_map = {}
    for b0 in (0,1):
        for b1 in (0,1):
            for b2 in (0,1):
                for b3 in (0,1):
                    t = (b0, b1, b2, b3)
                    r, c = _tuple_to_rc(t)
                    bit_map[(r, c)] = t
                    kmap[(r, c)] = 1 if t in minterms else 0

    # 2) Найдём «prime groups» из ячеек, где значение = 1
    prime_groups = _find_prime_groups(kmap, target_value=1)

    # 3) Переведём каждую группу в строку-импликант
    implicants = []
    for grp in prime_groups:
        implicants.extend(_group_to_implicant(grp, bit_map, is_dnf=True))
    return implicants, kmap  # возвращаем ещё и сам kmap для вывода

def minimize_cnf_karnaugh(maxterms):
    # 1) Построим kmap: 1, если не в maxterms; 0, если в maxterms.
    kmap = {}
    bit_map = {}
    for b0 in (0,1):
        for b1 in (0,1):
            for b2 in (0,1):
                for b3 in (0,1):
                    t = (b0, b1, b2, b3)
                    r, c = _tuple_to_rc(t)
                    bit_map[(r, c)] = t
                    kmap[(r, c)] = 0 if t in maxterms else 1

    # 2) Чтобы искать группы нулей, построим «инвертированную» карту
    inverted = {cell: (1 if val == 0 else 0) for cell, val in kmap.items()}

    # 3) Найдём «prime groups» среди ячеек, где inverted[cell] == 1
    prime_groups = _find_prime_groups(inverted, target_value=1)

    # 4) Переведём каждую группу в строку-макстерм
    clauses = []
    for grp in prime_groups:
        clauses.extend(_group_to_implicant(grp, bit_map, is_dnf=False))
    return clauses, kmap  # возвращаем ещё kmap (для вывода, чтобы показать нули)

def format_sdnf(implicants):
    if not implicants:
        return "0"
    return " ∨ ".join(f"({imp})" for imp in implicants)

def format_sknf(clauses):
    if not clauses:
        return "1"
    return " ∧ ".join(f"({cl})" for cl in clauses)

def _print_kmap(kmap, title="K-map"):
    print(f"\n{title}:")
    # Сначала заголовок столбцов
    header = "    " + "  ".join(_gray2[c] for c in range(4))
    print(header)
    # Затем каждая строка (с кодом строки и значениями)
    for r in range(4):
        row_label = _gray2[r]
        row_vals = "  ".join(str(kmap[(r, c)]) for c in range(4))
        print(f"{row_label} | {row_vals}")
    print()

def karnau_min(dnf_input, cnf_input):
    # 1) СДНФ-часть
    dnf_implicants, dnf_kmap = minimize_dnf_karnaugh(dnf_input)
    print("=== СДНФ: карта Карно (1 = минтерм) ===")
    _print_kmap(dnf_kmap, title="K-map (SDNF, где 1 = минтерм)")
    print("Простые импликанты (СДНФ):")
    for implic in dnf_implicants:
        print("  ", implic)
    print("Минимизированная СДНФ:")
    print("  ", format_sdnf(dnf_implicants))

    # 2) СКНФ-часть
    cnf_clauses, cnf_kmap = minimize_cnf_karnaugh(cnf_input)
    # Карту CNF удобнее показать в исходном виде (0 = макстерм) и в инвертированном (1 = макстерм).
    print("\n=== СКНФ: карта Карно (0 = макстерм) ===")
    _print_kmap(cnf_kmap, title="K-map (CNF, где 0 = макстерм)")
    # Для наглядности инвертируем (0→1, 1→0) и показываем, какие ячейки считались единицами при поиске prime-групп
    inverted = {cell: (1 if val == 0 else 0) for cell, val in cnf_kmap.items()}
    print("Инвертированная карта (1 = макстерм):")
    _print_kmap(inverted, title="Inverted K-map (для поиска макстермов)")

    print("Простые макстермы (СКНФ):")
    for clause in cnf_clauses:
        print("  ", clause)
    print("Минимизированная СКНФ:")
    print("  ", format_sknf(cnf_clauses))

