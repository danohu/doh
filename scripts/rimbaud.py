"""

"""
import re, sys


def markup(text):
    text = re.sub(r'([aeiou])', r'<span class="\1">\1</span>', text)
    return '<span class="rimbaud">%s</span>' % text

def surround(text):
    return '''
    <html>
    <head>
    <link rel="stylesheet" href="rimbaud.css">
    </head>
    <body>
    <span class="rimbaud">%s
    </span>
    <body>
    </html>''' % text

if __name__ == '__main__':
    if len(sys.argv) > 1:
        outfile = open(sys.argv[1], 'w')
    else:
        outfile = sys.stdout
    intext = sys.stdin.read()
    outfile.write(surround(markup(intext)))
