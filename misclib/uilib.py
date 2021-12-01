from PyQt5.QtWidgets import QWidget, QDesktopWidget

from loglib.loglib import loglib


class uilib:
    slogger = loglib(__name__)

    @staticmethod
    def get_text_size(font_name: str, font_size: int, text: str):
        """
        get text size w/h
        """

        from PyQt5.QtGui import QFontMetrics
        from PyQt5.QtGui import QFont
        font = QFont(font_name, font_size)
        fm = QFontMetrics(font)
        width = fm.width(text)
        height = fm.height()
        return width, height

    @staticmethod
    def get_elided_text(font=None, font_name: str = 'Arial', font_size: int = 12, text: str = None,
                        ui_width: int = None):
        """
        get elided text by elide left
        """

        from PyQt5.QtGui import QFontMetrics
        from PyQt5.QtGui import QFont

        if not font:
            font = QFont(font_name, font_size)
        fm = QFontMetrics(font)
        width, _ = uilib.get_text_size(font_name, font_size, text)
        if width > ui_width:
            from PyQt5.QtCore import Qt
            ret_text = fm.elidedText(text, Qt.ElideLeft, ui_width)
        else:
            ret_text = text
        return ret_text

    @staticmethod
    def resize_widget(widget: QWidget, ratio_w: float = 1, ratio_h: float = 1, center: bool = True):
        # resize by ratio fullscreen
        import PyQt5
        res = PyQt5.QtWidgets.QDesktopWidget().availableGeometry()
        uilib.slogger.info(f'full (w,h):({res.width()},{res.height()})')
        w, h = res.width() * ratio_w, res.height() * ratio_h
        uilib.slogger.info(f'resize (w,h):({w:.2f},{h: .2f})')
        widget.setFixedSize(w, h)
        widget.setMaximumSize(w, h)

        if center:
            # bring screen to center
            uilib.center(widget=widget)

    @staticmethod
    def center(widget: QWidget):
        # geometry of the main window
        qr = widget.frameGeometry()

        # center point of screen
        cp = QDesktopWidget().availableGeometry().center()

        # move rectangle's center point to screen's center point
        qr.moveCenter(cp)

        # top left of rectangle becomes top left of window centering it
        widget.move(qr.topLeft())
