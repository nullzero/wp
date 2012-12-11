from pywikipedia.redirect import RedirectGenerator, RedirectRobot

if __name__ == "__main__":
    gen = RedirectGenerator(namespaces = [0], use_api = True)
    bot = RedirectRobot(action = 'both', generator = gen, always = True)
    bot.run()
