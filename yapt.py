#!/usr/bin/env python3

#from PyQt5.QtCore import QThread
#from PyQt5.QtWidgets import QApplication, QLabel, QWidget, QPushButton, QVBoxself.layout. QMessageBox
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

import serial
import time

BG_COLOR = '#555555'
FG_COLOR = '#FFFFFF'
MENU_BTN_WIDTH = 120

class PicButton(QAbstractButton):
    def __init__(self, pixmap, pixmap_pressed, parent=None):
        super(PicButton, self).__init__(parent)
        # do not scale with window
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.pixmap = pixmap
        #self.pixmap_hover = pixmap_hover
        self.pixmap_pressed = pixmap_pressed

        self.pressed.connect(self.update)
        self.released.connect(self.update)

    def paintEvent(self, event):
        #pix = self.pixmap_hover if self.underMouse() else self.pixmap
        pix = self.pixmap
        if self.isDown():
            pix = self.pixmap_pressed

        painter = QPainter(self)
        painter.drawPixmap(event.rect(), pix)

    def enterEvent(self, event):
        self.update()

    def leaveEvent(self, event):
        self.update()

    def sizeHint(self):
        return QSize(187, 86)


class UARTThread(QThread):

    def __init__(self, uart, recv):
        QThread.__init__(self)
        self.uart = uart
        self.recv = recv

    def __del__(self):
        self.wait()

    def run(self):
        text = ''
        while True:
            text += self.uart.recv()
            self.recv.setText(text)
            time.sleep(0.1)


class UART():

    def __init__(self, baud):
        self.ser = serial.Serial('/dev/ttyUSB0', baud)

    def send(self, data):
        print(data.encode('utf-8'))
        self.ser.write(data.encode('utf-8'))

    def recv(self):
        a = self.ser.read(1)
        print(a)
        return a.decode()


class YAPTLayout(QWidget):

    def __init__(self, parent=None):
        super(YAPTLayout, self).__init__(parent)
        self.init_gui()
        
        self.uart = None
        self.baud_rate = None


    def init_gui(self):
        #window.setFixedSize(500, 500)
        #self.setStyleSheet('background-color:{};color:{};font-family:Courier'.format(BG_COLOR, FG_COLOR))
        self.layout = QGridLayout()

        self.setStyleSheet("""
            QPushButton {
                border: 1px solid #121212;
                border-radius: 2px;
                background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                      stop: 0 #FB432c, stop: 1 #EF4923);
                min-width: 80px;
                min-height: 22px;
            }

            QPushButton#StyledButton {
                color: #F00;
                background-color: #000;
            }
                           """)

        # baud rate
        baud_lab = QLabel('Baud rate')
        self.layout.addWidget(baud_lab, 0, 0)
        self.baud_btn = QPushButton('Baud rate')
        #self.baud_btn.setStyleSheet('QPushButton {background-color:#EF4923}')
        #self.baud_btn.setStyleSheet('QPushButton:pressed {background-color: qlineargradient(x1: 1, y1: 1, x2: 1, y2: 1, stop: 0 #EF4923, stop: 1 #EF4923, stop: 0 #EF4923, stop: 1 #EF4923)}')
        self.baud_btn.setFixedWidth(MENU_BTN_WIDTH)
        self.baud_btn.clicked.connect(self.select_baud)
        self.layout.addWidget(self.baud_btn, 1, 0)

        # data bits
        data_lab = QLabel('Data bits')
        self.layout.addWidget(data_lab, 0, 1)
        data_cmb = QComboBox()
        data_cmb.setFixedWidth(MENU_BTN_WIDTH)
        data_cmb.addItem('5')
        data_cmb.addItem('6')
        data_cmb.addItem('7')
        data_cmb.addItem('8')
        data_cmb.addItem('9')
        self.layout.addWidget(data_cmb, 1, 1)

        # stop bits
        stop_lab = QLabel('Stop bits')
        self.layout.addWidget(stop_lab, 0, 2)
        stop_cmb = QComboBox()
        stop_cmb.setFixedWidth(MENU_BTN_WIDTH)
        stop_cmb.addItem('1')
        stop_cmb.addItem('2')
        self.layout.addWidget(stop_cmb, 1, 2)
        
        # parity
        parity_lab = QLabel('Parity')
        self.layout.addWidget(parity_lab, 0, 3)
        parity_cmb = QComboBox()
        parity_cmb.setFixedWidth(MENU_BTN_WIDTH)
        parity_cmb.addItem('None')
        parity_cmb.addItem('Even')
        parity_cmb.addItem('Odd')
        self.layout.addWidget(parity_cmb, 1, 3)

        # device port
        dev_lab = QLabel('COM port')
        self.layout.addWidget(dev_lab, 0, 4)
        dev_cmb = QComboBox()
        dev_cmb.setFixedWidth(MENU_BTN_WIDTH)
        dev_cmb.addItem('COM1')
        dev_cmb.addItem('COM3')
        self.layout.addWidget(dev_cmb, 1, 4)
        
        # data format
        format_lab = QLabel('Data format')
        self.layout.addWidget(format_lab, 0, 5)
        format_cmb = QComboBox()
        format_cmb.setFixedWidth(MENU_BTN_WIDTH)
        format_cmb.addItem('Characters')
        format_cmb.addItem('Hex')
        format_cmb.addItem('Bin')
        self.layout.addWidget(format_cmb, 1, 5)

        recv_lab = QLabel('Data received')
        self.layout.addWidget(recv_lab, 2, 0)
        recv_le = QLineEdit()
        recv_le.setMinimumWidth(600)
        recv_le.setMinimumHeight(600)
        self.layout.addWidget(recv_le, 3, 0, 5, 5)

        # send field and button
        send_lab = QLabel('Data send')
        self.layout.addWidget(send_lab, 9, 0)
        send_le = QLineEdit()
        send_le.setMinimumWidth(600)
        self.layout.addWidget(send_le, 10, 0, 1, 5)
 
        send_btn = PicButton(QPixmap('send_up.png'), QPixmap('send_down.png'))
        send_btn.resize(187, 86)
        self.layout.addWidget(send_btn, 10, 5)


        conn = PicButton(QPixmap('connect_up.png'), QPixmap('connect_down.png'))#QPushButton('Connect')
        conn.resize(187, 86)
        #conn.setFixedWidth(MENU_BTN_WIDTH)
        conn.clicked.connect(self.connect)
        self.layout.addWidget(conn, 3, 5)

        echo_cb = QCheckBox('Echo')
        echo_cb.setChecked(True)
        self.layout.addWidget(echo_cb, 4, 5)

        color_cb = QCheckBox('Color')
        color_cb.setChecked(True)
        self.layout.addWidget(color_cb, 5, 5)


