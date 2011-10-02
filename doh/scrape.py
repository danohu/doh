"""
Collection of useful functions for property scrapers
Daniel O'Huiginn <daniel@ohuginn.net>
Sun Dec 16 16:32:27 CET 2007
"""


from BeautifulSoup import BeautifulSoup, BeautifulStoneSoup, Comment, ProcessingInstruction
#from ClientForm import ItemNotFoundError
#from operator import isCallable
from itertools import takewhile
from threading import Thread
#from xml.sax.saxutils import unescape
import logging
import os
import random
import re
import sys
import time
import datetime
import traceback
import urllib
import urllib2
import urlparse
import warnings
import types
import copy
import mechanize

debug = False

__all__ = ['amtextFromDict', 'applyToPages', 'beforeSoup',
          'cleanWhitespace', 'compareFunctions', 'curry', 'debug',
          'filePrintOrderedData', 'findAddressiest', 'findBetween',
          'findBetweenText', 'flattenList', 'flipre', 'getPages', 'getPrice',
          'getTagPosition', 'guessIsAddress', 'guessType', 'hastext',
          'makeMonthString', 'mocksoup', 'nosoup', 'numFromWord',
          'parseDate', 'printOrderedData', 'printOrderedDataOld', 'roadre',
          'runTest', 'savePage', 'seqSoup', 'statelist', 'states',
          'stateset', 'stripHTMLEntities', 'stripProperly',
          'tableToArray', 'tagtext', 'toStr', 'tidyText', 'tidyList',
          'uniq', 'urlSoup', 'urlStoneSoup', 'zipFromTown',
          'tagtextMulti', 'capWords', 'getPrettyText', 'capSentences',
          'latin1_to_ascii', 'tidyRates', 'rateDictFromIntervals',
          'rateDetailsFromIntervals', 'convert24Hour', 'unique',
          'dateRange','getStringentPrice','parseMinMaxRates']

MONTH_DICT = {'January': 1, 'February': 2, 'March': 3, 'April': 4, 'May': 5,
                 'June': 6, 'July': 7, 'August': 8, 'September': 9,
                 'October': 10, 'November': 11, 'December': 12}


RATE_SKEL =  {
    'label'        : '',
    'start_date'   : '',
    'end_date'     : '',
    'day_min_rate' : '',
    'day_max_rate' : '',
    'week_min_rate' : '',
    'week_max_rate' : '',
    'month_min_rate': '',
    'month_max_rate': '',
    'minimum_length': '',
    'turn_day'     : ''
    }
def rateskel():
    return copy.copy(RATE_SKEL)

#a lot of the scraped sites abbreviate the months on their availability pages
ABRV_MONTH_DICT = {'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'May': 5,
                 'Jun': 6, 'Jul': 7, 'Aug': 8, 'Sep': 9,
                 'Oct': 10, 'Nov': 11, 'Dec': 12}

#this makes it possible to get bedroom, bathroom, sleeps, etc. counts for sites
#that aren't consistent with using natural numbers, can use in conjunction with
#regular expression and numFromWord function (this is only used as last resort)
NUM_LIST = ["one", "two", "three", "four", "five", "six",
            "seven", "eight", "nine",  "ten", "eleven",
            "twelve", "thirteen", "fourteen", "fifteen",
            "sixteen", "seventeen", "eighteen", "nineteen", "twenty"]

#function that takes in a string like "December 2009" and
#a list of days and returns all booked dates
def formateDatesForMonth(monthyear, days):
    booked_dates = []
    my = monthyear.strip().split(' ')
    month = MONTH_DICT[my[0]]
    for d in days:
        day = "%s-%s-%s" %(my[1], month, d)
        booked_dates.append(day)
    return booked_dates

#quick way to format a date
def formDate(datestring, split='/'):
    d = datestring.split(split)
    return "%s-%s-%s" %(d[2], d[0], d[1])

def findStringInList(text, listof):
    listtext = " ".join(listof)
    regex = re.compile(text, re.I)
    match = re.search(regex, listtext, re.I)
    if match:
        return True
    else:
        return False

def cleanWhitespace(text):
   whitespacemap = {'&nbsp;'   : ' ',
                    '&quot;'   : '"',
                    '&amp;'    : '&',
                    '&bull;'   : '*',
                    "\\'"      : "'",
                   }
   for k,v in whitespacemap.iteritems():
       text = text.replace(k, v)
   return re.sub(r'\s+', ' ', text.strip())

def monthNumber(month):
    return MONTH_DICT.get(month)

def tidyText(text):
   newtext = cleanWhitespace(text)
   newertext = stripHTMLEntities(newtext)
   newesttext = newertext.strip()
   return newesttext

