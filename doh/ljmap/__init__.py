"""
Display links between the top LJs in Russia
"""
from BeautifulSoup import BeautifulSoup
import urllib2
import re

# regex to match any livejournal name
# XXX: ideally, we should also handle users with the old-style
# urls livejournal.com/user/fubar
ljre = re.compile('http://(.*)\.livejournal.com')

def y_topblogs_onepage(pagenum):
    url = 'http://blogs.yandex.ru/top/lj/?page=%s' % pagenum
    pagetext = urllib2.urlopen(url).read()
    soup = BeautifulSoup(pagetext)
    ljnames = []
    for url in soup.findAll('a', href=ljre):
        ljnames.append(ljre.search(url['href']).group(1))
    return sorted(set(ljnames))

def followers_from_ljname(ljname):
    friends = set()
    profileurl = 'http://%s.livejournal.com/profile?mode=full' % ljname
    soup = BeautifulSoup(urllib2.urlopen(profileurl).read())
    frienddiv = soup.find('div', id='fofs_body')
    for link in frienddiv.findAll('a', href=ljre):
        friends.add(ljre.search(link['href']).group(1))
    return sorted(friends)

