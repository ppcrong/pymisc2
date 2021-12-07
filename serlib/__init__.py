import enum


class ENUM_BAUDRATE(enum.IntEnum):
    """
    baudate
    """
    B_110 = 110
    B_300 = 300
    B_600 = 600
    B_1200 = 1200
    B_2400 = 2400
    B_4800 = 4800
    B_9600 = 9600
    B_14400 = 14400
    B_19200 = 19200
    B_38400 = 38400
    B_57600 = 57600
    B_115200 = 115200
    B_230400 = 230400
    B_460800 = 460800
    B_921600 = 921600


class ENUM_DATA(enum.Enum):
    """
    data
    """
    BIT_7 = '7 bit'
    BIT_8 = '8 bit'


class ENUM_PARITY(enum.Enum):
    """
    parity
    """
    NONE = 'none'
    ODD = 'odd'
    EVEN = 'even'
    MARK = 'mark'
    SPACE = 'space'


class ENUM_STOP_BITS(enum.Enum):
    """
    stop bits
    """
    BIT_1 = '1 bit'
    BIT_1p5 = '1.5 bit'
    BIT_2 = '2 bit'


class ENUM_FLOW_CONTROL(enum.Enum):
    """
    parity
    """
    XON_XOFF = 'Xon/Xoff'
    RTS_CTS = 'RTS/CTS'
    DSR_DTR = 'SDR/DTR'
    NONE = 'none'
