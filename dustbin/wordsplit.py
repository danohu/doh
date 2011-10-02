#!/usr/bin/env python

"""http://thenoisychannel.com/2011/08/08/retiring-a-great-interview-problem/"""

#words = set(('on', 'one', 'two', 'three', 'apple', 'pie'))
words = set(('a', 'aa', 'aaa', 'aaaa', 'aab'))

ticks = 1
known_results = {'ac' : ['foo']}

def splitter(text):
    global ticks
    global known_results
    ticks += 1
    if text in known_results:
        yield known_results[text]
    orig_text = text
    print('trying to split %s' % text)
    trialword = ''
    while text:
        trialword, text = (trialword + text[0], text[1:])
        if trialword in words:
            #if not tex:
            #    yield [trialword]
            try:
                result = [trialword]
                if text:
                    result += splitter(text).next()
                known_results[orig_text] = result
                yield(result)
            except StopIteration:
                print('backtracking')
                pass

def callsplitter(text):
    global ticks
    ticks = 0
    try:
        result = ' '.join(splitter(text).next())
        print('solved in %s ticks' % ticks)
        return result
    except StopIteration:
        print('abandoned in %s ticks' % ticks)
        return None
