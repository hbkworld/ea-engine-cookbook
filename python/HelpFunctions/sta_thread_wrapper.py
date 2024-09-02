import threading
import pythoncom

def run_in_sta_thread(func, *args, **kwargs):
    def wrapper():
        pythoncom.CoInitialize()
        func(*args, **kwargs)
        pythoncom.CoUninitialize()
    thread = threading.Thread(target=wrapper)
    thread.start()
    return thread