def tidyList(somelist):
   return [tidyText(x) for x in somelist]

def amtextFromDict(amdict):
   amitems = []
   for (key, value) in amdict.iteritems():
       cleankey = tidyText(key)
       cleanvalue = tidyText(value)
       if re.match('(no|none)', cleanvalue, re.IGNORECASE):
           continue
       elif re.match('(yes)', cleanvalue, re.IGNORECASE):
           amitems.append(cleankey)
       else:
           amitems.append('%s (%s)' % (cleankey, cleanvalue))
   amtext = ', '.join(amitems)
   return tidyText(amtext)

def curry(*args, **create_time_kwds):
   """
   very similar to python2.5's 'partial'
   """
   func = args[0]
   create_time_args = args[1:]
   def curried_function(*call_time_args, **call_time_kwds):
       args = create_time_args + call_time_args
       kwds = create_time_kwds.copy()
       kwds.update(call_time_kwds)
       return func(*args, **kwds)
   return curried_function


nosoup = BeautifulSoup("")

def tagtext(element, sep =' ', strip=False, clean=True, nocr=False):
    """
    Remove the html tags from a BeautifulSoup element,
    and return the text
    strip: whether to pass the text through 'strip' before returning it
    False: do not strip (default)
    True:  strip with standard strip() function
    [string]: pass the string to the strip() function, e.g. to remove particular characters
    sep: string to use when re-joining blocks of text
    """
    def dostrip(item):
        if not strip:
            return item
        elif strip is True:
            return item.strip()
        elif isinstance(strip, unicode) or isinstance(strip, str):
            return item.strip(strip)
        else:
            raise ValueError(
                "tagtext recieved an invalid argument for strip \
                - should be True, or unicode/string")
    items = []
    if not element:
        return ""
    if isinstance(element, unicode) or isinstance(element, str):
        if clean:
            return cleanWhitespace(dostrip(element))
        else:
            return dostrip(element)
    for x in element.recursiveChildGenerator():
        if not isinstance(x, unicode):
            continue
        items.append(dostrip(x))
    if nocr:
        items = filter(lambda i: i != '\n', items)
    text = sep.join(items)
    if clean:
        return cleanWhitespace(text)
    else:
        return text

def toStr(item, formatstring = '%.2f'):
   """Cast to string, with decent rounding/formatting
   includes re-formatting strings that contain numbers"""
   if item == None or item == "":
       return ""
   if isinstance(item, str) or isinstance(item, unicode):
       try:
           item = float(item)
       except ValueError:
           return item
   if isinstance(item, int) or isinstance(item, float):
       return formatstring % item
   try:
       return item.__str__()
   except AttributeError:
       return ""
def tableToArray(table, textOnly = True, *args, **kwargs):
   """
   Turns an html table into a 2-dimensional array, with each
   <td> or <th> represented by one element.
   Beware of using this on html tables with elements spanning multiple
   rows or multiple columns
   """
   lists = []
   try:
       for row in table.findAll('tr'):
           lists.append([x for x in row.findAll(['td', 'th'])])
       if not textOnly:
           return lists
   except AttributeError: #wasn't a real beautifulsoup object,probably None
       return lists
   textlists = []
   for row in lists:
       textlists.append([tagtext(x) for x in row])
   return textlists

def hastext(name, regex, ignore_case=False):
   """
   Utility to overcome BS's issues with searching for both text and
   name
   """
   if ignore_case == True:
       return lambda x: x.name == name and re.search(regex, tagtext(x), re.I)
   else:
       return lambda x: x.name == name and re.search(regex, tagtext(x))

def makeMonthString(datestring, formatstring = "%d %B %Y"):
   """
   reformat dates so they fit into the database
   """
   dateobj = time.strptime(datestring, formatstring)
   return "%04d-%02d-%02d" % (dateobj[:3])

def mocksoup(maybesoup):
   """A hack to circumvent BeautifulSoup's
   nasty habit of returning None when it can't find
   what it's looking for. Instead, return an empty string
   """
   if maybesoup:
       return maybesoup
   else:
       print("failed to find something in soup")
       #XXX could easily do proper warning here
       #by inspecting the stack
       return BeautifulSoup('')

def numFromWord(word, returnString=True, *args, **kwargs):
   """
   translate 'twelve' into '12', etc. works up to 20
   for more heavy-duty requirements,
       see http://sourceforge.net/projects/pynum2word/
    (set returnString = False to return 12 rather than '12')
   """
   word = word.lower()
   numberwords = ["one", "two", "three", "four", "five", "six",
            "seven", "eight", "nine",  "ten", "eleven",
            "twelve", "thirteen", "fourteen", "fifteen",
            "sixteen", "seventeen", "eighteen", "nineteen", "twenty"]
   numbers = range(1,21)
   numdict = dict(zip(numberwords,numbers))
   if word not in numdict:
       print "could not interpret %s as a number" % word
       return word
   answer = numdict[word]
   if returnString:
       return str(answer)
   else:
       return answer

