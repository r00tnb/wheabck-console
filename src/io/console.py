from src.io.base import MyIO
import src.config as config
import importlib
import sys
import os
import csv
import re

class ConsoleInput(MyIO):

    def __init__(self):
        super().__init__(sys.stdin.buffer)

    def read_ex(self, length: int, timeout=1, echo=False)-> str:
        '''从终端获取一段字符串

        参数:
            length: 指定最大读取的字节数
            timeout： 指定超时时间（单位毫秒）
            echo： 指定输入是否还打印到终端

        返回数据：
            返回读取到的字符串对象
        '''
        ch = ''
        if config.platform.startswith('linux'):
            termios = importlib.import_module('termios')
            # 获取标准输入的描述符
            fd = self.fileno()

            # 获取标准输入(终端)的设置
            old_ttyinfo = termios.tcgetattr(fd)

            # 配置终端
            new_ttyinfo = old_ttyinfo[:]

            # 使用非规范模式(索引3是c_lflag 也就是本地模式)
            new_ttyinfo[3] &= ~termios.ICANON
            # 关闭回显(输入不会被显示)
            if not echo:
                new_ttyinfo[3] &= ~termios.ECHO

            # 使设置生效
            termios.tcsetattr(fd, termios.TCSANOW, new_ttyinfo)
            # 从终端读取
            ch = os.read(fd, 1)
            os.

            # 还原终端设置
            termios.tcsetattr(fd, termios.TCSANOW, old_ttyinfo)
    
    def getch(self, echo=False)-> bytes:
        '''获取一个字符，返回它的字节对象
        '''
        ch = b''
        if config.platform.startswith('linux'):
            termios = importlib.import_module('termios')
            # 获取标准输入的描述符
            fd = self.fileno()

            # 获取标准输入(终端)的设置
            old_ttyinfo = termios.tcgetattr(fd)

            # 配置终端
            new_ttyinfo = old_ttyinfo[:]

            # 使用非规范模式(索引3是c_lflag 也就是本地模式)
            new_ttyinfo[3] &= ~termios.ICANON
            # 关闭回显(输入不会被显示)
            if not echo:
                new_ttyinfo[3] &= ~termios.ECHO

            # 使设置生效
            termios.tcsetattr(fd, termios.TCSANOW, new_ttyinfo)
            # 从终端读取
            ch = os.read(fd, 1)

            # 还原终端设置
            termios.tcsetattr(fd, termios.TCSANOW, old_ttyinfo)
        else:
            msvcrt = importlib.import_module('msvcrt')
            if echo:
                ch = msvcrt.getche()
            else:
                ch = msvcrt.getch()

        return ch

class ConsoleOutput(MyIO):

    def __init__(self):
        super().__init__(sys.stdout.buffer)

        self._echo = True
    
    def set_echo(self, echo:bool):
        self._echo = echo

    def write(self, s: str)-> int:
        if not self._echo:
            return len(s)
        return super().write(s)
