#!/usr/bin/env python3

from pickle import TRUE
from PyQt5 import QtGui, QtCore, QtWidgets
import cv2
import sys
import threading
import queue
import time

RGB_QUEUE = queue.Queue()
RGB_DEVICE = 'rtsp://admin:a12345678@192.168.1.64/1'


# class putStoppableThread(threading.Thread):
#     def __init__(self, cap):
#         super(putStoppableThread, self).__init__()
#         self.daemon = True
#         self.paused = True # start out paused
#         self.state = threading.Condition()
#         self.cap = cap

#     def run(self):
#         while True:
#             with self.state:
#                 if self.paused:
#                     self.state.wait()
#                 RGB_QUEUE.put(self.cap.read()[1])
#                 RGB_QUEUE.get() if RGB_QUEUE.qsize() > 1 else time.sleep(0.01)

#     def resume(self):
#         with self.state:
#             self.paused = False
#             self.state.notify() # unblock self is waiting

#     def pause(self):
#         with self.state:
#             self.paused = True


# class getStoppableThread(threading.Thread):
#     def __init__(self, show_widget):
#         super(getStoppableThread, self).__init__()
#         self.daemon = True
#         self.paused = True # start out paused
#         self.state = threading.Condition()
#         self.camera_label = show_widget

#     def run(self):
#         while True:
#             with self.state:
#                 if self.paused:
#                     self.state.wait()
#                 self.image = RGB_QUEUE.get()
#                 self.image = cv2.cvtColor(self.image, cv2.COLOR_BGR2RGB)

#                 # cv2.imshow("123", frame)
#                 # cv2.waitKey(1)
#                 if self.image is None or self.image.size == 0:
#                     continue
#                 show_image = QtGui.QImage(self.image.data, self.image.shape[1],self.image.shape[0], QtGui.QImage.Format_RGB888)
#                 self.camera_label.setPixmap(QtGui.QPixmap.fromImage(show_image))
#                 time.sleep(0.1)  # if update label too frequently will crash

#     def resume(self):
#         with self.state:
#             self.paused = False
#             self.state.notify() # unblock self is waiting

#     def pause(self):
#         with self.state:
#             self.paused = True


class MultiThreadWinPicture(QtWidgets.QWidget):
    def __init__(self, device_info):
        """
        Rewrite Qwidget to display pictures in label widget.
        """
        super(MultiThreadWinPicture, self).__init__()
        self.device_info = device_info
        self.cap = cv2.VideoCapture()
        self.set_ui()
        self.init_process()
        self.state = threading.Condition()

    def init_process(self):
        self.processes = []
        self.processes.append(threading.Thread(target=self.image_put))
        self.processes.append(threading.Thread(target=self.image_get))
        [process.setDaemon(True) for process in self.processes]   # 主线程退出则退出

        # self.processes.append(putStoppableThread(self.cap))
        # self.processes.append(getStoppableThread(self.camera_label))
        # [process.start() for process in self.processes]

    
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
            # if self.image is None or self.image.size == 0:
            #     continue
            show_image = QtGui.QImage(self.image.data, self.image.shape[1],self.image.shape[0], QtGui.QImage.Format_RGB888)
            self.camera_label.setPixmap(QtGui.QPixmap.fromImage(show_image))
            time.sleep(0.1)  # if update label too frequently will crash

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

  
    def open_camera(self):

        flag = self.cap.open(self.device_info)
        self.cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'))
        if flag == False:
            msg = QtWidgets.QMessageBox.information(self, "[error]", 
            str(self.device_info) + " camera can not connect!", QtWidgets.QMessageBox.Ok)
        else:
            [process.start() for process in self.processes]


    def close_camera(self):
        ...
        # [process.pause() for process in self.processes]
        
        # self.cap.release()
        # self.camera_label.clear()
        





if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    PAC = MultiThreadWinPicture(RGB_DEVICE)
    PAC.showMaximized()
    PAC.open_camera()
    # time.sleep(10)
    # PAC.close_camera()
    sys.exit(app.exec_())

