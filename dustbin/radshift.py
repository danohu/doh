"""
Listening to morning news programs on the radio is a great way to drift into
sleep while keeping some slight grip on current events.
The BBC and Radio France let me download the radio news for later listening. I've not found any decent German radio station that does. Hence a roll-your-own solution

set this up as a cron job. It will download 80m of radio to a timestamped file
"""

STATIONS = {
        'b5_aktuell' : 'http://streams.br-online.de/b5aktuell_1.m3u',
        'b5_plus'    : 'http://streams.br-online.de/b5plus_1.m3u',
        'deutschlandfunk' : 'http://www.dradio.de/streaming/dlf_lq_mp3.m3u',
        'dwelle_en'  : 'http://www.listenlive.eu/dw.m3u',
        'dwelle_de'  : 'http://www.listenlive.eu/dw-de.m3u',
        'fm4'        : 'http://mp3stream1.apasf.apa.at:8000/listen.pls',
        }
#best place to find stations: http://listenlive.eu

DEFAULT_STATION = 'b5_aktuell'

from datetime import datetime
from optparse import OptionParser
from threading import Thread
import os, sys, time, urllib2

parser = OptionParser()
parser.add_option("-s", "--station", dest="station" , default = 'b5_aktuell', help="station name; refer to STATIONS in code")
parser.add_option("-m", "--minutes",  dest="minutes", type = "int", default = 80, help = "how many minutes to record"  )
parser.add_option("--basedir",  dest="basedir", default="/home/tmp/radio")

class PullMp3(Thread):
    """
    Given an url and an open filehandle (NOT filename), read from the url
    into the filehandle
    XXX: this is a quick hack to get _something_ from an m3u file. Seems
    to be sufficient for how radio stations use mp3s, but won't work with
    more complex items (e.g. streamripper radio stations)
    Ideally, either this would be expanded to handle m3u, or we would plug
    in something else that does the same, or maybe even call an external
    program such as streamripper
    
    Docs on the format: http://hanna.pyxidis.org/tech/m3u.html
    """
    chunksize = 50000

    def __init__(self, url, whichfile):
        self.url = url
        self.output_file = whichfile
        Thread.__init__(self)

    def run(self):
        transferred = 0
        source = urllib2.urlopen(self.url)
        while True:
            chunk = source.read(self.chunksize)
            self.output_file.write(chunk)
            self.output_file.flush()
            if not chunk:
                print('finished')
                return
            transferred += self.chunksize
            print('transferred %sb' % transferred)


def control_download(station, minutes, basedir):
    """Set the download starting, and kill it when the time comes"""
    assert(station in STATIONS)
    assert(not os.path.isfile(basedir))
    if not os.path.exists(basedir):
        os.makedirs(basedir)
    filename = '%s/%s_%s.mp3' % (basedir, station, datetime.now().strftime('%F_%H%M'))
    f = open(filename, 'w')
    downloadurl = urllib2.urlopen(STATIONS[station]).readlines()[0].strip()
    downloader = PullMp3(downloadurl, f)
    downloadthread = downloader.run()
    for i in range(minutes):
        time.sleep(60) #1 min
        print('downloaded for %s minutes; %s remaining' % (i, minutes - i))
        if not downloader.is_alive():
            print('Download failed around %s minutes' % i)
            sys.exit(1)
    sys.exit(0)
    
if __name__ == '__main__':
    (options, args) = parser.parse_args()
    control_download(options.station, options.minutes, options.basedir)
    



