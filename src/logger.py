'''用于日志打印

Description:
    日志打印，单例模式，使用python内置模块logging

Export:
    logger （实例）

'''

__all__ = ['logger']

import logging
from src.ui.pretty import colour
from src.io.config import ioconfig
import src.config as config

class Logger:
    '''实现日志功能
    
    Description:
        包装logging模块，使用它的日志功能
    
    Attribute:
        
    
    '''

    ERROR = logging.ERROR
    WARNING = logging.WARNING
    INFO = logging.INFO
    DEBUG = logging.DEBUG
    TRACE = logging.DEBUG-1

    def __init__(self):
        self._logger = logging.getLogger('simple_logger')
        self._handler = logging.StreamHandler(ioconfig.stdout)
        self._formatter = logging.Formatter("")

        self._handler.setFormatter(self._formatter)
        self._handler.setLevel(config.logger_level)
        self._logger.setLevel(config.logger_level)
        self._logger.addHandler(self._handler)

        self._color_rule = [  # 高亮日志输出信息
            {
                'regexp': r"`[\s\S]*?`",  # ``高亮包裹的字符串
                'color': ['bold', 'yellow', '']
            },
            {
                'regexp': r"(?m)^\[\*\]",  # 信息
                'color': ['bold', 'blue', '']  # 对应mode, fore, back
            },
            {
                'regexp': r"(?m)^\[\+\]",  # 提示
                'color': ['bold', 'green', '']  # 对应mode, fore, back
            },
            {
                'regexp': r"(?m)^\[!\]",  # 错误
                'color': ['bold', 'red', '']  # 对应mode, fore, back
            },
            {
                'regexp': r"(?m)^\[(?:#|-)\]",  # 警告
                'color': ['bold', 'yellow', '']  # 对应mode, fore, back
            },
            {
                'regexp': r"(?m)^\[D\]",  # debug
                'color': ['', 'cyan', '']  # 对应mode, fore, back
            },
            {
                'regexp': r"(?m)^\[T\]",  # trace
                'color': ['note', '', '']  # 对应mode, fore, back
            }
        ]

    def info(self, msg: str, add=None):
        if add is not None:
            self._logger.info(colour(f"{'[+]' if add else '[-]' } {msg}", self._color_rule))
        else:
            self._logger.info(colour(f"[*] {msg}", self._color_rule))
    
    def debug(self, msg: str, exc_info=False):
        '''记录关键操作信息，如配置的修改
        '''
        self._logger.debug(colour(f"[D] {msg}", self._color_rule), exc_info=exc_info)

    def trace(self, msg: str, exc_info=False):
        '''比debug更详细的信息, 记录每个关键动作产生的冗余信息或临时信息
        '''
        self._logger.log(self.TRACE, colour(f"[T] {msg}", self._color_rule), exc_info=exc_info)

    def error(self, msg: str):
        self._logger.error(colour(f"[!] {msg}", self._color_rule))

    def warning(self, msg: str):
        self._logger.warning(colour.colorize(colour(f"[#] {msg}", self._color_rule), 'bold'))

    def set_level(self, level: int):
        self._logger.setLevel(level)


logger = Logger()