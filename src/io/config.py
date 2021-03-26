r'''配置全局的IO函数，如print、input
'''
import threading
import sys
from .console import ConsoleInput, ConsoleOutput
from .base import BufferedIO

__all__ = ['ioconfig']

class IOConfig:

    def __init__(self):
        self.__top_builtins = None
        self.__lock = threading.Lock()
        self.old_print = None
        self.__echo = True # 表示是否将输出回显到控制台

        self.__stdout = ConsoleOutput()
        self.__stdin = ConsoleInput()
        self.__stderr = ConsoleOutput()

        self.echo_on()

    @property
    def stdin(self)->ConsoleInput:
        return self.__stdin
    
    @property
    def stdout(self)->ConsoleOutput:
        return self.__stdout
    
    @property
    def stderr(self)->ConsoleOutput:
        return self.__stderr

    def register_top_builtins(self, built):
        if self.__top_builtins:
            return
        try:
            self.__top_builtins = built
            self.old_print = built.print
            del built.print
            built.print = self.new_print
        except BaseException:
            print("Register top builtins failed!")

    def new_print(self, *args, **kw):
        self.__lock.acquire()
        self.old_print(*args, **kw)
        self.__lock.release()

    def new_input(self, prompt='')-> str:
        self.new_print(prompt, end='', flush=True)
        return self.__stdin.readline().rstrip('\r\n')

    def echo_off(self)-> BufferedIO:
        self.__echo = False
        self.stdout.set_echo(False)
        self.stderr.set_echo(False)
        sys.stdout = BufferedIO()
        sys.stderr = sys.stdout
        return sys.stdout

    def echo_on(self):
        # 改写全局标准输入输出流
        sys.stdout = self.__stdout
        sys.stderr = self.__stderr
        self.stdout.set_echo(True)
        self.stderr.set_echo(True)


ioconfig = IOConfig()