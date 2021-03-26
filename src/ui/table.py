import re
import src.config as config
from src.ui.pretty import colour
import unicodedata

class TableAnalyseException(Exception):
    pass

class Tablor:
    '''向终端输出表格式内容

    Description:
        将列表中的内容以表格的形式输出到终端

    Attribute:


    '''
    def __init__(self):
        self._color_rule = [  # 表格中可能需要高亮的规则(应用在单元格)
            {
                'regexp': r"`[\s\S]*?`",  # ``高亮包裹的字符串
                'color': ['bold', 'yellow', '']
            },
            {
                # url
                'regexp': r'(?:\s+|^)((?:http|https)://[\w\-.:]+/\S+)(?:$|\s+)',
                'color': [('underline', 'bold'), 'blue', '']
            },
            {
                'regexp': r'(?:\s+|^)(\d+)(?:$|\s+)',  # 整数
                'color': ['', 'blue', '']
            },
            {
                'regexp': r'(?:\s+|^)(True|target)(?:$|\s+)',
                'color': ['bold', '', '']
            },
        ]

    def __call__(self, table: list, header=True, border=True, aligning='left', title='', pos=None, max_width=50, gap=' ', indent='    ', autocolor=True) -> str:
        '''格式化列表中的内容为表格样式

        Description:
            格式化列表中的内容为表格样式

        Arguments:
            table 需要转化的表格
                标准格式为
                    [['header1', 'header2'], [d1, d2], [d3, d4]]

            header 如果为真则表示列表的第一行为表头

            border 如果为真则绘制边框

            aligning 指定单元格的对其方式， 可选 left， right， center。使用方法："left-1, left-2, center-3, right-4"，该字符串可指定特定列的对齐方式，不指定
                    特定列将应用到所有列

            title 指定表格的标题， 若为空则不绘制

            pos 指定当前选中行， 会绘制一个箭头指向行， pos从1开始

            max_length 每列的最大宽度，单位字符数, 超过将会自动展开行.指定特定列的方法："50-1, 60-2, 80-3, 120-4"，该字符串可指定特定列的最大宽度，不指定
                    特定列将应用到所有列, 其中50-1里面50指定最大宽度，1指定第1列

            gap 当border为假时，指定每列之间的填充字符串

            indent 表格左侧缩进

            autocolor 为真时将对单元格内容自动着色

        Return:
            格式化后的字符串

        '''
        if table is None or not table or not table[0]:
            return ''
        try:
            return self.__analyse(table, header=header, border=border, aligning=aligning, title=title, pos=pos, max_width=max_width, gap=gap, indent=indent, autocolor=autocolor)
        except Exception as e:
            raise TableAnalyseException(e)

    def __wrap(self, table: list, pos: int, header: bool) -> list:
        '''如果单元格中有换行，则使换行输出到同一列
            table   A table
            pos     指定那一行为当前需要标记的行
            header  当前表格是否含有头部
        '''
        result = []
        headerlines = 0
        # 解析换行
        r = 0 if header else 1
        for line in table:
            tmp = []
            for c in range(len(line)):
                col = str(line[c])
                i = 0
                splitlist = re.split(r'[\r\n]+', col)
                color = None  # 上一行未闭合的颜色代码
                for l in splitlist:
                    if len(tmp) <= i:
                        tmp.append(['' for j in line])
                    if color:
                        l = color + l  # 上一行有未闭合的颜色代码，则添加到该行头
                        color = None
                    # 搜索最后一个颜色代码
                    ma = re.search(
                        r'(\033\[[\d;]+m)(?!.*?\033\[[\d;]+m.*?).*$', l)
                    if ma:
                        if not re.fullmatch(r'\033\[[0;]+m', ma.group(1)):
                            color = ma.group(1)
                            l += '\033[0m'  # 该行闭合着色
                    tmp[i][c] = line[c] if len(
                        splitlist) == 1 else l  # 无换行则使用原来的数据类型
                    i += 1
            result.extend(tmp)
            if r == 0:
                headerlines = len(tmp)
            elif r == pos:
                pos = len(result)-headerlines-len(tmp)+1
            r += 1
        return result, pos

    def __analyse(self, table: list, header: bool, border: bool, aligning="left", title="",
                  pos=None, max_width=50, gap='   ', indent='    ', autocolor=True) -> str:
        table, pos = self.__wrap(table, pos, header)
        if autocolor:
            for line in table:  # 对单元格进行着色
                for c in range(len(table[0])):
                    if header and c == 0:
                        continue
                    cell = str(line[c])
                    if line[c] is None:
                        line[c] = colour.colorize(cell, 'note', 'red')
                    else:
                        line[c] = colour(cell, self._color_rule)

        columns = len(table[0])
        result = ''
        width_list = [0 for i in range(columns)]  # 对应每列的字符最大宽度
        max_width_list = [(max_width if isinstance(max_width, int) else 50) for i in range(columns)] # 限制每列的最大宽度，超过将折叠行
        if isinstance(max_width, str):
            match = re.findall(r'(\d+)-(\d+?)', max_width)
            if match:
                for m in match:
                    col = int(m[1])
                    if col>columns or col <= 0:
                        continue
                    max_width_list[col-1] = int(m[0])

        # 检查每个单元格是否超过最大宽度，有的话添加一个换行符
        for row in table:
            for c in range(columns):
                cell = str(row[c])
                length = self._str_width(colour.normalize(cell))
                if width_list[c] < length:
                    width_list[c] = length
                if width_list[c] > max_width_list[c]:
                    width_list[c] = max_width_list[c]
                    col = ''
                    color_list = []  # like [[match, True], ...] True表示颜色代码为默认代码\033[0m
                    tmp = re.finditer(r'\033\[[\d;]+m', cell)
                    for ma in tmp:
                        if re.fullmatch(r'\033\[[0;]+m', ma.group(0)):
                            color_list.append([ma, True])
                        else:
                            color_list.append([ma, False])
                    chunk = 0
                    start = 0
                    end = 0
                    if color_list:
                        for color_tmp in color_list:  # 着色代码不占显示宽度
                            ma = color_tmp[0]
                            tmp_chunk = ma.start(0)-end
                            if chunk+tmp_chunk == max_width_list[c]:
                                end = ma.end(
                                    0) if color_tmp[1] else ma.start(0)
                                col += cell[start:end]+'\n'
                                start = end
                                chunk = 0
                            elif chunk+tmp_chunk > max_width_list[c]:
                                end = max_width_list[c]-chunk+end
                                col += cell[start:end]+'\n'
                                start = end
                                chunk = ma.start(0) - start
                                while chunk > max_width_list[c]:
                                    end = start+max_width_list[c]
                                    col += cell[start:end]+'\n'
                                    start = end
                                    chunk = ma.start(0)-start
                                if chunk == max_width_list[c]:
                                    end = ma.end(
                                        0) if color_tmp[1] else ma.start(0)
                                    col += cell[start:end]+'\n'
                                    start = end
                                    chunk = 0
                            else:
                                chunk += tmp_chunk
                            end = ma.end(0)
                        tmp_chunk = len(cell)-end
                        while chunk+tmp_chunk > max_width_list[c]:
                            end = max_width_list[c]-chunk+end
                            col += cell[start:end]+'\n'
                            start = end
                            chunk = 0
                            tmp_chunk = len(cell)-end
                        col += cell[start:]+'\n'
                    else:
                        while start+max_width_list[c] < length:
                            end = start+max_width_list[c]
                            col += cell[start:end]+'\n'
                            start = end
                        col += cell[start:]+'\n'

                    row[c] = col.rstrip('\r\n ')
        table, pos = self.__wrap(table, pos, header)

        if title != '' and title is not None:
            # 添加标题
            l = self._str_width(title)
            result += title+'\n'
            result += '='*l+'\n\n'

        aligning_list = ['left' for i in width_list]# 对齐方式列表
        match = re.findall(r'(left|center|right)-(\d+)', aligning)
        if match:
            for m in match:
                col = int(m[1])
                if col>columns or col<=0:
                    continue
                aligning_list[col-1] = m[0]

        border_line = ['-'*i for i in width_list]
        if border:
            result += indent + \
                self.__draw_line(border_line, width_list, aligning_list,
                                 '+', padding='-')+'\n'
        if header:
            result += indent + \
                self.__draw_line(table[0], width_list, aligning_list,
                                 '|' if border else gap)+'\n'
            result += indent + \
                self.__draw_line(border_line, width_list, aligning_list, 
                                 '+' if border else gap, padding='-')+'\n'
            table = table[1:]

        i = 1
        for row in table:
            if i == pos:
                result += colour.colorize('=> '.rjust(len(indent), ' '), 'bold', 'green') + \
                    self.__draw_line(
                        row, width_list, aligning_list, '|' if border else gap)+'\n'
            else:
                result += indent + \
                    self.__draw_line(
                        row, width_list, aligning_list, '|' if border else gap)+'\n'
            i += 1
        if border:
            result += indent + \
                self.__draw_line(border_line, width_list, aligning_list,
                                 '+', padding='-')+'\n'

        return '\n'+result

    def _str_width(self, s: str)-> int:
        '''获取字符串的宽度
        '''
        ret = 0
        for i in s:
            if unicodedata.east_asian_width(i) in "FWA":
                ret += 2
            else:
                ret += 1
        return ret

    def __draw_line(self, line: list, width_list: list, aligning_list:list, joint='|', padding=' ') -> str:
        result = joint
        for i in range(len(line)):
            d = str(line[i])
            tmp = colour.normalize(d)  # 防止着色代码占用长度
            tmp = width_list[i] - self._str_width(tmp)
            if aligning_list[i] == 'left':
                d = d+' '*tmp
            elif aligning_list[i] == 'right':
                d = ' '*tmp + d
            elif aligning_list[i] == 'center':
                t = int(tmp/2)
                d = ' '*t + d + ' '*(tmp-t)

            result += f"{padding}{d}{padding}{joint}"

        return result

tablor = Tablor()