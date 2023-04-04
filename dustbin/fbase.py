#!/usr/bin/env python

from freebase.api import HTTPMetawebSession, MetawebError

session = HTTPMetawebSession('www.freebase.com')

def listValues(freebase_type, values = ('name'), limit = 100):
    """Select certain properties from all members of a particular category
    on freebase"""
    querydict = {'type' : freebase_type, 'limit' : limit}
    for value in values:
        querydict[value] = None
    results = []
    for item in session.mqlread([querydict]):
        results.append(dict((k,v) for k,v in item.iteritems() if k in values))
    return results

