import re
import traceback
import os
from src.io.config import ioconfig
from src.core.payload import Payload, PHPPayload
from src.core.webshell import Webshell
import string
import random
import time
import inspect
import ctypes
import threading
from xml.sax.saxutils import escape, unescape


locker = threading.Lock() # 用于全局的锁

def input(prompt='', slow=False)-> str:
    print(prompt, end='', flush=True)
    ret = ''
    if not slow:
        ret = ioconfig.new_input()
    else:
        while True:
            ch = ioconfig.stdin.getch(True)
            ret += chr(ch)
            if chr(ch) == '\n':
                break
    return ret

def pathsplit(path: str)-> tuple:
    '''无论文件路径分隔符是哪个，把path分为（目录路径， 文件名）的元组返回
    '''
    i = path.rfind('/')
    j = path.rfind('\\')
    x = max(i, j)
    y = min(i, j)
    r = y if y != -1 else x

    return path[:r+1], path[r+1:]

def randomstr(length:int, words=string.ascii_letters+string.digits)->str:
    '''生成指定长度的字符串
    '''
    length = abs(length)
    length = 1 if length == 0 else length
    return ''.join(random.sample(words, length))

def templete_0(code: str, **kw)-> str:
        '''替换代码中的占位符${}，并返回替换后的结果
        '''
        for k, v in kw.items():
            if re.match(r'^\w+$', k):
                code = re.sub(r'\$\{\s*'+k+r'\s*\}', str(v), code) # 将替换${k}为指定的值
        return code

def correct_cmd_str(line: str, cmd: str)-> str:
    '''构造合法、正确的命令字符串，其中cmd表示插入的命令，line表示完整的命令行字符串，quote表示使用到的引号。最终，
    函数会对cmd进行正确的引号转义，使得整个命令行字符串合法。注：传入的cmd中最外层的引号不能有反斜杠
    '''
    start = line.find(cmd)
    end = start+len(cmd)
    if start == -1:
        return line
    tmp = line[:start]
    tmp_1 = list(re.finditer(r'(\\*").*?\1|(\\*\').*?\2', tmp))
    if tmp_1:
        tmp_1 = tmp_1[-1]
        tmp = tmp[tmp_1.end():]
    
    quote = "'\""
    for q in quote:
        a = re.findall(rf'\\*{q}', tmp)
        a = [i.count('\\') for i in a]
        if a:
            a = max(a)
            cmd = cmd.replace(q, "\\"*(a+1)+q)
    return line[:start]+cmd+line[end:]
    


def sleep(secs):
    return time.sleep((secs))

def kill_thread(threadid: int)-> bool:
    '''杀死指定线程
    '''
    tid = ctypes.c_long(threadid)
    res = ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, ctypes.py_object(SystemExit))
    if res != 1:
        return False
    return True

def xml_escape(data: str)-> str:
    return escape(data, {'\\':'&#x5c;'})

def xml_unescape(data: str)-> str:
    return unescape(data, {'&#x5c;':'\\'})