def flattenList(item, *args, **kwargs):
   """Recursively run through a list, returning the strings.
   Don't split the strings into their individual characters
   This is a horribly, horribly inefficient method, but it'll
   suffice for our purposes
   """
   try:
       x = iter(item)
   except TypeError: #item is not iterable
       return [item]
   if isinstance(item, unicode) or isinstance(item, str):
       return [item]
   else:
       flattened = []
       for subunit in item:
           flattened.extend(flattenList(subunit))
       return flattened

def getPrice(pricestring):
   """try to extract price from a string"""
   try:
       dollarprice = re.search('\$?( +)?[\d\,]+\.\d\d', pricestring)
       #$78, 900.89 for instance
       if dollarprice:
           price = re.sub('\D', '', (dollarprice.group()[:-3]))
           return float(price)
       elif re.match('^\d+$', pricestring):
           return float(pricestring)
       else:
           dollarprice = re.search('\$?( +)?[\d\,]+', pricestring)
           #$78, 900 for instance
           if dollarprice:
               price = re.sub('\D', '', (dollarprice.group()))
               return float(price)
           return False
   except:
       return False

def getStringentPrice(pricestring, enforce_dollar_sign=True, enforce_cents=False):
    regexp_str = r'([\d\,]+)'
    if enforce_dollar_sign == True:
        regexp_str = r'\$ *%s' % regexp_str
    if enforce_cents == True:
        regexp_str = r'%s\.\d{2}' % regexp_str
    else:
        regexp_str = r'%s\.?\d{0,2}' % regexp_str
    price_re = re.compile(regexp_str)
    match = price_re.search(pricestring)
    if match:
        price = match.group(1).replace(',','')
        try:
            return str(float(price))
        except:
            return False
    else:
        return False

def guessIsAddress(text):
   """Returns a percentage figure (0-100), covering the likelihood
   that the text represents an address"""
   estimate = 0
   lenCorrection = 15.0-(float(abs(27-len(text)))/4)
   statematch = re.compile('(\d{5}\W(%s)|(%s)\W\d{5})' % (statelist, statelist))
   #matches strings like 90210 CA or CA 90210
   if re.search('\d+\W?(st|rd|nd)', text, re.IGNORECASE):
       streetNum = 20 #things like 32nd (street)
   else:
       streetNum = 0
   if re.search('^\W*\d{1,4}', text):
       startNumbers = 10
   else:
       startNumbers = 0
   if re.search(roadre, text.lower()):
       roadName = 25 #common road names (road, avenue, etc)
   else:
       roadName = 0
   if re.search(statematch, text): #matches state and zip together
       stateCorrection = 50
   elif re.search(states, text): #matches state without zip
       stateCorrection = 15
   else:
       stateCorrection = 0
   if re.search('\d{5}', text): #bonus for a zip, with or without a state
       zipCorrection = 10
   else:
       zipCorrection = 0
   factors = [lenCorrection,
            stateCorrection,
            zipCorrection,
            streetNum,
            roadName,
            startNumbers]
   #if debug: print("**Start here**")
   for factor in factors:
       #if debug: print "%s:%s"%("Unknown", float(factor))
       estimate += float(factor)
   if estimate > 100:
       estimate = 100
   if estimate < 0:
       estimate = 0
   return estimate


def stripProperly(text):
   """Get rid of useless chars"""
   return re.sub('&nbsp;', '', text)

def stripHTMLEntities(inText):
   entityRegex = re.compile("(&nbsp;|&iexcl;|&cent;|&pound;|&euro;|&yen;|&brvbar;|&sect;|&uml;|&copy;|&ordf;|&laquo;|&not;|&shy;|&reg;|&macr;|&deg;|&plusmn;|&sup2;|&sup3;|&acute;|&micro;|&para;|&middot;|&cedil;|&sup1;|&ordm;|&raquo;|&frac14;|&frac12;|&frac34;|&iquest;|&Agrave;|&Aacute;|&Acirc;|&Atilde;|&Auml;|&Aring;|&AElig;|&Ccedil;|&Egrave;|&Eacute;|&Ecirc;|&Euml;|&Igrave;|&Iacute;|&Icirc;|&Iuml;|&ETH;|&Ntilde;|&Ograve;|&Oacute;|&Ocirc;|&Otilde;|&Ouml;|&times;|&Oslash;|&Ugrave;|&Uacute;|&Ucirc;|&Uuml;|&Yacute;|&THORN;|&szlig;|&agrave;|&aacute;|&acirc;|&atilde;|&auml;|&aring;|&aelig;|&ccedil;|&egrave;|&eacute;|&ecirc;|&euml;|&igrave;|&iacute;|&icirc;|&iuml;|&eth;|&ntilde;|&ograve;|&oacute;|&ocirc;|&otilde;|&ouml;|&divide;|&oslash;|&ugrave;|&uacute;|&ucirc;|&uuml;|&yacute;|&thorn;|&yuml;|&bull;)")
   outText = entityRegex.sub('', inText)
   return outText

