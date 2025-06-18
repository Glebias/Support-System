import random
from typing import List, Tuple

def f4(x: int, y: int) -> int:  
    return int(not x and y)

def f6(x: int, y: int) -> int:  
    return x ^ y

def f9(x: int, y: int) -> int:  
    return int(not (x ^ y))

def f11(x: int, y: int) -> int: 
    return int(x or not y)

def build_matrix(n = 16):
    return [[random.randint(0, 1) for _ in range(n)] for _ in range(n)]

def print_matrix(matrix):
    for row in matrix:
        print(' '.join(str(x) for x in row))

def get_word(matrix, idx):
    n = len(matrix)
    return [matrix[(idx + i) % n][idx] for i in range(n)]

def set_word(matrix, idx, word):
    n = len(matrix)
    for i in range(n):
        matrix[(idx + i) % n][idx] = word[i]
    return matrix

def read_addressed_column(matrix, idx):
    n = len(matrix)
    return [matrix[(idx + i) % n][i] for i in range(n)]

def set_addressed_column(matrix, idx, word):
    n = len(matrix)
    for i in range(n):
        matrix[(idx + i) % n][i] = word[i]
    return matrix

def execute_log_operations(log_func, idx1, idx2, res_idx, matrix):
    word1 = get_word(matrix, idx1)
    word2 = get_word(matrix, idx2)

    n = len(matrix)
    res_word = [log_func(word1[i], word2[i]) for i in range(n)]
    matrix = set_word(matrix, res_idx, res_word)

    return matrix

def compare_binary(s: List[int], a: List[int], idx: int = 0, g: int = False, l: int = False) -> Tuple[bool, bool]:
    new_g = g or (s[idx] and (not a[idx]) and (not l))
    new_l = l or ((not s[idx]) and a[idx] and (not g))
    if idx != len(s) - 1:
        return compare_binary(s, a, idx + 1, new_g, new_l)
    else:
        return new_g, new_l

# Сортировка выбором по бинарным спискам
def selection_sort_bin(numbers: List[List[int]]) -> List[List[int]]:
    n = len(numbers)
    for i in range(n):
        min_idx = i
        for j in range(i + 1, n):
            g, l = compare_binary(numbers[j], numbers[min_idx])
            if l:  # numbers[j] < numbers[min_idx]
                min_idx = j
        # Обмен
        numbers[i], numbers[min_idx] = numbers[min_idx], numbers[i]
    return numbers

def selection_sort(matrix):
    current_list: List[List[int]] = []

    for i in range(len(matrix)):
        word = get_word(matrix, i)
        current_list.append(word)
    
    result_list = selection_sort_bin(current_list)

    for i in range(len(matrix)):
        word = result_list[i]
        matrix = set_word(matrix, i, word)

    return matrix

def process_bin16(bits: List[int]) -> List[int]:
    # if len(bits) != 16 or any(b not in (0, 1) for b in bits):
    #     raise ValueError("На вход подан список не из 16 бит")

    # Выделяем сегменты
    V = bits[0:3]      # 3 бита
    A = bits[3:7]      # 4 бита
    B = bits[7:11]     # 4 бита
    
    a_val = int("".join(str(b) for b in A), 2)
    b_val = int("".join(str(b) for b in B), 2)

    sum_val = (a_val + b_val) & 0b11111  

    S_new = [int(x) for x in f"{sum_val:05b}"]

    # Собираем итоговый список
    result = []
    result.extend(V)
    result.extend(A)
    result.extend(B)
    result.extend(S_new)

    return result

def sum_by_key(matrix, key: List[int]):

    for i in range(len(matrix)):
        word = get_word(matrix, i)
        word_bits = word[0:3]

        a_val = "".join(str(b) for b in word_bits)
        b_val = "".join(str(b) for b in key)

        if a_val == b_val:
            res = process_bin16(word)
            print(f"Слово: {word}, под номером {i} переходит в: {res}")
            matrix = set_word(matrix, i, res)
    
    return matrix


if __name__ == "__main__":
    matrix = build_matrix(16)

    print("Исходная матрица:")
    print_matrix(matrix)

    idx = 2
    word1 = get_word(matrix, idx)
    word2 = read_addressed_column(matrix, idx)
    print(f"Получили слово под номером {idx}:")
    print(' '.join(str(x) for x in word1))
    print(f"Получили адресный столбец под номером {idx}:")
    print(' '.join(str(x) for x in word2))

    matrix = execute_log_operations(f4,6,7,idx,matrix)
    word1 = get_word(matrix, idx)
    print(f"Получили новое слово слово под номером {idx}, после применения логических операций:")
    print(' '.join(str(x) for x in word1))

    matrix = selection_sort(matrix)
    print("Матрица после сортировки:")
    print_matrix(matrix)

    key = [1,0,0]
    matrix = sum_by_key(matrix, key) 
