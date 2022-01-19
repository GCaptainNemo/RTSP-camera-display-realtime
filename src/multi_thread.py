#!/usr/bin/env python3

from pickle import TRUE
from PyQt5 import QtGui, QtCore, QtWidgets
import cv2
import sys
import threading
import queue
import time
import ctypes
import inspect


RGB_DEVICE = 'rtsp://admin:a12345678@192.168.1.64/1'


class ThreadOperator:
    @staticmethod
    def _async_raise(tid, exctype):
        """raises the exception, performs cleanup if needed"""
        tid = ctypes.c_long(tid)
        if not inspect.isclass(exctype):
            exctype = type(exctype)
        res = ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, ctypes.py_object(exctype))
        if res == 0:
            raise ValueError("[stop thread error] invalid thread id")
        elif res != 1:
            # """if it returns a number greater than one, you're in trouble,
            # and you should call it again with exc=NULL to revert the effect"""
            ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, None)
            raise SystemError("[stop thread error] PyThreadState_SetAsyncExc failed")

    @staticmethod
    def stop_thread(thread):
        """
        kill thread
        """
        ThreadOperator._async_raise(thread.ident, SystemExit)


class MultiThreadWinPicture(QtWidgets.QWidget):
    def __init__(self, device_info):
        """
        Rewrite Qwidget to display pictures in label widget.
        """
        super(MultiThreadWinPicture, self).__init__()
        self.device_info = device_info
        self.cap = None
        self.set_ui()
        # self.init_process()
        self.img_queue = queue.Queue()
        self.img_get_thread = None
        self.img_put_thread = None

    # def init_process(self):
    #     self.processes = []
    #     self.processes.append(threading.Thread(target=self.image_put))
    #     self.processes.append(threading.Thread(target=self.image_get))
    #     [process.setDaemon(True) for process in self.processes]   # 主线程退出则退出

        # self.processes.append(putStoppableThread(self.cap))
        # self.processes.append(getStoppableThread(self.camera_label))
        # [process.start() for process in self.processes]

    
    def image_put(self):
        while True:
            self.img_queue.put(self.cap.read()[1])
            self.img_queue.get() if self.img_queue.qsize() > 1 else time.sleep(0.01)

    def image_get(self):
        while True:
            self.image = self.img_queue.get()
            try:
                if self.image.data.shape[0]:
                    self.image = cv2.cvtColor(self.image, cv2.COLOR_BGR2RGB)
            except Exception as e:
                continue
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
        self.cap = cv2.VideoCapture()
        flag = self.cap.open(self.device_info)
        self.cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'))
        if flag == False:
            msg = QtWidgets.QMessageBox.information(self, "[error]", 
            str(self.device_info) + " camera can not connect!", QtWidgets.QMessageBox.Ok)
        else:
            print("[info] thread num: ", len(threading.enumerate()))
            try:
                if self.img_put_thread:
                    ThreadOperator.stop_thread(self.img_put_thread)
                if self.img_get_thread:
                    ThreadOperator.stop_thread(self.img_get_thread)
            except Exception as e:
                print(e)
            self.img_put_thread = threading.Thread(target=self.image_put)
            self.img_get_thread = threading.Thread(target=self.image_get)
            # self.img_put_thread.setDaemon(True)
            # self.img_get_thread.setDaemon(True)
            self.img_put_thread.start()
            self.img_get_thread.start()


    def close_camera(self):
        try:
            if self.img_put_thread:
                ThreadOperator.stop_thread(self.img_put_thread)
            if self.img_get_thread:
                ThreadOperator.stop_thread(self.img_get_thread)
            self.camera_label.clear()
        except Exception as e:
            print(e)
        
        

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    PAC = MultiThreadWinPicture(RGB_DEVICE)
    PAC.showMaximized()
    # time.sleep(10)
    # PAC.close_camera()
    sys.exit(app.exec_())

