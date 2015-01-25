import browser

class WebParser(object):

    url = ""
    db = None
    log = None

    config = dict()

    test_flag = False

    mq = None

    def __init__(self):
        pass

    def init(self, url):
        pass

    def setBrowser(self, url):
        return browser.Mozilla50, {}

    def parse( self, url, html ):
        return True, []
        
