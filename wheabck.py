from src.session_manager import session_manager
from src import config
from src.io.config import ioconfig
import re
import src


if __name__ == "__main__":
    ioconfig.register_top_builtins(__builtins__)
    session_manager.cmdloop()
