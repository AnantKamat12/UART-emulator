import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from uart_emulator.infrastructure.Logger import logger,HostType
lg=logger(3,"rxhost",0,HostType.RxHost)
lg.write("anant",2)
lg.write("abcd")
logger.logprint("ask",9)