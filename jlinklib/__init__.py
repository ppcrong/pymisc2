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

