import threading
import math
import copy

class ValueState:
    def __init__(self, value, solved: bool, ret):
        self.value = value # 原始值
        self.solved = solved # 值是否已经被处理
        self.ret = ret # 处理函数返回的结果

class Worker:
    '''handler是处理函数，由线程处理函数调用，类似def handler(v, *args, **kw) 其中v是vlist中的元素，由本实例进行平均分配给所有线程，args及kw由set_param函数设置
    '''
    def __init__(self, handler, vlist:list, thread_count=1):
       
        self.thread_count = thread_count
        self.handler = handler
        self.vlist = [ValueState(v, False, None) for v in vlist ] # 元素的第二项表示该元素是否已经由handler处理, 第三项表示handler函数的返回值

        self.args = ()
        self.kw = {}
        self._thread_list = []

        self._run = False

        self._lock = threading.Lock()

    def set_param(self, *args, **kw):
        '''向线程处理函数传递的额外参数
        '''
        self.args = args
        self.kw = kw

    def is_running(self)-> bool:
        for t in self._thread_list:
            if t.is_alive():
                return True
        return False

    def flush(self):
        '''刷新数据准备再次工作
        '''
        self.vlist = [ValueState(v.value, False, None) for v in self.vlist ]
        self._thread_list = []
        self._run = False

    def stop(self):
        self._run = False
        self.wait_end()

    def start(self):
        self._run = True
        step = math.ceil(len(self.vlist)/self.thread_count)
        for i in range(0, len(self.vlist), step):
            t = threading.Thread(target=self._worker, args=(self.vlist[i:i+step], ))
            t.setDaemon(True)
            self._thread_list.append(t)
        for t in self._thread_list:
            t.start()

    def wait_end(self):
        for t in self._thread_list:
            t.join()
        self._thread_list = []
        self._run = False

    def _worker(self, vlist: list):
        for v in vlist:
            if not self._run:
                return
            ret = self.handler(v.value, *self.args, **self.kw)
            self._lock.acquire()
            v.solved = True
            v.ret = ret
            self._lock.release()

    @property
    def current_vlist(self)->list:
        return copy.deepcopy(self.vlist)