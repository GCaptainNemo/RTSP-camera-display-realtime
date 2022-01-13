#!/usr/bin/env python3

from PyQt5 import QtGui, QtCore, QtWidgets
import cv2
import sys
import threading
import queue
import time

RGB_QUEUE = queue.Queue()
RGB_DEVICE = 'rtsp://admin:a12345678@192.168.1.64/1'

class MyWinPicture(QtWidgets.QWidget):
    def __init__(self, device_info):
        """
        Rewrite Qwidget to display pictures in label widget.
        """
        super(MyWinPicture, self).__init__()
        self.device_info = device_info
        self.cap = cv2.VideoCapture()
        self.set_ui()
        # self.init_slot()
        self.init_process()

    def init_process(self):
        self.processes = []
        self.processes.append(threading.Thread(target=self.image_put))
        self.processes.append(threading.Thread(target=self.image_get))
    
    def image_put(self):
        while True:
            RGB_QUEUE.put(self.cap.read()[1])
            RGB_QUEUE.get() if RGB_QUEUE.qsize() > 1 else time.sleep(0.01)

    def image_get(self):
        while True:
            self.image = RGB_QUEUE.get()
            self.image = cv2.cvtColor(self.image, cv2.COLOR_BGR2RGB)

            # cv2.imshow("123", frame)
            # cv2.waitKey(1)
            if self.image is None or self.image.size == 0:
                continue
            show_image = QtGui.QImage(self.image.data, self.image.shape[1],self.image.shape[0], QtGui.QImage.Format_RGB888)
            self.camera_label.setPixmap(QtGui.QPixmap.fromImage(show_image))
            time.sleep(0.1)  # if update label too frequently will crash

    def set_ui(self):
        self.camera_label = QtWidgets.QLabel("")
        self.camera_label.setScaledContents(True)
        vlayout = QtWidgets.QVBoxLayout()
        vlayout.addWidget(self.camera_label)
        self.setLayout(vlayout)

  
    def open_camera(self):

        flag = self.cap.open(self.device_info)
        self.cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'))
        if flag == False:
            msg = QtWidgets.QMessageBox.information(self, "[error]", 
            str(self.device_info) + " camera can not connect!", QtWidgets.QMessageBox.Ok)
        else:
            [process.start() for process in self.processes]


    def close_camera(self):
        self.cap.release()
        self.camera_label.clear()




if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    PAC = MyWinPicture(RGB_DEVICE)
    PAC.showMaximized()
    PAC.open_camera()
    sys.exit(app.exec_())

