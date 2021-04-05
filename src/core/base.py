from src.io.base import BufferedIO
from src.io.config import ioconfig
import re
import os
import sys
from src.logger import logger
from src.exception import NotCallableError
import importlib.util
import traceback
import abc
import typing

def load_module(name: str, path: str):
    '''加载指定文件路径处的模块
    '''
    sepc = importlib.util.spec_from_file_location(name, path)
    if sepc is None:
        return None
    module = importlib.util.module_from_spec(sepc)
    old = sys.modules.get(name)
    sys.modules[name] = module
    try:
        sepc.loader.exec_module(module)
    except BaseException as e:
        logger.debug(f'A {e.__class__.__name__} occured!', True)
        logger.warning(f'Module `{name}` maybe have some error. Load failed!') 
        module = None
    if old:
        sys.modules[name] = old
    else:
        sys.modules.pop(name)
    return module

def call_path(floor=1)-> str:
    '''返回调用该函数时指定层数的绝对路径
        floor 指定调用该函数时调用栈的层数，将会返回该层的文件路径
    '''
    stack = traceback.extract_stack()
    return os.path.abspath(stack[-floor-1].filename)

class Cmdline:
    '''支持的引号' " `
    '''
    def __init__(self, line:typing.Union[str, tuple, list]):
        if isinstance(line, str):
            self.__cmdline = line
            self.__cmdlist = tuple(self.__parsecmd(line))
        elif isinstance(line, list) or isinstance(line, tuple):
            self.__cmdlist = tuple(line)
            self.__cmdline = None
        else:
            raise ValueError('The type of Cmdline\'s options must be list,tuple or str!')
        if len(self.__cmdlist) == 0 or self.__cmdlist[0] == '':
            self.__cmdlist = (None,)

    @property
    def length(self):
        return len(self.__cmdlist)
    
    @property
    def cmdline(self):
        if self.__cmdline is None:
            if self.cmd is None:
                return ''
            else:
                tmp = list(self.__cmdlist)
                for i in range(len(tmp)):
                    if re.search(r'\s+', tmp[i]):
                        t = tmp[i].replace('"', '\"')
                        tmp[i] = f'"{t}"'
                self.__cmdline = ' '.join(tmp)

        return self.__cmdline

    @property
    def cmd(self):
        '''获取命令名称
        '''
        return self.__cmdlist[0]
    
    @property
    def options(self):
        '''获取参数列表
        '''
        return self.__cmdlist[1:]

    def __parsecmd(self, line: str)-> list:
        result = []
        # 解析命令字符串，转为命令列表的形式，如："ls -l a" 转为["ls", "-l", "a"]
        quote = None # 当前期待的引号
        quotestr = '"`\''
        end = 0
        space = ' \t\r\n'
        line = line.strip(space) # 命令行的开始与结束都不会有空白符
        length = len(line)
        for q in quotestr:
            if line.startswith(q):
                raise ValueError("Cmdline analyse error!")
        
        cur = ''
        quote_str= ''
        is_quote_over = False # 判断最后是否是从引号中退出
        while end < length:
            if line[end] in quotestr:
                if quote == line[end] and line[end-1] != '\\':
                    cur += quote_str.replace(f"\\{quote}", quote)
                    quote_str = ''
                    end += 1
                    quote = None
                elif quote is None:
                    quote = line[end]
                    end += 1
                else:
                    quote_str += line[end]
                    end += 1
                is_quote_over = True
                continue

            if quote is not None:
                quote_str += line[end]
                end += 1
                continue

            if line[end] not in space:
                cur += line[end]
                end += 1
                is_quote_over = False
                continue

            result.append(cur)
            cur = ''
            while line[end] in space:
                end += 1
            is_quote_over = False
        if quote is not None:
            raise ValueError("Cmdline analyse error!") 
        if cur or is_quote_over:
            result.append(cur)
        return result

class Plugin:
    pass

