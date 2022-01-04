import enum


def flash_progress(action, progress_string, percentage):
    from loglib.printlib import printlib
    printlib.draw_percent(percentage / 100, action.decode('ascii'))


class JLINK_EXE(enum.Enum):
    WINDOWS = 'JLink.exe'
    LINUX = 'JLinkExe'
    MACOSX = 'JLinkExe'


class JLINK_CMD(enum.Enum):
    si = 'interface'
    speed = 'speed'
    device = 'device'
    r = 'reset'
    h = 'halt'
    erase = 'erase'
    loadbin = 'loadbin'
    g = 'go'


class jcmd:
    """
    J-Link command
    https://wiki.segger.com/index.php?title=J-Link_Commander
    """

    def __init__(self,
                 cmd: str,
                 params: list):
        self.cmd = cmd
        self.params = params

    def __repr__(self) -> str:
        ret_str = super().__repr__()
        ret_str = '\n\t'.join((ret_str, f'cmd: {self.cmd}'))
        ret_str = '\n\t'.join((ret_str, f'params: {self.params}'))
        return ret_str
