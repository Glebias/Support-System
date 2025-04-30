def integer_to_binary(num: int) -> str:
    binary_num = ""

    while len(binary_num) < 8:
        while num >= 1:
            binary_num = str(num % 2) + binary_num
            num //= 2
        binary_num = '0' + binary_num

    return binary_num.zfill(8)  # Дополняем до 8 бит

def to_forward_code(num: float) -> str:
    binary_forward_code = integer_to_binary(abs(num))

    if num >= 0:
        binary_forward_code = '0' + binary_forward_code
    else:
        binary_forward_code = '1' + binary_forward_code

    return binary_forward_code


def to_reverse_code(num) -> str:
    binary_reverse_code = ""

    if num >= 0:
        binary_reverse_code = integer_to_binary(num)
        binary_reverse_code = '0' + binary_reverse_code
        
    else:
        binary_reverse_code = "".join('1' if x == '0' else '0' for x in integer_to_binary(abs(num)))
        binary_reverse_code = '1' + binary_reverse_code

    return binary_reverse_code



def to_additive_code(num) -> str:
    binary_additive_code = ""
    
    if num >= 0:
        binary_additive_code = integer_to_binary(num)
        binary_additive_code = '0' + binary_additive_code

    else:
        binary_reverse_code = to_reverse_code(num)
        # Create binary number in additive code using the reverse code
        index = len(binary_reverse_code) - 1
        for num_ in binary_reverse_code[::-1]:
            if num_ == '0':
                binary_additive_code = '1' + binary_additive_code
                if index >= 0:
                    binary_additive_code = binary_reverse_code[:index] + binary_additive_code
                break
            else:
                binary_additive_code = '0' + binary_additive_code
                index -= 1
    
    return binary_additive_code



def convert_digit(num: float) -> tuple[str, str, str]:
    """Конвертирует число в прямой, обратный и дополнительный коды."""
    forward_code = to_forward_code(num)
    reverse_code = to_reverse_code(num)
    additive_code = to_additive_code(num)
    return forward_code, reverse_code, additive_code

def binary_to_decimal(binary: str) -> int:

    if not binary:
        raise ValueError("Входная строка не может быть пустой")

    for bit in binary:
        if bit not in ('0', '1'):
            raise ValueError("Некорректный бит в двоичном числе")

    decimal_value = 0
    for i, bit in enumerate(reversed(binary)):
        if bit == '1':
            decimal_value += 2 ** i

    return decimal_value

def decimal_to_binary_fixed_point(number: float) -> str:
    # Определяем знак числа
    if number < 0:
        sign_bit = '1'
        number = abs(number)
    else:
        sign_bit = '0'

    # Разделяем число на целую и дробную части
    integer_part = int(number)
    fractional_part = number - integer_part

    # Переводим целую часть в двоичный вид
    binary_integer = integer_to_binary(integer_part)  # Убираем префикс '0b'

    # Переводим дробную часть в двоичный вид с точностью до 5 знаков
    binary_fractional = ''
    for _ in range(5):
        fractional_part *= 2
        bit = int(fractional_part)
        binary_fractional += str(bit)
        fractional_part -= bit

    # Объединяем целую и дробную части
    binary_number = binary_integer + '.' + binary_fractional

    # Возвращаем результат в прямом коде (знак + число)
    return sign_bit + binary_number

def convert_digit_by_standart(digit_to_convert):

    sign_bit = '0' if digit_to_convert >= 0 else '1'
    digit_to_convert = abs(digit_to_convert)

    # Разделяем число на целую и дробную части
    integer_part = int(digit_to_convert)
    fractional_part = digit_to_convert - integer_part

    # Переводим целую часть в двоичный вид
    binary_integer = bin(integer_part)[2:]  # Убираем префикс '0b'

    # Переводим дробную часть в двоичный вид
    binary_fractional = ''
    for _ in range(23):  # Ограничиваем мантиссу 23 битами
        fractional_part *= 2
        bit = int(fractional_part)
        binary_fractional += str(bit)
        fractional_part -= bit

    # Объединяем целую и дробную части
    binary_number = binary_integer + '.' + binary_fractional

    # Нормализуем число (приводим к виду 1.xxxx * 2^exp)
    if binary_integer == '0':
        # Если целая часть равна нулю, ищем первую единицу в дробной части
        first_one_index = binary_fractional.find('1')
        if first_one_index == -1:
            # Все нули (число равно нулю)
            exponent = 0
            mantissa = '0' * 23
        else:
            # Сдвигаем точку вправо до первой единицы
            exponent = - (first_one_index + 1)
            mantissa = binary_fractional[first_one_index + 1:]  # Убираем первую единицу
    else:
        # Сдвигаем точку влево до целой части
        exponent = len(binary_integer) - 1
        mantissa = (binary_integer[1:] + binary_fractional)[:23]  # Берем первые 23 бита

    # Вычисляем смещенную экспоненту (bias = 127)
    biased_exponent = exponent + 127

    # Переводим экспоненту в двоичный вид (8 бит)
    exponent_binary = bin(biased_exponent)[2:].zfill(8)

    # Дополняем мантиссу до 23 бит
    mantissa = mantissa.ljust(23, '0')

    # Собираем результат
    result = sign_bit + exponent_binary + mantissa

    return result
