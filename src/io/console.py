from src.io.base import MyIO
import src.config as config
import importlib
import sys
import os

class ConsoleInput(MyIO):
    def __init__(self):
        super().__init__(sys.stdin.buffer)
    
    def getch(self, echo=False)-> int:
        ch = 0
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

        return ord(ch)

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