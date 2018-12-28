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
        return QSize(325, 121)


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
        self.setStyleSheet('background-color:{};color:{};font-family:Courier'.format(BG_COLOR, FG_COLOR))
        self.layout = QGridLayout()

        # baud rate
        baud_lab = QLabel('Select baud rate')
        self.layout.addWidget(baud_lab, 0, 0)
        baud_btn = QPushButton('Baud rate')
        baud_btn.setFixedWidth(160)
        baud_btn.clicked.connect(self.select_baud)
        self.layout.addWidget(baud_btn, 1, 0)

        # data bits
        data_lab = QLabel('Select data bits')
        self.layout.addWidget(data_lab, 0, 1)
        data_cmb = QComboBox()
        data_cmb.setFixedWidth(160)
        data_cmb.addItem('5')
        data_cmb.addItem('6')
        data_cmb.addItem('7')
        data_cmb.addItem('8')
        data_cmb.addItem('9')
        self.layout.addWidget(data_cmb, 1, 1)

        # stop bits
        stop_lab = QLabel('Select stop bits')
        self.layout.addWidget(stop_lab, 0, 2)
        stop_cmb = QComboBox()
        stop_cmb.setFixedWidth(160)
        stop_cmb.addItem('1')
        stop_cmb.addItem('2')
        self.layout.addWidget(stop_cmb, 1, 2)

        # device port
        dev_lab = QLabel('Select COM port')
        self.layout.addWidget(dev_lab, 0, 3)
        dev_cmb = QComboBox()
        dev_cmb.setFixedWidth(160)
        dev_cmb.addItem('COM1')
        dev_cmb.addItem('COM3')
        self.layout.addWidget(dev_cmb, 1, 3)
        
        # data format
        format_lab = QLabel('Select data format')
        self.layout.addWidget(format_lab, 0, 4)
        format_cmb = QComboBox()
        format_cmb.setFixedWidth(160)
        format_cmb.addItem('Characters')
        format_cmb.addItem('Hex')
        format_cmb.addItem('Bin')
        self.layout.addWidget(format_cmb, 1, 4)


#        baud_dd = QComboBox()
#        baud_dd.addItem('9600')
#        baud_dd.addItem('115200')
#        self.layout.addWidget(baud_dd, 0, 0)
#        baud_dd.activated[str].connect(self.alert)

        self.send_text = QLineEdit()
        self.layout.addWidget(self.send_text, 2, 0)
        
        self.recv_text = QLineEdit()
        self.layout.addWidget(self.recv_text, 2, 1)
        
        self.baud = QLineEdit('9600')
        self.layout.addWidget(self.baud)

#        conn = PicButton(QPixmap('connect_up.png'), QPixmap('connect_down.png'))
        #conn.resize(325, 121)
#        conn.clicked.connect(self.connect)
#        self.layout.addWidget(conn)
      

        self.top = QPushButton('Send')
    #    top.setStyleSheet('background-color:#FF0000;color:#0000FF;')
        self.layout.addWidget(self.top)
        self.top.clicked.connect(self.send)


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
            self.baud_rate = baud_rate.text()


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