def guessType(propsoup, threshold = 2):
   """Try to guess the type of the property, by counting occurances of common
   house-types in the text
   List of types manually created by going through
   http://en.wikipedia.org/wiki/List_of_house_types and filtering out the crud
   Supply a threshold:a minimum number of times that a term should occur.
   If no term occurs often enough, an empty string will be returned
   NOTE: this was broken for some time. Keep an eye on it.
   """
   proptypes = ('cabin', 'chalet', 'condo', 'bungalow', 'cottage', 'ranch',
              'mansion', 'mews', 'apartment', 'flat', 'penthouse', 'loft',
              'studio', 'townhouse')
   pagetext = propsoup.renderContents().lower()
   besttype = ""
   maxcount = 0
   for element in proptypes:
       count = len(re.findall(element, pagetext))
       if count > maxcount:
           maxcount = count
           besttype = element
       elif count == maxcount and count>0:
           if len(element)>len(besttype):
               besttype = element
   if maxcount >= threshold:
       return besttype
   else:
       return ""
def findBetween(start, end):
   """Find the section of HTML between two BeautifulSoup tags
   NB: this doesn't work!
   This is used by the following classes - they all need checking
    miscsites/lfvacations and escapia/e2 have their own versions
    miscsites/rentalsathtebeach
    visualdata/seaside,outerbanks,palmsprings,joelamb
   """
   forwards = start.findAllNext()
   backwards = end.findAllPrevious()
   #forwards = start.findAllNext(lambda x: x == x._lastRecursiveChild())
   #backwards = end.findAllPrevious(lambda x: x == x._lastRecursiveChild())
   intersection = []
   for element in forwards:
       if element in backwards:
           # print "adding element..."
           #print element
           intersection.append(element)
   return intersection


def findBetweenText(startPoint, endPoint, sep = ''):
   """This one might work!"""
   nextitems  = startPoint.nextGenerator()
   betweenList = list(takewhile(lambda x: x is not endPoint, nextitems))
   betweenText = [x for x in betweenList if isinstance(x, unicode)]
   return sep.join(betweenText)

def findBetweenTextList(startPoint, endPoint):
   """This one might work!"""
   nextitems  = startPoint.nextGenerator()
   betweenList = list(takewhile(lambda x: x is not endPoint, nextitems))
   betweenText = [x for x in betweenList if isinstance(x, unicode)]
   return betweenText

def findAddressiest(resultset, threshold = 20):
   """Given a BeautifulSoup resultset, return the item which looks
   most like an address. If there is nothing that looks much like
   an address (based on threshold, which can be between 0
   (indiscriminate) and 100 (very, very selective), return an empty
   string
   This takes a 'best guess' approach to scraping the address.
   If you have any way of finding the address more precisely, then be
   sure to do so!"""
   #filter out short elements, and elements without text
   candidates = [x for x in resultset if len(tagtext(x))>5]
   if len(candidates)<1:
       return "", ""
   def sortlambda(x, y):
       return int(guessIsAddress(tagtext(x)) - guessIsAddress(tagtext(y)))
   candidates.sort(cmp = sortlambda)
   topcandidate = tagtext(candidates[-1])
   if guessIsAddress(topcandidate)>threshold:
       return topcandidate
   return ""

def uniq(longlist):
   """
   remove duplicates from a list
   yoinked from the python cookbook, props to Raymond Hettinger
   """
   shortlist = {}
   return [shortlist.setdefault(e,e) for e in longlist if e not in shortlist]


def zipFromTown(town, state):
   """Use the USPS zipcode lookup to find the zip for a town"""
   mech = mechanize.Browser()
   mech.open('http://zip4.usps.com/zip4/citytown.jsp')
   mech.select_form('form1')
   mech['city'] = town.strip('\t\r\n')
   mech['state'] = state
   soup = BeautifulSoup(mech.submit().read())
   zipelement = soup.form.findNext('td', 'main', padding = "5px 10px;")
   zipcode = zipelement.string.strip('\t\r\n')
   if not re.match('^\d{5}$', zipcode):
       warnings.warn('Failed to find zipcode from USPS\
       for town %s in state %s' % (town, state))
       return ""
   return zipcode

