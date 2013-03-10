# -*- coding: utf-8  -*-

def importiw(self, summary=None, sysop=False, botflag=True, dic={}):
    retry_attempt = 0
    retry_delay = 1
    dblagged = False
    newPage=True
    params = {
        'summary': self._encodeArg(summary, 'summary'),
        'format': 'jsonfm',
        'action': 'wbeditentity'
    }
    params['data'] = repr(dic).replace(u"'", u'"')
    params['token'] = self.site().getToken(sysop = sysop)
    if config.maxlag:
        params['maxlag'] = str(config.maxlag)
    if botflag:
        params['bot'] = 1

    while True:
        # Check whether we are not too quickly after the previous
        # putPage, and wait a bit until the interval is acceptable
        if not dblagged:
            put_throttle()
        output(u'Creating page %s via API' % self._originTitle)
        params['createonly'] = 1
        try:
            response, data = query.GetData(params, self.site(),
                                           sysop=sysop, back_response=True)
            if isinstance(data,basestring):
                raise KeyError
        except httplib.BadStatusLine, line:
            raise PageNotSaved('Bad status line: %s' % line.line)
        except ServerError:
            output(u''.join(traceback.format_exception(*sys.exc_info())))
            retry_attempt += 1
            if retry_attempt > config.maxretries:
                raise
            output(u'Got a server error when putting %s; will retry in a minute.' % 
                    (self))
            time.sleep(30)
            continue
        except ValueError: # API result cannot decode
            output(u"Server error encountered; will retry in a minute.")
            time.sleep(30)
            continue
        # If it has gotten this far then we should reset dblagged
        dblagged = False
        # Check blocks
        self.site().checkBlocks(sysop = sysop)
        # A second text area means that an edit conflict has occured.
        if response.code == 500:
            output(u"Server error encountered; will retry in a minute.")
            time.sleep(30)
            retry_delay *= 2
            if retry_delay > 30:
                retry_delay = 30
            continue
        if 'error' in data:
            errorCode = data['error']['code']
            output(u'Got an unknown error when putting data: %s' %errorCode)
        else:
            if data['success'] == u"1":
                return 302, response.msg, data['success']
        return response.code, response.msg, data
