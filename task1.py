p_input = 0


class Word:

    def __init__(self, typenum=10, word=""):
        """
        初始化Word类，用于存储词法分析结果。

        :param typenum: 单词的类型编号，默认为10（标识符）
        :param word: 单词字符串，默认为空字符串
        """
        self.typenum = typenum
        self.word = word


def scanner(input_str):
    """
    词法扫描器，从输入字符串中提取单词并返回其类型和值。

    :param input_str: 输入字符串
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


def main():
    """
    主函数，处理用户输入并调用词法扫描器。
    """
    while True:
        print("Enter Your words (end with #):")
        input_str = input().strip('#')  # 读取用户输入并去掉末尾的#
        over = 1
        global p_input
        p_input = 0
        while over < 1000 and over != -1:
            oneword = scanner(input_str)
            if oneword.word in ('\n', '\t'):
                continue
            if oneword.typenum < 1000:
                if oneword.typenum == 10:
                    print(f"({oneword.typenum}, '{oneword.word}')", end=' ')
                else:
                    print(f"({oneword.typenum}, {oneword.word})", end=' ')
                    # print(p_input)
                    # exit(0)
            over = oneword.typenum
        print("\npress # to exit:")
        if input() == '#':
            break


if __name__ == "__main__":
    main()
