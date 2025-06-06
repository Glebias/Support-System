LATIN_ALPHABET = [chr(i) for i in range(ord('A'), ord('Z') + 1)]

def diag_index_to_coords(k: int, N: int) -> tuple[int, int]:
    if k < 0 or k >= N * N:
        raise IndexError(f"Index k={k} out of range for N={N}")
    coords = []
    for d in range(2 * N - 1):
        start_i = max(0, d - (N - 1))
        end_i = min(N - 1, d)
        diag = [(i, d - i) for i in range(start_i, end_i + 1)]
        if d % 2 == 1:
            diag.reverse()
        coords.extend(diag)
    return coords[k]

def coords_to_diag_index(i: int, j: int, N: int) -> int:
    d = i + j
    base = d * (d + 1) // 2
    offset = i if d % 2 == 0 else j
    return base + offset

# Булевы функции для варианта 3
def f4(x: int, y: int) -> int:  # Запрет 2-го аргумента
    return int(x and not y)

def f6(x: int, y: int) -> int:  # Неравнозначность (XOR)
    return x ^ y

def f9(x: int, y: int) -> int:  # Эквивалентность (XNOR)
    return int(not (x ^ y))

def f11(x: int, y: int) -> int:  # Импликация (x→y)
    return int(not x or y)

class DiagMatrixProcessor:
    def __init__(self, matrix: list[list[int]]):
        self.mat = matrix
        self.N = len(matrix)
        self.word_size = 16  # Фиксированный размер слова
        
    def get_word(self, col: int, start_row: int) -> int:
        """Формирует 16-битное слово из столбца col, начиная со строки start_row"""
        word = 0
        for i in range(self.word_size):
            row_idx = (start_row + i) % self.N
            bit = self.mat[row_idx][col]
            word = (word << 1) | bit
        return word

    def update_matrix_from_word(self, col: int, start_row: int, word: int):
        """Обновляет матрицу из 16-битного слова"""
        for i in range(self.word_size-1, -1, -1):
            row_idx = (start_row + i) % self.N
            bit = (word >> (self.word_size - 1 - i)) & 1
            self.mat[row_idx][col] = bit

    def process(self, col_a: int, col_b: int, func) -> list[tuple[int, int]]:
        """Применяет булеву функцию к битам из двух столбцов"""
        results = []
        total = self.N * self.N
        for k in range(total):
            i, j = diag_index_to_coords(k, self.N)
            bit_a = self.mat[i][col_a]
            bit_b = self.mat[i][col_b]
            val = func(bit_a, bit_b)
            results.append((k, val))
        results.sort(key=lambda x: (x[1], x[0]))
        return results

    def add_fields_with_v(self, v_value: int):
        """Складывает поля A и B в словах с заданным значением V"""
        updates = []  # Сохраняем изменения для применения
        for col in range(self.N):
            for start_row in range(self.N):
                word = self.get_word(col, start_row)
                # Извлекаем поле V (биты 13-15)
                V = (word >> 13) & 0b111
                if V == v_value:
                    # Извлекаем поля A (биты 10-12) и B (биты 7-9)
                    A = (word >> 10) & 0b111
                    B = (word >> 7) & 0b111
                    # Складываем и обновляем поле A
                    C = (A + B) & 0b111
                    # Очищаем поле A и записыем новое значение
                    new_word = word & ~(0b111 << 10)
                    new_word |= (C << 10)
                    updates.append((col, start_row, new_word))
        
        # Применяем все обновления
        for col, start_row, new_word in updates:
            self.update_matrix_from_word(col, start_row, new_word)

    def execute_variant3(self, col_a: int, col_b: int, v_value: int) -> dict:
        """Выполняет все операции варианта 3"""
        # Применяем логические функции
        results = {
            'f6': self.process(col_a, col_b, f6),
            'f9': self.process(col_a, col_b, f9),
            'f4': self.process(col_a, col_b, f4),
            'f11': self.process(col_a, col_b, f11),
        }
        # Выполняем арифметическую операцию
        self.add_fields_with_v(v_value)
        return results

    def get_sorted_words(self) -> list[int]:
        """Возвращает отсортированный список слов"""
        words = []
        for col in range(self.N):
            for start_row in range(self.N):
                words.append(self.get_word(col, start_row))
        words.sort()
        return words
    
    def select_and_sum_fields_with_v(self, v_value: int) -> list[tuple[int, int]]:
        """
        Выбирает слова, где поле V совпадает с заданным значением,
        затем выбирает поля A и B и возвращает их сумму для каждого слова.
        
        :param v_value: Значение поля V для фильтрации слов
        :return: Список кортежей (индекс_слова, сумма_A_B)
        """
        results = []
        for col in range(self.N):
            for start_row in range(self.N):
                word = self.get_word(col, start_row)
                # Извлекаем поле V (биты 13-15)
                V = (word >> 13) & 0b111
                if V == v_value:
                    # Извлекаем поля A (биты 10-12) и B (биты 7-9)
                    A = (word >> 10) & 0b111
                    B = (word >> 7) & 0b111
                    # Складываем A и B
                    sum_AB = A + B
                    # Сохраняем индекс слова и сумму
                    word_index = col * self.N + start_row
                    results.append((word_index, sum_AB))
        return results

