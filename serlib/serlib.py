import datetime
from collections import deque
from concurrent.futures.thread import ThreadPoolExecutor

import serial
from PyQt5.QtCore import QThread, pyqtSignal
from serial import EIGHTBITS, PARITY_NONE, STOPBITS_ONE

from loglib.loglib import loglib
from serlib import QUEUE_READ_MAX


class serlib(QThread):
    """
    The library for serial port.
    """

    read_received = pyqtSignal(str)

    def __init__(self,
                 port: str,
                 baudrate: int = 115200,
                 bytesize: int = EIGHTBITS,
                 parity: str = PARITY_NONE,
                 stopbits: float = STOPBITS_ONE,
                 timeout: int = 1,
                 xonxoff: bool = False,
                 rtscts: bool = False,
                 write_timeout: int = 1,
                 dsrdtr: bool = False,
                 inter_byte_timeout: int = None,
                 read_received=None
                 ):
        super().__init__()
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S.%f')
        self.logger = loglib(f'{__name__}_p{port}_time{timestamp}')
        self.port = port
        self.serial = None
        self.bufr = deque(maxlen=QUEUE_READ_MAX)
        self.bufw = deque()
        if read_received:
            self.read_received.connect(read_received)
        else:
            self.read_received = None
        try:
            self.serial = serial.Serial(port=port,
                                        baudrate=baudrate,
                                        bytesize=bytesize,
                                        parity=parity,
                                        stopbits=stopbits,
                                        timeout=timeout,
                                        xonxoff=xonxoff,
                                        rtscts=rtscts,
                                        write_timeout=write_timeout,
                                        dsrdtr=dsrdtr,
                                        inter_byte_timeout=inter_byte_timeout
                                        )
        except Exception as e:
            self.logger.error(f'{type(e).__name__}!!! {e}')

    def is_opened(self):
        if self.serial:
            return self.serial.is_open
        else:
            self.logger.error('serial is None!!!')
            return False

    def in_waiting(self):
        if self.serial:
            return self.serial.in_waiting
        else:
            self.logger.error('serial is None!!!')
            return False

    def close(self):
        if self.serial:
            self.serial.close()
        else:
            self.logger.error('serial is None!!!')

    def write_data(self, data: str):
        """
        put write data into queue (write_thread check queue to write)
        """
        self.bufw.appendleft(data)

    def write(self, data: str):
        """
        direct write data
        """
        if self.serial:
            try:
                len_write = self.serial.write(data.encode())
                self.logger.info(f'WRITE len({len_write})')
                self.logger.info(f'WRITE >>> {data}')
            except Exception as e:
                self.logger.error(f'{type(e).__name__}!!! {e}')
        else:
            self.logger.error('serial is None!!!')

    def read(self, size: int):
        """
        direct read data
        """
        ret = None
        if self.serial:
            try:
                raw = self.serial.read(size=size)
                data = raw.decode()
                self.logger.info(f'READ len({len(data)})')
                self.logger.info(f'READ <<<\n{data}')
                ret = data
            except Exception as e:
                self.logger.error(f'{type(e).__name__}!!! {e}')
        else:
            self.logger.error('serial is None!!!')
        return ret

    def readline(self):
        ret = None
        if self.serial:
            try:
                raw = self.serial.readline()
                data = raw.decode()
                self.logger.info(f'READ len({len(data)})')
                self.logger.info(f'READ <<< {data}')
                ret = data
            except Exception as e:
                self.logger.error(f'{type(e).__name__}!!! {e}')
        else:
            self.logger.error('serial is None!!!')
        return ret

    def stop(self):
        self.close()

    # region [with]
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    # endregion [with]

    # region [thread]
    def run(self):
        self.logger.info(f'start!!!')
        with ThreadPoolExecutor(max_workers=2) as executor:
            executor.submit(self.write_thread)
            executor.submit(self.read_thread)
        self.logger.info('all done!!!')

    def read_thread(self):
        """
        keep reading and put data into read buffer
        """
        if not self.serial:
            self.logger.error('serial is None!!!')
            return

        while self.is_opened():
            size = self.in_waiting()
            # self.logger.info(f'size: {size}')
            if size:
                data = self.read(size)
                if data:
                    self.bufr.appendleft(data)
                    if self.read_received:
                        self.read_received.emit(data)

        # [TODO] this log won't be shown after stop
        self.logger.info('EXIT reading...')

    def write_thread(self):
        """
        keep writing when write buffer has data
        """
        if not self.serial:
            self.logger.error('serial is None!!!')
            return

        while self.is_opened():
            if len(self.bufw) > 0:
                self.write(self.bufw.pop())

        self.logger.info('EXIT writing...')

    # endregion [thread]

    @staticmethod
    def comports():
        import serial.tools.list_ports as lp
        return lp.comports()

    @staticmethod
    def devices():
        ports = serlib.comports()
        return [p.device for p in ports]

    @staticmethod
    def descriptions():
        ports = serlib.comports()
        return [p.description for p in ports]


if __name__ == "__main__":
    """
    For console test
    """
    with serlib(port='COM10') as s:
        if not s.is_opened():
            print(f'open {s.port} fail!!!')
        else:
            print(f'open {s.port} ok!!! is_opened: {s.is_opened()}')
            s.close()

    ps = serlib.comports()
    print(ps)
    devices = serlib.devices()
    descriptions = serlib.descriptions()
    print(devices)
    print(descriptions)