class Command(Plugin):
    '''命令的基类
    
    Description:
        所有命令需要基于该类，覆盖run方法以及构造函数中定义的属性。
    
    
    '''

    EXIT = -1 # 退出代码，会退出程序
    SUCCESS = 0 # 命令执行成功
    STOP = 1 # 命令执行失败，但不退出程序
    ERROR = 2 # 命令执行成功，但是发生了错误而退出
    
    def __init__(self, command=None, name=None, help=None):
        '''command指定一个可被调用的对象，类似 def command(args: Cmdline)->bool '''
        if command is not None and not hasattr(command, '__call__'):
            raise NotCallableError(f'`{command}` is not a callable object!')
        self.name = None if command is None else command.__name__
        self.__command = command
        self.help = None if command is None else command.__doc__

        if name is not None:
            self.name = name
        if help is not None:
            self.help = help


    def run(self, args: Cmdline)-> int:
        return self.__command(args)

class TerminalBase:
    '''参考Cmd模块改写的终端类'''

    def __init__(self):
        pass

    @property
    def prompt(self)->str:
        return '$ '

    def parsecmd(self, line: str)-> Cmdline:
        return Cmdline(line)

    def raw_input(self, msg: str)-> str:
        return input(msg)
    
    def input(self, msg: str)-> str:
        return ioconfig.new_input(msg)
    
    def cmdloop(self):
        line  = ''
        args = []
        stop = Command.SUCCESS
        logger.debug(f"Start the command loop on class `{__class__.__name__}`")
        self.preloop()
        while stop != Command.EXIT:
            try:
                line = self.raw_input(self.prompt)
                try:
                    args = self.parsecmd(line)
                except ValueError as e:
                    logger.debug('Failed to parse the command line')
                    logger.error(str(e))
                    continue

                args = self.precmd(args)

                stop = self.cmdhandler(args)
                stop = self.postcmd(stop, args)
            except (KeyboardInterrupt, EOFError):
                stop = self.interrupt_handler(args)
            except BaseException as e:
                stop = self.exception_handler(args, e)
                
        self.postloop()
        logger.debug(f"End the command loop on class `{__class__.__name__}`")

    def interrupt_handler(self, args: Cmdline)-> int:
        '''中断处理,返回False则不终端当前命令循环'''
        return Command.STOP
    def exception_handler(self, args: Cmdline, e: BaseException) -> int:
        traceback.print_exc()
        return Command.STOP
    def cmdhandler(self, args: Cmdline)-> int:
        '''处理命令， line为被precmd处理过的命令行字符串'''
        return Command.SUCCESS
    def precmd(self, args: Cmdline)-> Cmdline:
        '''命令被执行之前调用'''
        return args
    def postcmd(self, stop: int, args: Cmdline)-> int:
        '''命令执行结束后调用'''
        return stop

    def preloop(self):
        '''命令循环之前执行'''
        pass
    def postloop(self):
        '''命令循环之后执行'''
        pass

class SessionBase(dict):
    pass

class WebshellBase(Plugin):
    '''webshell 基类
    
    Description:
        用于描述如何与webshell交互、如何生成webshell
    
    Attribute:
        
    
    '''
    PHP = 'php'
    ASP_NET_CS = 'asp_net.cs' # 使用C#语言的.net
    ASP = 'asp'
    JSP = 'jsp'


class Payload:

    def __init__(self, _____path=None, **kw):
        self._code = b''
        self._global = {} # payload使用的全局变量

        if _____path:
            path = _____path.replace('/', os.sep)
            path = os.path.join(os.path.dirname(call_path(2)), path)
            self.from_file(path)

        for k, v in kw.items():
            self.set_var(k, v)

    @property
    def code(self)-> bytes:
        '''生成webshell使用的payload代码
        '''
        return self._code


    def from_file(self, path: str):
        '''从文件导入代码
        '''
        path = path.replace('/', os.sep)
        path = os.path.join(os.path.abspath(os.path.dirname(call_path(2))), path)
        with open(path, 'rb') as f:
            self._code = f.read()

    def from_string(self, code: str):
        '''从字符串导入代码
        '''
        self._code = code.encode()

    def from_bytes(self, code: bytes):
        '''从字节流导入代码
        '''
        self._code = code

    def get_var(self, name: str):
        if name in self._global:
            return self._global.get(name)
        raise AttributeError(f"No this global var `{name}`!")

    def set_var(self, name:str, value):
        '''更新、新增指定的变量
        '''
        self._global[name] = value
    def del_var(self, name: str):
        if name in self._global:
            self._global.pop(name)