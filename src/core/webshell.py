

from src.core.base import WebshellBase, Payload, Cmdline
import re
import threading
from functools import wraps
import abc
from src.logger import logger
from src.ui.pretty import colour

class Options:
    def __init__(self):
        self.__options = [] # 形如：[['name', 'value', True, 'description', ...], ...[...]]
        self.__temp_options = [] # 形如 [[name, value, threadID], ...] 用于存储使用一次即失效的临时选项
    
    def add_option(self, name: str, description: str, required=False, default=None, check=None, type=str):
        '''向options列表添加新项

            name        参数名称
            description 描述
            required    是否必选
            default     默认值
            check       检查参数值是否正确,如果布尔值为假则不检验
            type        指定参数类型，将会使用传入值转换参数，如：type=func， 则在传入参数时执行 func(value)，并使用其返回值
        '''
        if name in [i[0] for i in self.__options]:
            raise ValueError(f"Duplicate option name `{name}`")
        self.__options.append([name, default, required, check, description, type])
    
    def _get_option(self, name: str)-> list:
        for o in self.__options:
            if o[0] == name:
                return o
        return None
        
    def remove_option(self, name: str):
        o = self._get_option(name)
        if o is None:
            raise AttributeError(f'No option named `{name}`')
        self.__options.remove(o)
    def set_option(self, name: str, value):
        if not self.check(name, value):
            raise ValueError(f"Failed verification on option name `{name}`, value is `{value}`")
        o = self._get_option(name)
        try:
            o[1] = o[5](value)
        except:
            raise ValueError(f"Cannot convert type on option name `{name}`, value is `{value}`")

    def option_list(self): 
        tmp1 = []
        tmp2 = []
        for i in self.__options:
            if i[2] == True:
                tmp1.append(i[:5])
            else:
                tmp2.append(i[:5])
        tmp1 = sorted(tmp1, key=lambda x: ' ' if x[0]=='target' else x[0])
        tmp2 = sorted(tmp2, key=lambda x: x[0])
        tmp1.extend(tmp2)
        return [['Name', 'Current Value', 'Required', 'Check Rule', 'Description'], *tmp1]
    def unset_list(self):
        '''返回必选项未设置的列表
        '''
        result = []
        for option in self.__options:
            if option[2] and option[1] is None:
                result.append(option)
        return result

    def check(self, name: str, value)-> bool:
        '''检测指定参数的参数值是否合法
        '''
        value = str(value)
        o = self._get_option(name)
        if o is None:
            raise AttributeError(f'No option named `{name}`')

        if o[3]:
            if re.fullmatch(str(o[3]), value):
                return True
            else:
                return False
        return True

    def set_temp_option(self, name: str, value):
        '''对指定的选项设置临时值，临时选项需要调用destroy_all_temp_options方法来清除，一般由webshell客户端eval方法执行完毕后调用, 设置的选项是线程安全的.
        '''
        if not self.check(name, value):
            raise ValueError(f"Failed verification on option name `{name}`, value is `{value}`")

        o = self._get_option(name)
        try:
            value = o[5](value)
        except:
            raise ValueError(f"Cannot convert type on option name `{name}`, value is `{value}`")
        self.__temp_options.append([name, value, threading.current_thread().ident])

    def destroy_all_temp_options(self):
        '''销毁当前线程中所有的临时选项
        '''
        self.__temp_options = [i for i in self.__temp_options if i[2] != threading.current_thread().ident]
    
    def __getattr__(self, name: str):
        o = self._get_option(name)
        if o is None:
            raise AttributeError(f'No option named `{name}`')

        for i in range(len(self.__temp_options)):
            tmp = self.__temp_options[i]
            if tmp[0] == name and tmp[2] == threading.current_thread().ident:
                return tmp[1]
        return o[1]

