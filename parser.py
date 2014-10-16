import browser

class Parser(object):

    url = ""
    db = None

    def __init__(self):
        pass

    # Maybe need to do something....
    def init(self, url):
        print 'Super:init:' + url

    def setBrowser(self, url):
        return browser.Mozilla50

    def parse( self, url, html ):
        print "Super:Url:", url
        print "Super:Html:", html 
        return True, []
        