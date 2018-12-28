#!/usr/bin/env python3

#from PyQt5.QtCore import QThread
#from PyQt5.QtWidgets import QApplication, QLabel, QWidget, QPushButton, QVBoxself.initial_layout. QMessageBox
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

import serial
import time

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
        
        #window.setFixedSize(500, 500)
        self.setStyleSheet('background-color:#555555')
        self.initial_layout = QVBoxLayout()
        
        self.send_text = QLineEdit()
        self.initial_layout.addWidget(self.send_text)
        
        self.recv_text = QLineEdit()
        self.initial_layout.addWidget(self.recv_text)
        
        self.baud = QLineEdit('9600')
        self.initial_layout.addWidget(self.baud)

        conn = PicButton(QPixmap('connect_up.png'), QPixmap('connect_down'))
        #conn.resize(325, 121)
        conn.clicked.connect(self.connect)
        self.initial_layout.addWidget(conn)
      

        self.top = QPushButton('Send')
    #    top.setStyleSheet('background-color:#FF0000;color:#0000FF;')
        self.initial_layout.addWidget(self.top)
        self.top.clicked.connect(self.send)

        self.setLayout(self.initial_layout)
        
        self.uart = None
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
        self.setStyleSheet('background-color:#555555')
        self.initial_layout = QVBoxLayout()

        mb = self.menuBar()
        mb.addMenu('File')
        


        self.ww = YAPTLayout()
        self.initial_layout.addWidget(self.ww)

        self.setCentralWidget(self.ww)

        self.uart = None


def gui_init():

    app = QApplication([])
    app.setStyle('Fusion')

    window = YAPT()


    window.show()
    app.exec_()

if __name__ == '__main__':
    gui_init()
