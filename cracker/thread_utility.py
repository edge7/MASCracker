import threading


class PasswordUtility(object):
    def __init__(self):
        self.found = False
        self.password = None


class PrintingThread(threading.Thread):
    def __init__(self, name, ssid, output, lock, passwdUtility):
        threading.Thread.__init__(self)
        self.name = name
        self.ssid = ssid.lower()
        self.output = output
        self.lock = lock
        self.passwdUtility = passwdUtility

    def run(self):
        print("Starting " + self.name)
        done = False
        self.lock.acquire()
        while not done:

            line = self.output.readline()
            if line != "":
                try:
                    line = line.lower()
                    print(line)
                    if self.ssid in line:
                        done = True
                        self.passwdUtility.found = True
                        self.passwdUtility.password = line
                except:
                    pass
            else:
                done = True

        self.lock.release()
