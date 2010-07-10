#!/usr/bin/python

import hamster.client
import sys
import datetime
from optparse import OptionParser
storage = hamster.client.Storage()

DONE_FILE = '/home/src/notes/todo/done.txt'

DONE = True

"""
Set hamster status from the command-line, and log activities into a text
file.
Will doubtles need some tweaking to be useful to anybody except me
"""


def get_current_fact():
    facts = storage.get_todays_facts()
    if not facts: return None
    return facts[-1]

def change_task(newtask):
    """
    Accepts a string; starts the timer running it.
    logs the now-completed task to a done file

    returns a tuple of the name and time spent on the current task
    """
    donefile = open(DONE_FILE, 'a')
    oldfact = get_current_fact()
    newfact = storage.add_fact(newtask)
    if oldfact:
        curtime = datetime.datetime.now().strftime('%F %H%M')
        minutes = oldfact['delta'].seconds / 60
        if options.subtask:
            marker = '>'
        elif options.done:
            marker = 'x'
        else:
            marker = '.' 
        outstr = "%s %s %s:%sm\n" % (marker, curtime, oldfact['name'].format(), minutes)
        donefile.write(outstr)
    else:
        outstr = 'no existing task'
    return outstr

def get_newtask():
    if len(sys.argv) > 1:
        return ' '.join(sys.argv[1:])
    else:
        return sys.stdin.read()


parser = OptionParser()
parser.add_option('-n', '--notdone', dest = 'done', action = 'store_false', default = False)
parser.add_option('-d', '--done', dest = 'done', action = 'store_true')
parser.add_option('-s', '--subtask', dest = 'subtask', action = 'store_true', default = False)


if __name__ == '__main__':
    options, args = parser.parse_args()
    newtask = ' '.join(args) or sys.stdin.read()
    print(change_task(newtask))

