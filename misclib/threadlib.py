from pathlib import Path
from threading import Thread


class threadlib:

    def __init__(self):
        super().__init__()
        self.execute_bat_thread = None

    def execute_bat(self, bat: str, cb_done):
        import subprocess
        ex = subprocess.Popen([bat], stdout=subprocess.PIPE, shell=True, cwd=Path(bat).parent)
        stdout, stderr = ex.communicate()
        status = ex.wait()
        cb_done(stdout, stderr, status)

    def execute_bat_async(self, bat: str, cb_done):
        self.execute_bat_thread = Thread(target=self.execute_bat, args=(bat, cb_done))
        self.execute_bat_thread.start()
