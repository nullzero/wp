# -*- coding: utf-8  -*-

import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from pywikipedia.redirect import RedirectGenerator, RedirectRobot

if __name__ == "__main__":
    pywikibot.handleArgs("-log")
    pywikibot.output(u"'redirect script' is invoked. (%s)" % preload.getTime())
    gen = RedirectGenerator(namespaces = [0], use_api = True)
    bot = RedirectRobot(action = 'both', generator = gen, always = True)
    bot.run()
    pywikibot.output(u"'redirect script' terminated. (%s)" % preload.getTime())
    pywikibot.stopme()
