import re
import pandas as pd

# 单词符号及其种别码和类型描述
token_patterns = [
    (r'main', 'code_1', '预定义标识符'),
    (r'int', 'code_2', '关键字'),
    (r'char', 'code_3', '关键字'),
    (r'if', 'code_4', '关键字'),
    (r'else', 'code_5', '关键字'),
    (r'for', 'code_6', '关键字'),
    (r'while', 'code_7', '关键字'),
    (r'[a-zA-Z_][a-zA-Z0-9_]*', 'code_10', '标识符'),  # 匹配字母开头的标识符
    (r'\d+(\.\d+)?', 'code_20', '数字字面量'),
    (r'==', 'code_39', '等于比较符'),
    (r'=', 'code_21', '赋值运算符'),
    (r'\+', 'code_22', '加法运算符'),
    (r'-', 'code_23', '减法运算符'),
    (r'\*', 'code_24', '乘法运算符'),
    (r'/', 'code_25', '除法运算符'),
    (r'\(', 'code_26', '左括号'),
    (r'\)', 'code_27', '右括号'),
    (r'\[', 'code_28', '左方括号'),
    (r'\]', 'code_29', '右方括号'),
    (r'\{', 'code_30', '左大括号'),
    (r'\}', 'code_31', '右大括号'),
    (r'\.', 'code_32', '点运算符'),
    (r':', 'code_33', '冒号'),
    (r';', 'code_34', '分号'),
    (r'>', 'code_35', '大于比较符'),
    (r'<', 'code_36', '小于比较符'),
    (r'>=', 'code_37', '大于等于比较符'),
    (r'<=', 'code_38', '小于等于比较符'),
    (r'!=', 'code_40', '不等于比较符'),
    (r'\\0', 'code_1000', '空字符'),
    (r'ERROR', 'code_m1', '错误')  # 通配符匹配其他所有字符
]

# 编译正则表达式
token_re = '|'.join(f'(?P<{name}>{pattern})' for pattern, name, _ in token_patterns)


def lexer(prog):
    match_iter = re.finditer(token_re, prog)
    tokens = []

    for match in match_iter:
        token = match.group(match.lastgroup)  # 获取匹配的token
        code = match.lastgroup
        code = code[5:] if code[5] != 'm' else '-1'  # 处理种别码
        type_description = next((p[2] for p in token_patterns if p[1] == match.lastgroup), (None, '未知'))
        start_pos = match.start()  # 记录token的起始位置

        tokens.append((token, code, type_description, start_pos))

    return tokens


class Quad:
    def __init__(self, op, arg1, arg2, result):
        self.op = op  # 操作符
        self.arg1 = arg1  # 第一个操作数
        self.arg2 = arg2  # 第二个操作数（可选）
        self.result = result  # 结果（目标变量或跳转标签）

    def __str__(self):
        if self.op == 'ifFalse':
            return f"{self.op} {self.arg1} goto {self.result}"
        elif self.op == 'goto':
            return f"{self.op} {self.arg1} {self.result}"
        elif self.op == 'label':
            return f"{self.result}:"
        elif self.arg2:  # 例如 t1 = a + b
            return f"{self.result} = {self.arg1} {self.op} {self.arg2}"
        else:  # 赋值语句 t1 = 5
            return f"{self.result} = {self.arg1}"


