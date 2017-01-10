#!/bin/python
# Class-based implementation of a gracefull killer, to catch SIGTERMs and such
# from http://stackoverflow.com/questions/18499497/how-to-process-sigterm-signal-gracefully/31464349#31464349

import signal
import time

class GracefulKiller:
    kill_now = False
    def __init__(self):
        signal.signal(signal.SIGINT, self.exit_gracefully)
        signal.signal(signal.SIGTERM, self.exit_gracefully)

    def exit_gracefully(self,signum, frame):
        self.kill_now = True
