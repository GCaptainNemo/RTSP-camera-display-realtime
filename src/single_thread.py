#!/usr/bin/env python3

from PyQt5 import QtGui, QtCore, QtWidgets
import cv2
import sys


RGB_DEVICE = 'rtsp://admin:a12345678@192.168.1.64/1'

class SingleThreadWinPicture(QtWidgets.QWidget):
    def __init__(self, device_info):
        """
        Rewrite Qwidget to display pictures in label widget.
        """
        super(SingleThreadWinPicture, self).__init__()
        self.device_info = device_info
        self.cap = cv2.VideoCapture()
        self.timer = QtCore.QTimer() #初始化定时器
        self.set_ui()
        self.init_slot()

    def set_ui(self):
        self.camera_label = QtWidgets.QLabel("")
        self.camera_label.setScaledContents(True)
        vlayout = QtWidgets.QVBoxLayout()
        vlayout.addWidget(self.camera_label)
        # #########################################
        # add button
        # ########################################
        hlayout = QtWidgets.QHBoxLayout()
        self.start_button = QtWidgets.QPushButton("open")
        self.start_button.clicked.connect(self.open_camera)
        self.close_button = QtWidgets.QPushButton("close")
        self.close_button.clicked.connect(self.close_camera) # cannot stop thread
        
        hlayout.addWidget(self.start_button)
        hlayout.addWidget(self.close_button)
        vlayout.addLayout(hlayout)
        # ####################################################
        self.setLayout(vlayout)

    def init_slot(self):
        self.timer.timeout.connect(self.show_camera)
    
    def show_camera(self):
        flag, self.image = self.cap.read()
       
        # show = 
        if flag:
            self.image = cv2.cvtColor(self.image, cv2.COLOR_BGR2RGB)
            show_image = QtGui.QImage(self.image.data, self.image.shape[1],self.image.shape[0], QtGui.QImage.Format_RGB888)
            self.camera_label.setPixmap(QtGui.QPixmap.fromImage(show_image))

    def open_camera(self):
        flag = self.cap.open(self.device_info)
        self.cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'))
        if flag == False:
            msg = QtWidgets.QMessageBox.information(self, "[error]", 
            str(self.device_info) + " camera can not connect!", QtWidgets.QMessageBox.Ok)
        else:
            self.timer.start(30)


    def close_camera(self):
        self.timer.stop()
        self.cap.release()
        self.camera_label.clear()




if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    PAC = SingleThreadWinPicture(RGB_DEVICE)
    PAC.showMaximized()
    PAC.open_camera()
    sys.exit(app.exec_())

