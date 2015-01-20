from webparser import WebParser
from selector import Selector
from helper import urlhelper

class parser_home(WebParser):

    def __init__(self):
        super(parser_home, self).__init__()

    def parse( self, url, html ):

        # This site has a Sitemap so parser will use Sitemap
        # The Url http://www.gohappy.com.tw/ is a standard start key url

        if( url == 'http://www.gohappy.com.tw/' ):

            # This Page will redriect to sitemap
            if( self.test_flag ):
                print 'Hihi'
                print self.config['name']
                return False, []

            return True, ['http://www.gohappy.com.tw/intro/sitemap.html']

        elif( url == 'http://www.gohappy.com.tw/intro/sitemap.html' ):

            #Parse Sitemap
            sel = Selector( html )
            block = sel.xpath('//div[@class="sitemap_group"]')

            #remove some Block

            tmp = [] # Create a tmp Url List

            for __block in block:
                #print __block.xpath('dl/dt/a/@title')[0]
                level1 = __block.xpath('dl/dd/ul/li/a/@href')
                level2 = __block.xpath('dl/dd/div/ul/li/a/@href')

                for u in level1:
                    if ( u != '' ):
                        if( u.find('www.gohappy.com.tw') != -1 ):
                            tmp.append(u)
                        else:
                            tmp.append( 'http://www.gohappy.com.tw' + u )

                for u in level2:
                    if ( u != '' ):
                        if( u.find('www.gohappy.com.tw') != -1 ):
                            tmp.append(u)
                        else:
                            tmp.append( 'http://www.gohappy.com.tw' + u )

            return True, tmp
            
        else:
            return False, []


        
