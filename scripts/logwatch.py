#!/usr/bin/env python
"""
Logfile watch --> GUI notifications
because I'd rather have programmatic control than
be always rifling through settings

Public domain code by Dan O'Huiginn <daniel@ohuiginn.net>

"""

import pynotify
pynotify.init('logwatch')
from pyinotify import WatchManager, Notifier, ProcessEvent,\
                      EventsCodes

import re

def should_show(line, filepath):
    if 'vodo' in filepath:
        return True
    if re.search('(python|vodo|dan|oedipa|jamie|nisse)', line, re.I):
        return True
    if re.search('(motu|nginx|jquery)', filepath):
        return False
    return True

class PTmp(ProcessEvent):
    def process_IN_CREATE(self, event):
        self.notify_tail(event)

    def process_IN_MODIFY(self, event):
        self.notify_tail(event)

    def notify_tail(self, event):
        """
        Create notification with the last line of the file
        Inefficient for large files (reads the entire file)
        for efficiency, see http://www.manugarg.com/2007/04/tailing-in-python.html
        """
        f = open(event.pathname)
        try:
            lastline = f.readlines()[-1]
        except IndexError:
            lastline = 'ERROR: last line not available'
        if should_show(lastline, event.pathname):
            toast = pynotify.Notification('logwatch', lastline)
            toast.show()

def tailwatch(dir):
    FLAGS = EventsCodes.ALL_FLAGS
    mask = FLAGS['IN_CREATE'] |FLAGS['IN_DELETE'] | FLAGS['IN_MODIFY']
    wm = WatchManager()
    p = PTmp()
    notifier = Notifier(wm, p)
    wdd = wm.add_watch(dir, mask, rec=True)
    notifier.loop()


if __name__ == '__main__':
    tailwatch('/home/dan/.purple/logs')
