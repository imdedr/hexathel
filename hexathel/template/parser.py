from webparser import WebParser
from selector import Selector
from helper import urlhelper

class parser_{name}(WebParser):

    # Initial Parser
    def __init__(self):
        super(parser_{name}, self).__init__()

    # Parser Main Block
    def parse( self, url, html ):

        # Create XPath 
        sel = Selector( html )

        # Return State, New Link
        return True, []