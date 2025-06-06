from convertations import *

def sum(first_num, second_num):
    first_num_bin = to_additive_code(first_num)
    second_num_bin = to_additive_code(second_num)
    
    carry = 0
    result = ""

    for i in range(len(first_num_bin) - 1, -1, -1):
        bit_sum = int(first_num_bin[i]) + int(second_num_bin[i]) + carry
        result = str(bit_sum % 2) + result
        carry = bit_sum // 2
    
    return result

def subtraction(first_num, second_num):
    first_num_bin = to_additive_code(first_num)
    second_num_bin = to_additive_code(-second_num)
    
    max_len = max(len(first_num_bin), len(second_num_bin))
    first_num_bin = first_num_bin.zfill(max_len)
    second_num_bin = second_num_bin.zfill(max_len)

    carry = 0
    result = ""

    for i in range(max_len - 1, -1, -1):
        bit_sum = int(first_num_bin[i]) + int(second_num_bin[i]) + carry
        result = str(bit_sum % 2) + result
        carry = bit_sum // 2
    
    return result

def binary_subtract(a: str, b: str) -> str:
 
    max_len = max(len(a), len(b))
    a = a.zfill(max_len)
    b = b.zfill(max_len)

    carry = 0
    result = ""
    for i in range(max_len - 1, -1, -1):
        bit_a = int(a[i])
        bit_b = int(b[i])
        bit_diff = bit_a - bit_b - carry

        if bit_diff < 0:
            bit_diff += 2
            carry = 1
        else:
            carry = 0

        result = str(bit_diff) + result

    return result


def multiplication(num1, num2):
    bin_num1 = to_forward_code(num1)
    bin_num2 = to_forward_code(num2)
    
    sign1 = bin_num1[0] if bin_num1[0] in '01' else '0' 
    sign2 = bin_num2[0] if bin_num2[0] in '01' else '0'  

    
    result_sign = '0' if sign1 == sign2 else '1'  

    bin1_mod = bin_num1[1:]  
    bin2_mod = bin_num2[1:]

    result_mod = '0'  

    for i, bit in enumerate(reversed(bin2_mod)):
        if bit == '1':
            
            shifted = bin1_mod + '0' * i
 
            max_len = max(len(result_mod), len(shifted))
            result_mod = result_mod.zfill(max_len)  
            shifted = shifted.zfill(max_len)  

            carry = 0
            new_result = []

           
            for j in range(max_len - 1, -1, -1):
                sum_bits = carry + int(result_mod[j]) + int(shifted[j])
                new_result.insert(0, str(sum_bits % 2))  
                carry = sum_bits // 2 

            if carry:
                new_result.insert(0, '1') 

            result_mod = ''.join(new_result)  

    
    result_mod = result_mod[-8:]  

    result = result_sign + result_mod

    return result


def binary_divide(num1: int, num2: int) -> str:
    
    if num2 == 0:
        raise ValueError("Деление на ноль невозможно!")

    # Переводим числа в прямой код
    bin_num1 = to_forward_code(num1)
    bin_num2 = to_forward_code(num2)

    # Определяем знак результата
    sign1, sign2 = bin_num1[0], bin_num2[0]
    result_sign = '0' if sign1 == sign2 else '1'

    # Убираем знаковый бит
    bin1_mod, bin2_mod = bin_num1[1:], bin_num2[1:]

    # Выравниваем длины двоичных чисел
    max_len = max(len(bin1_mod), len(bin2_mod))
    bin1_mod = bin1_mod.zfill(max_len)
    bin2_mod = bin2_mod.zfill(max_len)

    # Деление двоичных чисел
    result_int = ''
    remainder = '0' * len(bin2_mod)  # Инициализируем остаток нулями

    for i in range(max_len):
        # Сдвигаем остаток влево и добавляем текущий бит делимого
        remainder = remainder[1:] + bin1_mod[i]

        # Если остаток больше или равен делителю, выполняем вычитание
        if binary_to_decimal(remainder) >= binary_to_decimal(bin2_mod):
            result_int += '1'
            remainder = binary_subtract(remainder, bin2_mod)
        else:
            result_int += '0'

    # Вычисление дробной части (точность до 5 знаков)
    result_frac = ''
    for _ in range(5):
        remainder += '0'  # Умножаем остаток на 2 (сдвигаем влево)
        if binary_to_decimal(remainder) >= binary_to_decimal(bin2_mod):
            result_frac += '1'
            remainder = binary_subtract(remainder, bin2_mod)
        else:
            result_frac += '0'

    # Собираем итоговый результат
    result_mod = result_int + '.' + result_frac
    result = result_sign + result_mod

    return result

def float_sum_by_standart(num1: float, num2: float) -> str:
    # Преобразуем числа в формат IEEE 754
    num1 = convert_digit_by_standart(num1)
    num2 = convert_digit_by_standart(num2)

    # Извлекаем знак, экспоненту и мантиссу
    sign1, exponent1, mantissa1 = num1[0], binary_to_decimal(num1[1:9]) - 127, '1' + num1[9:]
    sign2, exponent2, mantissa2 = num2[0], binary_to_decimal(num2[1:9]) - 127, '1' + num2[9:]

    # Выравниваем экспоненты
    if exponent1 > exponent2:
        mantissa2 = shift_mantissa(mantissa2, exponent1 - exponent2)
        exponent = exponent1
    else:
        mantissa1 = shift_mantissa(mantissa1, exponent2 - exponent1)
        exponent = exponent2

    # Сложение мантисс
    result_mantissa = add_mantissas(mantissa1, mantissa2)

    # Нормализация результата
    if result_mantissa[0] == '1':  # Если мантисса больше 1, нормализуем
        result_mantissa = result_mantissa[1:]  # Убираем 1 в начале мантиссы
        exponent += 1  # Увеличиваем экспоненту
    else:
        shift = 0
        while result_mantissa[0] == '0':  # Если мантисса меньше 1, сдвигаем
            result_mantissa = result_mantissa[1:] + '0'
            shift += 1
        exponent -= shift  # Уменьшаем экспоненту, если было сдвигание

    # Возвращаем результат в формате IEEE 754
    return '0' + integer_to_binary(exponent + 127).zfill(8)[1:] + '0' + result_mantissa[1:23]

def shift_mantissa(mantissa: str, shift: int) -> str:
    return '0' * shift + mantissa[:len(mantissa) - shift] if shift > 0 else mantissa

def add_mantissas(mantissa1: str, mantissa2: str) -> str:
    carry = 0
    result = ''
    for i in range(len(mantissa1) - 1, -1, -1):
        bit_sum = int(mantissa1[i]) + int(mantissa2[i]) + carry
        result = str(bit_sum % 2) + result
        carry = bit_sum // 2
    if carry:
        result = '1' + result 
    return result