roadre = re.compile('''\\b(frgs|byp|via|mt|lndg|vlg|ml|ctrs|ctr|hbr|trl|psge|crst|mdws|fwy|gdn|blfs|trak|hbr|fry|dv|stra|gdns|vlg|mdw|trl|sts|st|cres|prt|blf|grvs|lgts|spgs|ldg|trak|pkwy|dr|dv|stra|ave|riv|isle|est|byu|byu|upas|expy|spg|flt|clb|gdn|trl|jcts|tunl|rdg|vly|fry|pkwy|radl|stra|opas|strm|mtn|lck|orch|stra|lcks|bnd|jcts|mtn|ct|pne|ldg|cswy|bch|shrs|blf|bgs|tunl|grv|spgs|oval|vlg|via|nck|orch|lgt|st|shr|grn|is|tpke|msn|crse|trfy|ter|hwy|ave|gln|blvd|inlt|ln|brk|pnes|byp|mtn|aly|frst|jct|vws|dm|ct|cors|fwy|radl|xing|ext|clfs|mnrs|prts|gtwy|cres|sq|hbr|loop|hl|sqs|hwy|brks|br|ave|mtwy|rte|pl|smt|shr|trak|shl|fwy|blvd|ext|holw|vis|plns|sta|cir|mtns|vlgs|hvn|tpke|expy|sta|expy|pr|st|spur|tpke|radl|dr|shls|park|plz|mdws|aly|pr|spg|hvn|path|byp|mls|park|byp|tunl|cirs|holw|mnr|ctr|trak|cir|fls|lndg|plns|via|grv|cp|tpke|dr|fwy|pts|expy|pkwy|cor|xing|uns|ldg|cir|brg|expy|hbrs|park|knls|grns|tunl|flds|cmn|riv|vw|cres|cres|cswy|pkwy|jct|sta|gdn|mtn|xing|rpd|ky|way|trwy|ests|lf|pt|holw|cyn|vlg|spgs|jct|msn|un|brg|ctr|ft|gdn|ln|gtwy|aly|stra|hwy|vl|pln|mt|ctr|walk|sqs|hwy|cir|sq|jct|mtn|kys|pkwy|drs|ctr|rnch|wl|smt|cyn|hbr|rst|shrs|vis|iss|hls|cres|lk|vly|xrd|stra|stra|knl|ctr|cpe|hwy|tpke|blvd|vlys|vis|crk|spg|holw|trce|btm|strm|ave|gtwy|cir|frks|bg|trl|pr|lks|wls|frds|ext|is|plz|ter|exts|pkwy|iss|rd|rds|glns|msn|rdg|arc|cres|jct|vly|frk|mtns|btm|knl|frg|frd|cts|rnch|ft|trce|cyn|flts|anx|gtwy|rpds|vlg|cvs|riv|ave|pike|vis|frst|fld|br|frg|dl|anx|sq|cv|sq|skwy|rdgs|tunl|clf|ln|dv|anx|curv|rnch|smt|gdns|forges|bypas|viaduct|mnt|lndng|vill|mill|centers|cnter|hrbor|tr|passage|crest|meadows|freewy|garden|bluffs|trk|harbor|frry|div|straven|grdns|villg|meadow|trails|streets|street|crescent|port|bluf|groves|lights|spngs|lodg|tracks|pkway|drv|divide|strav|avenu|rivr|isles|estate|bayoo|bayou|underpass|expressway|sprng|flat|club|grden|trail|jctns|tunnel|rdge|vally|ferry|parkway|radiel|strvnue|overpass|stream|mntn|lock|orchrd|strvn|locks|bend|junctions|mountin|court|pine|ldge|causway|beach|shores|bluff|burgs|tunls|grov|sprngs|ovl|villag|vdct|neck|orchard|light|strt|shore|green|islnd|turnpike|mission|course|trafficway|terrace|hway|avenue|glen|boul|inlet|la|brook|pines|bypass|mtin|ally|forest|junction|views|dam|crt|corners|frway|radial|crossing|extn|cliffs|manors|ports|gatewy|crecent|square|harb|loops|hill|squares|highway|brooks|brnch|aven|motorway|route|place|sumit|shoar|trks|shoal|frwy|heights|boulevard|extnsn|hollows|vsta|plains|station|circl|mntns|villages|haven|turnpk|expr|stn|expw|prairie|str|spurs|trpk|rad|driv|shoals|prk|plza|medows|allee|prr|spng|havn|paths|bypa|mills|parks|byps|tunnels|circles|hllw|manor|centre|track|hgts|crcle|falls|landing|plaines|viadct|grove|camp|tpk|drive|freeway|points|exp|pky|corner|crssing|unions|lodge|circle|bridge|express|harbors|pk|knolls|greens|tunel|fields|common|river|view|crsent|crscnt|causeway|parkwy|juncton|statn|gardn|mntain|crssng|rapid|key|wy|throughway|estates|loaf|point|hollow|canyon|village|springs|jction|mssn|union|brdge|cent|frt|grdn|lanes|gtway|alley|stravenue|hiway|ville|plain|mount|centr|walks|sqrs|hiwy|crcl|sqre|jctn|mountain|keys|parkways|drives|center|ranch|well|sumitt|canyn|harbr|rest|shoars|vist|islnds|hills|cresent|lake|vlly|crossroad|strave|stravn|knol|cntr|cape|height|highwy|trnpk|boulv|valleys|vst|creek|spring|holws|trace|bottom|streme|avnue|gateway|circ|forks|burg|trls|prarie|lakes|wells|fords|extension|island|plaza|terr|extensions|pkwys|islands|road|roads|glens|missn|ridge|arcade|crsnt|junctn|valley|fork|mountains|bottm|knoll|forg|ht|ford|courts|ranches|fort|traces|cnyn|flats|anex|gatway|rapids|villiage|coves|rvr|av|pikes|vista|forests|field|branch|forge|dale|annex|sqr|cove|squ|skyway|ridges|tunnl|cliff|lane|dvd|annx|curve|rnchs|summit|gardens)\\b''')
''' '''
statelist = 'AK|AL|AR|AZ|CA|CO|CT|DC|DE|FL|GA|HI|IA|ID|IN|IL|KS|KY|LA|MA|MD|ME|MI|MN|MO|MS|MT|NC|ND|NE|NH|NJ|NM|NV|NY|OH|OK|OR|PA|RI|SC|SD|TN|TX|UT|VA|VT|WA|WI|WV|WY'
states = re.compile(statelist)
stateset = set(['WA', 'DE', 'DC', 'WI', 'WV', 'HI', 'FL', 'WY', 'NH', 'NJ',
             'NM', 'TX', 'LA', 'NC', 'ND', 'NE', 'TN', 'NY', 'PA', 'CA',
             'NV', 'VA', 'CO', 'AK', 'AL', 'AR', 'VT', 'IL', 'GA', 'IN',
             'IA', 'OK', 'AZ', 'ID', 'CT', 'ME', 'MD', 'MA', 'OH', 'UT',
             'MO', 'MN', 'MI', 'RI', 'KS', 'MT', 'MS', 'SC', 'KY', 'OR',
             'SD'])

