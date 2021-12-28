import datetime

import pylink

from loglib.loglib import loglib


class jlinklib2:
    """
    v2 wrapper for pylink
    (diff from v1 for behavior change)
    """

    def __init__(self,
                 dll_path: str = None,
                 dll_path_backup: str = None):
        super().__init__()
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S.%f')
        self.logger = loglib(f'{__name__}_time{timestamp}')
        self.jlink = self.init(dll_path=dll_path, dll_path_backup=dll_path_backup)

    def init(self,
             dll_path: str = None,
             dll_path_backup: str = None):
        """
        1. load dll_path
        2. load installed jlink dll
        3. load dll_path_backup
        """
        jlink = None
        while True:

            """
            load dll_path
            """
            if dll_path and not dll_path.isspace():
                try:
                    lib = pylink.Library(dllpath=dll_path)
                    jlink = pylink.JLink(lib=lib)
                except Exception as e:
                    self.logger.warning(f'{type(e).__name__}!!! {e}')

                if jlink:
                    break
                else:
                    self.logger.warning(f'cannot load dll_path: {dll_path}')
            else:
                self.logger.warning('dll_path is empty')

            """
            load installed jlink dll
            """
            try:
                jlink = pylink.JLink()
            except Exception as e:
                self.logger.warning(f'{type(e).__name__}!!! {e}')

            if jlink:
                break
            else:
                self.logger.warning(f'no default J-Link installed!!! next load dll_path_backup: {dll_path_backup}...')

            """
            load dll_path_backup
            """
            if dll_path_backup and not dll_path_backup.isspace():
                try:
                    lib = pylink.Library(dllpath=dll_path_backup)
                    jlink = pylink.JLink(lib=lib)
                except Exception as e:
                    self.logger.warning(f'{type(e).__name__}!!! {e}')

                if jlink:
                    break
                else:
                    self.logger.warning(f'cannot load dll_path_backup: {dll_path_backup}')
            else:
                self.logger.warning('dll_path_backup is empty')

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

    def get_lib(self):
        lib = None
        if self.jlink:
            lib = self.jlink._library
        return lib

    def connect(self,
                serial_no: int = None,
                interface=pylink.enums.JLinkInterfaces.SWD,
                device_xml: str = None,
                chip_name: str = None,
                speed: int = 10000,
                disable_dialog_boxes: bool = True):

        ret = False
        if not self.jlink:
            return ret

        while True:
            try:
                self.logger.info(f'num_connected_emulators: {self.jlink.num_connected_emulators()}')
                if disable_dialog_boxes:
                    self.jlink.disable_dialog_boxes()

                if serial_no:
                    self.jlink.open(serial_no=serial_no)
                else:
                    # so far support first jlink connection info
                    info = self.get_first_info(jlink=self.jlink)
                    if info:
                        # open jlink
                        self.jlink.open(serial_no=info.SerialNumber)
                        self.logger.info(f'jlink.firmware_version: {self.jlink.firmware_version}')
                        self.logger.info(f'jlink.hardware_version: {self.jlink.hardware_version}')
                    else:
                        self.logger.error('no jlink connected!!!')
                        break

                    # set interface (default is SWD)
                    ret = self.jlink.set_tif(interface)
                    self.logger.info(f'set_tif({interface}) ret: {ret}')

                    # set device xml path
                    if device_xml and not device_xml.isspace():
                        ret_code = self.jlink.exec_command(f'JLinkDevicesXMLPath = {device_xml}')
                        self.logger.info(f'exec_command (JLinkDevicesXMLPath={device_xml}) ret_code: {ret_code}')

                # connect jlink
                self.jlink.connect(chip_name=chip_name, speed=speed)
                self.logger.info(f'core_name: {self.jlink.core_name()}')

            except Exception as e:
                self.logger.error(f'{type(e).__name__}!!! {e}')
                break

            break

        return ret

    def get_first_info(self, jlink: pylink.JLink):
        info = None
        info_list = jlink.connected_emulators()
        for i, item in enumerate(info_list):
            self.logger.info(f'JLinkConnectInfo[{i}]: {item}')

        if len(info_list) > 0:
            info = info_list[0]

        return info

    # region [with]
    def __enter__(self):
        self.logger.info()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.logger.info()
        self.close()
    # endregion [with]


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

    if syslib.get_platform() == 'Windows':
        lib_name = pylink.Library.get_appropriate_windows_sdk_name()
        path_lib_622c = pathlib.Path(path_lib_622c_folder, f'{lib_name}.dll')
        path_lib_694d = pathlib.Path(path_lib_694d_folder, f'{lib_name}.dll')
        """
        load jlink 622c
        """
        j = jlinklib2(dll_path=str(path_lib_622c))
        j.close()

        """
        load jlink 694d
        """
        j = jlinklib2(dll_path=str(path_lib_694d))
        j.close()

        """
        test load backup (needs pc has no JLink installed for test)
        """
        fake_lib = pathlib.Path(fake_folder, f'{lib_name}.dll')
        demo_lib = pathlib.Path('../asset/jlink/6.94d', f'{lib_name}.dll')
        j = jlinklib2(dll_path=str(fake_lib), dll_path_backup=str(demo_lib))
        j.close()

        demo_lib = pathlib.Path('../asset/jlink/7.60b', f'{lib_name}.dll')
        j = jlinklib2(dll_path=str(fake_lib), dll_path_backup=str(demo_lib))
        j.close()

    elif syslib.get_platform() == 'Linux':
        with jlinklib2() as j:
            pass


if __name__ == "__main__":
    main()