class CommandExecutor(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def exec_command_on_server(self, cmd:str)->str:
        '''执行远程系统命令
        '''
        pass


class Webshell(WebshellBase):
    '''A webshell base class

    Note:
        All webshell must extend this class, and it should define class name to equal `webshell`.
    '''
    
    def __init__(self):
        self.options = Options()
        self.options.add_option('target', 'A target url', True, check=r'(http|https)://[\w\-.:]+/\S+')
        self.options.add_option('encoding', 'This encoding is used to decode the message sent back by the server.Character set code from Python.', False, default='UTF8')
        self.options.add_option('timeout', 
            'HTTP request timeout in seconds.If set to `0`, it will wait indefinitely for the request to complete', default=30.0, check=r"\d+(\.\d+)?", type=float)
        self.options.add_option('verbose', "Display detailed error information of the webshell client.\n0.Hidden all info.\n1.Only show error info.\n2.Show all error,warning info.", 
            check=r"0|1|2", default=2, type=int)
        self.options.add_option('command_executor', """You can specify a plug-in to execute system commands on the server (default is `exec`). The plug-in must inherit the commandexecutor class and implement exec_command method.""", 
            type=str, default='exec')
        self.help = self.__doc__ if self.__doc__ is not None else ''
        self.session = None
        self.type = None # 指定webshell的类型，如：php/sample_one_word, 这个值将在生成实例时一般由`use`命令填充

    class EvalError:
        def __init__(self, errcode: str=None, errmsg: str=None, iswarning: bool=True, onserver: bool=True):
            self.errcode = errcode # 错误代码
            self.errmsg = errmsg # 错误消息
            self.iswarning = iswarning # 是否是警告
            self.onserver = onserver # 该错误是否发生在服务器上
        
        def __str__(self):
            return f"{'Webshell' if self.onserver else 'Python'} {'warning' if self.iswarning else 'error'}: {self.errcode}: {self.errmsg}"

    @staticmethod
    def handle_evaled(func):
        '''用于在eval方法执行前后，做一些必要的操作
        '''
        @wraps(func)
        def wrapper(self, *args, **kw):
            ret = func(self, *args, **kw)
            self.options.destroy_all_temp_options()
            return ret
        return wrapper

    def exec_command(self, cmd)->str:
        '''在服务器上执行系统命令，所有插件应该使用该方法执行系统命令
        '''
        name = self.options.command_executor
        executor = self.session.command_map.get(name)
        if executor is None:
            logger.error(f"No command named `{name}`.")
            return None
        if not isinstance(executor, CommandExecutor):
            logger.error(f"Explot `{name}` is not a CommandExecutor!")
            return None
        
        return executor.exec_command_on_server(cmd)
    
    def connect(self)-> bool:
        '''connect target and return True, or False if connect failed. 
        '''
        pass

    def eval(self, payload: Payload):
        '''执行payload并获取返回结果, 一般payload为代码, 始终返回EvalResult对象'''
        pass

    def generate(self)-> bytes:
        '''生成并返回webshell代码'''
        pass

    def hook_start(self, session):
        '''当session创建时调用
        '''
        self.session = session

    def hook_loaded(self):
        '''当所属session加载完毕时调用
        '''
        # 修改command_executor的checkrule
        ok = []
        for n, e in self.session.command_map.items():
            if isinstance(e, CommandExecutor):
                ok.append(n)
        o = self.options._get_option("command_executor")
        if o:
            o[3] = rf'{"|".join(ok)}'
        

    def hook_destroy(self):
        '''当所属session被销毁时调用
        '''
        pass
        
class EvalResult:
    def __init__(self):
        self.__data = None # 若执行成功则存储执行的结果
        self.__errors = [] # EvalError的列表

    @property
    def data(self)-> str:
        return self.__data

    @data.setter
    def data(self, d: str):
        self.__data = d

    @property
    def errors(self)-> list:
        return self.__errors
        
    def is_success(self)-> bool:
        '''判断执行是否成功
        '''
        return self.data is not None

    def add_error_info(self, err:Webshell.EvalError):
        self.__errors.append(err)