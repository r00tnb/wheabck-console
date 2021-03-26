'''美化输出内容

Description:
    用于美化输出到命令行的内容，包括颜色高亮、格式化等

Export:
    colour 着色器的实例

'''
import re
import src.config as config
import unicodedata

class Colour:
    '''对字符串着色、改变样式

    Description:
        对输出到终端的字符串着色及改变它的样式

    '''
    color = {
        "fore": {   # 前景色
            'black': 30,  # 黑色
            'red': 31,  # 红色
            'green': 32,  # 绿色
            'blue': 34,  # 蓝色
            'yellow': 33,  # 黄色
            'purple': 35,  # 紫红色
            'cyan': 36,  # 青蓝色
            'white': 37,  # 白色
        },
        'back': {   # 背景
            'black': 40,  # 黑色
            'red': 41,  # 红色
            'green': 42,  # 绿色
            'yellow': 43,  # 黄色
            'blue': 44,  # 蓝色
            'purple': 45,  # 紫红色
            'cyan': 46,  # 青蓝色
            'white': 47,  # 白色
        },
        'mode': {   # 显示模式
            'mormal': 0,  # 终端默认设置
            'bold': 1,  # 高亮显示
            # 注释型文字，bash中为斜体，powershell中为灰体
            'note': 3 if config.shell not in ('powershell') else 2,
            'underline': 4,  # 使用下划线
            'blink': 5,  # 闪烁
            'invert': 7,  # 反白显示
            'hide': 8,  # 不可见
        }
    }

    def __init__(self):
        self.enable = config.support_shell()  # 指定着色是否可用

        self._color_rule =  [  # 高亮文档、帮助信息
            {
                'regexp': r"`[\s\S]*?`",  # ``高亮包裹的字符串
                'color': ['bold', 'yellow', '']
            },
            {
                # 一行中除去空白字符以 > 开始的的字符串认为是命令或脚本，则把它高亮显示
                'regexp': r"(?m)^[ \t]*>.*$",
                # 对应mode, fore, back, 其中mode可以使用列表包含需要的模式代码
                'color': ['', 'blue', '']
            },
            {
                # 一行中以:结尾的普通字符串认为它是标题，则把它高亮显示
                'regexp': r"(?m)^.*?[:：][ \t]*$",
                'color': ['bold', 'yellow', '']  # 对应mode, fore, back
            },
            {
                # 以 - 开头的单词认为是命令行选项
                'regexp': r"(?m)(?:^|\s+)-[\w\-]+?(?:$|\s+)",
                'color': ['', 'cyan', '']  # 对应mode, fore, back
            },
            {
                'regexp': r"(?m)#.*$",  # 以#开始的字符串认为是注释，则把它高亮显示
                'color': ['note', 'green', '']  # 对应mode, fore, back
            },
        ]

    def __colorlist(self, string: str, rules: list) -> list:
        '''生成最终着色规则列表，形如：[[startindex, endindex, ['note', 'red', 'black']]...]
        '''
        result = []
        if rules:
            for rule in rules:
                tmp = []
                matchtmp = list(re.finditer(rule['regexp'], string))
                color = rule['color']
                for t in matchtmp:
                    gtmp = []
                    if t.groups():
                        for i in range(len(t.groups())):
                            gtmp.append(
                                    [t.start(i+1), t.end(i+1), color])
                    else:
                        gtmp.append([t.start(), t.end(), color])
                    tmp.extend(gtmp)
                # 与上一个着色规则的列表合并，覆盖重合部分
                tmp = sorted(tmp, key=lambda x: x[0])
                resulttmp = result
                result = []
                i, j = 0, 0
                # 以tmp为基准
                while i < len(tmp) and j < len(resulttmp):
                    if tmp[i][0] >= resulttmp[j][0] and tmp[i][1] <= resulttmp[j][1]:  # center
                        if tmp[i][0] != resulttmp[j][0]:
                            result.append(
                                [resulttmp[j][0], tmp[i][0], resulttmp[j][2]])
                        if tmp[i][1] != resulttmp[j][1]:
                            result.append(
                                [tmp[i][1], resulttmp[j][1], resulttmp[j][2]])
                    elif tmp[i][0] >= resulttmp[j][1]:  # right
                        result.append(resulttmp[j])
                    elif tmp[i][1] <= resulttmp[j][0]:  # left
                        result.append(tmp[i])
                        i += 1
                        continue
                    elif tmp[i][0] < resulttmp[j][0] and tmp[i][1] < resulttmp[j][1] and tmp[i][1] > resulttmp[j][0]:  # left cross
                        result.append(
                            [tmp[i][1], resulttmp[j][1], resulttmp[j][2]])
                    elif tmp[i][0] > resulttmp[j][0] and tmp[i][1] > resulttmp[j][1] and tmp[i][0] < resulttmp[j][1]:  # right cross
                        result.append(
                            [resulttmp[j][0], tmp[i][0], resulttmp[j][2]])
                    j += 1
                while i < len(tmp):
                    result.append(tmp[i])
                    i += 1
                while j < len(resulttmp):
                    result.append(resulttmp[j])
                    j += 1
                result = sorted(result, key=lambda x: x[0])

        return result

    def __call__(self, string: str, rules:list=[]) -> str:
        '''根据预定义的规则修饰字符串，默认按照doc规则修饰

        Description:
            根据预定义的规则修饰字符串

        Arguments:


        Return:
            返回修饰后的字符串

        '''
        if not self.enable:
            return string

        if not rules:
            rules = self._color_rule

        result = self.__colorlist(string, rules)
        result.reverse()
        for rule in result:
            string = string[:rule[0]] + \
                self.colorize(string[rule[0]:rule[1]], *
                              rule[2]) + string[rule[1]:]

        return string

    def normalize(self, string: str) -> str:
        '''去除字符串中的颜色代码

        Description:
            去除字符串中的颜色代码

        '''
        return re.sub(r'\033\[[\d;]*m', '', string)

    def colorize(self, string: str, mode='', fore='', back='') -> str:
        r'''对字符串着色

        Description:
            对字符串按照指定的颜色、模式进行修饰

            一般来说终端会对"\033[v1;v2;v3;...m"类似的字符串进行解析来改变后续字符串的颜色及显示样式，其中v1、v2 ...等为颜色或模式代码，在`Colour.color`定义了部分代码。
            每个 `v` 代码都会覆盖前面同类型的代码设置，所以对于前景色、背景色、模式的代码位置没必要关心，
            但是对于代码值为0的需要放在最开始，因为该代码会恢复默认样式影响所有类型的代码。
            例如
                > echo -e "\033[2;34;47m123123\033[0m"
                > 123123 # 白底蓝字

                > echo -e "\033[34;2;47m123123\033[0m"
                > 123123 # 白底蓝字
            结果都是一样的

        Arguments:
            string  待修饰字符串
            mode    显示模式 可以是一个列表，包含需要的模式代码
            fore    前景色
            back    背景色

        Return:
            已经修饰过的字符串

        '''
        if not self.enable:
            return string

        v1 = []
        if isinstance(mode, tuple) or isinstance(mode, list):
            v1 = [Colour.color['mode'].get(i, 0) for i in mode]
        else:
            v1.append(Colour.color['mode'].get(mode, 0))

        v2 = Colour.color['fore'].get(fore, 0)
        v3 = Colour.color['back'].get(back, 0)
        tmp = sorted([*v1, v2, v3])  # 避免0代码放在后面了
        result = '\033['
        for i in tmp:
            result += f'{i};'
        result = result[:-1]+'m'+f'{string}\033[0m'
        return result

colour = Colour()