class NotCallableError(Exception):
    pass

class CodeExecuteError(Exception):
    '''代码执行错误
    '''
    pass

class CommandNotFound(Exception):
    '''命令找不到
    '''
    pass