def parse_binary_matrix(input_str: str) -> list[list[int]]:
    """Парсит строковое представление бинарной матрицы 16x16"""
    lines = input_str.strip().split('\n')
    matrix = []
    for line in lines:
        line = line.strip()
        if not line or line.startswith('|'):
            continue
        # Удаляем пробелы и преобразуем каждый символ в int
        row = [int(bit) for bit in line.replace(' ', '')]
        if len(row) != 16:
            raise ValueError("Each row must have exactly 16 bits")
        matrix.append(row)
    
    if len(matrix) != 16:
        raise ValueError("Matrix must have exactly 16 rows")
    
    return matrix

def generate_test_matrix():
    """Генерирует тестовую матрицу 16x16 с заданными V=5"""
    import random
    matrix = []
    for i in range(16):
        row = []
        for j in range(16):
            # Для столбцов 0 и 1 создаем чередующийся паттерн
            if j == 0:
                row.append(i % 2)  # 0,1,0,1...
            elif j == 1:
                row.append((i + 1) % 2)  # 1,0,1,0...
            else:
                row.append(random.randint(0, 1))
        matrix.append(row)
    
    # Установим V=5 (0b101) для некоторых слов
    # Для столбца 2, start_row=3: установим биты 13,14,15 = 1,0,1
    matrix[(3 + 13) % 16][2] = 1  # Бит 13
    matrix[(3 + 14) % 16][2] = 0  # Бит 14
    matrix[(3 + 15) % 16][2] = 1  # Бит 15
    
    # Для столбца 3, start_row=7
    matrix[(7 + 13) % 16][3] = 1
    matrix[(7 + 14) % 16][3] = 0
    matrix[(7 + 15) % 16][3] = 1
    
    return matrix

# Пример использования
if __name__ == "__main__":
    # Генерируем тестовую матрицу 16x16
    matrix = generate_test_matrix()
    
    print("Первые 4 строки матрицы:")
    for i in range(4):
        print(''.join(str(bit) for bit in matrix[i][:4]) + "...")
    
    processor = DiagMatrixProcessor(matrix)
    
    # Параметры варианта 3
    col_a = 0  # Первый столбец
    col_b = 1  # Второй столбец
    v_value = 0b101  # V=5 (0b101)
    
    # Выполняем операции варианта 3
    results = processor.execute_variant3(col_a, col_b, v_value)
    
    print("\nРезультаты логических операций (первые 5 элементов):")
    for func, data in results.items():
        print(f"{func}: {data[:5]}")
    
    # Проверяем изменения в матрице для слов с V=5
    print("\nПроверка обновления поля A:")
    # Для столбца 2, start_row=3
    word_before = processor.get_word(2, 3)
    print(f"Слово (col=2, start_row=3) до: {word_before:016b}")
    
    # Для столбца 3, start_row=7
    word_before = processor.get_word(3, 7)
    print(f"Слово (col=3, start_row=7) до: {word_before:016b}")
    
    # После обработки
    print("\nОбновленная матрица (первые 4 строки):")
    for i in range(4):
        print(''.join(str(bit) for bit in processor.mat[i][:4]) + "...")
    
    word_after = processor.get_word(2, 3)
    print(f"\nСлово (col=2, start_row=3) после: {word_after:016b}")
    
    word_after = processor.get_word(3, 7)
    print(f"Слово (col=3, start_row=7) после: {word_after:016b}")
    
    # Получаем и выводим отсортированный список слов
    sorted_words = processor.get_sorted_words()
    print("\nОтсортированные слова (первые 5):")
    for word in sorted_words[:5]:
        print(f"{word:016b} (дес: {word})")
        