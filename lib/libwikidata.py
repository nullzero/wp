# -*- coding: utf-8  -*-
"""
Play with wikidata site.
"""

__version__ = "1.0.1"
__author__ = "Sorawee Porncharoenwase"

import json, htmllib, time, traceback
import preload
import pwikipedia as pywikibot
import config, query

def createitem(datapage, summary=None, minorEdit=True,
               token=None, newToken=False, sysop=False, captcha=None,
               botflag=True, maxTries=-1, value={}):
    """
    Create new item.
    """
    return edititem(datapage, summary, minorEdit, token, newToken, 
                sysop, captcha, botflag, maxTries, value, iscreate=True)

def setitem(datapage, summary=None, minorEdit=True,
               token=None, newToken=False, sysop=False, captcha=None,
               botflag=True, maxTries=-1, value={}):
    """
    Set an item. This mean all old values will be cleared.
    """
    return edititem(datapage, summary, minorEdit, token, newToken, 
                sysop, captcha, botflag, maxTries, value, isset=True)
                   

def edititem(datapage, summary=None, minorEdit=True,
               token=None, newToken=False, sysop=False, captcha=None,
               botflag=True, maxTries=-1, value={}, iscreate=False, isset=False):
    """
    Just edit an item.
    """
    retry_attempt = 0
    retry_delay = 1
    dblagged = False
    newPage = True
    params = {
        'summary': datapage._encodeArg(summary, 'summary'),
        'format': 'jsonfm',
        'action': 'wbeditentity',
        'data': json.dumps(value),
    }
    print json.dumps(value)
    if __debug__:
        raw_input("ok?... ")
    if token:
        params['token'] = token
    else:
        params['token'] = datapage.site().getToken(sysop = sysop)
    if config.maxlag:
        params['maxlag'] = str(config.maxlag)
    if botflag:
        params['bot'] = 1
    if captcha:
        params['captchaid'] = captcha['id']
        params['captchaword'] = captcha['answer']
    if iscreate:
        params['createonly'] = 1
    else:
        datapage.get()
        params['id'] = datapage.title()
        params['nocreate'] = 1
    if isset:
        params['clear'] = 1
    while True:
        if (maxTries == 0):
            raise pywikibot.MaxTriesExceededError()
        maxTries -= 1
        # Check whether we are not too quickly after the previous
        # putPage, and wait a bit until the interval is acceptable
        if not dblagged:
            pywikibot.put_throttle()
        pywikibot.output(u'Editing page %s via API' % datapage._originTitle)
        try:
            response, data = query.GetData(params, datapage.site(),
                                           sysop=sysop, back_response=True)
            if isinstance(data, basestring):
                raise KeyError
        except httplib.BadStatusLine, line:
            raise pywikibot.PageNotSaved('Bad status line: %s' % line.line)
        except pywikibot.ServerError:
            pywikibot.output(u''.join(traceback.format_exception(*sys.exc_info())))
            retry_attempt += 1
            pywikibot.output(u'Got a server error when putting %s; will retry in %i minute%s.'
                   % (datapage, retry_delay, retry_delay != 1 and "s" or ""))
            time.sleep(30)
            continue
        except ValueError: # API result cannot decode
            output(u"Server error encountered; will retry in %i minute%s."
                   % (retry_delay, retry_delay != 1 and "s" or ""))
            time.sleep(30)
            continue
        # If it has gotten this far then we should reset dblagged
        dblagged = False
        # Check blocks
        datapage.site().checkBlocks(sysop = sysop)
        # A second text area means that an edit conflict has occured.
        if response.code == 500:
            pywikibot.output(u"Server error encountered; will retry in %i minute%s."
                   % (retry_delay, retry_delay != 1 and "s" or ""))
            time.sleep(30)
            continue
        if 'error' in data:
            errorCode = data['error']['code']
            pywikibot.output(u'Got an unknown error when putting data: %s' %errorCode)
        else:
            if unicode(data['success']) == u"1":
                print 302, response.msg, data['success']
                return 302, response.msg, data['success']
        print response.code, response.msg, data
        return response.code, response.msg, data
