import sys
import subprocess

class Twicord:
    def __init__(self):
        self.first_time = False


    def start(self):
        proc2 = subprocess.Popen([sys.executable, 'ws.py'])
        proc1 = subprocess.Popen([sys.executable, 'twitch.py'])
        proc1.wait()
        proc2.wait()



if __name__ == '__main__':
    twicord = Twicord()
    twicord.start()