#        send_btn = QPushButton('Send')
#        top.setStyleSheet('background-color:#FF0000;color:#0000FF;')
#        send_btn.clicked.connect(self.send)
#        self.layout.addWidget(send_btn, 10, 7)

#        baud_dd = QComboBox()
#        baud_dd.addItem('9600')
#        baud_dd.addItem('115200')
#        self.layout.addWidget(baud_dd, 0, 0)
#        baud_dd.activated[str].connect(self.alert)


#        conn = PicButton(QPixmap('connect_up.png'), QPixmap('connect_down.png'))
        #conn.resize(325, 121)
#        conn.clicked.connect(self.connect)
#        self.layout.addWidget(conn)
      



        self.setLayout(self.layout)
        


    def select_baud(self):
        """ Create pop-up to select baud rate. """
        diag = QDialog()
        diag.setStyleSheet('background-color:{};color:{};'.format(BG_COLOR, FG_COLOR))
        diag.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        diag.setWindowTitle('Baud rate')
        diag.setFixedSize(240, 110)

        lab = QLabel('Enter baud rate', diag)
        lab.move(10, 10)

        baud_rate = QLineEdit(diag)
        baud_rate.setFixedWidth(220)
        baud_rate.move(10, 30)

        btn_ok = QPushButton('Ok', diag)
        btn_ok.clicked.connect(diag.accept)
        btn_ok.setFixedWidth(100)
        btn_ok.move(10, 70)

        btn_cancel = QPushButton('Cancel', diag)
        btn_cancel.clicked.connect(diag.close)
        btn_cancel.setFixedWidth(100)
        btn_cancel.move(130, 70)

        diag.setWindowModality(Qt.ApplicationModal)
        ret = diag.exec_()

        if ret == 1:
            try:
                baud = int(baud_rate.text())
            except:
                self.alert('Baud rate must be an integer')
                return
            self.baud_rate = baud
            self.baud_btn.setText(str(baud))


    def connect(self):
        try:
            self.uart = UART(int(self.baud.text()))
            self.alert('Device connected')
            self.uartthread = UARTThread(self.uart, self.recv_text)
            self.uartthread.start()
        except ValueError:
            self.alert('Baud must be an integer')
        except Exception as e:
            self.alert('Something fucked up: {}'.format(e))
             
    def send(self):
        if self.uart is None:
            self.alert('You need to connect before sending')
            return

        try:
            self.uart.send(self.send_text.text())
        except Exception as e:
            self.alert('Wrong text format')

    def alert(self, msg):
            alert = QMessageBox()
            alert.setStyleSheet('background-color:{};color:{};'.format(BG_COLOR, FG_COLOR))
            alert.setWindowTitle('Alert')
            alert.setText(msg)
            alert.exec_()
    

class YAPT(QMainWindow):

    def __init__(self, parent=None):
        super(YAPT, self).__init__(parent)
        
        #window.setFixedSize(500, 500)
        self.setStyleSheet('background-color:{}'.format(BG_COLOR))
        self.layout = QVBoxLayout()

        self.setWindowTitle('Yet Another Python Terminal')

        mb = self.menuBar()
        mb.addMenu('File')
        
        self.yaptlayout = YAPTLayout()
        self.layout.addWidget(self.yaptlayout)

        self.setCentralWidget(self.yaptlayout)


def gui_init():

    app = QApplication([])
    app.setStyle('Fusion')

    window = YAPT()


    window.show()
    app.exec_()

if __name__ == '__main__':
    gui_init()