def lam(code):
   """It's probably bad form; but typing 'lambda x:' all the time
   is getting on my nerves.
   This is lambda, without a lot of the restrictions
   code is a string, which is fed to eval()
   arguments are passed as (x, y, z)
   e.g.
    >>>filter(lam('x>6'), range(1, 10))
   [7, 8, 9]
   This does have access to variables in the scope in which it is run
   """
   def runCode(*args, **kwargs):
       for (varname, var) in zip('xyzabcdefghijklm', args):
           locals()[varname] = var
       for (varname, var) in kwargs:
           locals()[varname] = var
       return eval(code)
   return runCode

def compareFunctions(one, two):
   """Little utility to check which functions are in one class, which are
   in both"""
   onefuncs = one.__dict__
   twofuncs = two.__dict__
   inboth = [x for x in onefuncs if x in twofuncs]
   inone = [x for x in onefuncs if x not in twofuncs]
   intwo = [x for x in twofuncs if x not in onefuncs]
   return({'one'  : inone,
           'two'  : intwo,
           'both' : inboth})


def savePage(pagetext, name = '/tmp/out.html'):
   """Just for debugging"""
   if os.path.isfile(name):
       os.remove(name)
   fh = open(name, 'w')
   fh.write(pagetext)
   fh.close()
   return name

def urlSoup(url, *args, **kwargs):
   """quick way to slurp the contents of an url into beautiful soup
      - mainly for testing"""
   return BeautifulSoup(urllib2.urlopen(url).read(), *args, **kwargs)

def urlStoneSoup(url):
   """quick way to slurp the contents of an url into beautiful stone soup
      - mainly for testing"""
   return BeautifulStoneSoup(urllib2.urlopen(url).read())


