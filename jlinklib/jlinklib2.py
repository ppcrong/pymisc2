import datetime
import pathlib

import pylink
from PyQt5.QtCore import pyqtSignal

import jlinklib
from jlinklib import jcmd, JLINK_CMD
from loglib.loglib import loglib
from misclib import try_catch


class jlinklib2:
    """
    v2 wrapper for pylink
    (diff from v1 for behavior change)
    """
    slogger = loglib(__name__)
    flash_progress = pyqtSignal(int, str, str)
    status = pyqtSignal(str)

    def __init__(self,
                 lib_path: str = None,
                 lib_path_backup: str = None,
                 flash_progress: pyqtSignal = None,
                 status: pyqtSignal = None):
        super().__init__()
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S.%f')
        self.logger = loglib(f'{__name__}_time{timestamp}')
        self.jlink = self.init(lib_path=lib_path, lib_path_backup=lib_path_backup)
        if flash_progress:
            self.flash_progress = flash_progress
        else:
            self.flash_progress = None
        if status:
            self.status = status
        else:
            self.status = None

    def init(self,
             lib_path: str = None,
             lib_path_backup: str = None):
        """
        1. load lib_path
        2. load installed jlink library
        3. load lib_path_backup
        """
        jlink = None
        while True:

            """
            load lib_path
            """
            if lib_path and not lib_path.isspace():
                try:
                    lib = pylink.Library(dllpath=lib_path)
                    jlink = pylink.JLink(lib=lib)
                except Exception as e:
                    self.logger.warning(f'{type(e).__name__}!!! {e}')

                if jlink:
                    break
                else:
                    self.logger.warning(f'cannot load lib_path: {lib_path}')
            else:
                self.logger.warning('lib_path is empty')

            """
            load installed jlink library
            """
            try:
                jlink = pylink.JLink()
            except Exception as e:
                self.logger.warning(f'{type(e).__name__}!!! {e}')

            if jlink:
                break
            else:
                self.logger.warning(f'no default J-Link installed!!! next load lib_path_backup: {lib_path_backup}...')

            """
            load lib_path_backup
            """
            if lib_path_backup and not lib_path_backup.isspace():
                try:
                    lib = pylink.Library(dllpath=lib_path_backup)
                    jlink = pylink.JLink(lib=lib)
                except Exception as e:
                    self.logger.warning(f'{type(e).__name__}!!! {e}')

                if jlink:
                    break
                else:
                    self.logger.warning(f'cannot load lib_path_backup: {lib_path_backup}')
            else:
                self.logger.warning('lib_path_backup is empty')

            break

        if jlink:
            self.logger.info(f'jlink.version: {jlink.version}')
            self.logger.info(f'jlink.lib: {jlink._library._path}')
        else:
            self.logger.error(f'failed to get jlink!!!')

        return jlink

    def close(self):
        if self.jlink:
            self.jlink.close()

    # region [function]
    def print_status(self, ret, text: str = ''):
        if type(ret) == bool and not ret:
            self.logger.e1(msg=text)
        else:
            self.logger.i1(msg=text)

        if self.status:
            self.status.emit(ret, text)

    def get_lib(self):
        lib = None
        if self.jlink:
            lib = self.jlink._library
        return lib

    def connect(self,
                serial_no: int = None,
                interface=pylink.enums.JLinkInterfaces.SWD,
                device_xml: str = '',
                chip_name: str = '',
                speed: int = 10000,
                disable_dialog_boxes: bool = True):
        self.logger.info(f'serial_no: {serial_no}')
        self.logger.info(f'interface: {interface}')
        self.logger.info(f'device_xml: {device_xml}')
        self.logger.info(f'chip_name: {chip_name}')
        self.logger.info(f'speed: {speed}')
        self.logger.info(f'disable_dialog_boxes: {disable_dialog_boxes}')

        ret = False
        if not self.jlink:
            return ret

        while True:
            ret, ret_msg = try_catch(self.jlink.num_connected_emulators)()
            self.print_status(ret=ret, text=ret_msg)
            if type(ret) == bool and not ret:
                break
            if ret <= 0:
                self.print_status(ret=False, text='no jlink connected!!!')
                break

            if disable_dialog_boxes:
                ret, ret_msg = try_catch(self.jlink.disable_dialog_boxes)()
                self.print_status(ret=ret, text=ret_msg)
                if type(ret) == bool and not ret:
                    break

            """
            open
            """
            if serial_no:
                ret, ret_msg = try_catch(self.jlink.open)(serial_no=serial_no)
                self.print_status(ret=ret, text=ret_msg)
                if type(ret) == bool and not ret:
                    break
            else:
                # so far support first jlink connection info
                info = self.get_first_info()
                if info:
                    # open jlink
                    ret, ret_msg = try_catch(self.jlink.open)(serial_no=info.SerialNumber)
                    self.print_status(ret=ret, text=ret_msg)
                    if type(ret) == bool and not ret:
                        break
                    self.logger.info(f'jlink.firmware_version: {self.jlink.firmware_version}')
                    self.logger.info(f'jlink.hardware_version: {self.jlink.hardware_version}')
                else:
                    self.print_status(ret=False, text='no jlink connected!!!')
                    break

            """
            set interface (default is SWD)
            """
            ret, ret_msg = try_catch(self.jlink.set_tif)(interface=interface)
            self.print_status(ret=ret, text=ret_msg)
            if type(ret) == bool and not ret:
                break

            """
            set device xml path
            """
            if device_xml and not device_xml.isspace():
                ret, ret_msg = try_catch(self.jlink.exec_command)(cmd=f'JLinkDevicesXMLPath = {device_xml}')
                self.print_status(ret=ret, text=ret_msg)
                if type(ret) == bool and not ret:
                    break

            """
            connect jlink
            """
            ret, ret_msg = try_catch(self.jlink.connect)(chip_name=chip_name, speed=speed)
            self.print_status(ret=ret, text=ret_msg)
            if type(ret) == bool and not ret:
                break

            ret = True
            self.logger.info(f'core_name: {self.jlink.core_name()}')

            break

        return ret

    def get_first_info(self):
        info = None
        ret, ret_msg = try_catch(self.jlink.connected_emulators)()
        if type(ret) == bool and not ret:
            return info

        for i, item in enumerate(ret):
            self.logger.info(f'JLinkConnectInfo[{i}]: {item}')

        if len(ret) > 0:
            info = ret[0]

        return info

    @staticmethod
    def get_device_name(jcmds: list[jcmd]):
        if not jcmds or len(jcmds) <= 0:
            jlinklib2.slogger.warning('cmds are invalid or empty!!!')
            return ''

        chip_name: str = ''
        for c in jcmds:
            if c.cmd == JLINK_CMD.device.name:
                chip_name = c.params[0]
                break
            else:
                continue

        return chip_name

    def process_jlink_cmds(self,
                           jcmds: list[jcmd],
                           device_xml: str = '',
                           base_path: str = ''
                           ):
        def on_progress(action: bytes, progress_string: bytes, percentage: int):
            if not action:
                action = ''
            else:
                action = action.decode('ascii')
            if not progress_string:
                progress_string = ''
            else:
                progress_string = progress_string.decode('ascii')

            """
            draw flash progress in console
            """
            from loglib.printlib import printlib
            printlib.draw_percent2(percent=percentage,
                                   text=action,
                                   text2=progress_string)

            """
            draw flash progress on ui
            """
            if self.flash_progress:
                self.flash_progress.emit(percentage,
                                         action,
                                         progress_string)

        ret = False
        if not jcmds or len(jcmds) <= 0:
            self.print_status(ret=ret, text='cmds are invalid or empty!!!')
            return ret

        """
        collect connect params
        """
        interface: int = pylink.enums.JLinkInterfaces.SWD
        chip_name: str = ''
        speed: int = 10000
        for c in jcmds:
            if c.cmd == JLINK_CMD.si.name:
                interface = int(c.params[0])
            elif c.cmd == JLINK_CMD.speed.name:
                speed = int(c.params[0])
            elif c.cmd == JLINK_CMD.device.name:
                chip_name = c.params[0]
            else:
                """
                ignore other cmds
                """
                continue

        """
        connect
        """
        ret = self.connect(interface=interface,
                           device_xml=device_xml,
                           chip_name=chip_name,
                           speed=speed)
        if not ret:
            self.logger.error('connect fail!!!')
            return ret

        """
        process remaining cmds
        """
        for c in jcmds:
            if c.cmd == JLINK_CMD.si.name or c.cmd == JLINK_CMD.speed.name or c.cmd == JLINK_CMD.device.name:
                """
                ignore connect params
                """
                continue
            else:
                if c.cmd == JLINK_CMD.r.name:
                    ret, ret_msg = try_catch(self.jlink.reset)()
                elif c.cmd == JLINK_CMD.h.name:
                    ret, ret_msg = try_catch(self.jlink.halt)()
                elif c.cmd == JLINK_CMD.erase.name:
                    ret, ret_msg = try_catch(self.jlink.erase)()
                elif c.cmd == JLINK_CMD.loadbin.name:
                    if base_path:
                        path = pathlib.Path(base_path, c.params[0])
                    else:
                        path = c.params[0]
                    address = int(c.params[1], 16)
                    ret, ret_msg = try_catch(self.jlink.flash_file)(path=str(path),
                                                                    addr=address,
                                                                    on_progress=on_progress)
                elif c.cmd == JLINK_CMD.g.name:
                    ret, ret_msg = try_catch(self.jlink.restart)()
                elif c.cmd == JLINK_CMD.exit.name:
                    ret, ret_msg = True, '[exit] ignore...'
                else:
                    """
                    ignore unsupported cmds
                    """
                    self.print_status(ret=False, text='unsupported jcmd!!!')
                    continue

                self.print_status(ret=ret, text=ret_msg)
                if type(ret) == bool and not ret:
                    break

        return ret

    # endregion [function]

    # region [with]
    def __enter__(self):
        self.logger.info()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.logger.info()
        self.close()

    # endregion [with]

    # region [static]
    @staticmethod
    def parse_jlink_file(file: str):
        """
        parse jlink file and get commands
        https://wiki.segger.com/index.php?title=J-Link_Commander

        Parameters
        ----------
        file : str
            jlink file path

        Returns
        -------
        list
            jlink cmds list
        """
        if not file or not pathlib.Path(file).is_file() or not file.endswith('.jlink'):
            jlinklib2.slogger.error(f'file: {file} is invalid!!!')
            return []

        cmds = []
        with open(file) as f:
            lines = f.readlines()
            for line in lines:
                list_cmd_line = line.split()
                if len(list_cmd_line) == 0:
                    continue

                """
                get cmd
                """
                cmd = list_cmd_line[0]
                list_cmd_line.pop(0)
                """
                get params
                """
                params = []
                for param in list_cmd_line:
                    if cmd == JLINK_CMD.loadbin.value:
                        # if cmd is loadbin, parse at least 2 params for bin file path and address
                        bin_params = param.split(sep=',')
                        if len(bin_params) >= 2:
                            # file path
                            params.append(bin_params[0])
                            # address
                            params.append(bin_params[1])
                    else:
                        params.append(param)

                cmds.append(jcmd(cmd=cmd, params=params))
        return cmds

    @staticmethod
    def get_jlink_cmder():
        libs = []
        jlink_app = ''

        """
        get library path and assign jlink app name according to platform
        """
        from misclib.syslib import syslib
        if syslib.get_platform2() == syslib.OS_WINDOWS:
            libs = list(pylink.Library.find_library_windows())
            jlink_app = jlinklib.JLINK_EXE.WINDOWS.value
        elif syslib.get_platform2() == syslib.OS_LINUX:
            libs = list(pylink.Library.find_library_linux())
            jlink_app = jlinklib.JLINK_EXE.LINUX.value
        elif syslib.get_platform2() == syslib.OS_MAC_OSX:
            libs = list(pylink.Library.find_library_darwin())
            jlink_app = jlinklib.JLINK_EXE.MACOSX.value

        """
        assemble folder and app name
        """
        if len(libs) > 0 and jlink_app:
            jlink_folder = pathlib.Path(libs[0]).parent
            return str(pathlib.Path(jlink_folder, jlink_app))
        else:
            return ''

    @staticmethod
    def open_jlink_cmder(file: str = None):
        if file:
            jlink_cmder = file
        else:
            jlink_cmder = jlinklib2.get_jlink_cmder()

        jlinklib2.slogger.info(f'J-Link Commander path: {jlink_cmder}')
        import pathlib
        if not jlink_cmder or not pathlib.Path(jlink_cmder).exists() or not pathlib.Path(jlink_cmder).is_file():
            jlinklib2.slogger.error('invalid J-Link Commander path')
            return False

        from misclib.syslib import syslib
        import subprocess
        if syslib.get_platform2() == syslib.OS_WINDOWS:
            subprocess.Popen(['start', pathlib.Path(jlink_cmder).name], shell=True,
                             cwd=pathlib.Path(jlink_cmder).parent)
        elif syslib.get_platform2() == syslib.OS_LINUX:
            subprocess.Popen(['open', jlink_cmder], shell=True)
        elif syslib.get_platform2() == syslib.OS_MAC_OSX:
            subprocess.Popen(['open', jlink_cmder], shell=True)
        return True
    # endregion [static]