def parser(tokens):
    quads = []
    temp_count = 0  # 用于生成唯一的临时变量名
    label_count = 0  # 用于生成标签

    def get_line_number(pos):
        """根据字符位置获取行号"""
        return prog[:pos].count('\n') + 1

    def program():
        if tokens[0][0] == 'main' and tokens[0][1] == '1':
            tokens.pop(0)
            if tokens[0][0] == '(' and tokens[0][1] == '26':
                tokens.pop(0)
                if tokens[0][0] == ')' and tokens[0][1] == '27':
                    tokens.pop(0)
                    return statement_block()
        raise SyntaxError(f"Invalid program at line {get_line_number(tokens[0][3])}, tips: {tokens[0]}")

    def statement_block():
        if tokens[0][0] == '{' and tokens[0][1] == '30':
            tokens.pop(0)
            while tokens and tokens[0][0] != '}':
                statement()
                if tokens[0][0] == ';' and tokens[0][1] == '34':
                    tokens.pop(0)
                    continue
            if tokens[0][0] == '}' and tokens[0][1] == '31':
                tokens.pop(0)
                return True
        elif tokens and (tokens[0][0] in ['if', 'while'] or tokens[0][1] == '10'):
            statement()
            return True
        raise SyntaxError(f"Invalid statement block at line {get_line_number(tokens[0][3])}, tips: {tokens[0]}")

    def statement():
        if tokens[0][0] == 'if' and tokens[0][1] == '4':
            return if_statement()
        elif tokens[0][0] == 'while' and tokens[0][1] == '7':
            return while_statement()
        elif tokens[0][2] == '标识符' and tokens[0][1] == '10':
            return assignment_statement()
        else:
            raise SyntaxError(f"Invalid statement at line {get_line_number(tokens[0][3])}, tips: {tokens[0]}")

    def if_statement():
        nonlocal tokens, quads, label_count
        if tokens and tokens[0][0] == 'if' and tokens[0][1] == '4':
            tokens.pop(0)
            if tokens[0][0] == '(' and tokens[0][1] == '26':
                tokens.pop(0)
                condition_result = condition()  # 获取比较结果的临时变量
                if tokens[0][0] == ')' and tokens[0][1] == '27':
                    tokens.pop(0)
                    # 生成跳转三地址代码
                    if_true_label = f'L{label_count}'
                    label_count += 1
                    if_false_label = f'L{label_count}'
                    label_count += 1
                    quads.append(Quad('ifFalse', condition_result, '', if_false_label))
                    quads.append(Quad('goto', '', '', if_true_label))
                    quads.append(Quad('label', '', '', if_true_label))
                    statement_block()  # 执行if语句块
                    quads.append(Quad('label', '', '', if_false_label))  # 如果条件不成立，跳到else部分
                    return True
        raise SyntaxError(f"Invalid if statement at line {get_line_number(tokens[0][3])}, tips: {tokens[0]}")

    def while_statement():
        nonlocal tokens, quads, label_count
        if tokens and tokens[0][0] == 'while' and tokens[0][1] == '7':
            start_label = f'L{label_count}'
            label_count += 1
            end_label = f'L{label_count}'
            label_count += 1
            quads.append(Quad('label', '', '', start_label))  # While的开始标签
            tokens.pop(0)
            if tokens[0][0] == '(' and tokens[0][1] == '26':
                tokens.pop(0)
                condition_result = condition()  # 获取条件表达式的计算结果
                if tokens[0][0] == ')' and tokens[0][1] == '27':
                    tokens.pop(0)
                    # 生成while语句的跳转
                    quads.append(Quad('ifFalse', condition_result, '', end_label))  # 条件为False时跳出循环
                    # quads.append(Quad('label', '', '', start_label))  # 进入循环体
                    statement_block()
                    quads.append(Quad('goto', '', '', start_label))  # 如果条件成立，跳回start_label
                    quads.append(Quad('label', '', '', end_label))  # while循环结束后的标签
                    return True
        raise SyntaxError(f"Invalid while statement at line {get_line_number(tokens[0][3])}, tips: {tokens[0]}")

    def assignment_statement():
        nonlocal tokens, quads, temp_count
        if tokens and tokens[0][2] == '标识符' and tokens[0][1] == '10':
            target = tokens.pop(0)[0]
            if tokens and tokens[0][0] == '=' and tokens[0][1] == '21':
                tokens.pop(0)
                expr_result = expression()  # 获取右侧表达式的计算结果
                quads.append(Quad('=', expr_result, '', target))  # 生成赋值三地址代码
                return True
        raise SyntaxError(f"Invalid assignment statement at line {get_line_number(tokens[0][3])}, tips: {tokens[0]}")

    def condition():
        nonlocal tokens, quads, temp_count

        # 解析条件表达式
        left_expr_result = expression()  # 获取左侧的表达式结果

        # 解析条件运算符 (<, >, <=, >=, ==, !=)
        if tokens[0][0] in ['<', '>', '<=', '>=', '==', '!='] and tokens[0][1] in ['35', '36', '37', '38', '39', '40']:
            op = tokens.pop(0)[0]  # 获取比较运算符
            right_expr_result = expression()  # 解析右侧的表达式

            # 为条件表达式生成一个临时变量来保存比较结果
            temp_count += 1
            temp_var = f't{temp_count}'

            # 生成三地址代码：比较运算
            quads.append(Quad(op, left_expr_result, right_expr_result, temp_var))

            # 返回临时变量作为条件判断的结果
            return temp_var

        raise SyntaxError(f"Invalid condition at line {get_line_number(tokens[0][3])}, tips: {tokens[0]}")

    def expression():
        nonlocal tokens, quads, temp_count
        term_result = term()  # 处理表达式中的项
        while tokens and tokens[0][0] in ['+', '-', '*', '/'] and tokens[0][1] in ['22', '23', '24', '25']:
            op = tokens.pop(0)[0]
            next_term_result = term()
            temp_count += 1
            temp_var = f't{temp_count}'
            quads.append(Quad(op, term_result, next_term_result, temp_var))
            term_result = temp_var
        return term_result

    def term():
        nonlocal tokens, quads, temp_count
        # 处理项中的操作符
        if tokens[0][0] == '(' and tokens[0][1] == '26':
            tokens.pop(0)
            result = expression()
            if tokens[0][0] == ')' and tokens[0][1] == '27':
                tokens.pop(0)
            return result
        elif tokens[0][2] == '数字字面量' and tokens[0][1] == '20':
            return tokens.pop(0)[0]
        elif tokens[0][2] == '标识符' and tokens[0][1] == '10':
            return tokens.pop(0)[0]

        raise SyntaxError(f"Invalid term at line {get_line_number(tokens[0][3])}, tips: {tokens[0]}")

    # 执行程序的分析
    try:
        program()
        if tokens:
            raise SyntaxError(f"Unexpected tokens remaining at line {get_line_number(tokens[0][3])}, tips: {tokens[0]}")
        return quads
    except SyntaxError as e:
        print(f"解析过程中发生错误: {e}")
        return []


def main():
    global prog
    with open('input.txt', 'r', encoding='utf-8') as file:
        prog = file.read()

    tokens = lexer(prog)
    # 创建DataFrame
    df = pd.DataFrame(tokens, columns=['单词符号', '种别码', '类型描述', '起始位置'])

    # 处理==在excel中的冲突
    df['单词符号'] = df['单词符号'].apply(lambda x: " " + x if x == '==' else x)

    # 打印结果
    print("\n词法分析结果:")
    print(df[['单词符号', '种别码', '类型描述']].to_string(index=False))

    # 将结果写入Excel
    df.to_excel('词法分析结果.xlsx', index=False, engine='openpyxl')
    print("\n结果已保存到 '词法分析结果.xlsx' 文件中。")

    quads = parser(tokens)
    print("\n三地址代码:")
    for quad in quads:
        print(quad)


if __name__ == "__main__":
    main()