def latin1_to_ascii (unicrap):
   return unicrap.encode('ascii', 'xmlcharrefreplace')

   """This takes a UNICODE string and replaces Latin-1 characters with
       something equivalent in 7-bit ASCII. It returns a plain ASCII string.
       This function makes a best effort to convert Latin-1 characters into
       ASCII equivalents. It does not just strip out the Latin-1 characters.
       All characters in the standard 7-bit ASCII range are preserved.
       In the 8th bit range all the Latin-1 accented letters are converted
       to unaccented equivalents. Most symbol characters are converted to
       something meaningful. Anything not converted is deleted.
   """
   xlate={0xc0:'A', 0xc1:'A', 0xc2:'A', 0xc3:'A', 0xc4:'A', 0xc5:'A',
       0xc6:'Ae', 0xc7:'C',
       0xc8:'E', 0xc9:'E', 0xca:'E', 0xcb:'E',
       0xcc:'I', 0xcd:'I', 0xce:'I', 0xcf:'I',
       0xd0:'Th', 0xd1:'N',
       0xd2:'O', 0xd3:'O', 0xd4:'O', 0xd5:'O', 0xd6:'O', 0xd8:'O',
       0xd9:'U', 0xda:'U', 0xdb:'U', 0xdc:'U',
       0xdd:'Y', 0xde:'th', 0xdf:'ss',
       0xe0:'a', 0xe1:'a', 0xe2:'a', 0xe3:'a', 0xe4:'a', 0xe5:'a',
       0xe6:'ae', 0xe7:'c',
       0xe8:'e', 0xe9:'e', 0xea:'e', 0xeb:'e',
       0xec:'i', 0xed:'i', 0xee:'i', 0xef:'i',
       0xf0:'th', 0xf1:'n',
       0xf2:'o', 0xf3:'o', 0xf4:'o', 0xf5:'o', 0xf6:'o', 0xf8:'o',
       0xf9:'u', 0xfa:'u', 0xfb:'u', 0xfc:'u',
       0xfd:'y', 0xfe:'th', 0xff:'y',
       0xa1:'!', 0xa2:'{cent}', 0xa3:'{pound}', 0xa4:'{currency}',
       0xa5:'{yen}', 0xa6:'|', 0xa7:'{section}', 0xa8:'{umlaut}',
       0xa9:'{C}', 0xaa:'{^a}', 0xab:'<<', 0xac:'{not}',
       0xad:'-', 0xae:'{R}', 0xaf:'_', 0xb0:'{degrees}',
       0xb1:'{+/-}', 0xb2:'{^2}', 0xb3:'{^3}', 0xb4:"'",
       0xb5:'{micro}', 0xb6:'{paragraph}', 0xb7:'*', 0xb8:'{cedilla}',
       0xb9:'{^1}', 0xba:'{^o}', 0xbb:'>>',
       0xbc:'{1/4}', 0xbd:'{1/2}', 0xbe:'{3/4}', 0xbf:'?',
       0xd7:'*', 0xf7:'/'
       }

   r = ''
   for i in unicrap:
       if xlate.has_key(ord(i)):
           r += xlate[ord(i)]
       elif ord(i) >= 0x80:
           pass
       else:
           r += str(i)
   return r


def convert24Hour(timestr):
   split = timestr.split(':')
   if len(split) < 2:
       return ''
   if int(split[0]) > 12:
       hour = int(split[0]) - 12
       ampm = 'pm'
   elif int(split[0]) == 0:
       hour = 12
       ampm = 'am'
   else:
       hour = int(split[0])
       ampm = 'am'

   return str(hour)+':'+str(split[1]) + ' ' + ampm


def tagtextMulti(elements,bigsep='\n',*args,**kwargs):
   items=[]
   for element in elements:
       thisitem=tagtext(element,*args,**kwargs).strip()
       if thisitem:
           items.append(thisitem)
   return bigsep.join(items)

def capWords(text):
   text_split = text.lower().split()
   text_list = [x.capitalize() for x in text_split]
   return ' '.join(text_list)

def capSentences(text):
   text_split = text.lower().split('.')
   text_list = [x.capitalize().strip() for x in text_split]
   return '. '.join(text_list)

def getPrettyText(soup):
   if soup is None:
       return ''
   text_html = str(soup)
   # prettify to break lines like HTML
   text_html = re.sub(r'</?p.*?>', '<br/>', text_html)
   text_html = re.sub(r'<li.*?>', '<br/>* ', text_html)    # text bullet
   text_html = re.sub(r'</li.*?>', '', text_html)
   text_html = text_html.replace("\n", "<br/>")
   text_soup = BeautifulSoup(text_html)
   text_line = ''
   text_lines = []
   pad_chars_re = re.compile(r'\s')
   for elem in text_soup.recursiveChildGenerator():
       if isinstance(elem, types.StringTypes) and not isinstance(elem, (Comment, ProcessingInstruction)):
           first_pad = ' ' if pad_chars_re.match(elem.string[:1]) else ''
           last_pad = ' ' if pad_chars_re.match(elem.string[-1:]) else ''
           clean_text = cleanWhitespace(elem.string)
           text_line += first_pad + clean_text + last_pad
       elif hasattr(elem, 'name') and elem.name == 'br':
           text_line = cleanWhitespace(text_line.strip())
           if len(text_line) > 0:
               text_lines.append(text_line)
           text_line = ''
   text_line = cleanWhitespace(text_line.strip())
   if len(text_line) > 0:
       text_lines.append(text_line)
   pretty_text = '\n'.join(text_lines)
   return pretty_text


