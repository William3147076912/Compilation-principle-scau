import re


# 四元式结构
class Quad:
    def __init__(self, result, arg1, op, arg2):
        self.result = result
        self.arg1 = arg1
        self.op = op
        self.arg2 = arg2

    def __str__(self):
        return f"{self.result} = {self.arg1} {self.op} {self.arg2}"


# 词法分析器
def lexer(prog):
    token_patterns = [
        (r'begin|if|then|while|do|end', 'reserved_word'),
        (r'[a-zA-Z][a-zA-Z0-9]*', 'identifier'),
        (r'\d+', 'number'),
        (r'<>', 'neq'),
        (r'<=', 'leq'),
        (r'>=', 'geq'),
        (r':=', 'assign'),
        (r'[+\-*/()]', 'operator'),
        (r';', 'semicolon'),
        (r'\s+', None)  # 忽略空白
    ]
    token_re = '|'.join(f'(?P<{name}>{pattern})' for pattern, name in token_patterns)
    # print(token_re)
    match_iter = re.finditer(token_re, prog)
    tokens = []
    for match in match_iter:
        if match.lastgroup != 'None':
            tokens.append((match.group(), match.lastgroup))
    return tokens


# 语法分析器
def parser(tokens):
    quads = []
    temp_count = 0  # 用于生成唯一的临时变量名
    i = 0

    # 检查程序是否以 'begin' 开始
    if tokens[i][0] != 'begin':
        raise SyntaxError("Program must start with 'begin'")
    i += 1

    # 解析语句序列
    while i < len(tokens) and tokens[i][0] != 'end':
        token, token_type = tokens[i]
        if token_type == 'identifier':
            next_token, next_type = tokens[i + 1]
            if next_type == 'assign':
                i += 2
                expr_result, i, temp_count = expression_parser(tokens, i, quads, temp_count)
                quads.append(Quad(token, expr_result, '', ''))
            else:
                raise SyntaxError(f"Expected ':=' after identifier, got {next_token}")
        elif token == ';':
            i += 1
        else:
            raise SyntaxError(f"Unexpected token: {token}")

    # 检查程序是否以 'end' 结束
    if tokens[i][0] != 'end':
        raise SyntaxError("Program must end with 'end'")

    return quads


# 更新表达式解析器以返回更新后的索引和临时变量计数器
def expression_parser(tokens, start, quads, temp_count):
    term_result, i, temp_count = term_parser(tokens, start, quads, temp_count)
    while i < len(tokens) and tokens[i][0] in ('+', '-'):
        op = tokens[i][0]
        i += 1
        next_term_result, i, temp_count = term_parser(tokens, i, quads, temp_count)
        temp_count += 1
        temp_var = f't{temp_count}'
        quads.append(Quad(temp_var, term_result, op, next_term_result))
        term_result = temp_var
    return term_result, i, temp_count


# 更新项解析器以返回更新后的索引和临时变量计数器
def term_parser(tokens, start, quads, temp_count):
    factor_result, i, temp_count = factor_parser(tokens, start, quads, temp_count)
    while i < len(tokens) and tokens[i][0] in ('*', '/'):
        op = tokens[i][0]
        i += 1
        next_factor_result, i, temp_count = factor_parser(tokens, i, quads, temp_count)
        temp_count += 1
        temp_var = f't{temp_count}'
        quads.append(Quad(temp_var, factor_result, op, next_factor_result))
        factor_result = temp_var
    return factor_result, i, temp_count


# 更新因子解析器以返回更新后的索引和临时变量计数器
def factor_parser(tokens, start, quads, temp_count):
    i, (token, token_type) = start, tokens[start]
    if token_type in ('identifier', 'number'):
        return token, i + 1, temp_count
    elif token == '(':
        i += 1
        expr_result, i, temp_count = expression_parser(tokens, i, quads, temp_count)
        if tokens[i][0] != ')':
            raise SyntaxError("Missing closing parenthesis")
        i += 1
        return expr_result, i, temp_count
    else:
        raise SyntaxError(f"Unexpected token: {token}")


# 主函数
def main():
    prog = input("请输入字符串: ")
    tokens = lexer(prog)
    try:
        quads = parser(tokens)
        print("\n四元式:")
        for quad in quads:
            print(quad)
    except SyntaxError as e:
        print(f"\n语法错误: {e}")


if __name__ == "__main__":
    main()
