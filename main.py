import sys
import subprocess
from utils.dbcontrol import Database

class Twicord:
    def __init__(self):
        self.first_time = False
        self.database = Database()

    async def first_time(self):
        print("Welcome to Twicord!\n")

    def start(self):
        print('Welcome to Twicord. Now starting...')
        proc2 = subprocess.Popen([sys.executable, 'ws.py'])
        proc1 = subprocess.Popen([sys.executable, 'twitch.py'])
        print(f'Twicord has started! Processes: Twitch [{proc1.pid}] and Webserver [{proc2.pid}] are up and running.')
        proc1.wait()
        proc2.wait()



if __name__ == '__main__':
    twicord = Twicord()
    twicord.start()

