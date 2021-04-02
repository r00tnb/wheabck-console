'''存储程序运行过程中的配置

Description:
    存储程序运行过程中的配置

Export:
    默认导出

'''
import os
import sys
import logging

# import threading
# __lock = threading.Lock()
# __old_print = __builtins__.print
# def new_print(*args, **kw): # 覆盖内建的print函数，使其线程安全
#     __lock.acquire()
#     __old_print(*args, **kw)
#     __old_print("123123")
#     __lock.release()
# del __builtins__.print
# __builtins__.print = new_print

def support_shell()-> bool:
    global shell
    if shell not in ('cmd'):
        return True
    return False

def current_shell()->str:
    if platform.lower().startswith('win'):
        if os.environ.get('PROMPT') and os.environ.get('COLUMNS') is None:
            return 'cmd'
        else:
            return 'powershell'
    else:
        return os.path.split(os.environ.get('SHELL'))[1]

#=========================
# 程序相关
#=========================

# name
app_name = "wheabck"

# 提示符
prompt = ">"

# 工作目录
work_path = os.getcwd()

# 代码目录
root_path = os.path.abspath(os.path.dirname(__file__))

# 程序目录
program_path = os.path.dirname(root_path)

# module路径
module_path = os.path.join(root_path, 'modules')

# api 搜索路径
sys.path.insert(0, root_path)

# 历史命令路径
history_path = os.path.join(program_path, '.history')

# 日志等级
logger_level = logging.INFO

# webshell连接存储路径
webshell_save_path = os.path.join(program_path, 'webshell_connections.xml')

# os information
platform = sys.platform
shell = current_shell() # 目前支持bash, sh, powershell

# 默认编辑器
editor = 'notepad' if 'win' in platform else 'vim'