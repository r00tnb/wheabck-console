from src.core.base import SessionBase, Cmdline, Command, load_module
from src.ui.pretty import tablor, colour
from src.core.webshell import Webshell
from src.logger import logger
from src.io.config import ioconfig
from src.exception import CommandNotFound
import src.config as config
import re
import os
from typing import Union
import sys

class Session(SessionBase):

    def __init__(self):
        self.update({
            'Command List':{ # 存储命令列表
                #'Core Commands':{},  键为命令名称，值为对应的命令对象
            },
            "Alias Commands":{},
            "Auto Complete":[
                # 所有命令补全函数形如self.docomplete
                self.docomplete,
            ],
            'State':{# 存储一些状态数据
                'client':None
            },
            'Prompt':lambda :f"{colour.colorize(config.app_name, 'underline')} {colour.colorize(config.prompt, 'bold', 'blue')} " # 用于terminal显示的prompt
        })

    @property
    def client(self)-> Webshell:
        return self.state.get('client')

    @property
    def prompt(self)->str:
        return self['Prompt']()
    
    @client.setter
    def client(self, client:Webshell):
        self.state['client'] = client

    @property
    def autocomplete_list(self)-> list:
        return self['Auto Complete']

    @property
    def state(self)-> dict:
        return self['State']
    
    def docomplete(self, text: str)-> dict:# 补全命令
        result = []
        if text=='' or self.cmdok(text):
            for cmd in self.command_map:
                if cmd.startswith(text.lower()):
                    result.append(cmd+' ')
        return {'pre':'', 'matchs':result}

    @property
    def command_map(self)-> dict:
        result = {}
        for v in self['Command List'].values():
            result.update(v)
        result.update(self.alias_command)
        return result
    
    @property
    def alias_command(self)-> dict:
        return self['Alias Commands']

    def _hook_loaded(self):
        '''当session加载完毕后执行
        '''
        for command in self.command_map.values():
            if command is None:
                continue
            command.hook_loaded()
    
    def _hook_destroy(self):
        '''当session销毁后执行
        '''
        for command in self.command_map.values():
            if command is None:
                continue
            command.hook_destroy()

    def exec(self, line:Union[str, tuple, list], echo=True):
        '''执行一个命令列表中的命令, echo为False时命令的输出和返回值将会作为该函数得返回值返回（不回显）类似 output, retcode， 反之回显命令的输出并返回命令的返回值
        '''
        args = Cmdline(line)
        cmd = None
        for name, command in self.command_map.items():
            if args.cmd == name:
                cmd = command
                break
        if cmd is None:
            raise CommandNotFound(f"No command named `{args.cmd}`")
        
        if echo:
            return cmd.run(args)

        result = ''
        out = ioconfig.echo_off()
        c = 0
        try:
            c = cmd.run(args)
        except SystemExit:
            pass
        finally:
            result = out.readall()
            ioconfig.echo_on()

        return result, c
    
    def has_cmd(self, cmd: str)-> bool:
        return cmd in self.command_map.keys()

    def cmdok(self, cmd: str)-> bool:
        '''验证命令命名是否标准'''
        if re.compile(r'^[\w\-]+$', re.M).match(cmd):
            return True
        return False


class WebshellSession(Session):

    def __init__(self, webshell: Webshell, ID: int):
        super().__init__()
        self.client = webshell
        self['session_id'] = ID # 记录当前webshell session的id
        # 所有状态信息应该在webshell建立连接后进行初始化
        self.state['type'] = webshell.type
        self.state['description'] = ''
        self.state['pwd'] = None
        self.state['name'] = None
        self.state['lang'] = None # 表示当前webshell使用的语言，如：php等
        self.state['Server Info'] = {
            'user':None, # 当前用户名
            'group':None, # 当前用户所在组名
            'domain':None, # 当前用户的域名
            'webshell_root':None, # webshell所在的目录
            'support_lang': (), # 表示当前服务器支持的动态语言类型，如：php, aspx等
            'os_type': None, # 服务器系统类型，如：windows,linux
            'tmpdir': None, # 服务器的临时文件目录
            'sep': None, # 服务器系统使用的文件路径分隔符
        }

    @property
    def id(self)-> int:
        return self['session_id']

    @property
    def server_info(self)-> dict:
        return self.state.get('Server Info')

    def isUnix(self)-> bool:
        return not self.isWindows()

    def isWindows(self)-> bool:
        if self.server_info['os_type'].lower().startswith('win'):
            return True
        return False


class MainSession(Session):
    '''
    '''

    def __init__(self):
        super().__init__()
        self['Command List']['Webshell Manage Commands'] = {}
        self['Modules'] = {}
        self['Session Map'] = {} # 保存webshell session
        self['current_session_id'] = None

    @property
    def session(self)-> WebshellSession:
        '''当前正在使用的webshell session
        '''
        return self.session_map.get(self['current_session_id'])

    @property
    def webshell_command(self)-> dict:
        return self['Command List']['Webshell Manage Commands']

    @property
    def session_map(self)-> dict:
        '''返回当前所有webshell session
        '''
        return self['Session Map']

    @property
    def modules(self)-> dict:
        '''获取所有可用模块'''
        return self['Modules']

    def loadexploit_to_session(self, module: dict, category: str, session:Session):
        '''将module中的exploit全部加载到指定的session中
        '''
        category = ' '.join([s.capitalize() for s in category.split('_')])+' Commands'
        for mod, m in module.items():
            if isinstance(m, dict):
                self.loadexploit_to_session(m, mod, session)
            elif m is not None:
                try:
                    exploit = m.exploit()
                    if exploit.support(session):
                        exploit.name = mod # 为模块重命名
                        lst = session['Command List'].get(category)
                        if lst is None:
                            session['Command List'][category] = {}
                            lst = session['Command List'][category]
                        lst.update({
                            mod:exploit
                        })
                        if hasattr(exploit, 'docomplete') and hasattr(exploit.docomplete, '__call__'):
                            session.autocomplete_list.append(exploit.docomplete)
                except Exception as e:
                    raise e
                    logger.error(f'Load exploit `{mod}` failed!')
