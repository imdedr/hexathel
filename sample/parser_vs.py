from webparser import WebParser
from selector import Selector
from helper import urlhelper

class parser_vs(WebParser):

    def __init__(self):
        super(parser_vs, self).__init__()

    def parse( self, url, html ):
        sel = Selector( html )
        link = sel.xpath('//div[@class="menu_block"]/ul/li/a/@href')

        tmp = []

        for u in link:
            if( u.find('www.gohappy.com.tw') != -1 ):
                tmp.append(u)
            else:
                tmp.append('http://www.gohappy.com.tw' + u)

        return True, tmp
