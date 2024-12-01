p_input, input_str, kk = 0, '', 0


class Word:

    def __init__(self, typenum=10, word=""):
        """
        初始化Word类，用于存储词法分析结果。

        :param typenum: 单词的类型编号，默认为10（标识符）
        :param word: 单词字符串，默认为空字符串
        """
        self.typenum = typenum
        self.word = word


def scanner():
    """
    词法扫描器，从输入字符串中提取单词并返回其类型和值。

    :return: Word对象，包含单词的类型和值
    """
    rwtab = ["begin", "if", "then", "while", "do", "end"]  # 关键字表
    global p_input  # 当前读取位置
    token = ""  # 当前单词缓冲区

    def getch():
        """
        从输入字符串中读取一个字符。

        :return: 当前字符，如果到达字符串末尾则返回'\0'
        """
        global p_input
        if p_input < len(input_str):
            ch = input_str[p_input]
            p_input += 1
            return ch
        return '\0'

    def getbc():
        """
        跳过空白字符（空格、换行、制表符）。

        :return: 下一个非空白字符
        """
        ch = getch()
        while ch in (' ', '\n', '\t'):
            ch = getch()
        return ch

    def concat(ch):
        """
        将字符追加到当前单词缓冲区。

        :param ch: 要追加的字符
        """
        nonlocal token
        token += ch

    def letter(ch):
        """
        判断字符是否为字母。

        :param ch: 要判断的字符
        :return: 如果是字母返回True，否则返回False
        """
        return 'a' <= ch <= 'z' or 'A' <= ch <= 'Z'

    def digit(ch):
        """
        判断字符是否为数字。

        :param ch: 要判断的字符
        :return: 如果是数字返回True，否则返回False
        """
        return '0' <= ch <= '9'

    def reserve():
        """
        检查当前单词是否为关键字。

        :return: 如果是关键字返回其类型编号，否则返回10（标识符）
        """
        for i, kw in enumerate(rwtab):
            if token == kw:
                return i + 1
        return 10

    def retract():
        """
        回退一个字符。
        """
        global p_input
        p_input -= 1

    ch = getbc()  # 获取第一个非空白字符
    if letter(ch):
        # 处理标识符
        while letter(ch) or digit(ch):
            concat(ch)
            ch = getch()
        retract()
        return Word(reserve(), token)
    elif digit(ch):
        # 处理数字
        while digit(ch):
            concat(ch)
            ch = getch()
        retract()
        return Word(11, token)
    else:
        # 处理特殊字符
        if ch == '=':
            getch()
            if ch == '=':
                return Word(39, "==")
            retract()
            return Word(25, '=')
        elif ch == '+':
            return Word(13, '+')
        elif ch == '-':
            return Word(14, '-')
        elif ch == '*':
            return Word(15, '*')
        elif ch == '/':
            return Word(16, '/')
        elif ch == '(':
            return Word(27, '(')
        elif ch == ')':
            return Word(28, ')')
        elif ch == '[':
            return Word(29, '[')
        elif ch == ']':
            return Word(30, ']')
        elif ch == '{':
            return Word(31, '{')
        elif ch == '}':
            return Word(32, '}')
        elif ch == ',':
            return Word(33, ',')
        elif ch == ':':
            next_ch = getch()
            if next_ch == '=':
                return Word(18, ':=')
            retract()
            return Word(17, ':')
        elif ch == ';':
            return Word(26, ';')
        elif ch == '>':
            next_ch = getch()
            if next_ch == '=':
                return Word(24, '>=')
            retract()
            return Word(23, '>')
        elif ch == '<':
            next_ch = getch()
            if next_ch == '=':
                return Word(22, '<=')
            retract()
            return Word(20, '<')
        elif ch == '!':
            next_ch = getch()
            if next_ch == '=':
                return Word(40, '!=')
            retract()
            return Word(-1, 'ERROR')
        elif ch == '\0':
            return Word(1000, 'OVER')
        elif ch in ('\n', '\t'):
            return Word(-1, 'ERROR')  # 这里可以调整逻辑，根据需求处理换行和制表符
        else:
            return Word(-1, f'ERROR: Unexpected character {ch}')


# 语句串分析程序，用于解析输入的语句串
def lrparser(word):
    # 语句序列解析函数，处理语句是否以；号结尾
    def yucu(word):
        while True:
            word = statement(word)
            if word is None:
                return None
            if word.typenum == 26:  # 有；号
                word = scanner()
            else:
                break
        return word

    # 单个语句分析函数
    def statement(word):
        if word is None:
            return None
        if word.typenum == 10:  # 字符串
            w = scanner()
            if w.typenum == 18:  # 赋值符号
                w = scanner()
                w = expression(w)
                if w is None:
                    return None
                return w
            else:
                print("assignment token error! 赋值号错误")
                return None
        else:
            print("statement error! 语句错误")
            return None

    # 表达式分析函数
    def expression(word):
        w = term(word)
        if w is None:
            return None
        while w.typenum in (13, 14):  # +-法
            w = scanner()
            w = term(w)
            if w is None:
                return None
        return w

    # 项解析函数
    def term(word):
        w = factor(word)
        if w is None:
            return None
        while w.typenum in (15, 16):  # */法
            w = scanner()
            w = factor(w)
            if w is None:
                return None
        return w

    # 因子解析函数
    def factor(word):
        global kk
        if word is None:
            return None
        if word.typenum in (10, 11):
            return scanner()
        elif word.typenum == 27:  # (
            w = scanner()
            w = expression(w)
            if w is None or w.typenum != 28:  # )
                print(") error!  ')' 错误")
                kk = 1
                return None
            return scanner()
        else:
            print("expression error!  表达式错误")
            kk = 1
            return None

    global kk
    if word is None:
        return
    if word.typenum == 1:  # 种别码为1，有关键字begin
        w = scanner()
        w = yucu(w)
        if w is None:
            return
        if w.typenum == 6:  # 种别码为6，有关键字end
            scanner()
            print("success  成功")
            # if w.typenum == 0 and kk == 0:
            #     print("success  成功")
            # else:
            #     print("Unexpected token after END!  在END后出现意外的符号")
        else:
            if kk != 1:
                print("lack END error!  错误 缺少END")
            kk = 1
    else:
        print("Begin error!  begin 错误")
        kk = 1


def main():
    """
    主函数，处理用户输入并调用词法扫描器。
    """
    while True:
        global p_input, input_str, kk
        print("Enter Your words (end with #):")
        input_str = input().strip('#')  # 读取用户输入并去掉末尾的#
        p_input = 0
        kk = 0
        print("Your words:", input_str)
        oneword = scanner()
        lrparser(oneword)
        print("press # to exit:")
        if input() == '#':
            break


if __name__ == "__main__":
    main()
