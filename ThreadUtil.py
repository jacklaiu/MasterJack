import threading

class AsyncExecution(threading.Thread):
    def __init__(self, method):
        threading.Thread.__init__(self)
        self.method = method
    def run(self):
        self.method()