def main():
    import pathlib
    path_lib_622c_folder = pathlib.Path('D:/GitLab/kp/kntools/apps/rdtool/asset/jlink/KL520/')
    path_lib_694d_folder = pathlib.Path('D:/GitLab/kp/kntools/apps/rdtool/asset/jlink/KL720/')
    fake_folder = pathlib.Path('Z:/Temp/')
    import pylink
    from misclib.syslib import syslib

    """
    load installed jlink
    """
    j = jlinklib2()
    j.close()

    if syslib.get_platform2() == syslib.OS_WINDOWS:
        lib_name = pylink.Library.get_appropriate_windows_sdk_name()
        path_lib_622c = pathlib.Path(path_lib_622c_folder, f'{lib_name}.dll')
        path_lib_694d = pathlib.Path(path_lib_694d_folder, f'{lib_name}.dll')
        """
        load jlink 622c
        """
        j = jlinklib2(lib_path=str(path_lib_622c))
        j.close()

        """
        load jlink 694d
        """
        j = jlinklib2(lib_path=str(path_lib_694d))
        j.close()

        """
        test load backup (needs pc has no JLink installed for test)
        """
        fake_lib = pathlib.Path(fake_folder, f'{lib_name}.dll')
        demo_lib = pathlib.Path('../asset/jlink/6.94d', f'{lib_name}.dll')
        j = jlinklib2(lib_path=str(fake_lib), lib_path_backup=str(demo_lib))
        j.close()

        demo_lib = pathlib.Path('../asset/jlink/7.60b', f'{lib_name}.dll')
        j = jlinklib2(lib_path=str(fake_lib), lib_path_backup=str(demo_lib))
        j.close()

    elif syslib.get_platform2() == syslib.OS_LINUX:
        with jlinklib2() as j:
            pass


if __name__ == "__main__":
    main()
