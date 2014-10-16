import lxml
import lxml.html

class Selector(object):

    lxml_object = None

    def __init__(self, html):
        super(Selector, self).__init__()
        self.lxml_object = lxml.html.fromstring( html )

    def xtree( self, html ):
        self.lxml_object = lxml.html.fromstring( html )

    def xpath( self, path ):
        return self.lxml_object.xpath( path )
