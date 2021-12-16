from serial import \
    SEVENBITS, EIGHTBITS, \
    PARITY_NONE, PARITY_ODD, PARITY_EVEN, PARITY_MARK, PARITY_SPACE, \
    STOPBITS_ONE, STOPBITS_ONE_POINT_FIVE, STOPBITS_TWO

BAUDRATES = (
    '110',
    '300',
    '600',
    '1200',
    '2400',
    '4800',
    '9600',
    '14400',
    '19200',
    '38400',
    '57600',
    '115200',
    '230400',
    '460800',
    '921600'
)

DICT_DATA = {
    '7 bit': SEVENBITS,
    '8 bit': EIGHTBITS,
}

DICT_PARITY = {
    'none': PARITY_NONE,
    'odd': PARITY_ODD,
    'even': PARITY_EVEN,
    'mark': PARITY_MARK,
    'space': PARITY_SPACE
}

DICT_STOP_BITS = {
    '1 bit': STOPBITS_ONE,
    '1.5 bit': STOPBITS_ONE_POINT_FIVE,
    '2 bit': STOPBITS_TWO,
}

FLOW_CONTROLS = (
    'Xon/Xoff',
    'RTS/CTS',
    'DSR/DTR',
    'none'
)

QUEUE_READ_MAX = 50
