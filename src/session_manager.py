'''处理session信息

Description:
    保存和处理当前已存在的session信息，类比metasploit的session

Export:
    session_manager (实例) session管理器的唯一实例
    session (实例) 当前session

'''
from src.core.terminal import Terminal
from src.core.base import Cmdline, Command, load_module
from src.core.exploit import Exploit
from src.core.session import Session, MainSession, WebshellSession
from src.core.webshell import Webshell
from src.logger import logger
import src.config as config
from src.ui.pretty import colour, tablor
import re
import os
import importlib

class SessionManager(Terminal):
    '''处理session列表和已经保存的webshell条目
    
    Description:
        管理存在的session和webshell
    
    实例中的方法说明：
        1. 类似 do_* 的方法可用在所有session中
        2. 类似__do_*， __docomplete* 的方法只适用在 名为manager的session中
    
    '''
    def __init__(self):
        super().__init__()

        self.__completecache = None # 用于自动补全的缓存
        self.webshell_count = 0 #记录webshell模块的数量
        self.exploit_count = 0 # 记录exploit模块的数量
        self.manager = MainSession()
        #self.manager.autocomplete_list.append(self.__docompletepath)

        # 初始化所有模块视图
        self.manager.modules.update(self.modulesinit(config.module_path))
        logger.debug(f"All modules have been loaded from `{config.module_path}`!")

        # 加载exploit到main session中
        self.manager.loadexploit_to_session(self.manager.modules.get('exploit', {}), 'exploit', self.manager)
        logger.debug("All exploits have been loaded to manager session(MainSession).")
        self.manager._hook_loaded()
        logger.debug("All the exploit loading hooks on manager session are executed.")

    @property
    def prompt(self)-> str:
        return self.session.prompt
 
    def modulesinit(self, root: str)-> dict: # 初始化模块
        result = {}
        if os.path.isdir(root):
            for fname in os.listdir(root):
                path = os.path.join(root, fname)
                if os.path.isdir(path):
                    result.update({
                        fname:self.modulesinit(path)
                    })
                elif fname == '__init__.py':
                    p, name = os.path.split(root)
                    module = load_module(name, path)
                    if hasattr(module, 'exploit'):
                        self.exploit_count += 1
                        logger.debug(f'Load exploit `{module.__name__}` sucessfully!')
                    elif hasattr(module, 'webshell'):
                        self.webshell_count += 1
                        logger.debug(f'Load webshell client `{module.__name__}` sucessfully!')
                    return module

        return result

    def cmdhandler(self, args: Cmdline)-> int:
        if args.cmd is None:
            return Command.STOP
        cmd = args.cmd
        func = self.session.command_map.get(cmd)
        if func is None:
            logger.error(f'No command named `{cmd}`.')
            return Command.STOP
        ret = func.run(args)
        logger.debug(f'A command line `{args.cmdline}` is executed, returns `{ret}`')
        return ret

    def preloop(self):
        logger.info(f"`{self.webshell_count}` webshell clients, `{self.exploit_count}` exploits, total `{self.exploit_count+self.webshell_count}` modules correctly loaded!")

    def postloop(self):
        # 销毁所有session
        ids = [str(i) for i in self.manager.session_map]
        if len(ids):
            self.manager.exec(['sessions', '-f', '-k', *ids])
            logger.debug(f'All sessions `{str(ids)}` have been killed!')
        self.manager._hook_destroy()
        logger.debug("All the exploit destroy hooks on manager session are executed.")
        super().postloop()

    @property
    def session(self)->Session:
        if self.manager.session is None:
            return self.manager
        return self.manager.session

    def complete(self, text: str, state: int):
        if self.__completecache is None:
            for autocomplete in self.session.autocomplete_list:
                self.__completecache = autocomplete(text)
                matchs = self.__completecache['matchs']
                if len(matchs) > 0:
                    if len(matchs) == 1:
                        self.__completecache['matchs'][0] = self.__completecache['pre']+self.__completecache['matchs'][0]
                    elif len(matchs) > 1:
                        i = 1
                        s = ''
                        while True:
                            s = matchs[0][:i]
                            for match in matchs:
                                if not match.startswith(s):
                                    s = s[:-1]
                                    break
                            if s == matchs[0][:i-1]:
                                break
                            i += 1
                        if not text.endswith(s):
                            self.__completecache['matchs'] = [self.__completecache['pre']+s]
                        elif s != '':
                            self.__completecache['matchs'].append('\x7f' if config.shell in ('powershell') else '') # 最后添加一个空项防止readline联想
                    break

        
        if state < len(self.__completecache['matchs']):
            return self.__completecache['matchs'][state]
        
        self.__completecache = None
        return None

session_manager = SessionManager()