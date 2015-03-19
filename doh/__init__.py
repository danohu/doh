import codecs
try:
    import cStringIO
except ImportError:
    # we're on python3, and don't need this faff anyway
    pass
import csv

class UnicodeCSVWriter:
    """
    A CSV writer which will write rows to CSV file "f",
    which is encoded in the given encoding.
    see http://www.python.org/doc/2.5.2/lib/csv-examples.html
    """

    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
        self.queue = cStringIO.StringIO()
        self.writer = csv.writer(self.queue, dialect=dialect, **kwds)
        self.stream = f

    def writerow(self, row):
        self.writer.writerow([codecs.encode(s, 'utf-8') for s in row])
        data = self.queue.getvalue()
        self.stream.write(unicode(data, 'utf-8'))
        self.queue.truncate(0)

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)


class UnicodeDictCSVWriter(UnicodeCSVWriter, csv.DictWriter):
    pass

def unicode_csv_writer(filename):
    """Create a csv object to write in unicode to a filename
    """
    f = codecs.open(filename, 'w', 'utf-8')
    return UnicodeCSVWriter(f)


# decorator to retry a func

def retry(func):
    def _inner(*args, **kwargs):
        max_retries = 3
        retries = 0
        while True:
            try:
                output = func(*args, **kwargs)
                return output
            except Exception:
                retries += 1
                if retries >= max_retries:
                    raise
    return _inner
