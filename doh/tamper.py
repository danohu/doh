"""tamper.py: interface to read output of the Firefox 'tamperdata' extension
and pass it to urllib2
Dan O'Huiginn <daniel@ohuiginn.net>, Sun Nov 18 16:20:18 CET 2007
"""
from BeautifulSoup import BeautifulStoneSoup
import urllib2,urllib

def requestdata(filename):
    text=open(filename,'r').read()
    soup=BeautifulStoneSoup(text)
    headers=soup.findAll('tdrequestheader')
    headerdict={}
    for x in headers:
        headername=urllib.unquote(x['name'])
        headervalue=urllib.unquote(x.string)
        headerdict[headername]=headervalue.strip('\n')
    postdata=soup.findAll('tdpostelement')
    postdict=dict([(x['name'],x.string) for x in postdata])
    poststring=urllib.urlencode(postdict)
    rawurl=soup.tdrequest['uri']
    url=urllib.unquote(rawurl)
    return (url,poststring,headerdict)

def request(filename, headers = True):
    (url,data,headers)=requestdata(filename)
    if headers:
        request=urllib2.Request(url,data,headers)
    else:
        request=urllib2.Request(url,data)
    #request=urllib2.Request(url=url,data=poststring)
    return request

def tofile(infile='/tmp/tamper.xml',outfile='/tmp/tampered.html', headers = True):
    urlrequest=request(infile, headers = headers)
    response=urllib2.urlopen(urlrequest)
    saveplace=open(outfile,'w')
    saveplace.write(response.read())
    return outfile
