
from src.core.webshell import Webshell
from src.core.session import WebshellSession
from src.core.payload import CSharpPayload
from src.logger import logger
import json
import os
import base64

class CSharpWebshell(Webshell):

    def __init__(self):
        super().__init__()
        self.options.add_option('extra_assemblys', 
            "Specifies the additional assembly path that the C # compiler will introduce.(Add `+` in front of value to add a path, and `-` delete a path, type `set extra_assemblys []` to empty)\nNote: c# may cache the assembly, when encountering a conflict, you need to manually cancel the additional assembly", 
            False, [], type=self.__check)

    def _generate_extra_assemblys_string(self)-> str:
        '''生成额外的程序集列表字符串，形如：c:\\1.dll; c:\\123.dll
        '''
        ret = ''
        for assembly in self.options.extra_assemblys:
            ret += assembly+";"
        ret.rstrip(';')
        return ret

    def __check(self, val:str)->list:
        old = self.options.extra_assemblys[:]
        if val.startswith('+'):
            old.append(val[1:])
        elif val.startswith('-'):
            val = val[1:]
            for i in range(len(old)):
                if old[i] == val:
                    old.pop(i)
                    break
        else:
            old = []
            val = val.strip('[]')
            tmp = val.split(',')
            for v in tmp:
                v = v.strip("' \"")
                if not v:
                    continue
                old.append(v)
        return old

    def hook_start(self, session: WebshellSession):
        super().hook_start(session)
        p = CSharpPayload('csharp/base/baseinfo.asp_net.cs')
        ret = self.eval(p)
        if not ret.is_success():
            logger.error("Basic info gather failed!")
            return
        info = json.loads(ret.data)
        session.state['name'] = info['host']
        session.state['pwd'] = info.get('pwd').strip()
        session.state['lang'] = self.ASP_NET_CS
        session.state['description'] = self.help.lstrip('\r\n ').split('\n')[0]
        session.server_info['user'] = info.get('user').strip()
        session.server_info['webshell_root'] = info.get('pwd').strip()
        session.server_info['support_lang'] = (self.ASP_NET_CS,)
        session.server_info['os_type'] = info.get('os_type').strip()
        session.server_info['tmpdir'] = info.get('tmpdir').strip()
        session.server_info['sep'] = info.get('sep').strip()
        session.server_info['domain'] = info.get('domain')
        session.server_info['group'] = info.get('group')

        if 'win' not in info['os_type'].lower():
            logger.warning("The target system is not windows. Some commands may fail.")
