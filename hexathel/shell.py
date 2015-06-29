import code
import urllib
import urllib2
import argparse
import imp
import sys
import os
import ConfigParser

def execute():
    from selector import Selector
    parser = argparse.ArgumentParser()
    parser.add_argument('-u', dest='url', type=str)
    parser.add_argument('-m', dest='method', type=str)
    parser.add_argument('-p', dest='payload', type=str)
    parser.add_argument('-t', dest='test_mode', action='store_const', const=1)
    parser.add_argument('-c', dest='config_load', action='store_const', const=1)
    args = parser.parse_args()
    url = args.url
    method = args.method
    payload = args.payload
    config_load = args.config_load
    test_mode = args.test_mode

    global mod_parser_path
    global mod_parser_instance
    global engine_path
    global config

    html = ''
    sel = None

    mod_parser_path = ''
    mod_parser_instance = None
    engine_path = os.path.dirname( os.path.abspath(__file__) )

    config = dict()

    def getUrl( url, vals = {} ):
        data = urllib.urlencode(vals)
        headers = { 'User-Agent' : 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1847.131 Safari/537.36' }
        if( vals == {} ):
            req = urllib2.Request(url=url, headers=headers)
        else:
            req = urllib2.Request(url, data, headers)
        response = urllib2.urlopen(req)
        return response.read()

    def loadParser( path ):
        global mod_parser_path
        global mod_parser_instance
        global config
        dir_path = os.path.dirname(os.path.abspath(path))
        sys.path.append(dir_path)
        mod_parser_path = path
        mod_parser_instance = __import__( path.split('/')[-1].split('.')[0], globals(), locals() )
        mod_parser_instance = getattr( mod_parser_instance, path.split('/')[-1].split('.')[0] )()
        
        if( test_mode == 1 ):
            mod_parser_instance.test_flag = True

        if( config_load == 1 ):
            mod_parser_instance.config = config['env']

    def reloadParser():
        global mod_parser_path
        global mod_parser_instance
        dir_path = os.path.dirname(os.path.abspath(mod_parser_path))
        del(sys.modules[mod_parser_path.split('/')[-1].split('.')[0]]) 
        mod_parser_instance = __import__( mod_parser_path.split('/')[-1].split('.')[0], globals(), locals() )
        mod_parser_instance = getattr( mod_parser_instance, mod_parser_path.split('/')[-1].split('.')[0] )()
        if( test_mode == 1 ):
            mod_parser_instance.test_flag = True

    def testParser():
        global mod_parser_path
        global mod_parser_instance
        print mod_parser_instance.parse(url, html)

    def loadConfig():
        global mod_parser_path
        global engine_path
        global config
        config['env'] = dict()

        # Read Path
        config_path = os.path.join( engine_path , 'template' ,'config.conf' )
        config_loader = ConfigParser.ConfigParser()
        config_loader.read( config_path )

        for sec in config_loader.sections():
            tmp = dict()
            for item in config_loader.items(sec):
                tmp[item[0]] = item[1]
            config[sec] = tmp

        # Check the user config file
        if( os.path.exists( os.path.join( mod_parser_path , 'config.conf' ) ) ):
            config_path = os.path.join( mod_parser_path , 'config.conf' )
            config_loader = ConfigParser.ConfigParser()
            config_loader.read( config_path )
            for sec in config_loader.sections():
                tmp = dict()
                for item in config_loader.items(sec):
                    tmp[item[0]] = item[1]
                config[sec] = tmp

    if ( method == None ):
        method = 'get'

    if( url != None ):
        html = getUrl(url)
        sel = Selector(html)
    else:
        print 'Url is missing.'
        return

    if( test_mode == 1 ):
        print '[Test Mode]'

    if ( config_load == 1 ):
        loadConfig()

    code.interact(banner= "Hexathel Spider Interact Tool\n[Object] sel : XPath Tool\n[Function] loadParser(path) : Load Parser\n[Function] reloadParser() : ReLoad Parser\n[Function] testParser(path) : Testing Parser", local=locals())

if __name__ == "__main__":
    execute()
