# -*- coding: utf-8 -*-

import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

try: from lib import preload
except:
    print "Cannot import preload. Exit!"
    sys.exit()

import wikipedia as pywikibot
from pywikipedia.redirect import RedirectGenerator, RedirectRobot

if __name__ == "__main__":
    pywikibot.handleArgs("-log")
    pywikibot.output(u"'redirect script' is invoked. (%s)" % libdate.getTime())
    gen = RedirectGenerator(namespaces = [0], use_api = True)
    bot = RedirectRobot(action = 'both', generator = gen, always = True)
    bot.run()
    pywikibot.output(u"'redirect script' terminated. (%s)" % libdate.getTime())
    pywikibot.stopme()
