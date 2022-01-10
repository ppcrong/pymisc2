from pathlib import Path
from threading import Thread


class threadlib:

    def __init__(self):
        super().__init__()
        self.execute_bat_thread = None
        self.execute_python3_thread = None

    def execute_bat(self,
                    bat: str,
                    cb_done):
        import subprocess
        ex = subprocess.Popen([bat], stdout=subprocess.PIPE, shell=True, cwd=Path(bat).parent)
        stdout, stderr = ex.communicate()
        status = ex.wait()
        if cb_done:
            cb_done(stdout, stderr, status)

    def execute_bat_async(self,
                          bat: str,
                          cb_done):
        self.execute_bat_thread = Thread(target=self.execute_bat, args=(bat, cb_done))
        self.execute_bat_thread.start()

    def execute_python3(self,
                        cmds: list,
                        cwd: str,
                        cb_done):
        args = ['python3']
        args.extend(cmds)
        import subprocess
        ex = subprocess.Popen(args=args, stdout=subprocess.PIPE, shell=True, cwd=cwd)
        stdout, stderr = ex.communicate()
        status = ex.wait()
        if cb_done:
            cb_done(stdout, stderr, status)

    def execute_python3_async(self,
                              cmds: list,
                              cwd: str,
                              cb_done):
        self.execute_python3_thread = Thread(target=self.execute_python3, args=(cmds, cwd, cb_done))
        self.execute_python3_thread.start()
