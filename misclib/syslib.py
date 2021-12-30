import sys


class syslib:
    OS_WINDOWS = 'Windows'
    OS_LINUX = 'Linux'
    OS_MAC_OSX = 'MacOSX'

    @staticmethod
    def get_platform():
        platforms = {
            'linux': syslib.OS_LINUX,
            'linux1': syslib.OS_LINUX,
            'linux2': syslib.OS_LINUX,
            'darwin': syslib.OS_MAC_OSX,
            'win32': syslib.OS_WINDOWS
        }
        if sys.platform not in platforms:
            return sys.platform

        return platforms[sys.platform]

    @staticmethod
    def is_raspberry_pi():
        """
        ref: https://stackoverflow.com/questions/41164147/raspberry-pi-python-detect-os
        """
        try:
            import RPi.GPIO
            ret = True
        except (ImportError, RuntimeError) as e:
            print(e)
            ret = False

        return ret
