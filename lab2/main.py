import itertools
import re

class ExpressionParser:
    def __init__(self):
        self.operators = {
            'not': {'prec': 5, 'assoc': 'right'},
            '!': {'prec': 5, 'assoc': 'right'},
            'and': {'prec': 4, 'assoc': 'left'},
            '&': {'prec': 4, 'assoc': 'left'},
            'or': {'prec': 3, 'assoc': 'left'},
            '|': {'prec': 3, 'assoc': 'left'},
            '→': {'prec': 2, 'assoc': 'right'},
            '↔': {'prec': 1, 'assoc': 'left'},
        }

    def tokenize(self, expr):
        token_re = re.compile(r'(\d+|\w+|→|↔|\(|\)|!|&|\||and|or|not)')
        tokens = []
        for match in token_re.finditer(expr):
            token = match.group(1).lower()
            if token == '!':  # Преобразуем ! в not
                tokens.append('not')
            else:
                tokens.append(token)
        return tokens

    def parse(self, expr):
        tokens = self.tokenize(expr)
        output = []
        stack = []
        for token in tokens:
            if token == '(':
                stack.append(token)
            elif token == ')':
                while stack and stack[-1] != '(':
                    output.append(stack.pop())
                stack.pop()
            elif token in self.operators:
                while stack and stack[-1] != '(' and self._compare_precedence(token, stack[-1]):
                    output.append(stack.pop())
                stack.append(token)
            else:
                output.append(token)
        while stack:
            output.append(stack.pop())
        return output

    def _compare_precedence(self, op1, op2):
        if op2 not in self.operators:
            return False
        op1_prec = self.operators[op1]['prec']
        op2_prec = self.operators[op2]['prec']
        if self.operators[op1]['assoc'] == 'left':
            return op1_prec <= op2_prec
        else:
            return op1_prec < op2_prec

def evaluate_postfix(postfix, variables_values):
    stack = []
    for token in postfix:
        if token in {'not', 'and', 'or', '→', '↔', '&', '|'}:
            if token == 'not':
                a = stack.pop()
                stack.append(not a)
            else:
                b = stack.pop()
                a = stack.pop() if token != 'not' else None
                if token == 'and' or token == '&':
                    stack.append(a and b)
                elif token == 'or' or token == '|':
                    stack.append(a or b)
                elif token == '→':
                    stack.append((not a) or b)
                elif token == '↔':
                    stack.append((a and b) or (not a and not b))
        elif token in variables_values:
            stack.append(variables_values[token])
        elif token.isdigit():
            stack.append(bool(int(token)))
        else:
            raise ValueError(f"Неизвестный токен: {token}")
    return stack.pop()

def get_variables(expr):
    variables = sorted(set(re.findall(r'\b[a-zA-Z]\b', expr)))
    return variables

def generate_truth_table(expr, variables):
    parser = ExpressionParser()
    try:
        postfix = parser.parse(expr)
    except Exception as e:
        print(f"Ошибка при разборе выражения: {e}")
        return []
    truth_table = []
    for combo in itertools.product([False, True], repeat=len(variables)):
        var_dict = {var: val for var, val in zip(variables, combo)}
        try:
            result = evaluate_postfix(postfix, var_dict)
        except Exception as e:
            print(f"Ошибка вычисления: {e}")
            return []
        combo_bin = [int(val) for val in combo]
        truth_table.append((combo_bin, int(result)))
    return truth_table

def build_sdnf_sknf(truth_table, variables):
    sdnf_terms = []
    sknf_terms = []
    sdnf_nums = []
    sknf_nums = []
    num_vars = len(variables)
    
    for combo, result in truth_table:
        num = sum(val << (num_vars - 1 - i) for i, val in enumerate(combo))
        if result == 1:
            # Формирование СДНФ
            sdnf_nums.append(num)
            terms = [f"!{var}" if val == 0 else var for var, val in zip(variables, combo)]
            sdnf_terms.append(f"({' & '.join(terms)})")
        else:
            # Формирование СКНФ (исправлено)
            sknf_nums.append(num)
            terms = [f"!{var}" if val == 1 else var for var, val in zip(variables, combo)]
            sknf_terms.append(f"({' | '.join(terms)})")
    
    sdnf = ' | '.join(sdnf_terms) if sdnf_terms else '0'
    sknf = ' & '.join(sknf_terms) if sknf_terms else '1'
    return sdnf, sknf, sdnf_nums, sknf_nums

def build_index_form(truth_table):
    binary_str = ''.join(str(result) for _, result in truth_table)
    return int(binary_str, 2) if binary_str else 0

# def main():
#     expr = input("Введите логическую функцию (например, (a->b)&c): ")
#     translated_expr = expr.replace('->', '→').replace('~', '↔')
#     variables = get_variables(translated_expr)
#     if not variables:
#         print("Нет переменных в выражении.")
#         return
#     if len(variables) > 5:
#         print("Допустимо до 5 переменных.")
#         return
#     truth_table = generate_truth_table(translated_expr, variables)
#     if not truth_table:
#         return
#     sdnf, sknf, sdnf_nums, sknf_nums = build_sdnf_sknf(truth_table, variables)
#     index_form = build_index_form(truth_table)
    
#     print("\nТаблица истинности:")
#     header = " | ".join(variables) + " | Результат"
#     print(header)
#     print("-" * len(header))
#     for combo, res in truth_table:
#         row = " | ".join(map(str, combo)) + f" | {res}"
#         print(row)
    
#     print("\nСДНФ:", sdnf)
#     print("Числовая форма (СДНФ):", ", ".join(map(str, sdnf_nums)) if sdnf_nums else "нет")
#     print("\nСКНФ:", sknf)
#     print("Числовая форма (СКНФ):", ", ".join(map(str, sknf_nums)) if sknf_nums else "нет")
#     print("\nИндексная форма:", index_form)

# if __name__ == "__main__":
#     main()