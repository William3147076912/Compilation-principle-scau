import re

import pandas as pd

# 单词符号及其种别码和类型描述
token_patterns = [
    (r'main', 'code_1', '标识符'),
    (r'int', 'code_2', '关键字'),
    (r'char', 'code_3', '关键字'),
    (r'if', 'code_4', '关键字'),
    (r'else', 'code_5', '关键字'),
    (r'for', 'code_6', '关键字'),
    (r'while', 'code_7', '关键字'),
    (r'[a-zA-Z_][a-zA-Z0-9_]*', 'code_10', '标识符'),  # 匹配字母开头的标识符
    (r'\d+', 'code_20', '数字字面量'),
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
    (r'==', 'code_39', '等于比较符'),
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
        type_description = next((p[2] for p in token_patterns if p[1] == match.lastgroup), (None, '未知'))
        tokens.append((token, code, type_description))
    return tokens


def main():
    prog = """
    main() {
        int a = 10;
        while (a > 0) {
            a = a - 1;
        }
    }
    """
    tokens = lexer(prog)
    # 创建DataFrame
    df = pd.DataFrame(tokens, columns=['单词符号', '种别码', '类型描述'])

    # 处理种别码
    df['种别码'] = df['种别码'].apply(lambda x: x[5:] if x[5] != 'm' else '-1')

    # 打印结果
    print("\n词法分析结果:")
    print(df.to_string(index=False))

    # 将结果写入Excel
    df.to_excel('词法分析结果.xlsx', index=False, engine='openpyxl')
    print("\n结果已保存到 '词法分析结果.xlsx' 文件中。")



if __name__ == "__main__":
    main()
