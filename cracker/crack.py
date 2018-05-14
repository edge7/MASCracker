import random
import threading
from subprocess import PIPE
import errno
import subprocess

from cracker.thread_utility import PrintingThread


class PasswordUtility(object):
    def __init__(self):
        self.found = False
        self.password = None


def runHashCat(handShakeFile, ssid, partition):
    lotsOf = list(partition)
    number = random.randint(1, 101000000)
    # Start HashCat SubProcess
    hashcat = subprocess.Popen(
        ["hashcat", "-m", "2500", handShakeFile, "--potfile-disable", "--status", "--status-timer", "30", "-w", "3",
         "--session", lotsOf[0]],
        stdin=PIPE, stdout=PIPE, bufsize=1)

    # Create Thread and lock
    passwdUtility = PasswordUtility()
    threadLock = threading.Lock()
    outputThread = PrintingThread("CheckOutput", ssid, hashcat.stdout, threadLock, passwdUtility)
    outputThread.start()

    # Feed subprocess stdin (hashcat stdin mode)
    for passwd in lotsOf:
        try:
            passwd = passwd.encode('utf-8')
            hashcat.stdin.write(passwd + "\n")
        except IOError as e:
            if e.errno == errno.EPIPE or e.errno == errno.EINVAL:

                print("ERROR :" + str(e))
                break
            else:
                # Raise any other error.
                raise

    hashcat.stdin.close()
    print("Stdin .. done!")

    # Waiting PrintingThread to check if passwd has been found
    threadLock.acquire()
    found = passwdUtility.found

    # Winner!
    if found:
        print("Password has been found, updating accumulator")
        print(passwdUtility.password)
        return passwdUtility.password

    # Looser!
    return False
