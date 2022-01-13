#!/usr/bin/env python3

import threading
import time
import inspect
import ctypes
 
def _async_raise(tid, exctype):
    """raises the exception, performs cleanup if needed"""
    # 在线程中丢出异常，使线程退出
    tid = ctypes.c_long(tid)
    if not inspect.isclass(exctype):
        exctype = type(exctype)
    res = ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, ctypes.py_object(exctype))
    if res == 0:
        raise ValueError("invalid thread id")
    elif res != 1:
        # """if it returns a number greater than one, you're in trouble,
        # and you should call it again with exc=NULL to revert the effect"""
        ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, None)
        raise SystemError("PyThreadState_SetAsyncExc failed")
 
def stop_thread(thread):
    _async_raise(thread.ident, SystemExit)
 
def print_time():
    while 2:
         print(111111111111)
         print(222222222222)
         print(333333333333)
         print(444444444444)
         print(555555555555)
         print(666666666666)
        #  time.sleep(3)

def start_thread():
    t = threading.Thread(target=print_time)
    t.setDaemon(True)
    t.start()
    return t

def kill_thread(t):
    stop_thread(t)

if __name__ == "__main__":
    index = 0
    while True:
        print("thread_num = ", len(threading.enumerate()))  # only 2 thread
    
        index += 1
        print(" ------------", index)
        thread = start_thread()
        stop_thread(thread)
        print("is_alive = ", thread.is_alive())
        if index > 1000:
            break
    print("stoped")
    # while 1:
    #     pass
