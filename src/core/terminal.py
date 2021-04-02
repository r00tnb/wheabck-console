
from src.core.base import TerminalBase, Cmdline, Command
from src.ui.pretty import colour, tablor
import src.config as config
from src.exception import CommandNotFound
from src.logger import logger
import importlib

class Terminal(TerminalBase):
    '''实现自动补全，历史命令等功能
    '''

    def __init__(self):
        super().__init__()
        
        self._readline = None # 指示是否包含readline库
        
        try:
            self._readline = importlib.import_module('readline')
            self._readline.set_completer(self.complete)
            self._readline.set_completer_delims('')
            self._readline.parse_and_bind('tab: complete')
            self._readline.clear_history()
            self._readline.read_history_file(config.history_path)
            if hasattr(self._readline, 'set_auto_history'):
                self._readline.set_auto_history(False)
        except ModuleNotFoundError:
            logger.warning("No module `readline`! You can type `pip install readline` to install it in Unix platform, or `pip install pyreadline` in windows platform.")
            logger.info("You can ignore this warning, but command will not be auto-completed and command history is not available.")
            self._readline = None
    
    def interrupt_handler(self, args: Cmdline)-> int:
        print('')
        if self.input(colour.colorize(f"Are you sure exit?(y/n) ", 'bold')).lower() == 'y':
            return Command.EXIT
        return Command.STOP
    
    def exception_handler(self, args: Cmdline, e: BaseException) -> int:
        if isinstance(e, SystemExit):
            return Command.STOP
        elif isinstance(e, CommandNotFound):
            logger.error(e)
            return Command.STOP
        return super().exception_handler(args, e)
        
    def precmd(self, args: Cmdline)-> Cmdline:
        if self._readline is not None and args.cmd is not None:
            self._readline.add_history(args.cmdline)
        return args

    def complete(self, text: str, state: int):
        return None

    def postloop(self):
        self._readline.set_history_length(1000)
        self._readline.write_history_file(config.history_path)
            