class URLOpenThread(Thread):
    def __init__(self, url, urlopen=urllib2.urlopen):
        self.url = url
        self.urlopen = urlopen
        Thread.__init__(self)
    def run(self):
        self.page = self.urlopen(self.url).read()

def seqSoup(S):
   return BeautifulSoup(''.join(map(str,S)))

def getTagPosition(tag):
   pos = []
   while tag != None:
       # doesn't automatically get text for some reason...
       offset = len(tag.findPreviousSiblings(text=False)) + \
           len(tag.findPreviousSiblings(text=True))
       pos.insert(0, offset)
       tag = tag.parent
   return pos

def beforeSoup(soup, end):
   new_soup = BeautifulSoup(str(soup))
   end_pos = getTagPosition(end)
   end_tag = new_soup.find(lambda tag: getTagPosition(tag) == end_pos)
   level_last_tag = end_tag
   while level_last_tag is not None:
       for rm_tag in level_last_tag.findNextSiblings():
           rm_tag.extract()
       # doesn't automatically get text for some reason...
       for rm_tag in level_last_tag.findNextSiblings(text=True):
           rm_tag.extract()
       level_last_tag = level_last_tag.parent
   end_tag.extract()
   return new_soup

def parseDate(datestr, yr=None, end=False):
   get_formatted = (lambda d: time.strftime('%F', d))

   for format in ['%B %d', '%b %d', '%B', '%b', '%m/%d']:
       try:
           full_datestr = datestr
           if yr is not None:
               if format == '%m/%d':
                   full_datestr += '/%d'%yr
               else:
                   full_datestr += ' %d'%yr
           if format == '%m/%d':
               format += '/%Y'
           else:
               format += ' %Y'
           dateobj = time.strptime(full_datestr, format)
           if end and format.lower() == '%b':
               # get last day instead of first
               e_yr, e_mo = dateobj[:2]
               _, last_day = calendar.monthrange(e_yr, e_mo)
               dateobj = list(dateobj)
               dateobj[2] = last_day
               dateobj = tuple(dateobj)
           return get_formatted(dateobj)
       except ValueError:
           pass
   memorial_re = re.compile(r'Memorial Day', re.I)
   if memorial_re.search(datestr) and yr is not None:
       last_weekday = datetime.date(yr, 5, 31).weekday()
       mon_date = 31 - last_weekday
       return get_formatted(datetime.date(yr, 5, mon_date).timetuple())
   labor_re = re.compile(r'Labor Day', re.I)
   if labor_re.search(datestr) and yr is not None:
       first_weekday = datetime.date(yr, 9, 1).weekday()
       if first_weekday == 0:
           mon_date = 1
       else:
           mon_date = 1 + 7 - first_weekday
       return get_formatted(datetime.date(yr, 9, mon_date).timetuple())
   m = re.search(r'Mid(?:-|\s+)(\w+)', datestr, re.I)
   if m is not None:
       if yr is None:
           yr = int(datestr.rsplit(None, 1)[1])
       month_name = m.group(1)
       for format in ['%B', '%b']:
           try:
               month = time.strptime(month_name, format)[1]
               _, last_day = calendar.monthrange(1900, month)
               dateobj = datetime.date(yr, month, last_day / 2)
               return get_formatted(dateobj.timetuple())
           except ValueError:
               pass
   return None

def fixTextCase(text):
   cap_next = True
   letters = list(text.lower())
   for i in xrange(len(letters)):
       letter = letters[i]
       if letter == '.':
           cap_next = True
       elif cap_next and letter.isalpha():
           letters[i] = letter.upper()
           cap_next = False
   return ''.join(letters)

def unique(S):
   result = []
   for s in S:
       if s not in result:
           result.append(s)
   return result

def dateRange(start_month, start_day, end_month, end_day):
   """Return range of dates as tuple of two Y-m-d strings.
   If end date occurs earlier than start date, advance end
   of the range to the next year."""
   now = datetime.date.today()
   start_date = datetime.date(now.year, start_month, start_day)
   end_date = datetime.date(now.year, end_month, end_day)
   if end_date <= start_date:
       end_date = datetime.date(now.year + 1, end_month, end_day)

   return start_date.strftime('%F'), end_date.strftime('%F')
